# PySplit
PySplit is a [LiveSplit](https://github.com/LiveSplit/LiveSplit)-style speedrun timer, run via the command line.

## Usage
To start a run on PySplit:

    $ python pysplit/runner.py run <speedrun_name>

PySplit consists of a client and server. By default, the command above will run instances of the client and server
together.

The client is a curses app with the following control defaults:
- space: start/split
- backspace: stop/reset
- q: quit

These controls can be configured. Values should be [ASCII key IDs](https://en.wikipedia.org/wiki/ASCII#Character_groups)
as used by curses.window.getch:

    controls:
      advance: 32  # space
      stop_reset: 127  # backspace/delete
      quit: 113  # q


## Configuration
Configuration is done via the file `~/.pysplit.yaml`. An alternative config file can be specified with the argument
`--config`. There is a section each for the client and server.

### Client config
The first required config is your name:

    client:
      runner_name: Some speedrunner

Then to add level names for a run category, for example 'Halo 1 Legendary', add the category name under `split_names`
with a list of split names:

    client:
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

    client:
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

The following optional configs are available to change the control keys and to play sounds when gold splits and PBs are
achieved:

    gold_sound: path/to/gold_sound.mp3
    pb_sound: path/to/pb_sound.mp3
    controls:
        advance: 32  # default = 32 (space)
        stop_reset: 127  # default = 127 (backspace)
        quit: 113  # default = 113 (q)

### Server config
There are no required server configs, but the following options are available:

    server:
      record_db: path/to/pysplit.sqlite  # default = ~/.pysplit.sqlite
      port: <server_port>  # default = 5000


## Running the client and server separately

The server can be run on its own with the command:

    $ python pysplit/runner.py server

Then to point the client at this, add the option `server_url` to the config file:

    client:
        server_url: http://localhost:5000

Then the client will connect to the running server:

    $ python pysplit/runner.py run <speedrun_name> ...


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
