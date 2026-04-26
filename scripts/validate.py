"""
GeoJSON Validator for OS-Bhugol

Validates GeoJSON files for:
1. Valid JSON syntax
2. Valid GeoJSON structure
3. Valid geometry (polygons close properly)
4. Required metadata fields present

Usage:
    python validate.py <path_to_validate>

Author: mahanvyakti
"""

import json
import sys
import os
from pathlib import Path


# Required fields for different entity types
REQUIRED_FIELDS = {
    'ward': ['ward_number', 'ward_name_en', 'entity_type', 'district', 'state'],
    'municipal_corporation': ['name_en', 'entity_type', 'district', 'state'],
    'tehsil': ['name_en', 'entity_type', 'district', 'state'],
    'district': ['name_en', 'entity_type', 'state']
}


def validate_polygon_closes(coordinates):
    """Check if polygon coordinates form a closed ring."""
    if not coordinates or len(coordinates) < 4:
        return False, "Polygon must have at least 4 coordinates"
    
    first = coordinates[0]
    last = coordinates[-1]
    
    if first[0] != last[0] or first[1] != last[1]:
        return False, f"Polygon does not close: first={first}, last={last}"
    
    return True, None


def validate_geometry(geometry):
    """Validate a GeoJSON geometry object."""
    errors = []
    
    geom_type = geometry.get('type')
    coordinates = geometry.get('coordinates')
    
    if not geom_type:
        errors.append("Missing geometry type")
        return errors
    
    if not coordinates:
        errors.append("Missing coordinates")
        return errors
    
    if geom_type == 'Polygon':
        for ring_idx, ring in enumerate(coordinates):
            valid, err = validate_polygon_closes(ring)
            if not valid:
                errors.append(f"Ring {ring_idx}: {err}")
    
    elif geom_type == 'MultiPolygon':
        for poly_idx, polygon in enumerate(coordinates):
            for ring_idx, ring in enumerate(polygon):
                valid, err = validate_polygon_closes(ring)
                if not valid:
                    errors.append(f"Polygon {poly_idx}, Ring {ring_idx}: {err}")
    
    return errors


def validate_properties(properties, entity_type=None):
    """Validate feature properties have required fields."""
    errors = []
    
    if not entity_type:
        entity_type = properties.get('entity_type', 'unknown')
    
    required = REQUIRED_FIELDS.get(entity_type, [])
    
    for field in required:
        if field not in properties:
            errors.append(f"Missing required field: {field}")
    
    return errors


def validate_feature(feature, index):
    """Validate a single GeoJSON feature."""
    errors = []
    prefix = f"Feature {index}"
    
    if feature.get('type') != 'Feature':
        errors.append(f"{prefix}: Invalid type (expected 'Feature')")
    
    geometry = feature.get('geometry')
    if not geometry:
        errors.append(f"{prefix}: Missing geometry")
    else:
        geom_errors = validate_geometry(geometry)
        for err in geom_errors:
            errors.append(f"{prefix}: {err}")
    
    properties = feature.get('properties', {})
    prop_errors = validate_properties(properties)
    for err in prop_errors:
        errors.append(f"{prefix}: {err}")
    
    return errors


def validate_geojson_file(filepath):
    """Validate a GeoJSON file."""
    errors = []
    warnings = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"], []
    except Exception as e:
        return [f"Error reading file: {e}"], []
    
    # Check top-level structure
    geojson_type = data.get('type')
    
    if geojson_type == 'FeatureCollection':
        features = data.get('features', [])
        if not features:
            warnings.append("Empty FeatureCollection")
        
        for idx, feature in enumerate(features):
            feat_errors = validate_feature(feature, idx)
            errors.extend(feat_errors)
    
    elif geojson_type == 'Feature':
        feat_errors = validate_feature(data, 0)
        errors.extend(feat_errors)
    
    else:
        errors.append(f"Unknown GeoJSON type: {geojson_type}")
    
    return errors, warnings


def validate_directory(path):
    """Validate all GeoJSON files in a directory."""
    path = Path(path)
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'files': {}
    }
    
    geojson_files = list(path.rglob('*.geojson'))
    
    for filepath in geojson_files:
        results['total'] += 1
        errors, warnings = validate_geojson_file(filepath)
        
        rel_path = str(filepath.relative_to(path))
        results['files'][rel_path] = {
            'errors': errors,
            'warnings': warnings,
            'valid': len(errors) == 0
        }
        
        if len(errors) == 0:
            results['passed'] += 1
            print(f"✓ {rel_path}")
        else:
            results['failed'] += 1
            print(f"✗ {rel_path}")
            for err in errors:
                print(f"    {err}")
    
    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate.py <path>")
        sys.exit(1)
    
    target = sys.argv[1]
    
    if os.path.isfile(target):
        errors, warnings = validate_geojson_file(target)
        if errors:
            print(f"✗ Validation failed:")
            for err in errors:
                print(f"  {err}")
            sys.exit(1)
        else:
            print(f"✓ Validation passed")
            if warnings:
                for warn in warnings:
                    print(f"  Warning: {warn}")
            sys.exit(0)
    
    elif os.path.isdir(target):
        results = validate_directory(target)
        print(f"\n{'='*50}")
        print(f"Total: {results['total']}, Passed: {results['passed']}, Failed: {results['failed']}")
        
        if results['failed'] > 0:
            sys.exit(1)
        sys.exit(0)
    
    else:
        print(f"Path not found: {target}")
        sys.exit(1)


if __name__ == '__main__':
    main()
