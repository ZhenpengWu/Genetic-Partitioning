import argparse
import sys

from app import App

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
    This is an implementation of a branch-and-bound based partitioning tool.
    """
    )

    parser.add_argument(
        "-v",
        "--verbose",
        help="enable verbose logging",
        action="store_true",
    )

    parser.add_argument(
        "-g",
        "--no-gui",
        help="""
        disable graphical user interface (GUI), and
        automatically enable if no other arguments specified
        """,
        action="store_true",
    )

    parser.add_argument("-i", "--infile", help="test input file")

    args = parser.parse_args()

    sys.setrecursionlimit(1500)

    App(args)
