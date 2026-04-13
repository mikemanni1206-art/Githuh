#!/usr/bin/env python3
"""
Trading App
-----------
Authenticate with your Charles Schwab or Polymarket account and trade
interactively from the command line.

Setup:
  1. Copy .env.example to .env and fill in credentials for the platform(s)
     you want to use.
  2. pip install -r requirements.txt
  3. python app.py

For Schwab:  Register at https://developer.schwab.com and create an app.
For Polymarket: Use the Ethereum private key for your Polymarket wallet.
"""

import sys


PLATFORM_MENU = """
╔══════════════════════════════════╗
║     Select Trading Platform      ║
╠══════════════════════════════════╣
║  1. Charles Schwab               ║
║  2. Polymarket                   ║
║  0. Exit                         ║
╚══════════════════════════════════╝
"""


def main() -> None:
    print(PLATFORM_MENU)
    choice = input("Select platform: ").strip()

    if choice == "1":
        from auth import get_client
        from trader import Trader
        import cli
        print("Schwab Trading App — connecting...")
        client = get_client()
        trader = Trader(client)
        cli.run(trader)

    elif choice == "2":
        from polymarket_auth import get_client as pm_get_client
        from polymarket_trader import PolymarketTrader
        import polymarket_cli
        print("Polymarket Trading App — connecting...")
        client = pm_get_client()
        trader = PolymarketTrader(client)
        polymarket_cli.run(trader)

    elif choice == "0":
        print("Goodbye.")
        sys.exit(0)

    else:
        print("Invalid choice.")
        sys.exit(1)


if __name__ == "__main__":
    main()
