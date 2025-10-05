#!/usr/bin/env python3
"""
Enhanced PDF processor for oil wells data extraction.
Extracts well information, stimulation data, and coordinates from PDF files.
"""

import os
import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import traceback

# Import PDF processing libraries
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("PyMuPDF not available")

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    print("PyPDF2 not available")

try:
    import pytesseract
    from PIL import Image
    import io
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("OCR libraries not available")

# For geocoding
try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError
    import time
    GEOCODING_AVAILABLE = True
except ImportError:
    GEOCODING_AVAILABLE = False
    print("Geopy not available for geocoding")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EnhancedPDFProcessor:
    def __init__(self, pdf_folder: str, output_folder: str = "extracted_data"):
        self.pdf_folder = pdf_folder
        self.output_folder = output_folder
        self.geocoder = Nominatim(user_agent="oil_wells_extractor") if GEOCODING_AVAILABLE else None
        
        # Create output directory
        os.makedirs(output_folder, exist_ok=True)
        
        # Enhanced regex patterns for various data extraction
        self.patterns = self._initialize_patterns()
        
        # Statistics tracking
        self.stats = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'coordinates_found': 0,
            'coordinates_geocoded': 0
        }

    def _initialize_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize comprehensive regex patterns for data extraction."""
        patterns = {}
        
        # API Number patterns
        patterns['api_number'] = re.compile(
            r'(?:API\s*(?:NO\.?|NUMBER)?:?\s*)?(\d{2}[-\s]?\d{3}[-\s]?\d{5}(?:[-\s]?\d{2})?)',
            re.IGNORECASE
        )
        
        # Well name patterns
        patterns['well_name'] = re.compile(
            r'(?:WELL\s*NAME:?\s*|NAME:?\s*)([A-Z0-9\s\-#]+?)(?:\s*(?:API|LOCATION|OPERATOR|$))',
            re.IGNORECASE
        )
        
        # Operator patterns
        patterns['operator'] = re.compile(
            r'(?:OPERATOR:?\s*|COMPANY:?\s*)([A-Z\s&.,\-]+?)(?:\s*(?:API|LOCATION|WELL|$))',
            re.IGNORECASE
        )
        
        # Coordinate patterns - Enhanced for various formats
        patterns['coordinates_dms'] = re.compile(
            r'(\d{1,3})\s*°\s*(\d{1,2})\s*[′\']\s*(\d{1,2}(?:\.\d+)?)\s*[″"]\s*([NSEW])',
            re.IGNORECASE
        )
        
        patterns['coordinates_decimal'] = re.compile(
            r'(-?\d{1,3}\.\d{4,})\s*[°]?\s*([NSEW])?',
            re.IGNORECASE
        )
        
        # Location patterns for geocoding
        patterns['location'] = re.compile(
            r'(?:LOCATION:?\s*|COUNTY:?\s*|TOWNSHIP:?\s*|SECTION:?\s*)([A-Z\s,\-]+?)(?:\s*(?:API|WELL|OPERATOR|$))',
            re.IGNORECASE
        )
        
        patterns['county'] = re.compile(
            r'(?:COUNTY:?\s*)([A-Z\s]+?)(?:\s*(?:STATE|TOWNSHIP|SECTION|$))',
            re.IGNORECASE
        )
        
        patterns['state'] = re.compile(
            r'(?:STATE:?\s*)([A-Z]{2})(?:\s|$)',
            re.IGNORECASE
        )
        
        # Township/Range/Section patterns (common in oil well locations)
        patterns['trs'] = re.compile(
            r'T(\d+[NS]?)\s*R(\d+[EW]?)\s*S(\d+)',
            re.IGNORECASE
        )
        
        # Stimulation data patterns
        patterns['date_stimulated'] = re.compile(
            r'(?:DATE\s*STIMULATED:?\s*|STIMULATION\s*DATE:?\s*)(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            re.IGNORECASE
        )
        
        patterns['formation'] = re.compile(
            r'(?:FORMATION:?\s*|TARGET:?\s*)([A-Z\s\-]+?)(?:\s*(?:TOP|BOTTOM|DEPTH|$))',
            re.IGNORECASE
        )
        
        patterns['depth_top'] = re.compile(
            r'(?:TOP:?\s*|FROM:?\s*)(\d+)(?:\s*FT|\s*FEET)?',
            re.IGNORECASE
        )
        
        patterns['depth_bottom'] = re.compile(
            r'(?:BOTTOM:?\s*|TO:?\s*)(\d+)(?:\s*FT|\s*FEET)?',
            re.IGNORECASE
        )
        
        patterns['proppant'] = re.compile(
            r'(?:PROPPANT:?\s*|SAND:?\s*)(\d+(?:,\d+)*)\s*(?:LBS|POUNDS)',
            re.IGNORECASE
        )
        
        patterns['pressure'] = re.compile(
            r'(?:PRESSURE:?\s*|MAX\s*PRESSURE:?\s*)(\d+)\s*(?:PSI|PSIG)',
            re.IGNORECASE
        )
        
        patterns['volume'] = re.compile(
            r'(?:VOLUME:?\s*|FLUID:?\s*)(\d+(?:\.\d+)?)\s*(BBL|BARRELS|GAL|GALLONS)',
            re.IGNORECASE
        )
        
        return patterns

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using multiple methods."""
        text = ""
        
        # Method 1: PyMuPDF (most reliable)
        if PYMUPDF_AVAILABLE:
            try:
                doc = fitz.open(pdf_path)
                for page in doc:
                    text += page.get_text()
                doc.close()
                if text.strip():
                    return text
            except Exception as e:
                logger.warning(f"PyMuPDF failed for {pdf_path}: {e}")
        
        # Method 2: PyPDF2
        if PYPDF2_AVAILABLE:
            try:
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        text += page.extract_text()
                if text.strip():
                    return text
            except Exception as e:
                logger.warning("PyPDF2 failed for %s: %s", pdf_path, e)
        
        # Method 3: OCR as fallback (if available)
        if OCR_AVAILABLE:
            try:
                return self._ocr_extract(pdf_path)
            except Exception as e:
                logger.warning(f"OCR failed for {pdf_path}: {e}")
        
        return text

    def _ocr_extract(self, pdf_path: str) -> str:
        """Extract text using OCR."""
        text = ""
        if not PYMUPDF_AVAILABLE:
            return text
            
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                page_text = pytesseract.image_to_string(img)
                text += page_text + "\n"
            doc.close()
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
        
        return text

    def extract_well_information(self, text: str) -> Dict[str, Any]:
        """Extract well information from text."""
        well_info = {}
        
        # Extract API number
        api_match = self.patterns['api_number'].search(text)
        if api_match:
            well_info['api_number'] = api_match.group(1).replace('-', '').replace(' ', '')
        
        # Extract well name
        name_match = self.patterns['well_name'].search(text)
        if name_match:
            well_info['well_name'] = name_match.group(1).strip()
        
        # Extract operator
        operator_match = self.patterns['operator'].search(text)
        if operator_match:
            well_info['operator_name'] = operator_match.group(1).strip()
        
        # Extract coordinates
        coordinates = self.extract_coordinates(text)
        if coordinates:
            well_info.update(coordinates)
        
        # Extract location information for potential geocoding
        location_info = self.extract_location_info(text)
        well_info.update(location_info)
        
        return well_info

    def extract_coordinates(self, text: str) -> Dict[str, Any]:
        """Extract coordinates using enhanced patterns for better success rate."""
        coords = {}
        
        # Enhanced coordinate patterns for better extraction
        enhanced_patterns = {
            # Decimal degrees patterns - more comprehensive
            'decimal_lat_lon': [
                r'(?:LAT|LATITUDE)[:\s]*([+-]?\d{1,2}\.\d{4,8})[^\d]*(?:LON|LONGITUDE)[:\s]*([+-]?\d{1,3}\.\d{4,8})',
                r'(?:LON|LONGITUDE)[:\s]*([+-]?\d{1,3}\.\d{4,8})[^\d]*(?:LAT|LATITUDE)[:\s]*([+-]?\d{1,2}\.\d{4,8})',
                r'([+-]?\d{1,2}\.\d{4,8})[,\s]+([+-]?\d{1,3}\.\d{4,8})',  # Simple lat,lon
                r'N\s*([+-]?\d{1,2}\.\d{4,8})[^\d]*W\s*([+-]?\d{1,3}\.\d{4,8})',  # N/W format
            ],
            
            # Enhanced DMS patterns
            'dms_comprehensive': [
                r'(\d{1,2})°\s*(\d{1,2})\'?\s*(\d{1,2}\.?\d*)\"?\s*([NS])[^\d]*(\d{1,3})°\s*(\d{1,2})\'?\s*(\d{1,2}\.?\d*)\"?\s*([EW])',
                r'([NS])\s*(\d{1,2})°\s*(\d{1,2})\'?\s*(\d{1,2}\.?\d*)\"?[^\d]*([EW])\s*(\d{1,3})°\s*(\d{1,2})\'?\s*(\d{1,2}\.?\d*)\"?',
                r'(\d{1,2})\s*°\s*(\d{1,2})\s*\'\s*(\d{1,2}\.?\d*)\s*\"\s*([NS])[^\d]*(\d{1,3})\s*°\s*(\d{1,2})\s*\'\s*(\d{1,2}\.?\d*)\s*\"\s*([EW])',
            ],
            
            # Surface/wellhead location patterns
            'wellhead_coords': [
                r'(?:WELLHEAD|SURFACE|SPUD)[^:]*[:\s]*([+-]?\d{1,2}\.\d{4,8})[,\s]*([+-]?\d{1,3}\.\d{4,8})',
                r'(?:SURFACE HOLE LOCATION)[^:]*[:\s]*([+-]?\d{1,2}\.\d{4,8})[,\s]*([+-]?\d{1,3}\.\d{4,8})',
            ]
        }
        
        # Try enhanced decimal patterns first
        for pattern in enhanced_patterns['decimal_lat_lon']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    if len(match.groups()) == 2:
                        lat, lon = float(match.group(1)), float(match.group(2))
                        # Global coordinate validation
                        if -90 <= lat <= 90 and -180 <= lon <= 180:
                            coords['latitude'] = str(lat)
                            coords['longitude'] = str(lon)
                            coords['coordinate_format'] = 'Decimal'
                            coords['coordinate_source'] = 'extracted'
                            return coords
                except (ValueError, AttributeError):
                    continue
        
        # Try enhanced DMS patterns
        for pattern in enhanced_patterns['dms_comprehensive']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    groups = match.groups()
                    if len(groups) >= 8:
                        # Parse DMS format
                        lat_deg, lat_min, lat_sec, lat_dir = float(groups[0]), float(groups[1]), float(groups[2]), groups[3]
                        lon_deg, lon_min, lon_sec, lon_dir = float(groups[4]), float(groups[5]), float(groups[6]), groups[7]
                        
                        lat = lat_deg + lat_min/60 + lat_sec/3600
                        if lat_dir.upper() == 'S':
                            lat = -lat
                            
                        lon = lon_deg + lon_min/60 + lon_sec/3600
                        if lon_dir.upper() == 'W':
                            lon = -lon
                        
                        if -90 <= lat <= 90 and -180 <= lon <= 180:
                            coords['latitude'] = str(lat)
                            coords['longitude'] = str(lon)
                            coords['coordinate_format'] = 'DMS'
                            coords['coordinate_source'] = 'extracted'
                            return coords
                except (ValueError, IndexError, AttributeError):
                    continue
        
        # Try wellhead patterns
        for pattern in enhanced_patterns['wellhead_coords']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    if len(match.groups()) == 2:
                        lat, lon = float(match.group(1)), float(match.group(2))
                        if -90 <= lat <= 90 and -180 <= lon <= 180:
                            coords['latitude'] = str(lat)
                            coords['longitude'] = str(lon)
                            coords['coordinate_format'] = 'Wellhead'
                            coords['coordinate_source'] = 'extracted'
                            return coords
                except (ValueError, AttributeError):
                    continue
        
        # Fallback to original patterns if enhanced ones don't work
        original_coords = self._extract_coordinates_original(text)
        if original_coords:
            return original_coords
        
        return coords
    
    def _extract_coordinates_original(self, text: str) -> Dict[str, Any]:
        """Original coordinate extraction as fallback."""
        coords = {}
        
        # Try DMS format first
        dms_matches = self.patterns['coordinates_dms'].findall(text)
        if dms_matches:
            lat_candidates = []
            lon_candidates = []
            
            for deg, min_val, sec, direction in dms_matches:
                decimal = float(deg) + float(min_val)/60 + float(sec)/3600
                if direction.upper() in ['S', 'W']:
                    decimal = -decimal
                
                if direction.upper() in ['N', 'S'] and -90 <= decimal <= 90:
                    lat_candidates.append(decimal)
                elif direction.upper() in ['E', 'W'] and -180 <= decimal <= 180:
                    lon_candidates.append(decimal)
            
            if lat_candidates and lon_candidates:
                coords['latitude'] = str(lat_candidates[0])
                coords['longitude'] = str(lon_candidates[0])
                coords['coordinate_format'] = 'DMS'
                coords['coordinate_source'] = 'extracted'
                return coords
        
        # Try decimal format
        decimal_matches = self.patterns['coordinates_decimal'].findall(text)
        if decimal_matches:
            lat_candidates = []
            lon_candidates = []
            
            for coord, direction in decimal_matches:
                coord_val = float(coord)
                
                # Determine if it's lat or lon based on range and direction
                if direction:
                    if direction.upper() in ['N', 'S'] and -90 <= coord_val <= 90:
                        if direction.upper() == 'S' and coord_val > 0:
                            coord_val = -coord_val
                        lat_candidates.append(coord_val)
                    elif direction.upper() in ['E', 'W'] and -180 <= coord_val <= 180:
                        if direction.upper() == 'W' and coord_val > 0:
                            coord_val = -coord_val
                        lon_candidates.append(coord_val)
                else:
                    # Guess based on typical ranges for North Dakota
                    if 45 <= abs(coord_val) <= 50:  # Likely latitude
                        lat_candidates.append(coord_val)
                    elif 95 <= abs(coord_val) <= 110:  # Likely longitude
                        lon_candidates.append(-abs(coord_val))  # Make negative for western hemisphere
            
            if lat_candidates and lon_candidates:
                coords['latitude'] = str(lat_candidates[0])
                coords['longitude'] = str(lon_candidates[0])
                coords['coordinate_format'] = 'Decimal'
                return coords
        
        return coords

    def extract_location_info(self, text: str) -> Dict[str, Any]:
        """Extract location information for potential geocoding."""
        location_info = {}
        
        # Extract county
        county_match = self.patterns['county'].search(text)
        if county_match:
            location_info['county'] = county_match.group(1).strip()
        
        # Extract state
        state_match = self.patterns['state'].search(text)
        if state_match:
            location_info['state'] = state_match.group(1).strip()
        
        # Extract Township/Range/Section
        trs_match = self.patterns['trs'].search(text)
        if trs_match:
            location_info['township'] = trs_match.group(1)
            location_info['range'] = trs_match.group(2)
            location_info['section'] = trs_match.group(3)
        
        # Extract general location
        location_match = self.patterns['location'].search(text)
        if location_match:
            location_info['location_description'] = location_match.group(1).strip()
        
        return location_info

    def geocode_location(self, well_info: Dict[str, Any]) -> Optional[Tuple[float, float]]:
        """Attempt to geocode location if coordinates not found directly."""
        if not GEOCODING_AVAILABLE or not self.geocoder:
            return None
        
        # Build location query with North Dakota bias
        location_parts = []
        
        # Build location queries - try specific to general
        if 'county' in well_info and 'state' in well_info:
            county = well_info['county'].strip()
            state = well_info['state'].strip()
            if county and state:
                location_parts.append(f"{county} County, {state}")
                # Also try without "County" suffix
                location_parts.append(f"{county}, {state}")
        
        # Try state alone if we have it
        if 'state' in well_info:
            state = well_info['state'].strip()
            if len(state) >= 2:  # Valid state abbreviation or name
                # Try common oil-producing states first
                oil_states = {
                    'ND': 'North Dakota', 'TX': 'Texas', 'OK': 'Oklahoma', 
                    'CO': 'Colorado', 'WY': 'Wyoming', 'NM': 'New Mexico',
                    'CA': 'California', 'AK': 'Alaska', 'PA': 'Pennsylvania'
                }
                if state.upper() in oil_states:
                    full_state = oil_states[state.upper()]
                    location_parts.append(full_state)
        
        # Try township/range/section with state context
        if 'township' in well_info and 'range' in well_info and 'section' in well_info:
            state = well_info.get('state', '')
            trs_query = f"T{well_info['township']} R{well_info['range']} S{well_info['section']}"
            if state:
                trs_query += f", {state}"
            location_parts.append(trs_query)
        
        # Use location descriptions if they seem specific
        if 'location_description' in well_info:
            location_desc = well_info['location_description'].strip()
            # Use if it seems like a real place name (not just abbreviations)
            if (len(location_desc) > 3 and 
                not location_desc.upper() in ['OF', 'TO', 'IN', 'ON', 'THE', 'AND'] and
                any(c.isalpha() for c in location_desc)):
                
                state = well_info.get('state', '')
                if state:
                    location_parts.append(f"{location_desc}, {state}")
                else:
                    location_parts.append(location_desc)
        
        for location_query in location_parts:
            try:
                time.sleep(1)  # Be respectful to the geocoding service
                location = self.geocoder.geocode(location_query, timeout=10)
                if location:
                    lat, lon = location.latitude, location.longitude
                    # Accept all valid global coordinates
                    if (-90.0 <= lat <= 90.0) and (-180.0 <= lon <= 180.0):
                        logger.info(f"Geocoded '{location_query}' to {lat}, {lon}")
                        return lat, lon
                    else:
                        logger.warning(f"Rejected invalid coordinates for '{location_query}': {lat}, {lon}")
            except (GeocoderTimedOut, GeocoderServiceError) as e:
                logger.warning(f"Geocoding failed for '{location_query}': {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected geocoding error for '{location_query}': {e}")
                continue
        
        return None

    def extract_stimulation_data(self, text: str) -> List[Dict[str, Any]]:
        """Extract stimulation data from text."""
        stim_data = []
        
        # For now, extract one stimulation record per PDF
        # This could be enhanced to handle multiple treatments
        stim_record = {}
        
        # Extract date
        date_match = self.patterns['date_stimulated'].search(text)
        if date_match:
            try:
                date_str = date_match.group(1)
                # Try to parse and standardize date format
                for fmt in ('%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y', '%m-%d-%y'):
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        stim_record['date_stimulated'] = date_obj.strftime('%Y-%m-%d')
                        break
                    except ValueError:
                        continue
            except Exception as e:
                logger.warning(f"Date parsing failed: {e}")
        
        # Extract formation
        formation_match = self.patterns['formation'].search(text)
        if formation_match:
            stim_record['stimulated_formation'] = formation_match.group(1).strip()
        
        # Extract depths
        top_match = self.patterns['depth_top'].search(text)
        if top_match:
            stim_record['top_ft'] = int(top_match.group(1))
        
        bottom_match = self.patterns['depth_bottom'].search(text)
        if bottom_match:
            stim_record['bottom_ft'] = int(bottom_match.group(1))
        
        # Extract proppant
        proppant_match = self.patterns['proppant'].search(text)
        if proppant_match:
            proppant_str = proppant_match.group(1).replace(',', '')
            stim_record['lbs_proppant'] = int(proppant_str)
        
        # Extract pressure
        pressure_match = self.patterns['pressure'].search(text)
        if pressure_match:
            stim_record['max_pressure_psi'] = int(pressure_match.group(1))
        
        # Extract volume
        volume_match = self.patterns['volume'].search(text)
        if volume_match:
            stim_record['volume'] = float(volume_match.group(1))
            stim_record['volume_units'] = volume_match.group(2)
        
        if stim_record:
            stim_data.append(stim_record)
        
        return stim_data

    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Process a single PDF file."""
        logger.info(f"Processing {os.path.basename(pdf_path)}")
        
        try:
            # Extract text
            text = self.extract_text_from_pdf(pdf_path)
            if not text.strip():
                logger.warning(f"No text extracted from {pdf_path}")
                return {}
            
            # Extract well information
            well_info = self.extract_well_information(text)
            
            # If no coordinates found, try geocoding
            if 'latitude' not in well_info or 'longitude' not in well_info:
                coords = self.geocode_location(well_info)
                if coords:
                    well_info['latitude'] = str(coords[0])
                    well_info['longitude'] = str(coords[1])
                    well_info['coordinate_source'] = 'geocoded'
                    self.stats['coordinates_geocoded'] += 1
                else:
                    logger.warning(f"No coordinates found for {pdf_path}")
            else:
                well_info['coordinate_source'] = 'extracted'
                self.stats['coordinates_found'] += 1
            
            # Extract stimulation data
            stim_data = self.extract_stimulation_data(text)
            
            result = {
                'source_file': os.path.basename(pdf_path),
                'well_information': well_info,
                'stimulation_data': stim_data,
                'raw_text': text[:1000] + "..." if len(text) > 1000 else text  # Store sample for debugging
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")
            logger.error(traceback.format_exc())
            return {}

    def process_all_pdfs(self) -> None:
        """Process all PDFs in the input folder."""
        pdf_files = [f for f in os.listdir(self.pdf_folder) if f.lower().endswith('.pdf')]
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.pdf_folder, pdf_file)
            self.stats['processed'] += 1
            
            try:
                result = self.process_pdf(pdf_path)
                if result:
                    # Save individual JSON file
                    output_file = os.path.join(
                        self.output_folder, 
                        f"{os.path.splitext(pdf_file)[0]}.json"
                    )
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    
                    self.stats['successful'] += 1
                    logger.info(f"Successfully processed {pdf_file}")
                else:
                    self.stats['failed'] += 1
                    logger.warning(f"Failed to extract data from {pdf_file}")
                    
            except Exception as e:
                self.stats['failed'] += 1
                logger.error(f"Exception processing {pdf_file}: {e}")
        
        # Save summary statistics
        self.save_processing_summary()

    def save_processing_summary(self) -> None:
        """Save processing statistics and summary."""
        summary = {
            'processing_date': datetime.now().isoformat(),
            'statistics': self.stats,
            'input_folder': self.pdf_folder,
            'output_folder': self.output_folder
        }
        
        summary_file = os.path.join(self.output_folder, 'processing_summary.json')
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        logger.info("=== PROCESSING SUMMARY ===")
        logger.info(f"Total PDFs processed: {self.stats['processed']}")
        logger.info(f"Successful extractions: {self.stats['successful']}")
        logger.info(f"Failed extractions: {self.stats['failed']}")
        logger.info(f"Coordinates found directly: {self.stats['coordinates_found']}")
        logger.info(f"Coordinates geocoded: {self.stats['coordinates_geocoded']}")


def main():
    """Main function to run the PDF processor."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced PDF processor for oil wells data')
    parser.add_argument('pdf_folder', help='Folder containing PDF files')
    parser.add_argument('--output', '-o', default='extracted_data', 
                       help='Output folder for extracted data (default: extracted_data)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_folder):
        logger.error(f"PDF folder not found: {args.pdf_folder}")
        return
    
    processor = EnhancedPDFProcessor(args.pdf_folder, args.output)
    processor.process_all_pdfs()


if __name__ == "__main__":
    main()