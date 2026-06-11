import folium
import sqlite3
from folium.plugins import MarkerCluster, HeatMap

def generate_map():
    # Connect to db
    conn = sqlite3.connect('probe_log.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT mac, vendor, randomized, ssid, latitude, longitude
    FROM probe_requests
    WHERE latitude != 0.0 and longitude != 0.0
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    if not rows: 
        print("[!] No location data found. Set LAT/LON coordinates in probe_logger.py")
        return

    #Center Map on first result
    m= folium.Map(location=[rows[0][4], rows[0][5]], zoom_start=15)

    #Marker Cluster for devices
    cluster = MarkerCluster().add_to(m)

    #Heatmap data
    heat_data = []

    for mac, vendor, randomized, ssid, lat, lon in rows:
        heat_data.append([lat, lon])

        #Color code by randomized status
        color = "red" if randomized == 1 else "blue"

        #Format randomized status
        rand_text = "Yes" if randomized == 1 else "No"

        folium.CircleMarker(
            location=[lat, lon],
            radius= 8,
            color = color,
            fill= True,
            popup= folium.Popup(
            f"MAC: {mac}<br>"
            f"Vendor: {vendor}<br>"
            f"Randomized: {rand_text}<br>"
            f"SSID: {ssid}",
            max_width=250
            )
        ).add_to(cluster)

        #Add heat map layer
    HeatMap(heat_data).add_to(m)

    m.save("probe_map.html")        
    print("[*]Map saved to probe_map.html - open it in your browser!")

generate_map()