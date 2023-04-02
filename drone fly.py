from __future__ import print_function
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time

import argparse
parser = argparse.ArgumentParser(
    description='Print out vehicle state information. Connects to SITL on local PC by default.')
parser.add_argument('--connect',
                    help="vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()
connection_string = args.connect

# 드론 연결부분
print("\nConnecting to vehicle on: %s" % connection_string)
vehicle = connect(connection_string, wait_ready=False)

# 드론 기본적인 상태정보출력함수


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

# 시동 및 이륙


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


def Patrol_Mission():
    print("Set default/target airspeed to 2")
    vehicle.airspeed = 2
    print("Going towards first point for 30 seconds ...")
    point1 = LocationGlobalRelative(37.340807327195925, 126.73091957660192, 20)
    vehicle.simple_goto(point1)

    time.sleep(30)

    print("Going towards second point for 30 seconds ...")
    point2 = LocationGlobalRelative(37.340577290298455, 126.73129421229582, 20)
    vehicle.simple_goto(point2, airspeed=2)

    time.sleep(30)

    print("Going towards third point for 30 seconds ...")
    point3 = LocationGlobalRelative(37.340358556544516, 126.73168714352946, 20)
    vehicle.simple_goto(point3, airspeed=2)

    time.sleep(30)

    print("Returning to Launch")

    vehicle.mode = VehicleMode("RTL")  # 지정홈으로 복귀

    time.sleep(30)

    vehicle.mode = VehicleMode("LAND")

    time.sleep(10)

    vehicle.armed = False

    print("Close vehicle object")
    vehicle.close()


set_home_location(37.34086053950629, 126.73153724175877, 0)

vehicle_state()

arm_and_takeoff(10)

Patrol_Mission()
