# Pi-touchscreen-timeout
Leaving the backlight on the Official Raspberry Pi touchscreen can quickly wear it out.
If you have a use that requires the RPi to be on all the time, but does not require the
display on all the time, then turning off the backlight while not in use can dramatically
increase the life of the backlight.

Pi-touchscreen-timeout will transparently turn off the display backlight after there 
have been no touches for a specifed timeout, independent of anything using the display
at the moment. It will then turn the touchscreen back on when it is touched.  The
timeout period is set by a command-line argument.

**Note:** This does not stop the touch event from getting to whatever is running on
the display. Whatever is running will still receive a touch event, even if the display
is off.

The preferred program to use is timeout.py, which will watch all inputs listed by 
'lsinput' for an event to turn the screen back on.  The C program only watches a
specified input device for events.

The programs both use a linux event device like `/dev/input/event0` to receive events
from the touchscreen.  When running the C program, the event device to use
is a command-line parameter without the /dev/input/ path specification.

Both programs use `/sys/class/backlight/rpi-backlight/bl_power` to turn the
backlight on and off.  The event device is a command-line parameter without the
/dev/input/ path specification.

# Installation - Python

The library 'evdev' is required to run this program.  Install it with pip:
```
pip install evdev
```

You can then run the program by giving it a single parameter, the amount of time
in seconds before the screen is blanked.
```
sudo python timeout.py 30
```
# Installation - C

Clone the repository and change directories:
```
git clone https://github.com/joehartley3/pi-touchscreen-timeout.git
cd pi-touchscreen-timeout
```
...or just download timeout.c.  Now you can build and run it!
```
gcc timeout.c -o timeout
sudo ./timeout 30 event0
```

**Note:** Either program must be run as root or with `sudo` to be able to access
the backlight.

It is recommended to run this at startup, for example by putting a line in 
`/etc/rc.local`.

### Conflict with console blanker

When running this program without X Windows running, such as when running a Kivy
program in the console at startup, you may run into a conflict with a console 
blanker.  In such an instance, the backlight will be turned on, but with the 
console blanked, it seems like the backlight has not come on.

In this case, follow one of these methods for disabling the console blanker:
   * Raspbian Jessie : 
     Add the following line to /etc/rc.local (on the line before the final exit 0) 
     and reboot:
```
  sh -c "TERM=linux setterm -blank 0 >/dev/tty0"
```

   Even though /dev/tty0 is used, this should propagate across all terminals.

   * Raspbian Wheezy :
     Edit /etc/kbd/config and change the values for the variable shown below, 
     then reboot:
```
  BLANK_TIME=0
```