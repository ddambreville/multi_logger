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

IP_ROBOT = "10.0.165.163"  # Optionnal (default 127.0.0.1)
CONFIG_FILE_PATH = "multi_logger.cfg"  # Optionnal (default multi_logger.cfg)
SAMPLE_PERIOD = 0.2  # Optionnal (default 1 second)
OUTPUT = "test.txt"  # Optionnal (default Console)
DECIMAL = 2  # Optionnal (default 2)
RT_PLOT = False  # Optionnal (default False)
CLASS_GETTER = True  # Optionnal (default False)
QUEUE_SIZE = 5  # Optionnal (default 5)

LOOP_TIME = 10  # Seconds


def main():
    """
    Call this function to try the multi_looger as an API.
    While the script is running, move the robot's HeadPitch if you want the
    printed values to change.
    """

    # Init the logger
    #
    logger = multi_logger.Logger(IP_ROBOT, CONFIG_FILE_PATH, SAMPLE_PERIOD,
                                 OUTPUT, DECIMAL, RT_PLOT, CLASS_GETTER,
                                 QUEUE_SIZE)

    # Start log
    logger.log()

    initial_time = time.time()
    while (time.time() - initial_time) < LOOP_TIME:
        datas = logger.get_data()
        print datas["HeadPitchPositionSensorValue"]

    # Stop log
    logger.stop()

if __name__ == '__main__':
    main()
