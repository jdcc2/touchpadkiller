import click
from touchpadkiller import TouchpadKiller
import logging
import os

@click.group()
def cli():
    pass

@click.command(help='List input devices under /dev/input/event*')
def listDevices():
    TouchpadKiller.listDevices()
    tp = TouchpadKiller.getFirstTouchpad()
    print(tp.fn, tp.name)

@click.command()
@click.option('--delay', default=0.3)
@click.option('--kbname', default=None, type=str, help='Device name of the keyboard as printed by list devices. Has precedence over selection by input device number.')
@click.option('--tpname', default=None, type=str, help='Device name of the touchpad as printed by list devices. Has precedence over selection by input device number.')
@click.option('--kbeventnr', default=-1, help='Device number of the keyboard under /dev/input/event*')
@click.option('--tpeventnr', default=-1, help='Device number of the touchpad under /dev/input/event*')
@click.option('--logfile', default=None, type=str, help='Specify a log file path')
@click.option('--log', is_flag=True, help='Enable file logging. Default log path is HOME/touchpadkiller/touchpadkiller.log')
def start(delay, kbname, tpname, kbeventnr, tpeventnr, logfile, log):

    logformat = '%(asctime)s:%(levelname)s:%(message)s'
    if log and logfile is not None:
        logging.basicConfig(format=logformat, filename=logfile, level=logging.DEBUG)
    elif log:
        #Get default log dir
        defaultlogdir = os.path.join(os.path.expanduser('~'), '.touchpadkiller')
        if not os.path.isdir(defaultlogdir):
            #Create default logdir
            os.mkdir(defaultlogdir, 0o770)

        logging.basicConfig(format=logformat, filename=os.path.join(defaultlogdir, 'touchpadkiller.log'), level=logging.DEBUG)
    keyboard = None
    touchpad = None
    if kbname is not None:
        keyboard = TouchpadKiller.getDeviceByName(kbname)
    elif kbeventnr != -1:
        keyboard = '/dev/input/event{}'.format(kbeventnr)
    else:
        keyboard = TouchpadKiller.getFirstKeyboard()

    if tpname is not None:
        touchpad = TouchpadKiller.getDeviceByName(tpname)
    elif tpeventnr != -1:
        touchpad = '/dev/input/event{}'.format(tpeventnr)
    else:
        touchpad = TouchpadKiller.getFirstTouchpad()

    #passing None as keyword or touchpad will raise a value error
    try:
        td = TouchpadKiller(keyboard, touchpad, delay)
        logging.info('Using the keyboard {} at {} to detect typing'.format(td.keyboard.name, td.keyboard.fn))
        logging.info('Disabling the touchpad {} at {} while typing'.format(td.touchpad.name, td.touchpad.fn))
        td.run()
    except ValueError as e:
        logging.error(e)
        logging.error('Exiting...')
        return


def execute():
    cli.add_command(listDevices)
    cli.add_command(start)
    cli()

if __name__ == "__main__":
    execute()
