#!/usr/bin/env python3

"""
• Klem 0 gemeenschappelijke – (omschakelbaar in impulskastje) ZWART
• Klem 1 +P actief levering naar klant (+A) BRUIN
• Klem 2 Q1 inductief levering naar klant (+i) ROOD
• Klem 3 Q4 capacitief levering naar klant (-c) ORANJE
• Klem 4 Synchronisatiepuls meetperiode GEEL
• Klem 5 Tariefuitgang NU/SU → toekomst vrij GROEN
• Klem 6 Tariefuitgang OUST → toekomst vrij BLAUW
• Klem 7 –P actief teruglevering van klant (-A) PAARS
• Klem 8 Q2 capacitief teruglevering van klant (+c) GRIJS
• Klem 9 Q3 inductief teruglevering van klant (-i) WIT
"""
import queue
import signal
import sys
import threading
import logging
import time
import django
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import pulscapture.settings
import RPi.GPIO as GPIO

settings.configure(default_settings=pulscapture.settings, DEBUG=True)
django.setup()

# Now this script or any imported module can use any part of Django it needs.
from api.models import PulseOutput, Pulse

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
logger = logging.getLogger(__name__)

P_O_ACTIEF_GPIO = 5
Q1_O_INDUCTIEF_GPIO = 6
Q4_O_CAPACITIEF_GPIO = 13

P_I_ACTIEF_GPIO = 16
Q2_O_INDUCTIEF_GPIO = 20
Q3_O_CAPACITIEF_GPIO = 21

TARIEF_DAG_NACHT_GPIO = 19
TARIEF_OUST_GPIO = 26

SYNC_GPIO = 12

pulses = {
    P_O_ACTIEF_GPIO: "+P actief levering",
    Q1_O_INDUCTIEF_GPIO: "Q1 inductief levering",
    Q4_O_CAPACITIEF_GPIO: "Q4 capacitief levering",
    P_I_ACTIEF_GPIO: "-P actief teruglevering",
    Q2_O_INDUCTIEF_GPIO: "Q2 capacitief teruglevering",
    Q3_O_CAPACITIEF_GPIO: "Q3 inductief teruglevering",
    SYNC_GPIO: "Synchronisatiepuls"
}

rQueue = queue.Queue()

pulse_outputs = PulseOutput.objects.all()


def signal_handler(sig, frame):
    print("CleanUp GPIO")
    GPIO.cleanup()
    sys.exit(0)


class PulseQueueHandler:

    def __init__(self, inQueue):
        self.inQueue = inQueue

        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        global pulse_outputs

        while True:
            try:
                s = self.inQueue.get(block=True, timeout=0.1)
            except queue.Empty:
                continue
            # ProcessQueueItem
            pulse_name = pulses.get(s)
            logger.debug(pulse_name)
            # Store Event

            pulse_output = pulse_outputs.get(channel=s)
            new_pulse = Pulse(pulse_output=pulse_output)
            new_pulse.save()
            # Calculate bucket values


def pulse_received_callback(channel):
    global rQueue
    rQueue.put(item=channel)


def set_pulse_channel(channel):
    GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(channel, GPIO.FALLING,
                          callback=pulse_received_callback, bouncetime=100)


def check_pulse_output_config(channel, name):
    global pulse_outputs

    try:
        pulse_output_found = pulse_outputs.get(channel=channel)
    except ObjectDoesNotExist:
        pulse_output = PulseOutput(channel=channel, name=name)
        pulse_output.save()


if __name__ == '__main__':

    GPIO.setmode(GPIO.BCM)

    # Handle the pulseitems on the queue
    pulseHandler = PulseQueueHandler(rQueue)

    # setup pulse channels
    for pulse in pulses.keys():
        set_pulse_channel(pulse)
        check_pulse_output_config(pulse, pulses[pulse])

    # refresh pulse_outputs in DB
    pulse_outputs = pulse_outputs.all()

    # test
    time.sleep(5)
    rQueue.put(P_O_ACTIEF_GPIO)

    # do cleanup on exit
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()
