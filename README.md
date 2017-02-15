# Touchpadkiller
Program to disable the touchpad while typing for Ubuntu. Includes an indicator for the panel.

Uses the generic input event interface in Linux (/dev/input/*) to disable the touchpad while typing.
This can be usefull for touchpads which have incomplete driver support and are configured as generic input devices.

#Pre-requisites 

Make sure the user running the program has access to the devices in `/dev/input` (`/dev/input/event*`).
This can be done by making sure the user is a member of the `input` group.

#Dependencies
- Python3 and pip
- Python3 bindings to GTK3

Both of these dependencies are typically installed on recent Ubuntu versions.
 
#Installation

From the root of the cloned repo dir:
```
pip3 install .
``` 

#Usage

List the available input devices:
```
touchpadkiller listdevices
``` 

Start touchpadkiller while specifying the touchpad and keyboard by name with logging to `$HOME/touchpadkiller/touchpadkiller.log` enabled:
```
touchpadkiller start --log --tpname "[touchpad name]" --kbname "[keyboard name]"
```

#Tips
Use `xinput list` to find all touchpads and keyboards.

If you are not sure which name your keyboard or touchpad has, run `xinput disable [id number from xinput list]`, check if your keyboard/touchpad stops working, and then re-enable using `xinput enable [id]`.
(WARNING: Have a back-up keyboard ready so you don't accidentally disable your only keyboard)

#License

GPLv3
