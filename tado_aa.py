#
# tado_aa.py (Tado Auto-Assist for Geofencing and Open Window Detection)
# Created by Adrian Slabu <adrianslabu@icloud.com> on 11.02.2021
# 

import sys
import time

from PyTado.interface import Tado

def main():

    global lastMessage
    global username
    global password
    global checkingInterval
    global errorRetringInterval

    lastMessage = ""

    username = "your_username@mail.com" # tado username
    password = "your_password" # tado password

    checkingInterval = 6.0 # checking interval (in seconds)
    errorRetringInterval = 20.0 # retrying interval (in seconds), in case of an error

    login()
    homeStatus()
    
def login():

    global t

    try:
        t = Tado(username, password)

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
        homeState = t.getHomeState()["presence"]
        devicesHome = []

        for mobileDevice in t.getMobileDevices():
            if (mobileDevice["location"]["relativeDistanceFromHomeFence"] == 0.0):
                devicesHome.append(mobileDevice["name"])

        if (lastMessage.find("Connection Error") != -1 or lastMessage.find("Waiting for the user to sign in") != -1):
            printm ("Connection established, everything looks good now, continuing..\n")

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
            t.setAway()
            printm ("Done!")
        elif (len(devicesHome) > 0 and homeState == "AWAY"):
            if (len(devicesHome) == 1):
                printm ("Your home is in AWAY Mode but the device " + devicesHome[0] + " is at home.")
            else:
                devices = ""
                for i in range(len(devicesHome) - 1):
                    if (i != len(devicesHome) - 1):
                        devices += devicesHome[i] + ", "
                    else:
                        devices += devicesHome[i]
                printm ("Your home is in AWAY Mode but the devices " + devices + " are at home.")

            printm ("Activating HOME mode.")
            t.setHome()
            printm ("Done!")

        devicesHome.clear()
        printm ("Waiting for a change in devices location or for an open window..")
        time.sleep(1)
        geofencing()

    except KeyboardInterrupt:
        printm ("Interrupted by user.")
        sys.exit(0)

    except Exception as e:
        if (str(e).find("location") != -1):
            printm ("I cannot get the location of one of the devices because the user signed out from tado app.\nWaiting for the user to sign in, until then the Geofencing Assist is NOT active.\nWaiting for an open window..")
            time.sleep(1)
            openWindowDetection()
        elif (str(e).find("NoneType") != -1):
            time.sleep(1)
            openWindowDetection()
        else:
            printm (str(e) + "\nConnection Error, retrying in " + str(errorRetringInterval) + " sec..")
            time.sleep(errorRetringInterval)
            homeStatus()

def openWindowDetection():

    try:
        for z in t.getZones():
            zoneID = z["id"]
            zoneName = z["name"]
            if (t.getOpenWindowDetected(zoneID)["openWindowDetected"] == True):
                printm (zoneName + ": open window detected, activating the OpenWindow mode.")
                t.setOpenWindow(zoneID)
                printm ("Done!")
                printm ("Waiting for a change in devices location or for an open window..")

        geofencing()

    except KeyboardInterrupt:
        printm ("Interrupted by user.")
        sys.exit(0)

    except Exception as e:
        printm (str(e) + "\nConnection Error, retrying in " + str(errorRetringInterval) + " sec..")
        time.sleep(errorRetringInterval)
        openWindowDetection()

def geofencing():

    try:
        homeState = t.getHomeState()["presence"]

        for mobileDevice in t.getMobileDevices():
            if (mobileDevice["location"]["relativeDistanceFromHomeFence"] == 0.0):
                devicesHome.append(mobileDevice["name"]) 

        if (lastMessage.find("Connection Error") != -1 or lastMessage.find("Waiting for the user to sign in") != -1):
            printm ("Connection established, everything looks good now, continuing..\n")
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
            t.setHome()
            printm ("Done!")
            printm ("Waiting for a change in devices location or for an open window..")

        elif (len(devicesHome) == 0 and homeState == "HOME"):
            printm ("Are no devices at home, activating AWAY mode.")
            t.setAway()
            printm ("Done!")
            printm ("Waiting for a change in devices location or for an open window..")

        devicesHome.clear()
        time.sleep(checkingInterval)
        openWindowDetection()

    except KeyboardInterrupt:
        printm ("Interrupted by user.")
        sys.exit(0)

    except Exception as e:
        if (str(e).find("location") != -1 or str(e).find("NoneType") != -1):
            printm ("I cannot get the location of one of the devices because the user signed out from tado app.\nWaiting for the user to sign in, until then the Geofencing Assist is NOT active.\nWaiting for an open window..")
            time.sleep(checkingInterval)
        else:
            printm (str(e) + "\nConnection Error, retrying in " + str(errorRetringInterval) + " sec..")
            time.sleep(errorRetringInterval)
        openWindowDetection()

def printm(message):
    global lastMessage
    if (message != lastMessage):
        lastMessage = (message)
        sys.stdout.write(message + "\n")

main()