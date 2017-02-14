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


"""
http://candidtim.github.io/appindicator/2014/09/13/ubuntu-appindicator-step-by-step.html

TODO

- automatically select the first keyboard and mouse when none are specified

"""





class TouchpadKiller:
    def __init__(self, keyboard_path, touchpad_path, delay):
        self.keyboard = InputDevice(keyboard_path)
        self.touchpad = InputDevice(touchpad_path)
        self.delay = delay
        self.lastTypeEvent = 0
        self.disabled = False
        self.eventLoop = None

    @staticmethod
    def listDevices():
        devices = [InputDevice(fn) for fn in list_devices()]
        for device in devices:
            print(device.fn, device.name, device.phys)

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
        while True:
            if time.time() > self.lastTypeEvent + self.delay and self.disabled:
                self.touchpad.ungrab()
                self.disabled = False
                #print("enable")
            elif time.time() < self.lastTypeEvent + self.delay and not self.disabled:
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
        print('Terminate signal received. Exiting..')
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
        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', self.quit)
        menu.append(item_quit)
        menu.show_all()
        return menu

    def quit(self, source):
        gtk.main_quit()
        self.eventProcess.terminate()








