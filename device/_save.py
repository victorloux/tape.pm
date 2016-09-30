#!/usr/bin/env python3

"""This file sends a file to the internet,
and prints out the code. Should be called from
within record.py

(c) 2016 Victor Loux / b00t consultants ltd"""

import logging
import os
import threading
import subprocess
import requests
# from PIL import Image

endpoint = 'http://tape.pm'
upload_key = '[your-upload-key-here]'
bitrate = "192"  # mp3 conversion bitrate
encodeFolder = "media/encoded/"
processedFolder = "media/sent/"


class RecordingProcess(threading.Thread):
    hash = None
    wav_location = None
    mp3_location = None

    def setParameters(self, hash, wav_location):
        """Sets the hash + location. Because it's a Threading subclass
        we can't easily pass these parameters to the constructor so have
        to do it separately, this should be called BEFORE rp.start()"""
        self.hash = hash
        self.wav_location = wav_location
        self.mp3_location = encodeFolder + hash + ".mp3"

    def setPrinter(self, printer):
        self.printer = printer

    def run(self):
        logging.debug("[%s] saved, processing %s", self.hash, self.wav_location)

        self.sendToPrinter()
        self.convert()
        self.upload()

    def sendToPrinter(self):
        """Sends the download code to the printer
        @todo: test it, and time how long the *code* takes
               it might have to be sent to a different thread again
               to avoid blocking the upload of the file

        See https://github.com/adafruit/Python-Thermal-Printer/
        for documentation + help on printing images
        """

        logging.info("[%s] Sending code to printer", self.hash)

        # self.printer.wake()# Call wake() before printing again, even if reset
        self.printer.setDefault()  # Restore printer to defaults

        # self.printer.printImage(Image.open("hello.png"))
        # self.printer.printBitmap(adalogo.width, adalogo.height, adalogo.data)
        self.printer.justify('C')
        self.printer.feed(2)
        # self.printer.println("_|_  _,       _              ")
        # self.printer.println(" |  / |  |/\_|/  |/\_/|/|/|  ")
        # self.printer.println(" |_/\/|_/|_/ |_/o|_/  | | |_/")
        # self.printer.println("         |       |           ")

        self.printer.println("|                              ")
        self.printer.println("|--- ,---.,---.,---. ,---.,-.-.")
        self.printer.println("|    ,---||   ||---' |   || | |")
        self.printer.println("`---'`---^|---'`---'o|---'` ' '")
        self.printer.println("          |          |         ")

        #self.printer.setSize('L')
        #self.printer.println("That was a\nnice tune!")
        self.printer.setSize('S')
        self.printer.println("Nice tune! You should listen\nto it again. Go to")
        #self.printer.println("Go to ")
        self.printer.setSize('L')
        self.printer.println("http://tape.pm")
        self.printer.setSize('S')
        self.printer.println("and enter your code:")

        self.printer.setSize('L')
        self.printer.println(str(self.hash))

        self.printer.setSize('S')
        self.printer.feed(1)
        self.printer.println("--------------------------------")
        self.printer.feed(4)

        # self.printer.sleep()      # Tell printer to sleep

    def convert(self):
        """Synchronous conversion from wav to mp3"""

        logging.info("[%s] Starting encoding", self.hash)

        rc = subprocess.call(["lame", "-Sb", bitrate, self.wav_location, self.mp3_location])

        if rc == 0:
            logging.info("[%s] mp3 encoding successful", self.hash)
        else:
            logging.error("[%s] Error during mp3 conversion", self.hash)

    def upload(self):
        logging.info("[%s] Starting upload", self.hash)

        with open(self.mp3_location, 'rb') as f:
            files = {'soundfile': f}
            payload = {'upload_key': upload_key}
            r = requests.post(endpoint + "/upload.php", files=files,
                              data=payload)

            if r.status_code == 200:
                self.moveFile()
                logging.info("[%s] Uploaded successfully", self.hash)

            else:
                logging.error("[%s] Error while uploading file: %d %s",
                              self.hash, r.status_code, r.text)

    def moveFile(self):
        """Move file elsewhere once it's been processed and uploaded *FOR SURE*
        (nb: to test first, but actually we should delete it to save space on
            the card as this might grow very quickly)
        """

        try:
            os.rename(self.wav_location, processedFolder + self.hash + ".wav")
            os.rename(self.mp3_location, processedFolder + self.hash + ".mp3")

        except Exception as e:
            logging.warn(type(e).__name__ + ': ' + str(e))
