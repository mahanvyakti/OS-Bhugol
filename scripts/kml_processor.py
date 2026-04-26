"""
KML Processor for OS-Bhugol

This script processes KML files to:
1. Add rich metadata (ExtendedData) to each polygon
2. Extract individual wards/entities into separate files
3. Convert KML to GeoJSON format
4. Extract boundary layers separately

Usage:
    python kml_processor.py <input_kml> <output_dir>

Author: mahanvyakti
"""

import xml.etree.ElementTree as ET
import json
import os
import re
import argparse
from datetime import datetime
from pathlib import Path

# KML namespace
KML_NS = {'kml': 'http://www.opengis.net/kml/2.2'}

# Marathi numerals for ward names
MARATHI_NUMERALS = {
    '01': '०१', '02': '०२', '03': '०३', '04': '०४', '05': '०५',
    '06': '०६', '07': '०७', '08': '०८', '09': '०९', '10': '१०',
    '11': '११', '12': '१२', '13': '१३', '14': '१४', '15': '१५',
    '16': '१६', '17': '१७', '18': '१८', '19': '१९', '20': '२०',
    '21': '२१', '22': '२२', '23': '२३', '24': '२४', '25': '२५',
    '26': '२६', '27': '२७', '28': '२८', '29': '२९', '30': '३०',
    '31': '३१', '32': '३२', '33': '३३', '34': '३४', '35': '३५',
    '36': '३६', '37': '३७', '38': '३८', '39': '३९', '40': '४०',
    '41': '४१', '42': '४२', '43': '४३', '44': '४४', '45': '४५',
    '46': '४६', '47': '४७', '48': '४८', '49': '४९', '50': '५०',
    '51': '५१', '52': '५२', '53': '५३', '54': '५४', '55': '५५',
    '56': '५६', '57': '५७', '58': '५८', '59': '५९', '60': '६०',
    '61': '६१', '62': '६२', '63': '६३', '64': '६४', '65': '६५',
    '66': '६६', '67': '६७', '68': '६८', '69': '६९', '70': '७०',
    '71': '७१', '72': '७२', '73': '७३', '74': '७४', '75': '७५',
    '76': '७६', '77': '७७', '78': '७८', '79': '७९', '80': '८०',
    '81': '८१', '82': '८२', '83': '८३', '84': '८४', '85': '८५',
    '86': '८६', '87': '८७', '88': '८८', '89': '८९', '90': '९०',
    '91': '९१', '92': '९२', '93': '९३', '94': '९४', '95': '९५',
    '96': '९६', '97': '९७', '98': '९८', '99': '९९', '100': '१००'
}


def parse_coordinates(coord_text):
    """Parse KML coordinate string into list of [lng, lat, alt] tuples."""
    coords = []
    for point in coord_text.strip().split():
        parts = point.split(',')
        if len(parts) >= 2:
            lng, lat = float(parts[0]), float(parts[1])
            alt = float(parts[2]) if len(parts) > 2 else 0
            coords.append([lng, lat, alt])
    return coords


def extract_ward_number(name):
    """Extract ward number from name like 'Ward01', 'Ward 01', 'Ward No.01', etc."""
    # Handle various formats: "Ward01", "Ward 01", "Ward No.01", "Ward No. 01"
    match = re.search(r'Ward\s*(?:No\.?\s*)?(\d+)', name, re.IGNORECASE)
    if match:
        return match.group(1).zfill(2)
    return None


def create_extended_data(ward_num, entity_type='ward'):
    """Create metadata dictionary for a ward/entity."""
    marathi_num = MARATHI_NUMERALS.get(ward_num, ward_num)
    
    return {
        'ward_number': int(ward_num),
        'ward_name_en': f'Ward {ward_num}',
        'ward_name_mr': f'प्रभाग {marathi_num}',
        'entity_type': entity_type,
        'parent_municipality': 'Nanded Waghala City Municipal Corporation',
        'parent_municipality_mr': 'नांदेड वाघाळा शहर महानगरपालिका',
        'district': 'Nanded',
        'district_mr': 'नांदेड',
        'state': 'Maharashtra',
        'state_mr': 'महाराष्ट्र',
        'country': 'India',
        'country_mr': 'भारत',
        'author': 'MC Nanded Waghala',
        'source_url': 'https://www.google.com/maps/d/viewer?mid=1_8SZuP7IvR3SbZuBo75ICCO2JWaXeb8',
        'created_date': datetime.now().strftime('%Y-%m-%d'),
        'data_year': 2025
    }


def create_boundary_metadata():
    """Create metadata for municipal corporation boundary."""
    return {
        'name_en': 'Nanded Waghala City Municipal Corporation',
        'name_mr': 'नांदेड वाघाळा शहर महानगरपालिका',
        'entity_type': 'municipal_corporation',
        'district': 'Nanded',
        'state': 'Maharashtra',
        'country': 'India',
        'author': 'MC Nanded Waghala',
        'source_url': 'https://www.nwcmc.gov.in/web/home.php',
        'created_date': datetime.now().strftime('%Y-%m-%d')
    }


def polygon_to_geojson(placemark, metadata):
    """Convert a KML Placemark with Polygon to GeoJSON Feature."""
    polygon = placemark.find('.//kml:Polygon', KML_NS)
    if polygon is None:
        return None
    
    outer_ring = polygon.find('.//kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', KML_NS)
    if outer_ring is None:
        return None
    
    coords = parse_coordinates(outer_ring.text)
    # GeoJSON uses [lng, lat] without altitude for 2D
    coords_2d = [[c[0], c[1]] for c in coords]
    
    feature = {
        'type': 'Feature',
        'properties': metadata,
        'geometry': {
            'type': 'Polygon',
            'coordinates': [coords_2d]
        }
    }
    
    return feature


def escape_xml(value):
    """Escape special XML characters."""
    if isinstance(value, str):
        return value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    return str(value)


def create_kml_with_extended_data(placemark, metadata, styles_xml=''):
    """Create a standalone KML file for a single placemark with ExtendedData."""
    name = metadata.get('ward_name_en', metadata.get('name_en', 'Unknown'))
    
    # Build ExtendedData XML with proper indentation and XML escaping
    extended_data = '      <ExtendedData>\n'
    for key, value in metadata.items():
        escaped_value = escape_xml(value)
        extended_data += f'        <Data name="{key}"><value>{escaped_value}</value></Data>\n'
    extended_data += '      </ExtendedData>'
    
    # Get polygon coordinates
    polygon = placemark.find('.//kml:Polygon', KML_NS)
    outer_ring = polygon.find('.//kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', KML_NS)
    coords = outer_ring.text.strip()
    
    kml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>{escape_xml(name)}</name>
    <description>Part of OS-Bhugol open geographic data project</description>
    <Placemark>
      <name>{escape_xml(name)}</name>
{extended_data}
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <tessellate>1</tessellate>
            <coordinates>
              {coords}
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>
'''
    return kml_content


def create_ward_meta_json(metadata, ward_dir):
    """Create _meta.json for individual ward directory."""
    meta = {
        'name': metadata['ward_name_en'],
        'name_local': metadata['ward_name_mr'],
        'type': 'ward',
        'ward_number': metadata['ward_number'],
        'parent': {
            'municipality': metadata['parent_municipality'],
            'district': metadata['district'],
            'state': metadata['state'],
            'country': metadata['country']
        },
        'sources': [{
            'title': 'Ward Delimitation Map',
            'url': metadata['source_url'],
            'accessed': metadata['created_date'],
            'department': 'Nanded Waghala City Municipal Corporation'
        }],
        'data_files': {
            'kml': f'ward-{metadata["ward_number"]:02d}.kml',
            'geojson': f'ward-{metadata["ward_number"]:02d}.geojson'
        },
        'contributors': [metadata['author']],
        'created': metadata['created_date'],
        'last_updated': metadata['created_date']
    }
    return meta


def process_kml(input_path, output_dir):
    """Main processing function."""
    print(f"Processing: {input_path}")
    print(f"Output directory: {output_dir}")
    
    # Parse KML
    tree = ET.parse(input_path)
    root = tree.getroot()
    
    # Find all Placemarks
    placemarks = root.findall('.//kml:Placemark', KML_NS)
    print(f"Found {len(placemarks)} placemarks")
    
    # Prepare output directories
    wards_dir = Path(output_dir) / 'wards'
    wards_dir.mkdir(parents=True, exist_ok=True)
    
    # Collections for combined files
    all_ward_features = []
    boundary_feature = None
    
    for placemark in placemarks:
        name_elem = placemark.find('kml:name', KML_NS)
        if name_elem is None:
            continue
        
        name = name_elem.text
        print(f"  Processing: {name}")
        
        # Check if this is a ward or boundary
        ward_num = extract_ward_number(name)
        
        if ward_num:
            # This is a ward
            metadata = create_extended_data(ward_num)
            
            # Create individual ward directory
            ward_folder = wards_dir / f'ward-{ward_num}'
            ward_folder.mkdir(exist_ok=True)
            
            # Create GeoJSON
            feature = polygon_to_geojson(placemark, metadata)
            if feature:
                all_ward_features.append(feature)
                
                # Save individual GeoJSON
                geojson_path = ward_folder / f'ward-{ward_num}.geojson'
                with open(geojson_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'type': 'FeatureCollection',
                        'features': [feature]
                    }, f, indent=2, ensure_ascii=False)
                print(f"    Created: {geojson_path}")
            
            # Create individual KML with ExtendedData
            kml_content = create_kml_with_extended_data(placemark, metadata)
            kml_path = ward_folder / f'ward-{ward_num}.kml'
            with open(kml_path, 'w', encoding='utf-8') as f:
                f.write(kml_content)
            print(f"    Created: {kml_path}")
            
            # Create _meta.json
            meta = create_ward_meta_json(metadata, ward_folder)
            meta_path = ward_folder / '_meta.json'
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)
            print(f"    Created: {meta_path}")
            
        elif 'Municipal Corporation' in name or 'City' in name or 'Boundary' in name:
            # This is the municipal boundary
            metadata = create_boundary_metadata()
            feature = polygon_to_geojson(placemark, metadata)
            if feature:
                boundary_feature = feature
    
    # Save combined wards GeoJSON
    if all_ward_features:
        combined_geojson = {
            'type': 'FeatureCollection',
            'name': 'Nanded Waghala City Municipal Corporation Wards',
            'features': all_ward_features
        }
        combined_path = wards_dir / 'all-wards.geojson'
        with open(combined_path, 'w', encoding='utf-8') as f:
            json.dump(combined_geojson, f, indent=2, ensure_ascii=False)
        print(f"Created combined: {combined_path}")
    
    # Save boundary
    if boundary_feature:
        boundary_geojson = {
            'type': 'FeatureCollection',
            'features': [boundary_feature]
        }
        boundary_path = Path(output_dir) / 'boundary.geojson'
        with open(boundary_path, 'w', encoding='utf-8') as f:
            json.dump(boundary_geojson, f, indent=2, ensure_ascii=False)
        print(f"Created boundary: {boundary_path}")
    
    print("\nProcessing complete!")
    return len(all_ward_features)


def main():
    parser = argparse.ArgumentParser(description='Process KML files for OS-Bhugol')
    parser.add_argument('input', help='Input KML file path')
    parser.add_argument('output', help='Output directory path')
    args = parser.parse_args()
    
    process_kml(args.input, args.output)


if __name__ == '__main__':
    main()
