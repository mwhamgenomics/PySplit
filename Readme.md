# PySplit
PySplit is a [LiveSplit](https://github.com/LiveSplit/LiveSplit)-style speedrun timer, run via the command line.

## Usage
To run from source:

    python bin/run.py <speedrun_name> --splits <level_1> <level_2> ...

If you have a config entry for `speedrun_name`, then `--splits` is not needed.
Optional arguments:
- `--nocolour` - do not use colours in stdout
- `--practice` - use SimpleTimer, which does not load or save times

## Configuration
Configurations for level names can be supplied in `~/.pysplit.yaml`. To add level names for a run, for example:

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
be changed at any time - just make sure the list of levels is still the same length:

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

## About saving split data
By default, PySplit uses a splits file in `~/.pysplit.sqlite`. A PySplit splits file is a SQLite database with the
following schema:

    CREATE TABLE runs (id text UNIQUE, name text, start_time text, total_time numeric);
    CREATE TABLE splits (id text UNIQUE, run_id text REFERENCES runs(id), idx numeric, start_time text, end_time text);

PySplit uses the `sqlite3` Python library to push and pull data from this file. It can also be interacted with directly
using the `sqlite3` C library:

    sqlite> SELECT id, start_time FROM runs WHERE name="Halo 1 Legendary";