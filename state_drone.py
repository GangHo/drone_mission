from __future__ import print_function
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal
import time
import argparse
import http.client
import json

# http setting
server = "서버이름.com"
port = 80

conn = http.client.HTTPConnection(server, port)
conn.request("GET", "/StateInfo")
response = conn.getresponse()
data = response.read()
conn.close()

doc = json.loads(data)
drone_state = doc["DroneState"]


parser = argparse.ArgumentParser(
    description='Print out vehicle state information. Connects to SITL on local PC by default.')
parser.add_argument('--connect',
                    help="vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()
connection_string = args.connect

# 드론 연결부분
print("\nConnecting to vehicle on: %s" % connection_string)
vehicle = connect(connection_string, wait_ready=False)

# 드론 기본적인 상태정보출력함수##########################################################################


def vehicle_state():

    vehicle.wait_ready('autopilot_version')
    print(" Autopilot Firmware version: %s" % vehicle.version)

    print(" Global Location (relative altitude): %s" %
          vehicle.location.global_relative_frame)  # 상대고도
    print(" Attitude: %s" % vehicle.attitude)  # YAW ,PITCH, ROLL
    print(" Velocity: %s" % vehicle.velocity)  # 속도
    print(" GPS HDOP: %s" % vehicle.gps_0.eph)  # GPS수평위치 오차
    print(" GPS VDOP: %s" % vehicle.gps_0.epv)  # GSP수직위치 오차
    print(" GPS fix type: %s" % vehicle.gps_0.fix_type)  # GPS 3이상
    print(" GPS satellites_visible: %s" %
          vehicle.gps_0.satellites_visible)  # 연결된 위성 개수
    print(" Battery: %s" % vehicle.battery)  # 배터리 상황
    print(" EKF OK?: %s" % vehicle.ekf_ok)  # Extended Kalman Filter 상태
    print(" Last Heartbeat: %s" % vehicle.last_heartbeat)  # 최근 드론과의 연결 상태(초)
    print(" Heading: %s" % vehicle.heading)  # 드론의 방향 0' or 360' 지도상 북쪽
    print(" Is Armable?: %s" % vehicle.is_armable)  # 시동가능여부
    print(" System status: %s" % vehicle.system_status.state)  # 드론 상태
  # airspeed에 바람속도 값이 반영된 값 바람을 등지면 속도가 빨라지고 맞바람이면 느려짐
    print(" Groundspeed: %s" % vehicle.groundspeed)
    print(" Airspeed: %s" % vehicle.airspeed)    # m/s로 일정한 값을 가짐
    print(" Mode: %s" % vehicle.mode.name)    # 기체의 모드상태
    print(" Armed: %s" % vehicle.armed)    # 시동이 걸렸는지 현재 시동 상태

# 홈 위치설정 (lat:위도, lon:경도, alt:고도)


def set_home_location(lat, lon, alt):
    print("\nSet new home location")
    my_location_alt = LocationGlobal(lat, lon, alt)  # home 위치설정 (고도설정 추후에 다시)
    vehicle.home_location = my_location_alt
    print(" New Home Location (from attribute - altitude should be 222): %s" %
          vehicle.home_location)  # 새롭게 설정된 home위치 출력

# 시동 및 이륙########################################################################################3


def arm_and_takeoff(TargetAlt):
    print("Basic pre-arm checks")
    # 시동이 걸리지 않을시 대기
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    vehicle.mode = VehicleMode("GUIDED")  # 비행모드 가이드모드
    vehicle.armed = True  # 시동 ON

    # 이륙전 기체의 시동상태 확인
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)
    # 이륙
        print("Taking off!")
        vehicle.simple_takeoff(TargetAlt)  # 목표고도로 이륙

  # 목표 고도에 도달하는 동안 현재 고도 출력
  #
    while True:
        # 현재 기체의 상대고도
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # 목표 고도에 도달하면 멈춤
        if vehicle.location.global_relative_frame.alt >= TargetAlt * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

# 상황 발생시 경고용 드론이 출동할 좌표값 리턴


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


# Main코드 #####################################################3
arm_and_takeoff(10)

# 드론 충전소에서 드론의 비행경로의 시작점으로 이동 (빠른속도로)
print("Going towards Start point for 20 seconds ...")
point1 = LocationGlobalRelative(
    37.340807327195925, 126.73091957660192, 10)  # 좌표값 업데이트할것
vehicle.simple_goto(point1, airspeed=7)

time.sleep(15)

# DroneState=CaptureGo로 상태 업데이트
conn = http.client.HTTPConnection(server, port)
conn.request("GET", "/StateInfo/update?DroneState=CaptureGo")
conn.getresponse()
conn.close()

while True:
    conn = http.client.HTTPConnection(server, port)
    conn.request("GET", "/StateInfo")
    response = conn.getresponse()
    data = response.read()
    conn.close()

    doc = json.load(data)
    drone_state = doc["DroneState"]
    if drone_state == "CaptureFinish":
        break
    elif drone_state == "Warning":
        lat, lon, alt = get_GPS()
        # http.POST?
    print("Waiting for Capture")
    time.sleep(0.1)

vehicle_state()
print(drone_state)

# 라즈베리가 카메라 캡쳐완료한 것을 확인 후 다음 경로로 이동
print("Going towards second point for 15 seconds ...")
point2 = LocationGlobalRelative(37.340577290298455, 126.73129421229582, 10)
vehicle.simple_goto(point2, airspeed=5)

time.sleep(7)
vehicle_state()
time.sleep(8)

# DroneState=CaptureGo로 상태 업데이트
conn = http.client.HTTPConnection(server, port)
conn.request("GET", "/StateInfo/update?DroneState=CaptureGo")
conn.getresponse()
conn.close()
print(drone_state)
vehicle_state()

while True:
    conn = http.client.HTTPConnection(server, port)
    conn.request("GET", "/StateInfo")
    response = conn.getresponse()
    data = response.read()
    conn.close()

    doc = json.load(data)
    drone_state = doc["DroneState"]
    if drone_state == "CaptureFinish":
        break
    elif drone_state == "Warning":
        lat, lon, alt = get_GPS()
        # http.POST?
    print("Waiting for Capture")
    time.sleep(0.1)

vehicle_state()
print(drone_state)

# 라즈베리가 카메라 캡쳐완료한 것을 확인 후 다음 경로로 이동

print("Going towards third point for 15 seconds ...")
point3 = LocationGlobalRelative(37.340358556544516, 126.73168714352946, 10)
vehicle.simple_goto(point3, airspeed=5)

time.sleep(7)
vehicle_state()
time.sleep(8)

conn = http.client.HTTPConnection(server, port)
conn.request("GET", "/StateInfo/update?DroneState=CaptureGo")
conn.getresponse()
conn.close()
print(drone_state)
vehicle_state()

while True:
    conn = http.client.HTTPConnection(server, port)
    conn.request("GET", "/StateInfo")
    response = conn.getresponse()
    data = response.read()
    conn.close()

    doc = json.load(data)
    drone_state = doc["DroneState"]
    if drone_state == "CaptureFinish":
        break
    print("Waiting for Capture")
    time.sleep(0.1)

vehicle_state()
print(drone_state)


print("Returning to Launch")

vehicle.mode = VehicleMode("RTL")  # 지정홈으로 복귀

conn = http.client.HTTPConnection(server, port)
conn.request("GET", "/StateInfo/update?DroneState=GoHome")
conn.getresponse()
conn.close()
print(drone_state)
vehicle_state()

time.sleep(40)


vehicle.armed = False
time.sleep(5)

while vehicle.armed:
    print(" Waiting for disarmed...")
    time.sleep(1)

print("Close vehicle object")
vehicle.close()
