# drone_mission
Battery:voltage=12.399,current=0.09,level=96


while True:
    lat, lon, alt = get_GPS()
    if ((lat - 0.00002) <= lat <= (lat + 0.00002)) & ((lon - 0.00002) <= lon <= (lon + 0.00002)) & ((alt - 0.05) <= alt <= (alt + 0.05)):
        break
        
        
        
        
def get_GPS():
    Warn_GPS = str(vehicle.location.global_relative_frame)
    # lat 추출
    lat_str = Warn_GPS.split("lat=")[1].split(",")[0]
    lat = float(lat_str)

    # lon 추출
    lon_str = Warn_GPS.split("lon=")[1].split(",")[0]
    lon = float(lon_str)

    # alt 추출
    alt_str = Warn_GPS.split("alt=")[1]
    alt = float(alt_str)
    return lat, lon, alt
