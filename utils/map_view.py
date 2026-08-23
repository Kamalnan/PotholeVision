import folium
import os

def generate_map(geo_detections):
    """
    Builds a Folium map from all GPS-tagged detections and saves it as
    an HTML file. Returns the file path, or None if there's no data.
    """
    if not geo_detections:
        return None

    avg_lat = sum(d[2] for d in geo_detections) / len(geo_detections)
    avg_lon = sum(d[3] for d in geo_detections) / len(geo_detections)
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=15)

    for d in geo_detections:
        _, timestamp, lat_, lon_, conf, path, times = d
        folium.Marker(
            location=[lat_, lon_],
            popup=f"Confidence: {conf:.2f}<br>Seen {times}x<br>Last: {timestamp}",
            icon=folium.Icon(color='red', icon='exclamation-triangle', prefix='fa')
        ).add_to(m)

    map_path = os.path.abspath('pothole_map.html')
    m.save(map_path)
    return map_path