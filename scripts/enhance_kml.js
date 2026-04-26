/**
 * KML Enhancer for OS-Bhugol
 * 
 * Adds ExtendedData to KML placemarks including:
 * - Ward metadata (name, Marathi name)
 * - Area in sq km
 * - Perimeter in km
 * - Author
 * 
 * Usage: node enhance_kml.js <input_kml> <output_kml>
 * 
 * Author: mahanvyakti
 */

const fs = require('fs');
const path = require('path');

// Marathi numerals
const MARATHI_NUMERALS = {
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
};

// Earth radius in km
const EARTH_RADIUS_KM = 6371;

// Convert degrees to radians
function toRadians(degrees) {
    return degrees * Math.PI / 180;
}

// Haversine distance between two points
function haversineDistance(lat1, lon1, lat2, lon2) {
    const dLat = toRadians(lat2 - lat1);
    const dLon = toRadians(lon2 - lon1);
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return EARTH_RADIUS_KM * c;
}

// Calculate polygon area using Shoelace formula (in sq km, approximate)
function calculatePolygonArea(coords) {
    if (coords.length < 3) return 0;
    
    // Use spherical excess formula for more accurate area
    let total = 0;
    const n = coords.length;
    
    for (let i = 0; i < n; i++) {
        const j = (i + 1) % n;
        const lat1 = toRadians(coords[i].lat);
        const lon1 = toRadians(coords[i].lng);
        const lat2 = toRadians(coords[j].lat);
        const lon2 = toRadians(coords[j].lng);
        
        total += (lon2 - lon1) * (2 + Math.sin(lat1) + Math.sin(lat2));
    }
    
    total = Math.abs(total / 2);
    return total * EARTH_RADIUS_KM * EARTH_RADIUS_KM;
}

// Calculate perimeter
function calculatePerimeter(coords) {
    let perimeter = 0;
    for (let i = 0; i < coords.length - 1; i++) {
        perimeter += haversineDistance(
            coords[i].lat, coords[i].lng,
            coords[i+1].lat, coords[i+1].lng
        );
    }
    return perimeter;
}

// Parse coordinates from KML coordinate string
function parseCoordinates(coordStr) {
    const coords = [];
    const points = coordStr.trim().split(/\s+/);
    for (const point of points) {
        const [lng, lat, alt] = point.split(',').map(Number);
        if (!isNaN(lng) && !isNaN(lat)) {
            coords.push({ lng, lat, alt: alt || 0 });
        }
    }
    return coords;
}

// Extract ward number from name
function extractWardNumber(name) {
    // Handle various formats: "Ward01", "Ward 01", "Ward No.01", "Ward No. 01"
    const match = name.match(/Ward\s*(?:No\.?\s*)?(\d+)/i);
    return match ? match[1].padStart(2, '0') : null;
}

// Create ExtendedData XML for a ward
function createWardExtendedData(wardNum, area, perimeter) {
    const marathiNum = MARATHI_NUMERALS[wardNum] || wardNum;
    const today = new Date().toISOString().split('T')[0];
    
    return `      <ExtendedData>
        <Data name="ward_number"><value>${parseInt(wardNum)}</value></Data>
        <Data name="ward_name_en"><value>Ward ${wardNum}</value></Data>
        <Data name="ward_name_mr"><value>प्रभाग ${marathiNum}</value></Data>
        <Data name="entity_type"><value>ward</value></Data>
        <Data name="parent_municipality"><value>Nanded Waghala City Municipal Corporation</value></Data>
        <Data name="parent_municipality_mr"><value>नांदेड वाघाळा शहर महानगरपालिका, नांदेड.</value></Data>
        <Data name="district"><value>Nanded</value></Data>
        <Data name="district_mr"><value>नांदेड</value></Data>
        <Data name="state"><value>Maharashtra</value></Data>
        <Data name="state_mr"><value>महाराष्ट्र</value></Data>
        <Data name="country"><value>India</value></Data>
        <Data name="country_mr"><value>भारत</value></Data>
        <Data name="area_sq_km"><value>${area.toFixed(4)}</value></Data>
        <Data name="perimeter_km"><value>${perimeter.toFixed(4)}</value></Data>
        <Data name="author"><value>MC Nanded Waghala</value></Data>
        <Data name="source_url"><value>https://www.google.com/maps/d/viewer?mid=1_8SZuP7IvR3SbZuBo75ICCO2JWaXeb8&amp;ll=19.15299972076274%2C77.33199104582202&amp;z=17</value></Data>
        <Data name="data_year"><value>2025</value></Data>
        <Data name="created_date"><value>${today}</value></Data>
      </ExtendedData>
`;
}

// Create ExtendedData XML for boundary
function createBoundaryExtendedData(area, perimeter) {
    const today = new Date().toISOString().split('T')[0];
    
    return `      <ExtendedData>
        <Data name="name_en"><value>Nanded Waghala City Municipal Corporation</value></Data>
        <Data name="name_mr"><value>नांदेड वाघाळा शहर महानगरपालिका</value></Data>
        <Data name="entity_type"><value>municipal_corporation</value></Data>
        <Data name="district"><value>Nanded</value></Data>
        <Data name="district_mr"><value>नांदेड</value></Data>
        <Data name="state"><value>Maharashtra</value></Data>
        <Data name="state_mr"><value>महाराष्ट्र</value></Data>
        <Data name="country"><value>India</value></Data>
        <Data name="country_mr"><value>भारत</value></Data>
        <Data name="area_sq_km"><value>${area.toFixed(4)}</value></Data>
        <Data name="perimeter_km"><value>${perimeter.toFixed(4)}</value></Data>
        <Data name="author"><value>MC Nanded Waghala</value></Data>
        <Data name="source_url"><value>https://www.nwcmc.gov.in/web/home.php?uid=1&amp;id=MAR#</value></Data>
        <Data name="data_year"><value>2025</value></Data>
        <Data name="created_date"><value>${today}</value></Data>
      </ExtendedData>
`;
}

// Main processing function
function processKML(inputPath, outputPath) {
    console.log(`Processing: ${inputPath}`);
    
    let kml = fs.readFileSync(inputPath, 'utf8');
    
    // Find all Placemarks and enhance them
    const placemarkRegex = /<Placemark>([\s\S]*?)<\/Placemark>/g;
    
    kml = kml.replace(placemarkRegex, (match, content) => {
        // Extract name
        const nameMatch = content.match(/<name>(.*?)<\/name>/);
        if (!nameMatch) return match;
        
        const name = nameMatch[1];
        
        // Extract coordinates
        const coordMatch = content.match(/<coordinates>([\s\S]*?)<\/coordinates>/);
        if (!coordMatch) return match;
        
        const coords = parseCoordinates(coordMatch[1]);
        const area = calculatePolygonArea(coords);
        const perimeter = calculatePerimeter(coords);
        
        console.log(`  ${name}: Area=${area.toFixed(4)} sq km, Perimeter=${perimeter.toFixed(4)} km`);
        
        // Determine if ward or boundary
        const wardNum = extractWardNumber(name);
        let extendedData;
        
        if (wardNum) {
            extendedData = createWardExtendedData(wardNum, area, perimeter);
        } else if (name.includes('Municipal') || name.includes('City') || name.includes('Boundary')) {
            extendedData = createBoundaryExtendedData(area, perimeter);
        } else {
            return match; // Skip unknown placemarks
        }
        
        // Insert ExtendedData after styleUrl
        const styleUrlMatch = content.match(/<styleUrl>.*?<\/styleUrl>/);
        if (styleUrlMatch) {
            const insertPos = content.indexOf(styleUrlMatch[0]) + styleUrlMatch[0].length;
            const newContent = content.slice(0, insertPos) + '\n' + extendedData + content.slice(insertPos);
            return `<Placemark>${newContent}</Placemark>`;
        }
        
        return match;
    });
    
    fs.writeFileSync(outputPath, kml, 'utf8');
    console.log(`\nEnhanced KML saved to: ${outputPath}`);
}

// CLI
if (process.argv.length < 4) {
    console.log('Usage: node enhance_kml.js <input_kml> <output_kml>');
    console.log('Example: node enhance_kml.js wards.kml wards_enhanced.kml');
    process.exit(1);
}

const inputPath = process.argv[2];
const outputPath = process.argv[3];

processKML(inputPath, outputPath);
