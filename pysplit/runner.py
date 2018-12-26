import os
import sys
import subprocess
from time import sleep
from signal import SIGINT
from pysplit import client, server
from pysplit.config import cfg


def main():
    cfg.configure()
    action = cfg['positional']

    if action == 'server':
        server.main()

    elif cfg['internal_server']:
        server_proc = subprocess.Popen(
            [sys.executable, __file__, 'server'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        sleep(0.1)
        client.main()
        os.kill(server_proc.pid, SIGINT)
        server_proc.wait()

    else:
        client.main()


if __name__ == '__main__':
    main()
