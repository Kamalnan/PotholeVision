import exifread

def extract_gps(image_file):
    """
    Extracts GPS latitude/longitude from an uploaded image's EXIF data.
    Returns (latitude, longitude) as floats, or (None, None) if no GPS data found.
    """
    tags = exifread.process_file(image_file, details=False)

    lat_tag = tags.get('GPS GPSLatitude')
    lat_ref_tag = tags.get('GPS GPSLatitudeRef')
    lon_tag = tags.get('GPS GPSLongitude')
    lon_ref_tag = tags.get('GPS GPSLongitudeRef')

    if not (lat_tag and lon_tag):
        return None, None

    def convert_to_degrees(value):
        # EXIF GPS coordinates are stored as degrees, minutes, seconds
        d, m, s = value.values
        return float(d.num) / d.den + (float(m.num) / m.den) / 60 + (float(s.num) / s.den) / 3600

    lat = convert_to_degrees(lat_tag)
    if lat_ref_tag and lat_ref_tag.values[0] != 'N':
        lat = -lat

    lon = convert_to_degrees(lon_tag)
    if lon_ref_tag and lon_ref_tag.values[0] != 'E':
        lon = -lon

    return lat, lon