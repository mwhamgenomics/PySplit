from datetime import datetime


runs = (
    {
        'name': 'a_run',
        'runner': 'me',
        'start_time': datetime(2018, 2, 19, 12),
        'splits': (
            {'idx': 0, 'start_time': datetime(2018, 2, 19, 12), 'end_time': datetime(2018, 2, 19, 12, 3, 59), 'total_time': 239},
            {'idx': 1, 'start_time': datetime(2018, 2, 19, 12, 3, 59)}
        )
    },
    {
        'name': 'a_run',
        'runner': 'me',
        'start_time': datetime(2018, 2, 19, 12, 30),
        'end_time': datetime(2018, 2, 19, 12, 41, 1),
        'total_time': 661,
        'splits': (
            {'idx': 0, 'start_time': datetime(2018, 2, 19, 12, 30), 'end_time': datetime(2018, 2, 19, 12, 34, 1), 'total_time': 241},
            {'idx': 1, 'start_time': datetime(2018, 2, 19, 12, 34, 1), 'end_time': datetime(2018, 2, 19, 12, 38, 1), 'total_time': 240},
            {'idx': 2, 'start_time': datetime(2018, 2, 19, 12, 38, 1), 'end_time': datetime(2018, 2, 19, 12, 41, 1), 'total_time': 180},
        )
    },
    {
        'name': 'a_run',
        'runner': 'me',
        'start_time': datetime(2018, 2, 19, 13, 30),
        'end_time': datetime(2018, 2, 19, 13, 40, 46),
        'total_time': 646,
        'splits': (
            {'idx': 0, 'start_time': datetime(2018, 2, 19, 13, 30), 'end_time': datetime(2018, 2, 19, 13, 34), 'total_time': 240},
            {'idx': 1, 'start_time': datetime(2018, 2, 19, 13, 34), 'end_time': datetime(2018, 2, 19, 13, 37, 40), 'total_time': 220},
            {'idx': 2, 'start_time': datetime(2018, 2, 19, 13, 37, 40), 'end_time': datetime(2018, 2, 19, 13, 40, 46), 'total_time': 186},
        )
    },
    {
        'name': 'a_run',
        'runner': 'someone',
        'start_time': datetime(2018, 2, 19, 13, 30),
        'end_time': datetime(2018, 2, 19, 13, 40, 45),
        'total_time': 645,
        'splits': (
            {'idx': 0, 'start_time': datetime(2018, 2, 19, 13, 30), 'end_time': datetime(2018, 2, 19, 13, 34), 'total_time': 240},
            {'idx': 1, 'start_time': datetime(2018, 2, 19, 13, 34), 'end_time': datetime(2018, 2, 19, 13, 37, 39), 'total_time': 219},
            {'idx': 2, 'start_time': datetime(2018, 2, 19, 13, 37, 39), 'end_time': datetime(2018, 2, 19, 13, 40, 45), 'total_time': 186},
        )
    },
    {
        'name': 'a_run',
        'runner': 'me',
        'start_time': datetime(2018, 2, 19, 14, 30),
        'end_time': datetime(2018, 2, 19, 14, 41, 3),
        'total_time': 663,
        'splits': (
            {'idx': 0, 'start_time': datetime(2018, 2, 19, 14, 30), 'end_time': datetime(2018, 2, 19, 14, 34, 3), 'total_time': 243},
            {'idx': 1, 'start_time': datetime(2018, 2, 19, 14, 34, 3), 'end_time': datetime(2018, 2, 19, 14, 38, 13), 'total_time': 250},
            {'idx': 2, 'start_time': datetime(2018, 2, 19, 14, 38, 13), 'end_time': datetime(2018, 2, 19, 14, 41, 3), 'total_time': 170},
        )
    }
)
