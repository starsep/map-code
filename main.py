from pathlib import Path

from geodesk import Features

mazowieckie = Features("data/mazowieckie")
warsaw = mazowieckie(
    "a[admin_level=8][population>50000][boundary=administrative][name=Warszawa]"
).one
buildings = mazowieckie("a[building=apartments]").within(warsaw)
with Path("generated/buildings.js").open("w") as f:
    f.write("const buildings = [\n")
    for building in buildings:
        levels = max(building.num("building:levels"), 1)
        estimatedBuildingArea = int(building.area * levels)
        if estimatedBuildingArea > 100:
            f.write(f"[{building.lat}, {building.lon}, {estimatedBuildingArea}],\n")
    f.write("];\n")
