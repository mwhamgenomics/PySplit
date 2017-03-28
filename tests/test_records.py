from unittest import TestCase
from pysplit import records

records.record_db = ':memory:'
cursor = records.cursor()


data = (
    records.SpeedRun(
        'a_speedrun',
        'a',
        (
            records.Split('a_speedrun', 'a_level',           1, '2017-03-20 12:00:00', '2017-03-20 12:05:30'),
            records.Split('a_speedrun', 'another_level',     2, '2017-03-20 12:05:30', '2017-03-20 12:10:00'),
            records.Split('a_speedrun', 'yet_another_level', 3, '2017-03-20 12:10:00', '2017-03-20 12:15:30')
        )
    ),
    records.SpeedRun(
        'a_speedrun',
        'b',
        (
            records.Split('a_speedrun', 'a_level',           1, '2017-03-21 13:01:45', '2017-03-21 13:06:45'),
            records.Split('a_speedrun', 'another_level',     2, '2017-03-21 13:06:45', '2017-03-21 13:11:10'),
            records.Split('a_speedrun', 'yet_another_level', 3, '2017-03-21 13:11:10', '2017-03-21 13:16:30')
        )
    ),
    records.SpeedRun(
        'a_speedrun',
        'c',
        (
            records.Split('a_speedrun', 'a_level',           1, '2017-03-22 11:40:53', '2017-03-22 11:45:50'),
            records.Split('a_speedrun', 'another_level',     2, '2017-03-22 11:45:50', '2017-03-22 11:51:01'),
            records.Split('a_speedrun', 'yet_another_level', 3, '2017-03-22 11:51:01', '2017-03-22 11:56:14')
        )
    )
)
for run in data:
    run.push()


class TestRecords(TestCase):
    def test_get_run(self):
        s = records.SpeedRun('a_speedrun', 'c')
        self.assertEqual(
            s.splits,
            (
                records.Split('a_speedrun', 'a_level', 1, '2017-03-22 11:40:53', '2017-03-22 11:45:50'),
                records.Split('a_speedrun', 'another_level', 2, '2017-03-22 11:45:50', '2017-03-22 11:51:01'),
                records.Split('a_speedrun', 'yet_another_level', 3, '2017-03-22 11:51:01', '2017-03-22 11:56:14')
            )
        )

    def test_get_best_run(self):
        obs = records.get_best_run('a_speedrun')
        self.assertEqual(obs, data[0])

    def test_get_average_run(self):
        obs = records.get_average_run('a_speedrun')
        exp = records.SpeedRun(
            'a_speedrun',
            'avg_run',
            (
                records.Split('a_speedrun', 'a_level', 1, records.null_time, '2017-03-24 19:05:09'),
                records.Split('a_speedrun', 'another_level', 2, records.null_time, '2017-03-24 19:04:42'),
                records.Split('a_speedrun', 'yet_another_level', 3, records.null_time, '2017-03-24 19:05:21')
            )
        )
        self.assertEqual(obs, exp)
