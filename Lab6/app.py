from flask import Flask, render_template, jsonify
import csv
import os
import re
import logging

app = Flask(__name__)

# Configuration
CSV_FILE = "step2_output/csv_data/wells_for_web.csv"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced regex patterns for various coordinate formats
DMS = re.compile(
    r"(?P<deg>\d{1,3})\s*°\s*(?P<min>\d{1,2})['\s]+(?P<sec>\d{1,2}(?:\.\d+)?)?\s*\"?\s*(?P<dir>[NSEW])",
    re.IGNORECASE,
)

# More flexible DMS pattern for coordinates with different separators
DMS_FLEXIBLE = re.compile(
    r"(?P<deg>\d{1,3})\s*[°\s]*\s*(?P<min>\d{1,2})\s*['\s]*\s*(?P<sec>\d{1,2}(?:\.\d+)?)?\s*[\"']?\s*(?P<dir>[NSEW])",
    re.IGNORECASE,
)

# Decimal degrees with various formats
DECIMAL = re.compile(r"(-?\d{1,3}\.\d+)")

# Pattern for coordinates like "48.109 deg" or "-103.728 deg"
DEG_PATTERN = re.compile(r"(-?\d{1,3}\.\d+)\s*deg", re.IGNORECASE)

# Pattern for coordinates with mixed separators like "48° 1' 44.700 N"
MIXED_DMS = re.compile(
    r"(?P<deg>\d{1,3})\s*°\s*(?P<min>\d{1,2})\s*['\s]*\s*(?P<sec>\d{1,2}(?:\.\d+)?)\s*(?P<dir>[NSEW])",
    re.IGNORECASE,
)

# ND bounding box
# Global coordinate bounds - accept all valid coordinates worldwide
LAT_MIN, LAT_MAX = -90.0, 90.0  # Full latitude range
LON_MIN, LON_MAX = -180.0, 180.0  # Full longitude range

def in_bounds(lat, lon):
    """Check if coordinates are valid globally (not restricted to specific region)"""
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
    if not cell or cell.strip() == '' or cell == '\\N': 
        return None
    
    u = cell.upper().strip()
    
    # Skip obviously invalid entries
    if any(invalid in u for invalid in ['of Well Head', 'Longitude:', 'Datum:', 'Project', 'Used', 'Mean', 'Thickness']):
        return None
    
    # Try DMS format first
    for pattern in [DMS, DMS_FLEXIBLE, MIXED_DMS]:
        m = pattern.search(u)
        if m:
            val = dms_to_decimal(m)
            if -90 <= val <= 90: 
                return val
    
    # Try decimal degrees with "deg" suffix
    m = DEG_PATTERN.search(u)
    if m:
        val = float(m.group(1))
        if "S" in u and val > 0: 
            val = -val
        if -90 <= val <= 90: 
            return val
    
    # Try plain decimal degrees
    if "DEG" in u or "LAT" in u or any(char.isdigit() for char in u):
        m = DECIMAL.search(u)
        if m:
            val = float(m.group(1))
            if "S" in u and val > 0: 
                val = -val
            if -90 <= val <= 90: 
                return val
    
    return None

def parse_lon(cell):
    if not cell or cell.strip() == '' or cell == '\\N': 
        return None
    
    u = cell.upper().strip()
    
    # Skip obviously invalid entries
    if any(invalid in u for invalid in ['of Well Head', 'Longitude:', 'Datum:', 'Project', 'Used', 'Mean', 'Thickness']):
        return None
    
    # Try DMS format first
    for pattern in [DMS, DMS_FLEXIBLE, MIXED_DMS]:
        m = pattern.search(u)
        if m:
            val = dms_to_decimal(m)
            if -180 <= val <= 180: 
                return val
    
    # Try decimal degrees with "deg" suffix
    m = DEG_PATTERN.search(u)
    if m:
        val = float(m.group(1))
        if "W" in u and val > 0: 
            val = -val
        if -180 <= val <= 180: 
            return val
    
    # Try plain decimal degrees
    if "DEG" in u or "LON" in u or any(char.isdigit() for char in u):
        m = DECIMAL.search(u)
        if m:
            val = float(m.group(1))
            if "W" in u and val > 0: 
                val = -val
            if -180 <= val <= 180: 
                return val
    
    return None

def load_wells():
    """Load well data from CSV file."""
    wells = []
    stats = {
        'total_rows': 0,
        'valid_coordinates': 0,
        'invalid_coordinates': 0,
        'out_of_bounds': 0,
        'missing_data': 0,
        'source': 'csv'
    }
    
    if CSV_FILE and os.path.exists(CSV_FILE):
        wells = load_wells_from_csv(stats)
    else:
        logger.error("CSV data file not found: %s", CSV_FILE)
    
    logger.info("Data Loading Statistics:")
    logger.info("  Source: %s", stats['source'])
    logger.info("  Total rows processed: %d", stats['total_rows'])
    logger.info("  Wells with valid coordinates: %d", stats['valid_coordinates'])
    logger.info("  Wells with invalid coordinates: %d", stats['invalid_coordinates'])
    logger.info("  Wells out of bounds: %d", stats['out_of_bounds'])
    logger.info("  Rows with missing data: %d", stats['missing_data'])
    
    return wells

def load_wells_from_csv(stats):
    """Load wells from CSV file."""
    wells = []
    
    try:
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                stats['total_rows'] += 1
                
                # Extract coordinates
                try:
                    lat = float(row.get('latitude', '')) if row.get('latitude') else None
                    lon = float(row.get('longitude', '')) if row.get('longitude') else None
                except (ValueError, TypeError):
                    lat = lon = None
                
                if lat is not None and lon is not None:
                    if in_bounds(lat, lon):
                        well = {
                            "api_number": row.get('api_number', ''),
                            "well_name": row.get('well_name', ''),
                            "operator_name": row.get('operator_name', ''),
                            "latitude": lat,
                            "longitude": lon,
                            "county": row.get('county', ''),
                            "state": row.get('state', ''),
                            "coordinate_source": row.get('coordinate_source', ''),
                            "datum": row.get('datum', ''),
                            "surface_hole_location": row.get('surface_hole_location', ''),
                            "well_status": row.get('well_status', ''),
                            "well_type": row.get('well_type', ''),
                            "closest_city": row.get('closest_city', ''),
                            "barrels_oil_produced": row.get('barrels_oil_produced', ''),
                            "gas_produced": row.get('gas_produced', ''),
                            "date_stimulated": row.get('date_stimulated', ''),
                            "stimulated_formation": row.get('stimulated_formation', ''),
                            "lbs_proppant": row.get('lbs_proppant', ''),
                            "max_pressure_psi": row.get('max_pressure_psi', '')
                        }
                        wells.append(well)
                        stats['valid_coordinates'] += 1
                    else:
                        stats['out_of_bounds'] += 1
                else:
                    stats['invalid_coordinates'] += 1
    
    except Exception as e:
        logger.error("Error loading CSV file: %s", e)
    
    return wells



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/wells")
def api_wells():
    return jsonify(load_wells())

@app.route("/api/stats")
def api_stats():
    wells = load_wells()
    operators = {}
    for well in wells:
        op = well.get('operator_name', 'Unknown')
        operators[op] = operators.get(op, 0) + 1
    
    return jsonify({
        'total_wells': len(wells),
        'operators': operators,
        'bounds': {
            'lat_min': LAT_MIN,
            'lat_max': LAT_MAX,
            'lon_min': LON_MIN,
            'lon_max': LON_MAX
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)