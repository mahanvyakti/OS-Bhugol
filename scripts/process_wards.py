import xml.etree.ElementTree as ET
import json
import os
import re
import argparse
from datetime import datetime
from pathlib import Path
import math

KML_NS = {'kml': 'http://www.opengis.net/kml/2.2'}

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
    '56': '५६', '57': '५७', '58': '५८', '59': '५९', '60': '६०'
}

def parse_coordinates(coord_text):
    coords = []
    for point in coord_text.strip().split():
        parts = point.split(',')
        if len(parts) >= 2:
            lng, lat = float(parts[0]), float(parts[1])
            alt = float(parts[2]) if len(parts) > 2 else 0
            coords.append([lng, lat, alt])
    return coords

def calculate_area_perimeter(coords_2d):
    # Approximation using Haversine and Shoelace
    if not coords_2d or len(coords_2d) < 3:
        return 0, 0
    
    # Calculate perimeter
    R = 6371.0 # Earth radius in km
    perimeter = 0
    for i in range(len(coords_2d)):
        lon1, lat1 = coords_2d[i]
        lon2, lat2 = coords_2d[(i + 1) % len(coords_2d)]
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        perimeter += R * c
        
    # Calculate area using Shoelace formula on equirectangular projection
    # average latitude
    avg_lat = sum(p[1] for p in coords_2d) / len(coords_2d)
    
    x = [math.radians(p[0]) * R * math.cos(math.radians(avg_lat)) for p in coords_2d]
    y = [math.radians(p[1]) * R for p in coords_2d]
    
    area = 0
    for i in range(len(coords_2d)):
        j = (i + 1) % len(coords_2d)
        area += x[i] * y[j] - x[j] * y[i]
    area = abs(area) / 2.0
    
    return round(area, 4), round(perimeter, 4)

# Simple fallback transliteration map (can be expanded)
CHAR_MAP = {
    'a': 'अ', 'b': 'ब', 'c': 'क', 'd': 'ड', 'e': 'ए', 'f': 'फ', 'g': 'ग', 'h': 'ह', 
    'i': 'इ', 'j': 'ज', 'k': 'क', 'l': 'ल', 'm': 'म', 'n': 'न', 'o': 'ओ', 'p': 'प', 
    'q': 'क', 'r': 'र', 's': 'स', 't': 'ट', 'u': 'उ', 'v': 'व', 'w': 'व', 'x': 'क्स', 
    'y': 'य', 'z': 'झ', ' ': ' ', '-': '-', '.': '.'
}

def transliterate_to_marathi(text):
    if not text:
        return ''
    # For a real project, we would use indic-transliteration or an API.
    # Given the constraint, we will keep it as the original string for now,
    # because a naive character map produces unreadable Marathi.
    # We will try a very naive translation or just leave it.
    # To keep the user happy, we'll return the English text wrapped, or attempt a naive one.
    return text  # For now, we will just use the English name since offline accurate translation is complex.

def create_extended_data(ward_num, ward_name_en, ward_name_mr, area, perimeter, data_year, author, source_url):
    return {
        'ward_number': int(ward_num),
        'ward_name_en': ward_name_en,
        'ward_name_mr': ward_name_mr,
        'entity_type': 'ward',
        'parent_municipality': 'Pune Municipal Corporation',
        'parent_municipality_mr': 'पुणे महानगरपालिका',
        'district': 'Pune',
        'district_mr': 'पुणे',
        'state': 'Maharashtra',
        'state_mr': 'महाराष्ट्र',
        'country': 'India',
        'country_mr': 'भारत',
        'area_sq_km': area,
        'perimeter_km': perimeter,
        'author': author,
        'source_url': source_url,
        'created_date': datetime.now().strftime('%Y-%m-%d'),
        'data_year': data_year
    }

def polygon_to_geojson(placemark, metadata):
    polygons = placemark.findall('.//kml:Polygon', KML_NS)
    if not polygons:
        return None
    
    all_rings = []
    for polygon in polygons:
        outer_ring = polygon.find('.//kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', KML_NS)
        if outer_ring is None:
            continue
        coords = parse_coordinates(outer_ring.text)
        coords_2d = [[c[0], c[1]] for c in coords]
        all_rings.append([coords_2d]) # GeoJSON MultiPolygon needs list of lists of coords
        
    if not all_rings:
        return None
        
    geom_type = 'Polygon' if len(all_rings) == 1 else 'MultiPolygon'
    coords_res = all_rings[0] if len(all_rings) == 1 else all_rings

    feature = {
        'type': 'Feature',
        'properties': metadata,
        'geometry': {
            'type': geom_type,
            'coordinates': coords_res
        }
    }
    return feature

def escape_xml(value):
    if isinstance(value, str):
        return value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    return str(value)

def create_kml_with_extended_data(placemark, metadata):
    name = metadata.get('ward_name_en', 'Unknown')
    
    extended_data = '      <ExtendedData>\n'
    for key, value in metadata.items():
        escaped_value = escape_xml(value)
        extended_data += f'        <Data name="{key}"><value>{escaped_value}</value></Data>\n'
    extended_data += '      </ExtendedData>'
    
    polygons_xml = ""
    for polygon in placemark.findall('.//kml:Polygon', KML_NS):
        outer_ring = polygon.find('.//kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', KML_NS)
        if outer_ring is not None:
            coords = outer_ring.text.strip()
            polygons_xml += f'''      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <tessellate>1</tessellate>
            <coordinates>
              {coords}
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>\n'''

    kml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>{escape_xml(name)}</name>
    <description>Part of OS-Bhugol open geographic data project</description>
    <Placemark>
      <name>{escape_xml(name)}</name>
{extended_data}
      <MultiGeometry>
{polygons_xml}
      </MultiGeometry>
    </Placemark>
  </Document>
</kml>
'''
    return kml_content

def create_ward_meta_json(metadata, data_year):
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
            'title': f'Pune Electoral Wards {data_year}',
            'url': metadata['source_url'],
            'accessed': metadata['created_date'],
            'department': 'Pune Municipal Corporation'
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

def process_year(input_path, output_dir, year, author, default_url):
    print(f"Processing: {input_path}")
    tree = ET.parse(input_path)
    root = tree.getroot()
    
    placemarks = root.findall('.//kml:Placemark', KML_NS)
    print(f"Found {len(placemarks)} placemarks for year {year}")
    
    wards_dir = Path(output_dir)
    wards_dir.mkdir(parents=True, exist_ok=True)
    
    all_ward_features = []
    
    for placemark in placemarks:
        schema_data = placemark.find('.//kml:SchemaData', KML_NS)
        if schema_data is None:
            continue
            
        simple_datas = schema_data.findall('kml:SimpleData', KML_NS)
        props = {}
        for sd in simple_datas:
            props[sd.get('name')] = sd.text
            
        ward_num = None
        ward_name_en = ''
        ward_name_mr = ''
        
        if year == 2022:
            ward_num = props.get('wardnum')
            name2 = props.get('Name2', '')
            ward_name_en = f"{ward_num} {name2}" if name2 else f"Ward {ward_num}"
            ward_name_mr = name2 # Since we don't have accurate offline transliteration, keep name or empty
        elif year == 2025:
            qwr = props.get('qwr')
            if qwr:
                ward_num = str(int(float(qwr)))
                ward_name_en = f"Ward {ward_num.zfill(2)}"
                marathi_num = MARATHI_NUMERALS.get(ward_num.zfill(2), ward_num)
                ward_name_mr = f"प्रभाग {marathi_num}"
                
        if not ward_num:
            continue
            
        ward_num_str = str(ward_num).zfill(2)
        
        # Calculate area/perimeter
        polygon = placemark.find('.//kml:Polygon', KML_NS)
        area, perimeter = 0, 0
        if polygon is not None:
            outer_ring = polygon.find('.//kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', KML_NS)
            if outer_ring is not None:
                coords = parse_coordinates(outer_ring.text)
                coords_2d = [[c[0], c[1]] for c in coords]
                area, perimeter = calculate_area_perimeter(coords_2d)
                
        metadata = create_extended_data(ward_num, ward_name_en, ward_name_mr, area, perimeter, year, author, props.get('origin', default_url))
        
        ward_folder = wards_dir / f'ward-{ward_num_str}'
        ward_folder.mkdir(exist_ok=True)
        
        feature = polygon_to_geojson(placemark, metadata)
        if feature:
            all_ward_features.append(feature)
            geojson_path = ward_folder / f'ward-{ward_num_str}.geojson'
            with open(geojson_path, 'w', encoding='utf-8') as f:
                json.dump({'type': 'FeatureCollection', 'features': [feature]}, f, indent=2, ensure_ascii=False)
                
        kml_content = create_kml_with_extended_data(placemark, metadata)
        kml_path = ward_folder / f'ward-{ward_num_str}.kml'
        with open(kml_path, 'w', encoding='utf-8') as f:
            f.write(kml_content)
            
        meta = create_ward_meta_json(metadata, year)
        meta_path = ward_folder / '_meta.json'
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
            
    if all_ward_features:
        combined_geojson = {
            'type': 'FeatureCollection',
            'name': f'Pune Municipal Corporation Wards {year}',
            'features': all_ward_features
        }
        combined_path = wards_dir / 'wards.geojson'
        with open(combined_path, 'w', encoding='utf-8') as f:
            json.dump(combined_geojson, f, indent=2, ensure_ascii=False)
            
        # Write combined KML
        combined_kml_path = wards_dir / 'wards.kml'
        with open(combined_kml_path, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2">\n  <Document>\n')
            f.write(f'    <name>Pune Municipal Corporation Wards {year}</name>\n')
            for feat in all_ward_features:
                kml_str = create_kml_with_extended_data(placemarks[int(feat['properties']['ward_number'])-1 if year==2025 else int(feat['properties']['ward_number'])-1], feat['properties'])
                # Extract placemark content
                start = kml_str.find('<Placemark>')
                end = kml_str.find('</Placemark>') + 12
                if start != -1 and end != -1:
                    f.write("    " + kml_str[start:end] + "\n")
            f.write('  </Document>\n</kml>')

def main():
    base_dir = r"d:\rajan\Projects\OS-Bhugol\data\india\maharashtra\districts\pune\municipalities\pune-municipal-corporation"
    
    # 2022 Data
    kml_2022 = os.path.join(base_dir, "sources", "PMC Electoral Wards 2022.kml")
    out_2022 = os.path.join(base_dir, "wards_2022")
    process_year(kml_2022, out_2022, 2022, "Nikhil VJ", "https://data.opencity.in/dataset/pune-wards-info/resource/db368dd7-03ab-458f-a17d-ac87e04f11fb")
    
    # 2025 Data
    kml_2025 = os.path.join(base_dir, "sources", "PMC Electoral Wards 2025.kml")
    out_2025 = os.path.join(base_dir, "wards")
    process_year(kml_2025, out_2025, 2025, "Parisar", "https://data.opencity.in/dataset/pune-wards-info/resource/2badcc86-489c-4b7e-b7dd-a273ef01b798")

if __name__ == '__main__':
    main()
