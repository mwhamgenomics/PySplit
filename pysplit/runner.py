import os
import argparse
from pysplit import client, server
from pysplit.config import cfg


def main():
    """
    Set up argparsers, and call the right main method.

    A separate shared arguments parser runs parse_known_args and passes the specific args to the subparsers. This way,
    shared args can be before or after the subparser args:

        pysplit --config example_pysplit.yaml run a_speedrun
        pysplit run a_speedrun --config example_pysplit.yaml

    Apparently it's a complicated subject:
    https://stackoverflow.com/questions/50543820/argparse-options-for-subparsers-override-main-if-both-share-parent
    https://stackoverflow.com/questions/7498595/python-argparse-add-argument-to-multiple-subparsers
    """

    shared = argparse.ArgumentParser()
    default_config_file = os.path.expanduser('~/.pysplit.yaml')
    shared.add_argument('--config', default=default_config_file, help='Alternate config file to %s' % default_config_file)
    args, argv = shared.parse_known_args()

    a = argparse.ArgumentParser()
    subparsers = a.add_subparsers()

    ls_subparser = subparsers.add_parser('ls', help='List available run categories')
    ls_subparser.set_defaults(func=client.list_runs)

    client_subparser = subparsers.add_parser('run', help='Start a new speedrun timer')
    client_subparser.add_argument('name', help='Run category to start')
    client_subparser.set_defaults(func=client.main)

    server_subparser = subparsers.add_parser('server', help='Start a PySplit server')
    server_subparser.set_defaults(func=server.main)

    args = a.parse_args(argv, namespace=args)
    cfg.load(args.config)
    args.func(args)


if __name__ == '__main__':
    main()
