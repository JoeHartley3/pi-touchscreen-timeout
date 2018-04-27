#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# timeout.py - a little program to blank the RPi touchscreen and unblank it
#     on an input event.  Based on a C program by https://github.com/timothyhollabaugh
#
#     The biggest difference between the two programs (besides the port to Python)
#     is that this program scans ALL the input devices for an event and unblanks for any
#     event.
#
#     2018-04-27 - Joe Hartley, https://github.com/JoeHartley3
#
#     Note that when not running X Windows, the console framebuffer may blank and not return on touch.
#     Use one of the following fixes:
#
#     * Raspbian Jessie
#       Add the following line to /etc/rc.local (on the line before the final exit 0) and reboot:
#          sh -c "TERM=linux setterm -blank 0 >/dev/tty0"
#       Even though /dev/tty0 is used, this should propagate across all terminals.
#
#     * Raspbian Wheezy
#       Edit /etc/kbd/config and change the values for the variable shown below, then reboot:
#          BLANK_TIME=0


import sys
import evdev
from datetime import datetime, timedelta
from select import select


def init_backlight():
    lfd = None
    try:
        lfd = open('/sys/class/backlight/rpi_backlight/bl_power', 'r+')
    except Exception as e:
        print('Error {} accessing backlight control'.format(e))
        exit(-2)
    try:
        lfd.read()
    except Exception as e:
        print("Error {} reading backlight file".format(e))
        exit(-3)
    return lfd


def lightswitch(state='on'):
    try:
        if state == 'off':
            lightfd.write('1')
        else:
            lightfd.write('0')
        lightfd.flush()
    except Exception as e:
        print('Error {} turning backlight {}'.format(e, state))


if len(sys.argv) != 2:
    print("Usage: timeout <timeout_sec>\n"
          "    Scans all devices listed by lsinput for activity, turns off backlight when\n"
          "    no input found for <timeout_sec> seconds")
    exit(1)

lightfd = init_backlight()
timeout = timedelta(**{'seconds': int(sys.argv[1])})
# Enumerate all the input devices to scan for activity
devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
devices = {dev.fd: dev for dev in devices}

on = True
now = datetime.now()
touch = now
while True:
    # Cycle through the devices scanning for events.  The last parameter is the wait between checks.
    # 0.1 (1/10 second) has a load of around 0.5% of one CPU core. Using zero (no wait) consumes 100%
    # of a core, while no value at all blocks the device.
    r, w, x = select(devices, [], [], 0.1)
    for fd in r:
        now = datetime.now()
        for event in devices[fd].read():
            touch = datetime.fromtimestamp(event.timestamp())
            if not on:
                print('Turning on')
                on = True
                lightswitch('on')
    if now - touch > timeout:
        if on:
            print("Turning off")
            on = False
            lightswitch('off')
    now = datetime.now()
