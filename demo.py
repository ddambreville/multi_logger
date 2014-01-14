#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Created on 2014/01/14

@author : Emmanuel NALEPA
@contact : enalepa[at]aldebaran-robotics.com
@copyright : Aldebaran Robotics 2014

@requires : - multi_logger (Available with git clone
              git@git.aldebaran.lan:test-nao/picolog_adc24_python_driver.git)
            - naoqi python SDK  (Available on Version Gate)
              for logging from ALMemory

@platform : - Windows, Linux (PC or robot), OS X
            - If use of ADC24, only Windows

@summary : This module is an example of using multi_logger as an API
@source_availables : ALMemory
@pep8 : Complains with all rules

"""

# Import the multi logger module
import multi_logger

# Import time is just for example purpose
import time

IP_ROBOT = "10.0.255.21"  # Optionnal (default 127.0.0.1)
CONFIG_FILE_PATH = "multi_logger.cfg"  # Optionnal (default multi_logger.cfg)
SAMPLE_PERIOD = 0.5  # Optionnal (default 1 second)
OUTPUT = "Console"  # Optionnal (default Console)
DECIMAL = 2  # Optionnal (default 2)


def main():
    """Call this function to try the multi_looger as an API."""

    # Init the logger
    #
    logger = multi_logger.Logger(IP_ROBOT, CONFIG_FILE_PATH, SAMPLE_PERIOD,
                                 OUTPUT, DECIMAL)

    # Start log
    #
    logger.log()

    #
    # DO YOUR STUFFS #
    # BLAH BLAH BLAH #
    #
    time.sleep(10)

    # Stop log
    #
    logger.stop()

if __name__ == '__main__':
    main()
