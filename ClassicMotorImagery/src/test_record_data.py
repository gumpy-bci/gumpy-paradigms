import unittest
import pylsl
import time
import os
from record_data import RecordData, NoRecordingDataError


def test_record(channel_data=[], time_stamps=[]):
    x = 1.0
    while True:
        time_stamps.append(pylsl.local_clock())
        channel_data.append([x, x + 1.0, x + 2.0, x + 3.0])
        x += 4.0

        time.sleep(0.1)


def test_record_no_data(channel_data=[], time_stamps=[]):
    while True:
        pass


class TestRecordData(unittest.TestCase):
    def setUp(self):
        self.record_data = RecordData(256, 22, record_func=test_record)

    def test_constructor(self):
        record_data = self.record_data

        self.assertEqual(record_data.Fs      , 256               , "wrong frequency")
        self.assertEqual(record_data.age     , 22                , "wrong age")
        self.assertEqual(record_data.gender  , "male"            , "wrong gender")
        self.assertEqual(record_data.add_info, "with no feedback", "wrong add_info")

    def test_as_dict(self):
        self.assertEqual(
            dict(self.record_data),
            {
                "trial"             : [],
                "X"                 : [],
                "time_stamps"       : [],
                "trial_time_stamps" : [],
                "Y"                 : [],
                "Fs"                : 256,
                "age"               : 22,
                "gender"            : "male",
                "add_info"          : "with no feedback"
            },
            "wrong dictionary format"
        )

    def test_recording_session(self):
        record_data = self.record_data

        record_data.start_recording()
        for trial in range(3):
            time.sleep(0.5)
            record_data.add_trial(trial)
            time.sleep(0.5)

        mat_file = record_data.stop_recording_and_dump()

        self.assertEqual(
            record_data.trial,
            [24, 34, 44],
            "wrong trial start indexes"
        )

        self.assertEqual(
            len(record_data.X),
            50,
            "wrong length of recorded data"
        )

        os.remove(mat_file)

    def test_no_recording_data(self):
        record_data = RecordData(256, 22, record_func=test_record_no_data)

        cought_recording_exception = False
        try:
            record_data.start_recording()
        except NoRecordingDataError:
            cought_recording_exception = True

        self.assertTrue(cought_recording_exception)


if __name__ == '__main__':
    unittest.main()
