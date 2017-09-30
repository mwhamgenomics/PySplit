import sys
import signal
from os.path import dirname, abspath


if __name__ == '__main__':
    sys.path.append(dirname(dirname(abspath(__file__))))
    from pysplit import server
    server.cfg.configure()

    signal.signal(signal.SIGINT, server.stop)
    signal.signal(signal.SIGUSR1, server.advance)
    server.main(server.cfg['record_db'])
