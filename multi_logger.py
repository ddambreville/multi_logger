#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Created on 2014/01/06

@author: Emmanuel NALEPA
@contact: enalepa[at]aldebaran-robotics.com
@copyright: Aldebaran Robotics 2014
@requires: naoqi python SDK (Available on Version Gate)
@platform : Windows, Linux (PC or robot), OS X
@summary: This module permits to log datas from several sources
@source_availables : ALMemory
@pep8 : Complains without rules R0913 and W0212
@version : 1


"""

import sys
import time
from naoqi import ALProxy
import argparse
import ConfigParser
import threading
# from collections import OrderedDict

DEFAULT_CONFIG_FILE = "multi_logger.cfg"
DEFAULT_PERIOD = 1
DEFAULT_OUTPUT = "Console"
DEFAULT_DECIMAL = 2

LOGGERS_CONFIG_FILE = "config.cfg"


class Logger(object):

    """
        Logger class
        This class permits to log datas from several sources
    """

    def __init__(self, robotIP, configFilePath=DEFAULT_CONFIG_FILE,
                 samplePeriod=DEFAULT_PERIOD, output=DEFAULT_OUTPUT,
                 decimal=DEFAULT_DECIMAL):
        """
            Initialize the logger.
            - robotIP : IP adress of the robot
              (Examples : "bn10.local" or "127.0.0.1")
            - configFilePath (optional) : Path of the configuration file
            - samplePeriod (optional) : Sample period
            - output (optional) : Output where results will be written
            - decimal (optional) : Number of decimal for the Time variable
        """

        self.robotIP = robotIP
        self.configFilePath = configFilePath
        self.samplePeriod = samplePeriod
        self.output = output
        self.mem = ALProxy("ALMemory", robotIP, 9559)
        self.decimal = decimal
        self.configFileDic = self._readConfigFile(self.configFilePath)
        self.loggersConfigfileDic = self._readConfigFile(LOGGERS_CONFIG_FILE)

        if output != "Console":
            try:
                self.logFile = open(output, "w")
            except IOError:
                print "ERROR : File", output, "cannot be oppened."
                sys.exit()

        # Initialize ADC24 if need to do it
        if "ADC24" in self.configFileDic.keys():
            import picolog_adc24_manager

            if "ADC24" not in self.loggersConfigfileDic.keys():
                print "multi_logger.py ERROR : You want to use ADC24 " + \
                    "logger but there is no section for it in config.cfg"
                sys.exit()

            dicAdc24 = self.loggersConfigfileDic["ADC24"]

            if "NoiseRejection" not in dicAdc24.keys():
                print "multi_logger.py ERROR : Key \"NoiseRejection\" has " + \
                    " to be in the \"ADC24\" section of \"config.cfg\"."
                sys.exit()

            if "ConversionTime" not in dicAdc24.keys():
                print "multi_logger.py ERROR : Key \"ConversionTime\" has " + \
                    " to be in the \"ADC24\" section of \"config.cfg\"."
                sys.exit()

            noiseRejection = dicAdc24["NoiseRejection"][0]
            conversionTime = dicAdc24["ConversionTime"][0]

            # Opening module
            sys.stdout.write("ADC24 : Opening module ... ")
            sys.stdout.flush()
            self.adc24 = picolog_adc24_manager.ModuleAdc24()
            sys.stdout.write("OK\n")

            # Setting noise rejection
            sys.stdout.write("ADC24 : Setting noise rejection module ... ")
            sys.stdout.flush()
            self.adc24.setMains(noiseRejection)
            sys.stdout.write("OK\n")

            # Enabling channels
            sys.stdout.write("ADC24 : Setting channels ... ")
            sys.stdout.flush()
            for channelConfig in self.configFileDic["ADC24"].values():
                (channel, voltageRange, end) = channelConfig

                self.adc24.enableAnalogInChannel(int(channel), voltageRange,
                                                 end)
            sys.stdout.write("OK\n")

            # Setting intervals (in SetInterval, periods are set in
            # milli-seconds.)
            sys.stdout.write("ADC24 : Setting intervals ... ")
            sys.stdout.flush()
            self.adc24.setInterval(int(samplePeriod * 1000), conversionTime)

            sys.stdout.write("OK\n")

            # Start logging on ADC24 (1 sample for each channel at a time,
            # windowed mode
            sys.stdout.write("ADC24 : Run ... ")
            sys.stdout.flush()
            self.adc24.run(1, "BM_WINDOW")

            sys.stdout.write("OK\n")

            # Waiting ADC24 is ready
            sys.stdout.write("ADC24 : Wait ready ... ")
            sys.stdout.flush()
            while not self.adc24.isReady():
                pass

            sys.stdout.write("OK\n")

        headers = ["Time"]
        for probe in self.configFileDic.values():
            for key in probe.keys():
                headers.append(key)

        toWrite = ", ".join(headers).replace(" ", "")

        if output == "Console":
            print toWrite
        else:
            print "Logging ..."
            self.logFile.write(toWrite + "\n")

        self.t0 = time.time()

    @classmethod
    def _listConfigFileSections(cls, configFilePaths):
        """List all the sections of the config file <configFilePaths>"""
        config = ConfigParser.ConfigParser()
        config.optionxform = str
        config.read(configFilePaths)

        return config.sections()

    @classmethod
    def _readConfigFileSection(cls, configFilePath, section):
        """
            Use ConfigParser for reading a configuration file.
            Returns an dictionnary with keys/values of the section.
        """

        config = ConfigParser.ConfigParser()
        config.optionxform = str
        config.read(configFilePath)

        if config.has_section(section):
            configSection = config._sections[section]
            configSection.pop("__name__")

            for key, value in configSection.items():
                configSection[key] = value.split()

            return configSection

        else:
            return {}

    def _readConfigFile(self, configFilePath):
        """ Return the dictionnary corresponding to the configuration file."""
        dic = {}
        for section in self._listConfigFileSections(configFilePath):
            dic[section] = self._readConfigFileSection(configFilePath, section)

        return dic

    def log1Line(self):
        """Write 1 log line output in file or console."""

        elapsedTime = time.time() - self.t0
        elapsedTimeRound = round(elapsedTime, self.decimal)

        values = [elapsedTimeRound]

        for probe, dicToLog in self.configFileDic.items():
            if probe == "ALMemory":
                alMemoryKeys = ["".join(memoryValue)
                                for memoryValue in dicToLog.values()]
                values += self.mem.getListData(alMemoryKeys)

            if probe == "ADC24":
                adc24ValuesDic = self.adc24.getValues()
                values += [value[0] for value in adc24ValuesDic.values()]

        toWrite = str(values).strip('[]').replace(" ", "")

        if self.output == "Console":
            print toWrite
        else:
            self.logFile.write(toWrite + "\n")

    # def log(self):
    #     """
    #         Log in file or console.
    #         Use a threding timer calling itself. If you have a better idea
    #         to have a periodically not drifting sampling, I am interrested
    #         in !
    #     """
    #     def myTimer(period):
    #         """Define the timer which let to log periodically."""
    #         if self.hasToLog is True:
    #             try:
    #                 threading.Timer(period, myTimer, [period]).start()
    #                 self.log1Line()
    #             except KeyboardInterrupt:
    #                 sys.exit()

    #     myTimer(self.samplePeriod)

    def log(self):
        """
            Log in file or console.
        """

        # This function uses a sleep.
        # I tried to use a threding timer calling itself (only way I know on
        # Python to do a periodically timer). It works fine, but with this way
        # we can't catch a Keyboard interrupt and stop properly picologgers ...
        # For the timer implementation, just see "log" above ...
        while True:
            self.log1Line()
            time.sleep(self.samplePeriod)


def main():
    """Read the configuration file and begin logging."""
    try:
        parser = argparse.ArgumentParser(description="Log datas from ALMemory")

        parser.add_argument("robotIP", help="Robot IP or name")

        parser.add_argument("-c", "--configFile", dest="configFile",
                            default=DEFAULT_CONFIG_FILE,
                            help="configuration log file\
                            (default: multi_logger.cfg)")

        parser.add_argument("-p", "--period", dest="period", type=float,
                            default=DEFAULT_PERIOD,
                            help="sampling period in seconds (default: 1 sec)")

        parser.add_argument("-o", "--output", dest="output",
                            default=DEFAULT_OUTPUT,
                            help="output file or console (default: Console)")

        parser.add_argument("-d", "--decimal", dest="decimal", type=int,
                            default=DEFAULT_DECIMAL,
                            help="number of decimals for time (default: 2)")

        parser.add_argument(
            "-v", "--version", action="version", version="%(prog)s 1.1")

        args = parser.parse_args()

        logger = Logger(
            args.robotIP, args.configFile, args.period, args.output,
            args.decimal)

        logger.log()

    except KeyboardInterrupt:
        sys.exit()

if __name__ == '__main__':
    main()
