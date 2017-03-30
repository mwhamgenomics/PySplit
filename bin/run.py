import sys
from os.path import dirname, abspath

if __name__ == '__main__':
    sys.path.append(dirname(dirname(abspath(__file__))))
    from pysplit import main
    sys.exit(main())
