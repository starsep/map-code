plugins {
    kotlin("jvm") version "1.8.0"
    application
}

group = "com.starsep"
version = "1.0"

repositories {
    mavenCentral()
}

dependencies {
    implementation("com.geodesk:geodesk:0.1.4")
    testImplementation(kotlin("test"))
}

tasks.test {
    useJUnitPlatform()
}

kotlin {
    jvmToolchain(17)
}

application {
    mainClass.set("MainKt")
}