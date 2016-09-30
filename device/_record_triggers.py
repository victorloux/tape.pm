# @this file must be included from record.py

import sys
import select
import termios
import threading

class KeyPoller:
    def __enter__(self):
        # Save the terminal settings
        self.fd = sys.stdin.fileno()
        self.new_term = termios.tcgetattr(self.fd)
        self.old_term = termios.tcgetattr(self.fd)

        # New terminal setting unbuffered
        self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

        return self

    def __exit__(self, type, value, traceback):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    def poll(self):
        dr, dw, de = select.select([sys.stdin], [], [], 0)
        if not dr == []:
            return sys.stdin.read(1)
        return None

class RecordTrigger(threading.Thread):
    callback = None
    RPi = False
    active = True

    def setCallbackAndRPi(self, triggerRecordingCallback, RPi=False):
        self.callback = triggerRecordingCallback
        self.RPi = RPi

    def run(self):
        """The code below is only executed if we're on the
        Raspberry Pi and we need a GPIO pin to trigger sth"""
        if self.RPi:
            import RPi.GPIO as GPIO

            GPIO.setmode(GPIO.BCM)
            GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

            GPIO.add_event_detect(23, GPIO.RISING,
                                  callback=self.callback,
                                  bouncetime=300)

        # This starts a new thread with the KeyPress method
        self.loopPollForKeyPress()

    def stop(self):
        self.active = False

    # This function will be the one running in a separate thread
    # It constantly polls for a key press, if there is then
    # it will execute the callback code (self.callback())
    def loopPollForKeyPress(self):
        with KeyPoller() as keypoller:
            while self.active:
                character = keypoller.poll()
                if character is not None:
                    if character == "r":
                        self.callback()
                    # print(character)
