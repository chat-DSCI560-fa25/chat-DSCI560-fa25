from flask import Flask, render_template, jsonify
import csv, re

app = Flask(__name__)
CSV_FILE = "well_information.csv"

# Regex for DMS with direction
DMS = re.compile(
    r"(?P<deg>\d{1,3})\s*°\s*(?P<min>\d{1,2})['\s]+(?P<sec>\d{1,2}(?:\.\d+)?)?\s*\"?\s*(?P<dir>[NSEW])",
    re.IGNORECASE,
)
# Regex for decimal degrees with decimal point
DECIMAL = re.compile(r"(-?\d{1,3}\.\d+)")

# ND bounding box
LAT_MIN, LAT_MAX = 47.0, 49.5
LON_MIN, LON_MAX = -104.5, -96.5

def in_bounds(lat, lon):
    return LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX

def dms_to_decimal(m):
    deg = int(m.group("deg"))
    minutes = int(m.group("min"))
    seconds = float(m.group("sec")) if m.group("sec") else 0.0
    val = deg + minutes/60 + seconds/3600
    if m.group("dir").upper() in ("S", "W"):
        val = -val
    return val

def parse_lat(cell):
    if not cell: return None
    u = cell.upper()
    m = DMS.search(u)
    if m:
        val = dms_to_decimal(m)
        if -90 <= val <= 90: return val
    if "DEG" in u or "LAT" in u:
        m = DECIMAL.search(u)
        if m:
            val = float(m.group(1))
            if "S" in u and val > 0: val = -val
            if -90 <= val <= 90: return val
    return None

def parse_lon(cell):
    if not cell: return None
    u = cell.upper()
    m = DMS.search(u)
    if m:
        val = dms_to_decimal(m)
        if -180 <= val <= 180: return val
    if "DEG" in u or "LON" in u:
        m = DECIMAL.search(u)
        if m:
            val = float(m.group(1))
            if "W" in u and val > 0: val = -val
            if -180 <= val <= 180: return val
    return None

def load_wells():
    wells = []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 5: continue
            api, name, operator = row[0], row[1], row[2]
            lat_raw, lon_raw = row[3], row[4]
            datum = row[5] if len(row) > 5 else None
            surface = row[6] if len(row) > 6 else None

            lat = parse_lat(lat_raw)
            lon = parse_lon(lon_raw)

            if lat is not None and lon is not None and in_bounds(lat, lon):
                wells.append({
                    "api_number": api,
                    "well_name": name,
                    "operator_name": operator,
                    "latitude": lat,
                    "longitude": lon,
                    "datum": datum,
                    "surface_hole_location": surface
                })
    return wells

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/wells")
def api_wells():
    return jsonify(load_wells())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
