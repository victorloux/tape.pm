#!/usr/bin/env python3
"""Constantly records an audio stream from the microphone input,
and save the last n seconds to a file upon pressing a button or key.

(c) 2016 Victor Loux / b00t consultants ltd"""

import argparse
import logging
import time
import sounddevice as sd
import soundfile as sf
import numpy as np
from hashids import Hashids

import netifaces as ni
import subprocess

# above are libraries; this is the project's own modules
import _record_triggers
import _save
from Adafruit_Thermal import Adafruit_Thermal

RPi = True  # True to use button on GPIO, false to use keys
logfile = "project.log"
outputFolder = "media/tmp/"

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s] (%(threadName)s) %(message)s',
                    handlers=[logging.FileHandler(logfile),
                              logging.StreamHandler()])

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("-d", "--duration", type=int, default=60,
                    help="Duration to record, in seconds (omitting will \
                    default to 60 seconds")
parser.add_argument("-r", "--sample-rate", type=int, default=44100, help="Sample\
                     rate to record (omitting will default to 44,100Hz)")
parser.add_argument("-s", "--startup", action='store_true', help="Print startup info")
args = parser.parse_args()

# initiate hash generator with only lowercase characters,
# & deleting ones that look like each other (o 0, i 1 l, s 5)
hashids = Hashids(alphabet='abcdefghjkmnpqrtuvwxyz02346789')
printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)

print("Press R to record")

##################################
# Variables used throughout
recordingLength = args.sample_rate * args.duration  # number of frames to keep
recordStream = np.array([0], dtype=np.int32)
status = None
inputStream = None

##################################


def saveRecordingCallback(indata, frames, time, status):
    """This callback is called continuously by the PySoundDevice's Stream
    every n frames (usually 512, but exact number given in frames)
    it will update our recordStream array to add the new data from the stream.
    If the array contains more than the max amount of time we want to record,
    then it will start removing frames from the beginning of the array as well
    to ensure it does not get too big over time and only contains what we save
    """
    global recordStream

    if status:
        logging.warning(str(status))

    recordStream = np.append(recordStream, indata)

    if len(recordStream) > recordingLength:
        # [frames:] means 'slice the array recordStream, start from number of
        # frames just added, stop at the end of array
        recordStream = recordStream[frames:]

        # alternatively: (this might be more performant? @todo)
        # recordStream = np.delete(recordStream, list(range(0, args.sample_rate)), 0)

##################################

lastRecording = time.time()


def triggerRecordingCallback(channel=None):
    """When the button (or key) is pressed this will be called
    It takes the current recording, saves it into a file,
    and triggers the web upload + print code

    the channel argument is unused but it's sent by the GPIO lib"""
    global lastRecording

    print("PUSHY PUSH " + str(channel))

    # Here: check the last recording was made > 6 seconds ago
    if(lastRecording >= time.time() - 6):
        return

    lastRecording = time.time()

    maxIdentifier = 1460000000  # max timestamp / change after 20/06/16 to avoid potential dupes
    uniqueId = hashids.encode(int(time.time() - maxIdentifier))
    logging.info("[%s] Requested recording (%i frames, %f s)",
                 uniqueId,
                 len(recordStream),
                 len(recordStream) / args.sample_rate)

    # Save the file
    filename = outputFolder + uniqueId + ".wav"
    # sf.write(filename, recordStream, args.sample_rate, subtype='VORBIS', format='OGG')
    sf.write(filename, recordStream, args.sample_rate, "PCM_16")

    rp = _save.RecordingProcess()
    rp.setParameters(uniqueId, filename)
    rp.setPrinter(printer)
    rp.daemon = True
    rp.start()


def printStartupInfo():
    """Prints out IP addresses and SSID so we can access it headless"""
    printer.feed(3)
    printer.setSize('L')
    printer.println("Boot complete!")

    # Wait for a connection on the wifi first
    tries = 0
    wifi_connected = False

    while tries < 6:
        sd.sleep(5000)
        a = ni.ifaddresses("wlan0")

        if((2 in a) and ('addr' in a[2][0])):
            wifi_connected = True
            break

        tries = tries + 1

    printer.setSize('M')
    printer.println("IP addresses")
    printer.setSize('S')

    for iface in ni.interfaces():
        a = ni.ifaddresses(iface)

        if((2 in a) and ('addr' in a[2][0])):
            printer.println(iface + ": " + a[2][0]['addr'])
        else:
            printer.println(iface + ": not connected")

        logging.info("CONNECT iface %s: %s", iface, a)

    printer.setSize('M')
    printer.println("Wifi SSID")

    printer.setSize('S')
    if wifi_connected:
        s = subprocess.check_output(["iwgetid", "wlan0", "-r"])
        printer.println(s.decode())
    else:
        printer.println("No connection after 5 tries")

    printer.feed(6)

##################################

rt = _record_triggers.RecordTrigger()
rt.daemon = True

try:
    rt.setCallbackAndRPi(triggerRecordingCallback, RPi)
    rt.start()

    # As we start up: wait for network connection + print device info
    if(args.startup):
        printStartupInfo()

    inputStream = sd.InputStream(channels=1, callback=saveRecordingCallback,
                                 samplerate=args.sample_rate, blocksize=0,
                                 latency=0.3)
    inputStream.start()

    # make the loop continuous without blocking too many resources
    while True:
        sd.sleep(2000)

except KeyboardInterrupt:
    parser.exit('\nInterrupted by user')

except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))

finally:
    inputStream.stop()
    inputStream.close()
    rt.stop()

    printer.wake()        # Call wake() before printing again, even if reset
    printer.setDefault()  # Restore printer to defaults
    printer.sleep()       # Tell printer to sleep

    if RPi:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()
