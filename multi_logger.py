#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2014/01/06
Last modification 2014/05/05

@author: Emmanuel NALEPA
@contact: enalepa[at]aldebaran-robotics.com
@copyright: Aldebaran Robotics 2014

@requires:  - naoqi python SDK  (Available on Version Gate)
              for logging from ALMemory

            - usbtc08.dll and picolog_tc08_manager.py for logging from
              Picolog TC08
              (Available with git clone
              git@git.aldebaran.lan:test-nao/picolog_tc08_python_driver.git)

            - PicoHRDL.dll and picolog_adc24_manager.py for logging from
              Picolog ADC24
              (Available with git clone
              git@git.aldebaran.lan:test-nao/picolog_adc24_python_driver.git)

            - cpu_interrupt_manager.py for logging CPU usage and interrupts
              (Available with git clone
               git@git.aldebaran.lan:test-nao/cpu_interrupt.git)

@platform : - Windows, Linux (PC or robot), OS X
            - If use of TC08 or/and ADC24, only Windows

@summary: This module permits to log datas from several sources
@source availables : ALMemory, Picolog TC08 and Picolog ADC24, CPU usage and
                     interrupts

@known issues : - For TC08, in the configuration file, you have to put channels
                  in order (1, 2 .. 8)
                - For ADC24, in the configuration file, you have to put
                  channels in order (1, 2, ...., 16).
                - You cannot choose the order of probes in the log file

@pep8 : Complains without rules R0902, R0912, R0913, R0914, R0915 and W0212
"""

import sys
import os
import time
import argparse
import ConfigParser
import threading
import subprocess
from Queue import Queue


DEFAULT_CONFIG_FILE = "multi_logger.cfg"
DEFAULT_PLOT_CONFIG_FILE = "easy_plot.cfg"
DEFAULT_PERIOD = 1
DEFAULT_OUTPUT = "Console"
DEFAULT_DECIMAL = 2
DEFAULT_IP = "127.0.0.1"
DEFAULT_RT_PLOT = False
DEFAULT_CLASS_GETTER = False
DEFAULT_QUEUE_SIZE = 5

LOGGERS_CONFIG_FILE = "probs_config.cfg"


class Logger(object):

    """
        Logger class
        This class permits to log datas from several sources
    """

    def __init__(
        self,
        robot_ip,
        config_file_path=DEFAULT_CONFIG_FILE,
        sample_period=DEFAULT_PERIOD,
        output=DEFAULT_OUTPUT,
        decimal=DEFAULT_DECIMAL,
        rt_plot=DEFAULT_RT_PLOT,
        class_getter=DEFAULT_CLASS_GETTER,
        queue_size=DEFAULT_QUEUE_SIZE):
        """
            Initialize the logger.
            - robot_ip : IP adress of the robot
              (Examples : "bn10.local" or "127.0.0.1")
            - config_file_path (optional) : Path of the configuration file
            - sample_period (optional) : Sample period
            - output (optional) : Output where results will be written
            - decimal (optional) : Number of decimal for the Time variable
        """

        self.robot_ip = robot_ip
        self.config_file_path = config_file_path
        self.sample_period = sample_period
        self.output = output
        self.decimal = decimal
        self.class_getter = class_getter
        self.config_file_dic = self._read_config_file(self.config_file_path)
        self.loggers_config_file_dic = self._read_config_file(
            LOGGERS_CONFIG_FILE)
        self.has_to_log = True
        self.max_queue_size = queue_size
        self.queue = Queue(maxsize=self.max_queue_size)
        self.rt_plot = rt_plot
        if self.rt_plot is True:
            try:
                import easy_plot_connection
                self.plot_server = easy_plot_connection.Server(local_plot=True)
            except ImportError:
                message = "Impossible to import easy_plot_connection library"
                raise ImportError(message)

        if output != "Console":
            try:
                self.log_file = open(output, "w")
            except IOError:
                print "ERROR : File", output, "cannot be oppened."
                sys.exit()

        # Initialise CPU Load logger if need to do it
        if "CPULoad" in self.config_file_dic.keys():
            from cpu_interrupt_manager import CpuLoad
            self.cpu_load = CpuLoad()

        # Initialise Interrupts if need to do it
        if "Interrupts" in self.config_file_dic.keys():
            from cpu_interrupt_manager import Interrupts
            self.interrupts = Interrupts()

        # Initialize ALMemory if need to do it
        if "ALMemory" in self.config_file_dic.keys():
            from naoqi import ALProxy
            self.mem = ALProxy("ALMemory", robot_ip, 9559)

        # Initialize TC08 if need to do it
        if "TC08" in self.config_file_dic.keys():
            import picolog_tc08_manager

            if "TC08" not in self.loggers_config_file_dic.keys():
                print "multi_logger.py ERROR : You want to use TC08 " + \
                    "logger but there is no section for it in probs_config.cfg"
                sys.exit()

            dic_tc08 = self.loggers_config_file_dic["TC08"]

            if "NoiseRejection" not in dic_tc08.keys():
                print "multi_logger.py ERROR : Key \"NoiseRejection\" has " + \
                    " to be in the \"TC08\" section of \"probs_config.cfg\"."
                sys.exit()

            noise_rejection_tc08 = dic_tc08["NoiseRejection"][0]

            # Opening module
            sys.stdout.write("TC08 : Opening module ... ")
            sys.stdout.flush()
            self.tc08 = picolog_tc08_manager.ModuleTc08()
            sys.stdout.write("OK\n")

            # Setting noise rejection
            sys.stdout.write("TC08 : Setting noise rejection module ... ")
            sys.stdout.flush()
            self.tc08.setMains(noise_rejection_tc08)
            sys.stdout.write("OK\n")

            # Enabling channels
            sys.stdout.write("TC08 : Setting channels ... ")
            sys.stdout.flush()
            for channel_config in self.config_file_dic["TC08"].values():
                (channel, thermo_couple_type) = channel_config

                self.tc08.setChannel(int(channel), thermo_couple_type)

            sys.stdout.write("OK\n")

            # Getting minimum sampling interval
            sys.stdout.write("TC08 : Gettint minimum sampling interval ... ")
            sys.stdout.flush()
            minimum_sampling_interval = self.tc08.getMinimumIntervalMs()
            sys.stdout.write("OK\n")

            # Start logging on TC08
            sys.stdout.write("TC08 : Run ... ")
            sys.stdout.flush()
            self.tc08.run(minimum_sampling_interval)
            sys.stdout.write("OK\n")

        # Initialize ADC24 if need to do it
        if "ADC24" in self.config_file_dic.keys():
            import picolog_adc24_manager

            if "ADC24" not in self.loggers_config_file_dic.keys():
                print "multi_logger.py ERROR : You want to use ADC24 " + \
                    "logger but there is no section for it in probs_config.cfg"
                sys.exit()

            dic_adc24 = self.loggers_config_file_dic["ADC24"]

            if "NoiseRejection" not in dic_adc24.keys():
                print "multi_logger.py ERROR : Key \"NoiseRejection\" has " + \
                    " to be in the \"ADC24\" section of \"probs_config.cfg\"."
                sys.exit()

            if "ConversionTime" not in dic_adc24.keys():
                print "multi_logger.py ERROR : Key \"ConversionTime\" has " + \
                    " to be in the \"ADC24\" section of \"probs_config.cfg\"."
                sys.exit()

            noise_rejection_adc24 = dic_adc24["NoiseRejection"][0]
            conversion_time = dic_adc24["ConversionTime"][0]

            # Opening module
            sys.stdout.write("ADC24 : Opening module ... ")
            sys.stdout.flush()
            self.adc24 = picolog_adc24_manager.ModuleAdc24()
            sys.stdout.write("OK\n")

            # Setting noise rejection
            sys.stdout.write("ADC24 : Setting noise rejection module ... ")
            sys.stdout.flush()
            self.adc24.setMains(noise_rejection_adc24)
            sys.stdout.write("OK\n")

            # Enabling channels
            sys.stdout.write("ADC24 : Setting channels ... ")
            sys.stdout.flush()
            for channel_config in self.config_file_dic["ADC24"].values():
                (channel, voltage_range, end) = channel_config

                self.adc24.enableAnalogInChannel(int(channel), voltage_range,
                                                 end)
            sys.stdout.write("OK\n")

            # Setting intervals (in SetInterval, periods are set in
            # milli-seconds)
            sys.stdout.write("ADC24 : Setting intervals ... ")
            sys.stdout.flush()
            self.adc24.setInterval(int(sample_period * 1000), conversion_time)

            sys.stdout.write("OK\n")

            # Start logging on ADC24 (1 sample for each channel at a time,
            # windowed mode)
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

        self.headers = ["Time"]
        for probe in self.config_file_dic.values():
            for key in probe.keys():
                self.headers.append(key)

        self.rt_headers = list(self.headers)
        self.rt_headers.remove("Time")

        to_write = ", ".join(self.headers).replace(" ", "")

        if output == "Console":
            if rt_plot == False:
                print to_write
        else:
            print "Logging ..."
            self.log_file.write(to_write + "\n")
            self.log_file.flush()

        self.t_zero = time.time()

    @classmethod
    def _list_config_file_sections(cls, config_file_paths):
        """List all the sections of the probs_config file <config_file_paths>"""
        probs_config = ConfigParser.ConfigParser()
        probs_config.optionxform = str
        probs_config.read(config_file_paths)

        return probs_config.sections()

    @classmethod
    def _read_config_file_section(cls, config_file_path, section):
        """
            Use ConfigParser for reading a configuration file.
            Returns an dictionnary with keys/values of the section.
        """

        probs_config = ConfigParser.ConfigParser()
        probs_config.optionxform = str
        probs_config.read(config_file_path)

        if probs_config.has_section(section):
            config_section = probs_config._sections[section]
            config_section.pop("__name__")

            for key, value in config_section.items():
                config_section[key] = value.split()

            return config_section

        else:
            return {}

    def _read_config_file(self, config_file_path):
        """ Return the dictionnary corresponding to the configuration file."""
        dic = {}
        for section in self._list_config_file_sections(config_file_path):
            dic[section] = self._read_config_file_section(
                config_file_path, section)

        return dic

    def log1Line(self, rt_plot=True):
        """Write 1 log line output in file or console."""

        elapsed_time = time.time() - self.t_zero
        elapsed_time_round = round(elapsed_time, self.decimal)

        values = [elapsed_time_round]

        for probe, dic_to_log in self.config_file_dic.items():
            if probe == "CPULoad":
                cpu_load_keys = ["".join(cpuLoadValue)
                                 for cpuLoadValue in dic_to_log.values()]

                values += self.cpu_load.calcLoad(cpu_load_keys)

            if probe == "Interrupts":
                interrupts_keys = ["".join(interruptsValue)
                                   for interruptsValue in dic_to_log.values()]

                values += self.interrupts.calcInterrupts(interrupts_keys)

            if probe == "ALMemory":
                almemory_keys = ["".join(memoryValue)
                                 for memoryValue in dic_to_log.values()]
                values += self.mem.getListData(almemory_keys)

            if probe == "TC08":
                tc08_values_dic = self.tc08.getValues()
                values += [value for value in tc08_values_dic.values()]

            if probe == "ADC24":
                adc24_values_dic = self.adc24.getValues()
                values += [value[0] for value in adc24_values_dic.values()]

        to_write = str(values).strip('[]').replace(" ", "")

        if self.rt_plot is True or self.class_getter is True:
            values.pop(0)  #remove time value

        if self.rt_plot is True:
            self.plot_server.add_list_point(elapsed_time,
                                            zip(self.rt_headers, values))

        if self.class_getter is True:
            dict_to_add = dict(zip(self.rt_headers, values))
            if not self.queue.full():
                self.queue.put(dict_to_add)
            else:
                self.queue.get()
                self.queue.put(dict_to_add)

        if self.output == "Console":
            if rt_plot == False:
                print to_write
        else:
            self.log_file.write(to_write + "\n")
            self.log_file.flush()

    # def log(self):
    #     """
    #         Log in file or console.
    #         Use a threding timer calling itself. If you have a better idea
    #         to have a periodically not drifting sampling, I am interrested
    #         in !
    #     """
    #     def myTimer(period):
    #         """Define the timer which let to log periodically."""
    #         threading.Timer(period, myTimer, [period]).start()
    #         self.log1Line()

    #     myTimer(self.sample_period)

    def log(self, rt_plot=True):
        """Log in file or console."""

        # This function uses a sleep.
        # I tried to use a threding timer calling itself(only way I know on
        # Python to do a periodically timer). It works fine, but with this way
        # we can't catch a Keyboard interrupt and stop properly picologgers ...
        # For the timer implementation, just see "log" above ...

        def loop(period):
            """Log 1 line and sleep during a period"""
            while self.has_to_log is True:
                time.sleep(period)
                self.log1Line(rt_plot)

        log_thread = threading.Thread(target=loop, args=(self.sample_period,))
        log_thread.daemon = True
        log_thread.start()

    def stop(self):
        """Stop logging."""
        self.has_to_log = False

        # Stop using queue. Avoid to run into trouble in threading
        self.queue.task_done()

        # This dirty sleep is necessary to allow time to the thread to exit
        # before the main program
        time.sleep(1)


    def get_data(self):
        """
        Return last logged line as a dictionnary.
        """
        if not self.queue.empty():
            return self.queue.get()
        else:
            while self.queue.empty():
                time.sleep(0.05)
            return self.queue.get()


def main():
    """Read the configuration file and start logging."""
    parser = argparse.ArgumentParser(description="Log datas from ALMemory")

    parser.add_argument("-i", "--IP", dest="robot_ip", default=DEFAULT_IP,
                        help="Robot IP or name (default: 127.0.0.1)")

    parser.add_argument("-c", "--configFile", dest="configFile",
                        default=DEFAULT_CONFIG_FILE,
                        help="configuration log file\
                        (default: multi_logger.cfg)")

    parser.add_argument("-r", "--rtConfigFile", dest="rtConfigFile",
                        default=DEFAULT_PLOT_CONFIG_FILE,
                        help="real time plot configuration file\
                        (default: easy_plot.cfg")

    parser.add_argument("-p", "--period", dest="period", type=float,
                        default=DEFAULT_PERIOD,
                        help="sampling period in seconds (default: 1 sec)")

    parser.add_argument("-o", "--output", dest="output",
                        default=DEFAULT_OUTPUT,
                        help="output file or console (default: Console)")

    parser.add_argument("-d", "--decimal", dest="decimal", type=int,
                        default=DEFAULT_DECIMAL,
                        help="number of decimals for time (default: 2)")

    parser.add_argument("-v", "--version", action="version",
                        version="%(prog)s 3.0")

    parser.add_argument("--plot", dest="plot", const=True, action="store_const",
                        default=DEFAULT_RT_PLOT,
                        help="--plot allow use of real time plot")


    args = parser.parse_args()

    # Check if Real Time configuration file exists
    if not os.path.exists (args.rtConfigFile):
        print "ERROR : File " + args.rtConfigFile + " doesn't exist."
        print "This file is the easy_plot configuration file, useful for"
        print "real time plot."

        sys.exit()

    # Logger initialisation
    logger = Logger(args.robot_ip, args.configFile,
                    args.period, args.output, args.decimal, args.plot,
                    DEFAULT_CLASS_GETTER, DEFAULT_QUEUE_SIZE)

    # easy_plot subprocess creation
    if args.plot is True:
        popen_list = ['easy_plot']
        popen_list.extend(['-c', str(args.rtConfigFile)])
        popen_list.extend(['-i', DEFAULT_IP])
        popen_list.extend(['-r', str(args.period)])

        # launch easy_plot process
        subprocess.Popen(popen_list)

    # Log
    logger.log(args.plot)

    # Continue if the user hit "Enter"
    # Do nothing specially in case of KeyboardInterrupt (Ctrl-C)
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass

    logger.stop()


if __name__ == '__main__':
    main()
