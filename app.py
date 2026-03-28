#!/usr/bin/env python3
"""
Schwab Trading App
------------------
Authenticate with your Charles Schwab account and trade stocks
interactively from the command line.

Setup:
  1. Register at https://developer.schwab.com and create an app.
  2. Copy .env.example to .env and fill in your credentials.
  3. pip install -r requirements.txt
  4. python app.py
"""

from auth import get_client
from trader import Trader
import cli


def main() -> None:
    print("Schwab Trading App — connecting...")
    client = get_client()
    trader = Trader(client)
    cli.run(trader)


if __name__ == "__main__":
    main()
