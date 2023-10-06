import com.geodesk.feature.FeatureLibrary
import com.geodesk.feature.Filters
import java.io.File

fun main() {
    val library = FeatureLibrary("data/mazowieckie.gol")
    val cities = library.select("a[admin_level=8][population>50000]")
    val warsaw = cities.select("*[name=Warszawa]").first()
    val buildings = library.select("a[building=apartments]").select(Filters.intersects(warsaw))
    val outputFile = File("../generated/buildings.js")
    val writer = outputFile.bufferedWriter()
    writer.write("const buildings = [\n")
    for (building in buildings) {
        val buildingLevels = building.tag("building:levels").toIntOrNull() ?: 1
        val estimatedBuildingArea = (building.area() * buildingLevels).toInt()
        if (estimatedBuildingArea > 100) {
            writer.write("[${building.lat()}, ${building.lon()}, $estimatedBuildingArea],\n")
        }
    }
    writer.write("];\n")
    writer.close()
}