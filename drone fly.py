from __future__ import print_function
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal
import time
import argparse
import http.client
import requests
import json


server = "3.36.83.51"
port = 8000

parser = argparse.ArgumentParser(
    description='Print out vehicle state information. Connects to SITL on local PC by default.')
parser.add_argument('--connect',
                    help="vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()
connection_string = args.connect


point1_lat = 37.338405279041886
point1_lon = 126.7350526878168  
point1_alt = 8
point1 = LocationGlobalRelative(point1_lat, point1_lon, point1_alt)

point2_lat =  37.33836265424870
point2_lon = 126.73513041951286
point2_alt = 8
point2 = LocationGlobalRelative(point2_lat, point2_lon, point2_alt)

point3_lat = 37.33829526710607
point3_lon = 126.7352152909514
point3_alt = 8
point3 = LocationGlobalRelative(point3_lat, point3_lon, point3_alt)

point4_lat = 37.33821061324027
point4_lon = 126.73513377457854
point4_alt = 8	
point4 = LocationGlobalRelative(point4_lat, point4_lon, point4_alt)

home_lat = 37.33825882203562
home_lon = 126.73503486473739
home_alt = 8
land = LocationGlobalRelative(home_lat, home_lon, home_alt)


print("\nConnecting to vehicle on: %s" % connection_string)
vehicle = connect(connection_string, wait_ready=False)

########################################


def vehicle_state():

    vehicle.wait_ready('autopilot_version')
    print(" Autopilot Firmware version: %s" % vehicle.version)

    print(" Global Location (relativ altitude): %s" %
          vehicle.location.global_relative_frame)
    print(" Attitude: %s" % vehicle.attitude)
    print(" Velocity: %s" % vehicle.velocity)
    print(" GPS HDOP: %s" % vehicle.gps_0.eph)
    print(" GPS VDOP: %s" % vehicle.gps_0.epv)
    print(" GPS fix type: %s" % vehicle.gps_0.fix_type)
    print(" GPS satellites_visible: %s" %
          vehicle.gps_0.satellites_visible)  #
    print(" Battery: %s" % vehicle.battery)
    print(" EKF OK?: %s" % vehicle.ekf_ok)
    print(" Last Heartbeat: %s" % vehicle.last_heartbeat)
    print(" Heading: %s" % vehicle.heading)
    print(" Is Armable?: %s" % vehicle.is_armable)
    print(" System status: %s" % vehicle.system_status.state)

    print(" Groundspeed: %s" % vehicle.groundspeed)
    print(" Airspeed: %s" % vehicle.airspeed)
    print(" Mode: %s" % vehicle.mode.name)
    print(" Armed: %s" % vehicle.armed)


def set_home_location(lat, lon, alt):
    print("\nSet new home location")
    my_location_alt = LocationGlobal(lat, lon, alt)
    vehicle.home_location = my_location_alt
    print(" New Home Location (from attribute - altitude should be 222): %s" %
          vehicle.home_location)

# set_home_location(37.338281423673735,126.7355722162276,220)


def arm_and_takeoff(TargetAlt):
    print("Basic pre-arm checks")

    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        print("Waiting for arming...")
        time.sleep(1)

        print("Taking off!")
        vehicle.simple_takeoff(TargetAlt)

  #
    while True:

        print(" Altitude: ", vehicle.location.global_relative_frame.alt)

        if vehicle.location.global_relative_frame.alt >= TargetAlt * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


def get_HomeGPS():
    Home_GPS = str(vehicle.home_location)

    lat_str = Home_GPS.split("lat=")[1].split(",")[0]
    lat = float(lat_str)

    lon_str = Home_GPS.split("lon=")[1].split(",")[0]
    lon = float(lon_str)

    return lat, lon


def get_GPS():
    Warn_GPS = str(vehicle.location.global_relative_frame)

    lat_str = Warn_GPS.split("lat=")[1].split(",")[0]
    lat = float(lat_str)

    lon_str = Warn_GPS.split("lon=")[1].split(",")[0]
    lon = float(lon_str)

    alt_str = Warn_GPS.split("alt=")[1]
    alt = float(alt_str)

    return lat, lon, alt


conn = http.client.HTTPConnection(server, port)

conn.request("GET", "/StateInfo/PATROL_STATUS?STATUS=PATROL_STANDBY")
response = conn.getresponse()
conn.close()

conn.request("GET", "/StateInfo/DETECT_STATUS1?STATUS=NO_DETECTED")
response = conn.getresponse()
conn.close()
conn.request("GET", "/StateInfo/DETECT_STATUS2?STATUS=NO_DETECTED")
response = conn.getresponse()
conn.close()
conn.request("GET", "/StateInfo/DETECT_STATUS3?STATUS=NO_DETECTED")
response = conn.getresponse()
conn.close()
conn.request("GET", "/StateInfo/DETECT_STATUS4?STATUS=NO_DETECTED")
response = conn.getresponse()
conn.close()
conn.request("GET", "/StateInfo/DRONE_DIRECTION?STATUS=FORWARD")
response = conn.getresponse()
conn.close()
while True:
    time.sleep(1)
    conn = http.client.HTTPConnection(server, port)
    conn.request("GET", "/StateInfo/PATROL_STATUS")
    response = conn.getresponse()
    data = response.read()
    patrol = json.loads(data)
    patrol_state = patrol["PATROL_STATUS"]
##################close!############3
    vehicle_state()
    print("--------------------------------------------------------------------------------------")

    print(patrol_state)

    if patrol_state == "PATROL_STANDBY":
        pass

    if patrol_state == "PATROL_TAKEOFF":
        print("Patrol_takeoff")
        arm_and_takeoff(8)
        conn.request("GET", "/StateInfo/PATROL_STATUS?STATUS=PATROL_MOVE1")

    if patrol_state == "PATROL_MOVE1":
        print("Going towards First Point")
        vehicle.simple_goto(point1, airspeed=1)

        while True:
            lat, lon, alt = get_GPS()
            time.sleep(0.5)
            vehicle.simple_goto(point1, airspeed=1)
            time.sleep(0.1)
            if (point1_lat - 0.00003 <= lat <= point1_lat + 0.00003) and (point1_lon-0.00003 <= lon <= point1_lon+0.00003):
                break
        print("PATROL_Arrived")
        time.sleep(2)
        conn.request("GET", "/StateInfo/PATROL_STATUS?STATUS=PATROL_CAPTURE1")

        #Patrol_lat, Patrol_lon, Patrol_alt = get_GPS()

    if patrol_state == "PATROL_MOVE2":
        print("Going towards Second Point")

        vehicle.simple_goto(point2, airspeed=1)
        while True:
            lat, lon, alt = get_GPS()
            time.sleep(0.5)
            vehicle.simple_goto(point2, airspeed=1)
            time.sleep(0.1)
            if (point2_lat-0.00003 <= lat <= point2_lat + 0.00003) and (point2_lon - 0.00003 <= lon <= point2_lon + 0.00003):
                break
        print("PATROL_Arrived")
        time.sleep(3)
        conn.request("GET", "/StateInfo/PATROL_STATUS?STATUS=PATROL_CAPTURE2")

        #Patrol_lat, Patrol_lon, Patrol_alt = get_GPS()

    if patrol_state == "PATROL_MOVE3":
        print("Going towards Third Point")

        vehicle.simple_goto(point3, airspeed=1)
        while True:

            lat, lon, alt = get_GPS()
            time.sleep(0.5)
            vehicle.simple_goto(point3, airspeed=1)
            time.sleep(0.1)
            if (point3_lat - 0.00003 <= lat <= point3_lat + 0.00003) and (point3_lon - 0.00003 <= lon <= point3_lon + 0.00003):
                break
        print("PATROL_Arrived")
        time.sleep(2)
        conn.request("GET", "/StateInfo/PATROL_STATUS?STATUS=PATROL_CAPTURE3")

    if patrol_state == "PATROL_MOVE4":
        print("Going towards Fourth Point")

        vehicle.simple_goto(point4, airspeed=1)
        while True:
            lat, lon, alt = get_GPS()
            time.sleep(0.5)
            vehicle.simple_goto(point4, airspeed=1)
            time.sleep(0.1)
            if (point4_lat-0.00003 <= lat <= point4_lat+0.00003) and (point4_lon - 0.00003 <= lon <= point4_lon+0.00003):
                break
        print("PATROL_Arrived")
        time.sleep(2)
        conn.request("GET", "/StateInfo/PATROL_STATUS?STATUS=PATROL_CAPTURE4")
    time.sleep(1)
    if patrol_state == "PATROL_CAPTURE1":
        print("Waiting Capture1")
        vehicle.simple_goto(point1, airspeed=1)

    if patrol_state == "PATROL_CAPTURE2":
        print("Waiting Capture2")
        vehicle.simple_goto(point2, airspeed=1)

    if patrol_state == "PATROL_CAPTURE3":
        print("Waiting Capture3")
        vehicle.simple_goto(point3, airspeed=1)

    if patrol_state == "PATROL_CAPTURE4":
        print("Waiting Capture4")
        vehicle.simple_goto(point4, airspeed=1)

    Warn_Battery = str(vehicle.battery)
    lev_str = Warn_Battery.split("level=")[1]
    level = int(lev_str)
    print(level)
    print("-------------------------------------------------------------------------------------")
    if level < 30:
        print("Battery level : %d, Return to Launch" % level)
        conn.request("GET", "/StateInfo/PATROL_STATUS?STATUS=PATROL_RETURN")

    if patrol_state == "PATROL_RETURN":

        vehicle.simple_goto(land, airspeed=1)
        while True:
            lat, lon, alt = get_GPS()
            time.sleep(0.1)
            if (home_lat-0.00003 <= lat <= home_lat+0.00003) and (home_lon - 0.00003 <= lon <= home_lon+0.00003):
                break
        print("PATROL_Arrived")
        time.sleep(2)
        vehicle.mode = VehicleMode("LAND")
        while True:
            lat, lon, alt = get_GPS()
            time.sleep(0.1)
            if (0 <= alt <= 0.25):
                break
        time.sleep(7)
        vehicle.armed = False

