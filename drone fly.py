from __future__ import print_function
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal
import time

import argparse
parser = argparse.ArgumentParser(
    description='Print out vehicle state information. Connects to SITL on local PC by default.')
parser.add_argument('--connect',
                    help="vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()
connection_string = args.connect


print("\nConnecting to vehicle on: %s" % connection_string)
vehicle = connect(connection_string, wait_ready=False)

# def wildcard_callback(self, attr_name, value):
#     print (" CALLBACK: (%s): %s" %(attr_name,value))
#     time.sleep(10)

# print("\nAdd attribute callback detecting any attribute change")
# vehicle.add_attribute_listener('*',wildcard_callback)

# print("Wait is so callback invoked before observer removed")
# time.sleep(1)

# print("Remove Vehicle attribute observer")
# vehicle.remove_attribute_listener('*',wildcard_callback)

def vehicle_state():

    vehicle.wait_ready('autopilot_version')
    print(" Autopilot Firmware version: %s" % vehicle.version)

    print(" Global Location (relative altitude): %s" %
          vehicle.location.global_relative_frame)  
    print(" Attitude: %s" % vehicle.attitude)  
    print(" Velocity: %s" % vehicle.velocity)  
    print(" GPS HDOP: %s" % vehicle.gps_0.eph)  
    print(" GPS VDOP: %s" % vehicle.gps_0.epv) 
    print(" GPS fix type: %s" % vehicle.gps_0.fix_type)  
    print(" GPS satellites_visible: %s" %
          vehicle.gps_0.satellites_visible)  
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




def arm_and_takeoff(TargetAlt):
    print("Basic pre-arm checks")

    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    vehicle.mode = VehicleMode("GUIDED") 
    vehicle.armed = True  

  
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)
	vehicle.armed = True  
        print("Taking off!")
        vehicle.simple_takeoff(TargetAlt)  


  #
    while True:

        print(" Altitude: ", vehicle.location.global_relative_frame.alt)

        if vehicle.location.global_relative_frame.alt >= TargetAlt * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


<<<<<<< HEAD
arm_and_takeoff(10)

print("Set default/target airspeed to 2")
vehicle.airspeed = 2
print("Going towards first point for 30 seconds ...")
point1 = LocationGlobalRelative(37.340807327195925, 126.73091957660192, 10)
vehicle.simple_goto(point1)

time.sleep(30)

print("Going towards second point for 30 seconds ...")
point2 = LocationGlobalRelative(37.340577290298455, 126.73129421229582, 10)
# 이렇게 하면  wp1에서wp2까지 약20초 소요 넉넉하게25초 줄것
vehicle.simple_goto(point2, airspeed=2)

time.sleep(30)

print("Going towards third point for 30 seconds ...")
point3 = LocationGlobalRelative(37.340358556544516, 126.73168714352946, 10)
vehicle.simple_goto(point3, airspeed=2)

time.sleep(30)

print("Returning to Launch")

vehicle.mode = VehicleMode("RTL")  # 지정홈으로 복귀

time.sleep(30)

vehicle.mode = VehicleMode("LAND")

time.sleep(10)

vehicle.armed = False
time.sleep(5)
while vehicle.armed:
    print(" Waiting for disarmed...")
    time.sleep(1)

print("Close vehicle object")
vehicle.close()


# set_home_location(37.34086053950629, 126.73153724175877, 0)

vehicle_state()
=======
print("\nAdd `attitude` attribute callback/observer on `vehicle`")     

#
#set_home_location(37.3380809527555, 126.735575740178,700)
#

arm_and_takeoff(4)

print("Set default/target airspeed to 2")
vehicle.airspeed = 2
print("Going towards first point for 30 seconds ...")
point1 = LocationGlobalRelative(37.338077247868775, 126.73593403945812, 10)
vehicle.simple_goto(point1,airspeed=3)

time.sleep(10)
vehicle_state()
time.sleep(5)
vehicle_state()

print("Going towards second point for 30 seconds ...")
point2 = LocationGlobalRelative(37.3379570118895, 126.73555360549537, 10)
vehicle.simple_goto(point2, airspeed=3)

time.sleep(10)
vehicle_state()
time.sleep(5)

print("Going towards third point for 30 seconds ...")
point3 = LocationGlobalRelative(37.338056244024486, 126.73560685946146, 10)
vehicle.simple_goto(point3, airspeed=3)

time.sleep(7)
vehicle_state()
time.sleep(5)

print("RTL")
vehicle.mode = VehicleMode("RTL") 
time.sleep(15)



#print("LAND MODE")

#vehicle.mode = VehicleMode("LAND") 

#time.sleep(7)
vehicle_state()



time.sleep(5)

vehicle_state()
cnt=0
vehicle.armed = False
time.sleep(3)
while vehicle.armed:
    print("waitting DisArmed")
    time.sleep(1)
    cnt+=1
    if(cnt>10):
    	print("Faile to DisArmed")
        break

vehicle.armed = False
time.sleep(5)
print("Close vehicle object")
vehicle.close()


#set_home_location(37.34086053950629, 126.73153724175877,-200)



>>>>>>> 7ed1605f08f26c6cc3e195d2714ec80d796c2b59
