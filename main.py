import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List

import geojson
import httpx
import numpy as np
from geodesk import Features, Coordinate
from geojson import FeatureCollection, Feature
from jinja2 import Environment, PackageLoader
from scipy.spatial import Voronoi
from shapely import Polygon, LinearRing, Point

mazowieckie = Features("data/mazowieckie")
warsaw = mazowieckie(
    "a[admin_level=8][population>50000][boundary=administrative][name=Warszawa]"
).one
outputDir = Path("output")
templatesDir = Path("templates")
javascriptDir = Path("js")
outputJavascriptDir = outputDir / "js"


@dataclass
class GeneratedMap:
    mapDirName: str
    scriptName: str
    title: str
    generateFunction: Callable[["GeneratedMap"], None]

    @property
    def mapDir(self) -> Path:
        return outputDir / self.mapDirName

    @property
    def dataPath(self) -> Path:
        return self.mapDir / "data.js"


def generateApartmentsHeatmap(generatedMap: GeneratedMap):
    buildings = mazowieckie("a[building=apartments]").within(warsaw)
    with generatedMap.dataPath.open("w") as f:
        f.write("export const buildings = [\n")
        for building in buildings:
            levels = max(building.num("building:levels"), 1)
            estimatedBuildingArea = int(building.area * levels)
            if estimatedBuildingArea > 100:
                f.write(f"[{building.lat}, {building.lon}, {estimatedBuildingArea}],\n")
        f.write("];\n")


def generateBicycleParkingHeatmap(generatedMap: GeneratedMap):
    bicycleParkings = mazowieckie(
        "*[amenity=bicycle_parking][bicycle_parking=stands]"
    ).within(warsaw)
    with generatedMap.dataPath.open("w") as f:
        f.write("export const bicycleParkings = [\n")
        for bicycleParking in bicycleParkings:
            # capacity = min(max(bicycleParking.num("capacity"), 2)
            capacity = 1
            f.write(f"[{bicycleParking.lat}, {bicycleParking.lon}, {capacity}],\n")
        f.write("];\n")


def generateVeturiloVoronoi(generatedMap: GeneratedMap):
    delta = 0.001
    latDistance = Point(warsaw.centroid).distance(
        Point(Coordinate(lat=warsaw.centroid.lat + delta, lon=warsaw.centroid.lon))
    )
    lonDistance = Point(warsaw.centroid).distance(
        Point(Coordinate(lat=warsaw.centroid.lat, lon=warsaw.centroid.lon + delta))
    )
    scalingFactor = latDistance / lonDistance
    veturiloStations = mazowieckie(
        "*[amenity=bicycle_rental][network=Veturilo]"
    ).within(warsaw)
    points = np.array(
        [[station.lat * scalingFactor, station.lon] for station in veturiloStations]
    )
    vor = Voronoi(points)
    vorVertices = [Coordinate(lat=v[0] / scalingFactor, lon=v[1]) for v in vor.vertices]
    voronoiRegionOutput = []
    for region in vor.regions:
        coords = []
        for index in region:
            if index != -1:
                coords.append(vorVertices[index])
        if len(coords) < 3:
            continue
        ring = Polygon(LinearRing(coords))
        clippedRegion = ring & warsaw.shape
        clippedRegionPolygon = (
            clippedRegion
            if clippedRegion.geom_type == "Polygon"
            else clippedRegion.convex_hull
        )
        voronoiRegionOutput.append(
            [
                (point.lat, point.lon)
                for point in map(
                    lambda c: Coordinate(*c), clippedRegionPolygon.exterior.coords
                )
            ]
        )
    veturiloOutput = [
        (station.lat, station.lon, station.name) for station in veturiloStations
    ]
    with generatedMap.dataPath.open("w") as f:
        f.write("export const veturilo = \n")
        f.write(json.dumps(veturiloOutput))
        f.write(";\n")
        f.write("export const lines = [\n")
        f.write(json.dumps(voronoiRegionOutput))
        f.write("];\n")


def fetchIsochrone(point: Coordinate):
    url = f'http://localhost:8989/isochrone?profile=foot&point={point.lat},{point.lon}&distance_limit=500&buckets=1'
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()["polygons"]

def generateSubwayAccess(generatedMap: GeneratedMap):
    subwayStations = mazowieckie("*[station=subway]")
    features = []
    for station in subwayStations:
        data = fetchIsochrone(station.centroid)
        features.append(Feature(geometry=Point(station.lon, station.lat)))
        features.extend(data)
    # features.sort(key=lambda feature: feature["properties"]["bucket"])
    with (generatedMap.mapDir / "data.geojson").open("w") as f:
        geojson.dump(FeatureCollection(features), f)


def generateIndex(generatedMaps: List[GeneratedMap]):
    environment = Environment(loader=PackageLoader("main", "template"))
    template = environment.get_template("index.html.j2")
    with (outputDir / "index.html").open("w", encoding="utf-8") as f:
        f.write(template.render(dict(generatedMaps=generatedMaps)))


def generateMap(generatedMap: GeneratedMap):
    environment = Environment(loader=PackageLoader("main", "template"))
    template = environment.get_template("map.html.j2")
    with (generatedMap.mapDir / "index.html").open("w", encoding="utf-8") as f:
        f.write(template.render(dict(title=generatedMap.title)))
    shutil.copy(
        javascriptDir / generatedMap.scriptName, generatedMap.mapDir / "index.js"
    )


def main():
    generatedMaps = [
        GeneratedMap(
            mapDirName="mieszkania",
            scriptName="apartments.js",
            title="Warszawa: Heatmapa powierzchni mieszkań",
            generateFunction=generateApartmentsHeatmap,
        ),
        GeneratedMap(
            mapDirName="stojaki",
            scriptName="bicycleStands.js",
            title="Warszawa: Heatmapa stojaków rowerowych",
            generateFunction=generateBicycleParkingHeatmap,
        ),
        GeneratedMap(
            mapDirName="veturilo-voronoi",
            scriptName="veturiloVoronoi.js",
            title="Warszawa: Diagram Woronoja stacji Veturilo",
            generateFunction=generateVeturiloVoronoi,
        ),
        GeneratedMap(
            mapDirName="metro",
            scriptName="subway.js",
            title="Warszawa: Dostępność stacji metra",
            generateFunction=generateSubwayAccess,
        ),
    ]
    generateIndex(generatedMaps)
    for generatedMap in generatedMaps:
        generatedMap.mapDir.mkdir(exist_ok=True)
        generatedMap.generateFunction(generatedMap)
        generateMap(generatedMap)


if __name__ == "__main__":
    main()
