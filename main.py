import argparse
import sys

from app import App

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
    This is an implementation of a Genetic and Kernighan-Lin based partitioning tool.
    """
    )

    parser.add_argument(
        "-v",
        "--verbose",
        help="enable verbose logging",
        action="store_true",
    )

    parser.add_argument(
        "-q",
        "--quick",
        help="enable quick mode for kl",
        action="store_true",
    )

    args = parser.parse_args()

    sys.setrecursionlimit(1500)

    App(args)
