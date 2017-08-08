from pysplit import records

speedruns = (
    records.SpeedRun(
        'a_speedrun',
        'another_runner',
        'a',
        (
            records.Split('a_speedrun', 1, '2017-03-20 12:00:00', '2017-03-20 12:05:30'),
            records.Split('a_speedrun', 2, '2017-03-20 12:05:30', '2017-03-20 12:10:00'),
            records.Split('a_speedrun', 3, '2017-03-20 12:10:00', '2017-03-20 12:15:30')
        )
    ),
    records.SpeedRun(
        'a_speedrun',
        'a_runner',
        'b',
        (
            records.Split('a_speedrun', 1, '2017-03-21 13:01:45', '2017-03-21 13:06:45'),
            records.Split('a_speedrun', 2, '2017-03-21 13:06:45', '2017-03-21 13:11:10'),
            records.Split('a_speedrun', 3, '2017-03-21 13:11:10', '2017-03-21 13:16:30')
        )
    ),
    records.SpeedRun(
        'a_speedrun',
        'a_runner',
        'c',
        (
            records.Split('a_speedrun', 1, '2017-03-22 11:40:53', '2017-03-22 11:45:50'),
            records.Split('a_speedrun', 2, '2017-03-22 11:45:50', '2017-03-22 11:51:01'),
            records.Split('a_speedrun', 3, '2017-03-22 11:51:01', '2017-03-22 11:56:14')
        )
    )
)
