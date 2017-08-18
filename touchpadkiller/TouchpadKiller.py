from evdev import InputDevice, ecodes, categorize, list_devices
import time
import click
import asyncio
import signal
from multiprocessing import Process
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk
gi.require_version('AppIndicator3', '0.1')
from gi.repository import AppIndicator3 as appindicator
import logging

"""
http://candidtim.github.io/appindicator/2014/09/13/ubuntu-appindicator-step-by-step.html

TODO

- detect if a mouse button was pressed but not released yet
- automatically select the first keyboard and mouse when none are specified

"""





class TouchpadKiller:

    def __init__(self, keyboard, touchpad, delay):
        """

        :param keyboard: InputDevice or path to keyboard device (/dev/input/event*)
        :param touchpad: InputDevice or path to touchpad device (/dev/input/event*)
        :param delay: seconds to wait after typing stops to re-enable touchpad
        """
        if isinstance(keyboard, InputDevice):
            self.keyboard = keyboard
        elif isinstance(keyboard, str):
            self.keyboard = InputDevice(keyboard)
        else:
            raise ValueError('Invalid keyboard argument')

        if isinstance(touchpad, InputDevice):
            self.touchpad = touchpad
        elif isinstance(touchpad, str):
            self.touchpad = InputDevice(touchpad)
        else:
            raise ValueError('Invalid touchpad argument')

        self.delay = delay
        self.lastTypeEvent = 0
        self.disabled = False
        self.eventLoop = None

    @staticmethod
    def listDevices():
        devices = [InputDevice(fn) for fn in list_devices()]
        print('[PATH] - "[NAME]" - [PHYS]')
        for device in devices:
            print('{} - "{}" - {}'.format(device.fn, device.name, device.phys))
            print("active keys")
            print(device.active_keys())
            caps = device.capabilities()

    @staticmethod
    def getFirstTouchpad():
        """
        touchpad.fn contains the device path

        :return: touchpad or None
        """
        devices = [InputDevice(fn) for fn in list_devices()]
        touchpad = None
        #Search the input devices if it has a mouse button it is a mouse :-|
        for device in devices:
            caps = device.capabilities()
            if ecodes.EV_KEY in caps:
                for key in caps[ecodes.EV_KEY]:
                    if key == ecodes.BTN_MOUSE:
                        touchpad = device

                if touchpad is not None:
                    break
        return touchpad

    @staticmethod
    def getFirstKeyboard():
        devices = [InputDevice(fn) for fn in list_devices()]
        keyboard = None
        # Search the input devices if it has an ESC key it is a keyboard :-|
        for device in devices:
            caps = device.capabilities()
            if ecodes.EV_KEY in caps:
                for key in caps[ecodes.EV_KEY]:
                    if key == ecodes.KEY_ESC:
                        keyboard = device

                if keyboard is not None:
                    break
        return keyboard

    @staticmethod
    def getDeviceByName(devicename):
        devices = [InputDevice(fn) for fn in list_devices()]
        result = None
        # Search the input devices if it has an ESC key it is a keyboard :-|
        for device in devices:
            if device.name.lower() == devicename.lower():
                result = device

        return result

    async def detectTyping(self):

        async for event in self.keyboard.async_read_loop():
            if event.type == ecodes.EV_KEY \
                    and event.code != ecodes.KEY_LEFTCTRL\
                    and event.code != ecodes.KEY_RIGHTCTRL \
                    and event.code != ecodes.KEY_LEFTSHIFT \
                    and event.code != ecodes.KEY_RIGHTSHIFT \
                    and event.code != ecodes.KEY_RIGHTALT \
                    and event.code != ecodes.KEY_LEFTALT:
                        #Non-modifier keypress detected
                    self.lastTypeEvent = time.time()
                    #print('keyevent')

    async def controlTouchpad(self):
        print("yoeloeeleo")
        logging.warn("controltouchpad")
        while True:

            if time.time() > self.lastTypeEvent + self.delay and self.disabled:

                self.touchpad.ungrab()
                self.disabled = False
                #print("enable")
            elif time.time() < self.lastTypeEvent + self.delay and not self.disabled:
                print("yolo")
                print(self.touchpad.active_keys())
                self.touchpad.grab()
                self.disabled = True
                #print("disabled")

            await asyncio.sleep(0.1)

    def runEventLoop(self, loop):

        # device = InputDevice('/dev/input/event16')
        asyncio.ensure_future(self.detectTyping())
        asyncio.ensure_future(self.controlTouchpad())
        #self.eventLoop = asyncio.get_event_loop()
        self.eventLoop = loop
        asyncio.set_event_loop(loop)
        for signame in ('SIGINT', 'SIGTERM'):
            self.eventLoop.add_signal_handler(getattr(signal, signame), self.stopEventLoop)
        self.eventLoop.run_forever()

    def stopEventLoop(self):
        logging.info('Terminate signal received. Exiting..')
        self.eventLoop.stop()

    def run(self):
        indicator = appindicator.Indicator.new('Touchpaddisabler', 'input-tablet',
                                               appindicator.IndicatorCategory.SYSTEM_SERVICES)
        indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        indicator.set_menu(self.build_menu())
        loop = asyncio.get_event_loop()
        # import threading
        self.eventProcess = Process(target=self.runEventLoop, args=(loop,))
        self.eventProcess.start()

        signal.signal(signal.SIGINT, signal.SIG_DFL)
        gtk.main()
        self.eventProcess.join()

    def build_menu(self):
        menu = gtk.Menu()
        #create unclickable menuitems for the keyboard and touchpad
        #TODO make the touchpad/keyboard item a toggle to disable/enable the device permanently
        item_touchpad = gtk.MenuItem('TouchPad: {}'.format(self.touchpad.name), sensitive=False)
        item_keyboard = gtk.MenuItem('Keyboard: {}'.format(self.keyboard.name), sensitive=False)
        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', self.quit)
        menu.append(item_touchpad)
        menu.append(item_keyboard)
        menu.append(item_quit)
        menu.show_all()
        return menu

    def quit(self, source):
        gtk.main_quit()
        self.eventProcess.terminate()








