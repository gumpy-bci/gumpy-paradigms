import os

if os.name == "nt":
    # DIRTY workaround from stackoverflow
    # when using scipy, a keyboard interrupt will kill python
    # so nothing after catching the keyboard interrupt will
    # be executed

    import imp
    import ctypes
    import thread
    import win32api

    basepath = imp.find_module('numpy')[1]
    ctypes.CDLL(os.path.join(basepath, 'core', 'libmmd.dll'))
    ctypes.CDLL(os.path.join(basepath, 'core', 'libifcoremd.dll'))

    def handler(dwCtrlType, hook_sigint=thread.interrupt_main):
        if dwCtrlType == 0:
            hook_sigint()
            return 1
        return 0

    win32api.SetConsoleCtrlHandler(handler, 1)


import threading           # NOQA
import scipy.io as sio     # NOQA
import pylsl               # NOQA
from utils import time_str # NOQA
import time                # NOQA
import serial


class NoRecordingDataError(Exception):
    def __init__(self):
        self.value = "Received no data while recording"

    def __str__(self):
        return repr(self.value)


def record(ser, channel_data=[], channel_force=[], time_stamps=[]):
    streams = pylsl.resolve_stream('type', 'EEG')
    inlet   = pylsl.stream_inlet(streams[0])

    while True:
        try:
            sample, time_stamp = inlet.pull_sample()
            time_stamp += inlet.time_correction()

            time_stamps.append(time_stamp)
            channel_data.append(sample)

            #output_str = ser.readline()

            """
            if output_str.endswith('\n'):
                output_str = output_str.translate(None, ' \n\t\r')
                try:
                    force_sample = list(map(float, output_str.split(';')))

                    if len(force_sample) != 5:
                        force_sample = [0, 0, 0, 0, 0]
                except ValueError:
                    force_sample = [0, 0, 0, 0, 0]

            else:
                force_sample = [0, 0, 0, 0, 0]
            
            try:
                channel_force.append(float(output_str))
            except ValueError:
                channel_force.append(0)

            """
            try:
                channel_force.append(float(ser.readline()))
            except ValueError:
                channel_force.append(0)

            # first col of one row of the record_data matrix is time_stamp,
            # the following cols are the sampled channels
        except KeyboardInterrupt:
            complete_samples = min(len(time_stamps), len(channel_data), len(channel_force))
            sio.savemat("recording_" + time_str() + ".mat", {
                "time_stamps"  : time_stamps[:complete_samples],
                "channel_data" : channel_data[:complete_samples],
                "channel_force" : channel_force[:complete_samples]
            })
            break


class RecordData():
    def __init__(self, Fs, age, gender="male", with_feedback=False,
                 record_func=record):
        # timepoints when the subject starts imagination
        self.trial = []

        self.X = []

        self.force = []

        self.trial_time_stamps = []
        self.time_stamps       = []

        # 0 negative_feedback
        # 1 positive feedback
        self.feedbacks = []

        # containts the lables of the trials:
        # 1: left
        # 2: right
        # 3: both hands
        self.Y = []

        # sampling frequncy
        self.Fs = Fs

        self.gender   = gender
        self.age      = age
        self.add_info = "with feedback" if with_feedback else "with no feedback"


        port = "COM3"
        baudrate = 2000000
        self.serialPort = serial.Serial(port, baudrate)

        recording_thread = threading.Thread(
            target=record_func,
            args=(self.serialPort, self.X, self.force, self.time_stamps),
        )
        recording_thread.daemon = True
        self.recording_thread   = recording_thread

    def __iter__(self):
        yield 'trial'            , self.trial
        yield 'age'              , self.age
        yield 'X'                , self.X
        yield 'force'            , self.force
        yield 'time_stamps'      , self.time_stamps
        yield 'trial_time_stamps', self.trial_time_stamps
        yield 'Y'                , self.Y
        yield 'Fs'               , self.Fs
        yield 'gender'           , self.gender
        yield 'add_info'         , self.add_info
        yield 'feedbacks'        , self.feedbacks

    def add_trial(self, label):
        self.trial_time_stamps.append(pylsl.local_clock())
        self.Y.append(label)

    def add_feedback(self, feedback):
        self.feedbacks.append(feedback)

    def start_recording(self):
        self.recording_thread.start()
        time.sleep(2)
        if len(self.X) == 0 or len(self.force) == 0:
            raise NoRecordingDataError()

    def set_trial_start_indexes(self):
        i = 0
        for trial_time_stamp in self.trial_time_stamps:
            for j in range(i, len(self.time_stamps)):
                time_stamp = self.time_stamps[j]
                if trial_time_stamp <= time_stamp:
                    self.trial.append(j - 1)
                    i = j
                    break

    def stop_recording_and_dump(self, file_name="session_" + time_str() + ".mat"):
        self.set_trial_start_indexes()
        sio.savemat(file_name, dict(self))

        self.serialPort.close()

        return file_name


if __name__ == '__main__':
    record()
