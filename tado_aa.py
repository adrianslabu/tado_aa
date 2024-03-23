#
# tado_aa.py (Tado Auto-Assist for Geofencing and Open Window Detection)
# Created by Adrian Slabu <adrianslabu@icloud.com> on 11.02.2021
# 

import sys
import os
import time
import inspect

from datetime import datetime
from PyTado.interface import Tado

def main():

    global lastMessage
    global username
    global password
    global minTemp, maxTemp, enableTempLimit
    global checkingInterval
    global errorRetringInterval
    global enableLog
    global logFile
    global enableLogRotation
    global maxLines


    lastMessage = ""

    #Settings
    #--------------------------------------------------
    username = "your_tado_username" # tado username
    password = "your_tado_password" # tado password

    checkingInterval = 10.0 # checking interval (in seconds)
    errorRetringInterval = 30.0 # retrying interval (in seconds), in case of an error
    minTemp = 5 # minimum allowed temperature, applicable only if enableTempLimit is "TRUE"
    maxTemp = 25 # maximum allowed temperature, applicable only if enableTempLimit is "TRUE"
    enableTempLimit = True # activate min and max temp limit with "True" or disable it with "False"
    enableLog = False # activate the log with "True" or disable it with "False"
    logFile = "/l.log" # log file location
    enableLogRotation = False
    maxLines = 50 #log maximum number of lines
    #--------------------------------------------------

    login()
    homeStatus()
    
def login():

    global t

    try:
        t = Tado(username, password, None, False)

        if (lastMessage.find("Connection Error") != -1):
            printm ("Connection established, everything looks good now, continuing..\n")

    except KeyboardInterrupt:
        printm ("Interrupted by user.")
        sys.exit(0)

    except Exception as e:
        if (str(e).find("access_token") != -1):
            printm ("Login error, check the username / password !")
            sys.exit(0)
        else:
            printm (str(e) + "\nConnection Error, retrying in " + str(errorRetringInterval) + " sec..")
            time.sleep(errorRetringInterval)
            login()    

def homeStatus():
    
    global devicesHome

    try:
        homeState = t.get_home_state()["presence"]
        devicesHome = []

        for mobileDevice in t.get_mobile_devices():
            if (mobileDevice["settings"]["geoTrackingEnabled"] == True):
                if (mobileDevice["location"] != None):
                    if (mobileDevice["location"]["atHome"] == True):
                        devicesHome.append(mobileDevice["name"])

        if (lastMessage.find("Connection Error") != -1 or lastMessage.find("Waiting for the device location") != -1):
            printm ("Successfully got the location, everything looks good now, continuing..\n")

        if (len(devicesHome) > 0 and homeState == "HOME"):
            if (len(devicesHome) == 1):
                printm ("Your home is in HOME Mode, the device " + devicesHome[0] + " is at home.")
            else:
                devices = ""
                for i in range(len(devicesHome)):
                    if (i != len(devicesHome) - 1):
                        devices += devicesHome[i] + ", "
                    else:
                        devices += devicesHome[i]
                printm ("Your home is in HOME Mode, the devices " + devices + " are at home.")
        elif (len(devicesHome) == 0 and homeState == "AWAY"):
            printm ("Your home is in AWAY Mode and are no devices at home.")
        elif (len(devicesHome) == 0 and homeState == "HOME"):
            printm ("Your home is in HOME Mode but are no devices at home.")
            printm ("Activating AWAY mode.")
            t.set_away()
            printm ("Done!")
        elif (len(devicesHome) > 0 and homeState == "AWAY"):
            if (len(devicesHome) == 1):
                printm ("Your home is in AWAY Mode but the device " + devicesHome[0] + " is at home.")
            else:
                devices = ""
                for i in range(len(devicesHome)):
                    if (i != len(devicesHome) - 1):
                        devices += devicesHome[i] + ", "
                    else:
                        devices += devicesHome[i]
                printm ("Your home is in AWAY Mode but the devices " + devices + " are at home.")

            printm ("Activating HOME mode.")
            t.set_home()
            printm ("Done!")

        devicesHome.clear()
        printm ("Waiting for a change in devices location or for an open window..")
        printm ("Temp Limit is {0}, min Temp({1}) and max Temp({2})".format("ON" if (enableTempLimit) else "OFF", minTemp, maxTemp))
        time.sleep(1)
        engine()

    except KeyboardInterrupt:
        printm ("Interrupted by user.")
        sys.exit(0)

    except Exception as e:
        if (str(e).find("location") != -1):
            printm ("I cannot get the location of one of the devices because the Geofencing is off or the user signed out from tado app.\nWaiting for the device location, until then the Geofencing Assist is NOT active.\nWaiting for an open window..")
            time.sleep(1)
            engine()
        elif (str(e).find("NoneType") != -1):
            time.sleep(1)
            engine()
        else:
            printm (str(e) + "\nConnection Error, retrying in " + str(errorRetringInterval) + " sec..")
            time.sleep(errorRetringInterval)
            homeStatus()

def engine():

    while(True):
        try:
            #Open Window Detection
            for z in t.get_zones():
                    zoneID = z["id"]
                    zoneName = z["name"]
                    if (t.get_open_window_detected(zoneID)["openWindowDetected"] == True):
                        printm (zoneName + ": open window detected, activating the OpenWindow mode.")
                        t.set_open_window(zoneID)
                        printm ("Done!")
                        printm ("Waiting for a change in devices location or for an open window..")
            #Temp Limit
                    if (enableTempLimit == True):
                        if (t.get_state(zoneID)['setting']['type'] == 'HEATING' and t.get_state(zoneID)['setting']['power'] == "ON"):
                            setTemp = t.get_state(zoneID)['setting']['temperature']['celsius']
                            currentTemp = t.get_state(zoneID)['sensorDataPoints']['insideTemperature']['celsius']

                            if (float(setTemp) > float(maxTemp)):
                                t.set_zone_overlay(zoneID,0,maxTemp)
                                printm("{0}: Set Temp ({1}) is higher than the desired max Temp({2}), set {0} to {2} degrees!".format(zoneName, setTemp, maxTemp))
                            elif (float(setTemp) < float(minTemp)):
                                t.set_zone_overlay(zoneID,0,minTemp)
                                printm("{0}: Set Temp ({1}) is lower than the desired min Temp({2}), set {0} to {2} degrees!".format(zoneName, setTemp, minTemp))
                
            #Geofencing
            homeState = t.get_home_state()["presence"]

            devicesHome.clear()

            for mobileDevice in t.get_mobile_devices():
                if (mobileDevice["settings"]["geoTrackingEnabled"] == True):
                    if (mobileDevice["location"] != None):
                        if (mobileDevice["location"]["atHome"] == True):
                            devicesHome.append(mobileDevice["name"])

            if (lastMessage.find("Connection Error") != -1 or lastMessage.find("Waiting for the device location") != -1):
                printm ("Successfully got the location, everything looks good now, continuing..\n")
                printm ("Waiting for a change in devices location or for an open window..")

            if (len(devicesHome) > 0 and homeState == "AWAY"):
                if (len(devicesHome) == 1):
                    printm (devicesHome[0] + " is at home, activating HOME mode.")
                else:
                    devices = ""
                    for i in range(len(devicesHome)):
                        if (i != len(devicesHome) - 1):
                            devices += devicesHome[i] + ", "
                        else:
                            devices += devicesHome[i]
                    printm (devices + " are at home, activating HOME mode.")
                t.set_home()
                printm ("Done!")
                printm ("Waiting for a change in devices location or for an open window..")

            elif (len(devicesHome) == 0 and homeState == "HOME"):
                printm ("Are no devices at home, activating AWAY mode.")
                t.set_away()
                printm ("Done!")
                printm ("Waiting for a change in devices location or for an open window..")

            devicesHome.clear()
            time.sleep(checkingInterval)

        except KeyboardInterrupt:
                printm ("Interrupted by user.")
                sys.exit(0)

        except Exception as e:
                if (str(e).find("location") != -1 or str(e).find("NoneType") != -1):
                    printm ("I cannot get the location of one of the devices because the Geofencing is off or the user signed out from tado app.\nWaiting for the device location, until then the Geofencing Assist is NOT active.\nWaiting for an open window..")
                    time.sleep(checkingInterval)
                else:
                    printm (str(e) + "\nConnection Error, retrying in " + str(errorRetringInterval) + " sec..")
                    time.sleep(errorRetringInterval)

def printm(message):
    global lastMessage

    if enableLog and message != lastMessage:
        try:
            with open(logFile, "a") as log:
                log.write(datetime.now().strftime('%d-%m-%Y %H:%M:%S') + " # " + message + "\n")
                log.close()
        except Exception as e:
            sys.stdout.write(datetime.now().strftime('%d-%m-%Y %H:%M:%S') + " # " + str(e) + "\n")

        lastMessage = message
        sys.stdout.write(datetime.now().strftime('%d-%m-%Y %H:%M:%S') + " # " + message + "\n")

        # Check the number of lines in the log file
        if enableLogRotation and count_lines(logFile) >= maxLines:
            rotate_log()

def count_lines(file_path):
    with open(file_path) as file:
        return sum(1 for line in file)

def rotate_log():
    global logFile
    # Create a new log file with a timestamp
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    new_log_file = f"your_log_file_{timestamp}.log"
    
    # Close the current log file and rename it
    os.rename(logFile, new_log_file)
    
    # Open a new log file
    with open(logFile, "w"):
        pass

main()
