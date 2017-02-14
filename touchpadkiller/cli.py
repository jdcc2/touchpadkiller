import click
from touchpadkiller import TouchpadKiller

@click.group()
def cli():
    pass

@click.command(help='List input devices under /dev/input/event*')
def listDevices():
    TouchpadKiller.listDevices()

@click.command()
@click.option('--delay', default=0.3)
@click.option('--kbeventnr', default=3, help='Device number of the keyboard under /dev/input/event*')
@click.option('--tpeventnr', default=16, help='Device number of the touchpad under /dev/input/event*')
def start(delay, kbeventnr, tpeventnr):

    td = TouchpadKiller('/dev/input/event{}'.format(kbeventnr), '/dev/input/event{}'.format(tpeventnr), delay)
    td.run()


def execute():
    cli.add_command(listDevices)
    cli.add_command(start)
    cli()

if __name__ == "__main__":
    execute()
