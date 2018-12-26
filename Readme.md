# PySplit
PySplit is a [LiveSplit](https://github.com/LiveSplit/LiveSplit)-style speedrun timer, run via the command line.

## Usage
PySplit consists of a client and server. To run the server from source:

    python pysplit/runner.py server

The client can then be run separately:

    python pysplit/runner.py <speedrun_name> ...

Alternatively, both can be run at once with the argument `--internal_server`, or by specifying the configuration
`internal_server: True`.

The client is a curses app with the following control defaults:
- space: start/split
- backspace: stop/reset
- q: quit

These controls can be configured. Values should be integer key IDs as used by curses:

    controls:
        advance: 32
        stop_reset: 127
        quit: 113


## Configuration
Configuration is done via the file `~/.pysplit.yaml`. An alternative config file can be specified with the argument
`--config`.

To add level names for a run category, for example 'Halo 1 Legendary', add the category name under `split_names` with a
list of split names:

    split_names:
        'Halo 1 Legendary':
          - Pillar of Autumn
          - Halo
          - Truth and Reconciliation
          - Silent Cartographer
          - Assault on the Control Room
          - 343 Guilty Spark
          - The Library
          - Two Betrayals
          - Keyes
          - The Maw

Because PySplit saves the index of each split (i.e, whether it is split 1, 2, etc.) and not the name, level names can be
changed at any time - just make sure the list of levels is still the same length. You can also automatically assign a
run category's level names to another category by specifying a category name instead of a list of level names.

    split_names:
        'Halo 1 Legendary':
          - Reset here a lot
          - Betraying teammates
          - TnR
          - Choke door launch here
          - AotCR
          - 343GS
          - Brown hallways and Flood
          - Lose run here
          - Keyes bump
          - Warthog run

        'Halo 1 Easy': 'Halo 1 Legendary'

Two other configurations are required:

    runner_name: a_runner
    server_url: 'http://localhost:5000'

The following configurations are optional:

    gold_sound: path/to/gold_sound.mp3
    pb_sound: path/to/pb_sound.mp3
    internal_server: True  # default = False
    record_db: path/to/alternate_pysplit.sqlite
    port: server_port  # default = 5000
    controls:
        advance: 32  # default = 32 (space)
        stop_reset: 127  # default = 127 (backspace)
        quit: 113  # default = 113 (q)

## About saving split data
By default, PySplit uses a splits file in `~/.pysplit.sqlite`. A PySplit splits file is a SQLite database with the
following schema:

    CREATE TABLE runs (id numeric UNIQUE, name text, runner text, start_time datetime, end_time datetime, total_time numeric);
    CREATE TABLE splits (id numeric UNIQUE, run_id numeric REFERENCES runs(id), idx numeric, start_time datetime, end_time datetime, total_time numeric);

PySplit uses the sqlite3 Python library to push and pull data from this file. It can also be interacted with directly
in a sqlite3 shell:

    sqlite> SELECT id, runner, start_time, total_time FROM runs WHERE name="Halo 1 Legendary" ORDER BY total_time ASC;

## Signal handling
The server handles SIGINT to stop cleanly. The client handles SIGUSR1 to call `self.advance`. This means that the
PySplit client can run in the background under the control of an external process.


## Roadmap
- More command line tools for looking at past runs
    - best run, avg run, best possible run
- Web interface?
- Cross-platform sound
