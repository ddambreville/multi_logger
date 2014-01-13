Name      : al_memory_logger.cfg
Version   : 1.1
Date      : 2014/01/07
Author    : Emmanuel NALEPA
Contact   : enalepa[at]aldebaran-robotics.com
Copyright : Aldebaran Robotics 2013
Requires  : naoqi python SDK  (Available on Version Gate)
Summmary  : This module permits log data from ALMemory

**************
HOW IT WORKS ?
**************

1) Configure the file describing the keys you want to log.
__________________________________________________________

A example is provided in "alMemoryLogger.cfg"

For each line :
- First "word" is the variable name to be written in the log file
	(Example : HeadPitchCurrent)
- Second "word" is the ALMemory key
	(Example : Device/SubDeviceList/HeadPitch/ElectricCurrent/Sensor/Value)

If the first letter is "#", the line is interpreted as commentary.
Blank lines are allowed in the configuration file.

2) Launch the logger.
_____________________

Minimum command : python alMemoryLogger.py [IP_ROBOT]
- Where [IP_ROBOT] is the robot IP.

If you run the script on the robot, [IP_ROBOT] could be 127.0.0.1 or
localhost.

python alMemoryLogger.py -h : Show help

python alMemoryLogger.py -v : Show version

python alMemoryLogger.py -p [PERIOD] -c [CONFIGFILE] -o [OUTPUT]

Note : On linux, you can replace python alMemoryLogger.py
	   by ./alMemoryLogger.py.

- Where [PERIOD] (optional) is the sampling period, in second.
  If not specified, the default sampling period is 1 second.

- Where [CONFIGFILE] (optional) is the path to the configuration file.
  If not specified, the default configuration file is "alMemoryLogger.cfg".

- Where [OUTPOUT] (optional) is the path to the output file.
  If not specified, the default output is the console.

*******************************************************************************

If you detected any bug or if you need a special feature, please contact the
author.

Prices :
- Bug fix     : 1 beer  + 1 chocolate bar
- New feature : 2 beers + 2 chocolate bars