from setuptools import setup
setup(name='touchpad-killer',
      version='1.0',
      packages=['touchpadkiller'],
      license='GPL',
      install_requires=['click', 'evdev'],
      entry_points = {
        'console_scripts': ['touchpadkiller=touchpadkiller.cli:execute'],
        },

    )

