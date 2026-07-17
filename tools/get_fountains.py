# -*- coding: utf-8 -*-

# estas estan incluidas con Phyton
import math
import sys
import glob
import re
import json
import os
import shutil
import subprocess

# ============================================================
# CHECK DEPENDENCIAS
# ============================================================
try:
    import osmium
except ImportError:
    print()
    print("ERROR: pyosmium no está instalado")
    print()
    print("Instalar con:")
    print("pip install osmium")
    print()
    sys.exit(1)

# ============================================================
# FUNCIONES
# ============================================================
def get_screen_size(device):

    sizes = {
        "edge130plus": [200, 303, "rectangle"],
        "edgemtb": [240, 320, "rectangle"],
        "edgeexplore2": [240, 400, "rectangle"],
        "edge530": [246, 322, "rectangle"],
        "edge540": [246, 322, "rectangle"],
        "edge830": [246, 322, "rectangle"],
        "edge840": [246, 322, "rectangle"],
        "edge1030": [282, 470, "rectangle"],
        "edge1030plus": [282, 470, "rectangle"],
        "edge1030bontrager": [282, 470, "rectangle"],
        "edge1040": [282, 470, "rectangle"],
        "edge550": [420, 600, "rectangle"],
        "edge850": [420, 600, "rectangle"],
        "edge1050": [480, 800, "rectangle"],
        "vivoactive5": [390, 390, "circle"],
    }
    return sizes.get(
        device,
        [266, 366]
    )
def check_device(device):

    valid_devices = [
        "edge1030",
        "edge1030bontrager",
        "edge1030plus",
        "edge1040",
        "edge1050",
        "edge130plus",
        "edge530",
        "edge540",
        "edge550",
        "edge830",
        "edge840",
        "edge850",
        "edgeexplore2",
        "edgemtb",
        "vivoactive5",
    ]

    return device.lower() in valid_devices

# ============================================================
# CONFIG
# ============================================================

MAX_POINTS =        1800    #para garantizar que el proyecto data field pueda compilar

# ============================================================
# ARGUMENTOS
# ============================================================

if len(sys.argv) != 7:
    print("Uso:")
    print("py get_fountains.py <lat> <lon> <radio-km> <filtro-km> <nombre> <dispositivo>")
    print("Ejemplo:")
    print("py get_fountains.py 43.1336 -1.6664 100 0.5 example edge530")
    sys.exit(1)

CENTER_LAT =        float(sys.argv[1])
CENTER_LON =        float(sys.argv[2])
RADIUS_KM =         float(sys.argv[3])
MIN_DISTANCE_KM =   float(sys.argv[4])       #distancia min entre fuentes para eliminar duplicados cercanos
NAME =              sys.argv[5]
DEVICE =            sys.argv[6]
FILE_OUT = NAME

if(check_device(DEVICE) == False):
    print("Dispositivo no valido. Dispositivos validos:")
    print("  edge1030, edge1030bontrager, edge1030plus, edge1040, edge1050,")
    print("  edge130plus, edge530, edge540, edge550, edge830, edge840,")
    print("  edge850, edgeexplore2, edgemtb, vivoactive5")
    sys.exit(1)


pbf_files = glob.glob("*.osm.pbf")

if not pbf_files:
    print("No se encontraron ficheros .osm.pbf")
    sys.exit(1)

print()
print("Ficheros .osm.pbf encontrados:")


for pbf in pbf_files:
    print(f"  {pbf}")

# ============================================================
# BORRAR CARPETA TILES SI EXISTE
# ============================================================
TILES_DIR = os.path.join(
    "..",
    "source",
    "tiles"
)
if os.path.exists(TILES_DIR):
    shutil.rmtree(TILES_DIR)

coords = []


# ============================================================
# DISTANCIA
# ============================================================

def distance_km(lat1, lon1, lat2, lon2):

    R = 6371.0

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c

# ============================================================
# HANDLER
# ============================================================

class WaterHandler(osmium.SimpleHandler):

    def node(self, n):

        tags = n.tags

        is_drinking = (
            tags.get("amenity")
            == "drinking_water"
        )

        is_spring = (
            tags.get("natural")
            == "spring"
        )

        if not (is_drinking or is_spring):
            return

        try:

            lat = n.location.lat
            lon = n.location.lon

        except Exception:
            return

        dist = distance_km(
            CENTER_LAT,
            CENTER_LON,
            lat,
            lon
        )

        if dist <= RADIUS_KM:

            coords.append(
                (lat, lon)
            )

# ============================================================
# LEER PBF
# ============================================================

for pbf_file in pbf_files:

    #print()
    print(f"Procesando {pbf_file}...")

    handler = WaterHandler()

    handler.apply_file(
        pbf_file,
        locations=True
    )

print(
    f"Fuentes encontradas: {len(coords)}"
)

# ============================================================
# ELIMINAR DUPLICADOS EXACTOS
# ============================================================

unique = set()
filtered = []

for lat, lon in coords:

    key = (
        round(lat, 6),
        round(lon, 6)
    )

    if key not in unique:

        unique.add(key)

        filtered.append(
            (lat, lon)
        )

coords = filtered

print(
    f"Fuentes Unicas: {len(coords)}"
)

# ============================================================
# FILTRAR POR DISTANCIA MÃÂNIMA
# ============================================================

#print(f"Eliminando fuentes a menos de {MIN_DISTANCE_KM} km")

filtered = []

for lat, lon in coords:

    keep = True

    for lat2, lon2 in filtered:

        if distance_km(
            lat,
            lon,
            lat2,
            lon2
        ) < MIN_DISTANCE_KM:

            keep = False
            break

    if keep:

        filtered.append(
            (lat, lon)
        )

coords = filtered

print(
    f"Fuentes filtro {MIN_DISTANCE_KM} KM: "
    f"{len(coords)}"
)


if len(coords) > MAX_POINTS:

    print(
        f"Limitando a {MAX_POINTS} "
        #f"fuentes mÃ¡s cercanas..."
    )

    coords.sort(
        key=lambda p: distance_km(
            CENTER_LAT,
            CENTER_LON,
            p[0],
            p[1]
        )
    )

    coords = coords[:MAX_POINTS]

print(
    f"Fuentes finales: "
    f"{len(coords)}"
)


def get_tile_name(lat, lon):

    lat_abs = abs(lat)
    lon_abs = abs(lon)

    lat_major = int(lat_abs)
    lat_decimal = int((lat_abs - lat_major) * 10)

    lon_major = int(lon_abs)
    lon_decimal = int((lon_abs - lon_major) * 10)

    text_lat_major = (
        f"m{lat_major}"
        if lat < 0
        else f"{lat_major}"
    )

    text_lon_major = (
        f"m{lon_major}"
        if lon < 0
        else f"{lon_major}"
    )

    return (
        f"f_"
        f"{text_lat_major}_{lat_decimal}_"
        f"{text_lon_major}_{lon_decimal}"
    )

# ============================================================
# GENERAR MC POR TILES
# ============================================================

os.makedirs(
    TILES_DIR,
    exist_ok=True
)
#os.makedirs(
 #   "tiles",
  #  exist_ok=True
#)

tiles = {}

for lat, lon in coords:

    tile_name = get_tile_name(
        lat,
        lon
    )

    if tile_name not in tiles:
        tiles[tile_name] = []

    tiles[tile_name].append(
        (lat, lon)
    )

for tile_name, points in tiles.items():

    output_file = os.path.join(
        TILES_DIR,#"tiles",
        f"{tile_name}.mc"
    )

    class_name = (
        tile_name
        .replace("-", "m")
        .replace(".", "_")
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(f"class {class_name} {{\n")
        f.write("    static function getFuentes() {\n")
        f.write("        return [\n")

        for lat, lon in points:

            f.write(
                f"            {lat:.7f}, {lon:.7f},\n"
            )

        f.write("        ];\n")
        f.write("    }\n")
        f.write("}\n")

    #print(f"{tile_name}.mc -> {len(points)} fuentes")


print(f"Tiles generados: {len(tiles)}")

# ============================================================
# GENERAR TILELOADER
# ============================================================

loader_file = os.path.join(
    TILES_DIR,#"tiles",
    "TileLoader.mc"
)

with open(
    loader_file,
    "w",
    encoding="utf-8"
) as f:

    f.write("class TileLoader {\n\n")

    f.write(
        "    static function getTileData(tileLatMajor, tileLatMinor, tileLonMajor, tileLonMinor) {\n\n"
    )

    generated = set()

    for tile_name in sorted(tiles.keys()):

        # f_43_3_-1_9
        name = tile_name.replace(
            "f_", ""
        )

        parts = name.split("_")

        if "m" in parts[0]:
            parts[0] = parts[0].replace("m", "")
            parts[0] = -int(parts[0])
        else:
            parts[0] = int(parts[0])

        if "m" in parts[2]:
            parts[2] = parts[2].replace("m", "")
            parts[2] = -int(parts[2])
        else:
            parts[2] = int(parts[2])

        lat_major = int(parts[0])
        lat_minor = int(parts[1])
        lon_major = int(parts[2])
        lon_minor = int(parts[3])

        class_name = (
            tile_name
            .replace("fountains_", "f_")
            .replace("-", "m")
            .replace(".mc", "")
        )

        key = (
            lat_major,
            lat_minor,
            lon_major,
            lon_minor
        )

        # evitar duplicar condiciones
        if key in generated:
            continue

        generated.add(key)

        f.write(
            f"        if ("
            f"tileLatMajor == {lat_major} && "
            f"tileLatMinor == {lat_minor} && "
            f"tileLonMajor == {lon_major} && "
            f"tileLonMinor == {lon_minor}"
            f") {{\n"
        )

        f.write(
            f"            return {class_name}.getFuentes();\n"
        )

        f.write(
            "        }\n\n"
        )

    f.write(
        "        return null;\n"
    )

    f.write(
        "    }\n"
    )

    f.write(
        "}\n"
    )

print(f"Tileloader.mc ok")

# ============================================================
# GENERAR CONFLOADER
# ============================================================

loader_file = os.path.join(
    TILES_DIR,#"tiles",
    "ConfLoader.mc"
)

SCREENX, SCREENY, SCREEN_SHAPE= get_screen_size(DEVICE)

with open(
    loader_file,
    "w",
    encoding="utf-8"
) as f:

    f.write("class ConfLoader {\n\n")

    f.write(
        "    static function getConfData() {\n"
    )
    f.write(
        "        return [\n"
    )
    f.write(
        f"            {MIN_DISTANCE_KM},\n"
    )
    f.write(
        f"            {RADIUS_KM},\n"
    )
    f.write(
        f"            \"{NAME}\",\n"
    )
    f.write(
        f"            \"{DEVICE}\",\n"
    )
    f.write(
        f"            {SCREENX},\n"
    )
    f.write(
        f"            {SCREENY},\n"
    )
    f.write(
        f"            \"{SCREEN_SHAPE}\",\n"
    )
    f.write(
        "        ];\n"
    )
    f.write(
        "    }\n"
    )
    f.write(
        "}\n"
    )

print(f"Confloader.mc ok")

# ============================================================
# GENERAR GEOJSON
# ============================================================

mc_files = glob.glob("../source/tiles/f_*.mc")

if not mc_files:
    print("No se encontraron ficheros .mc")
    exit()

features = []

for mc_file in mc_files:

    with open(
        mc_file,
        "r",
        encoding="utf-8"
    ) as f:

        content = f.read()

    m = re.search(
        r"return\s*\[(.*?)\];",
        content,
        flags=re.DOTALL
    )

    if not m:
        print(f"No se encontraron coordenadas en {mc_file}")
        continue

    nums = re.findall(r"-?\d+(?:\.\d+)?", m.group(1))

    if len(nums) % 2 != 0:
        print(f"ERROR en {mc_file}")
        print(m.group(1))
        continue

    for i in range(0, len(nums), 2):

        lat = float(nums[i])
        lon = float(nums[i + 1])

        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        lon,
                        lat
                    ]
                },
                "properties": {}
            }
        )

geojson = {
    "type": "FeatureCollection",
    "features": features
}

with open(
    "fountains.geojson",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        geojson,
        f,
        ensure_ascii=False,
        indent=2
    )

print(f"fountains.geojson ok ({len(features)} puntos)")

# ============================================================
# COMPILAR
# ============================================================
print()
print(f"Compilar fountains...")

sdk_download = "https://developer.garmin.com/connect-iq/sdk/"

sdk_root = os.path.join(
    os.environ["APPDATA"],
    "Garmin",
    "ConnectIQ",
    "Sdks"
)

sdks = sorted(
    glob.glob(
        os.path.join(
            sdk_root,
            "connectiq-sdk-*"
        )
    )
)

if not sdks:
    raise RuntimeError(
        "No se encontro ningun SDK Connect IQ , descargar: " + sdk_download
    )

sdk_dir = sdks[-1]

monkeybrains = os.path.join(
    sdk_dir,
    "bin",
    "monkeybrains.jar"
)

script_dir = os.path.dirname(
    os.path.abspath(__file__)
)
prj_dir = os.path.abspath(
    os.path.join(
        script_dir,
        ".."
    )
)

print("SDK path : " + sdk_dir)
print("Prj path : " + prj_dir)
print("Name     : " + NAME + ".prg")
print("Device   : " + DEVICE)

cmd = [
    "java",
    "-Xms1g",
    "-Dfile.encoding=UTF-8",
    "-Dapple.awt.UIElement=true",
    "-jar",
    rf"{monkeybrains}",
    "-o",
    rf"{prj_dir}\{NAME}.prg",
    "-f",
    rf"{prj_dir}\monkey.jungle",
    "-y",
    rf"{prj_dir}\developer_key",
    "-d",
    DEVICE,
    "-w"
]

result = subprocess.run(
    cmd,
    capture_output=True,
    text=True
)

print(result.stdout)

if result.returncode != 0:
    print(result.stderr)
    raise RuntimeError("Error compilando")

print()
print("================================")
print("FIN")
print("================================")