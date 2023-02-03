"""Command-line interface."""
import fire

from .czds import CZDS


def main():
    """Main entry point for the command line interface of CZDS."""
    fire.Fire(CZDS)


if __name__ == "__main__":
    main()
