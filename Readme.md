# PySplit
PySplit is a [LiveSplit](https://github.com/LiveSplit/LiveSplit)-style speedrun timer, run via the command line.

## Usage
PySplit consists of a client and server. To run the server from source:

    python bin/server.py

The client can then be run separately:

    python bin/client.py <speedrun_name> ...

This enters a curses app with the following controls:
- space: start/split
- backspace: stop/reset
- q: quit


## Configuration
Configurations for level names can be supplied in `~/.pysplit.yaml`. To add level names for a run category, for example
Halo 1 Legendary, add the category name with a list of names under `split_names`:

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

Because PySplit saves the index of each split (i.e, whether it is level 1, 2, etc.) and not the name, level names can
be changed at any time - just make sure the list of levels is still the same length. You can also automatically assign a
run category's level names to another category by specifying a category name instead of a list of level names.

    split_names:
        'Halo 1 Legendary':
          - Reset here a lot
          - (Don't) save marines
          - TnR
          - Choke door launch here
          - AotCR
          - 343GS
          - SO MUCH FLOOD
          - Lose run here
          - Keyes bump
          - Warthog run

        'Halo 1 Easy': 'Halo 1 Legendary'


## About saving split data
By default, PySplit uses a splits file in `~/.pysplit.sqlite`. A PySplit splits file is a SQLite database with the
following schema:

    CREATE TABLE runs (id numeric UNIQUE, name text, runner text, start_time datetime, end_time datetime, total_time numeric);
    CREATE TABLE splits (id numeric UNIQUE, run_id numeric REFERENCES runs(id), idx numeric, start_time datetime, end_time datetime, total_time numeric);

PySplit uses the sqlite3 Python library to push and pull data from this file. It can also be interacted with directly
in a sqlite3 shell:

    sqlite> SELECT id, runner, start_time, total_time FROM runs WHERE name="Halo 1 Legendary" ORDER BY total_time ASC;


## Signal handling
The server handles SIGINT to stop cleanly. The client handles SIGUSR1 to call `self.advance`. This means that PySplit
can run in the background under the control of an external process.


## Roadmap
- More command line tools for looking at past runs
    - best run, avg run, best possible run
- Screenshot for intro to docs
- Web interface
- Configurable controls
