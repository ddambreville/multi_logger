Name      : multi_logger.py
Version   : 1.0
Date      : 2014/01/13
Author    : Emmanuel NALEPA
Contact   : enalepa[at]aldebaran-robotics.com
Copyright : Aldebaran Robotics 2014
Requires  : - naoqi python SDK  (Available on Version Gate) for logging from ALMemory
            - PicoHRDL.dll and picolog_adc24_manager.py for logging from Picolog ADC24
              (Available with git clone git@git.aldebaran.lan:test-nao/picolog_adc24_python_driver.git)
Summmary  : This module permits log data from ALMemory and/or Picolog ADC24

**************
HOW IT WORKS ?
**************

1) Configure the file describing what you want to log.
__________________________________________________________

A example is provided in "multi_logger.cfg"

To log from ALMemory :

Write [ALMemory], and after :

For each line :
- First "word" is the variable name to be written in the log file
	(Example : HeadPitchCurrent)
- Second "word" is the ALMemory key
	(Example : Device/SubDeviceList/HeadPitch/ElectricCurrent/Sensor/Value)

First and second "word" has to be separated by ":".

To log from PicoLog ADC24:
Write [ADC24], and after :

- First "word" is the variable name to be written in the log file
  (Example : BatCurrent)
- Second "word" is the number of the channel you want to log. It has to be
  between 1 and 16
- Third "word" is the voltage range. It has to be HRDL_[XX]_MV,
  where [XX] must be 39, 78, 156, 313, 625, 1250 or 2500. (Example HRDL_39_MV)
- "Word" number 4 is the "end" of the channel. It has to be "single-ended" or
  "differential". If "differential", the voltage of channel "i" will be
  compared to the voltage of channel "i+1".

If the first letter is "#", the line is interpreted as commentary.
Blank lines are allowed in the configuration file.

2) Launch the logger.
_____________________

Minimum command : python alMemoryLogger.py

If you run the script on the robot, [IP_ROBOT] could be 127.0.0.1 or
localhost.

python alMemoryLogger.py -h : Show help

python alMemoryLogger.py -v : Show version

python alMemoryLogger.py -p [PERIOD] -c [CONFIGFILE] -o [OUTPUT] -d [DECIMAL]
                         -i [ROBOTIP]

Note : On linux, you can replace python alMemoryLogger.py
	   by ./alMemoryLogger.py.

- Where [PERIOD] (optional) is the sampling period, in second.
  If not specified, the default sampling period is 1 second.

- Where [CONFIGFILE] (optional) is the path to the configuration file.
  If not specified, the default configuration file is "alMemoryLogger.cfg".

- Where [OUTPUT] (optional) is the path to the output file.
  If not specified, the default output is the console.

- Where [DECIMAL] (optional) is the number of decimal of the Time variable.
  If not specified, the default decimal number is 2.

- Where [IPROBOT] (optional) is the IP adress of the robot.
  If not specified, the default IP adress is 127.0.0.1 (localhost)

*******************************************************************************

If you detected any bug or if you need a special feature, please contact the
author.

Prices :
- Bug fix     : 1 beer  + 1 chocolate bar
- New feature : 2 beers + 2 chocolate bars