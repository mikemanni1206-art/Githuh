#!/usr/bin/env python3
"""
Trading App — Schwab (stocks) or Polymarket (prediction markets)
----------------------------------------------------------------
Setup:
  1. Copy .env.example to .env and fill in your credentials.
  2. pip install -r requirements.txt
  3. python app.py              # interactive mode picker
     python app.py --schwab     # start directly in Schwab mode
     python app.py --polymarket # start directly in Polymarket mode
"""

import sys


def _pick_mode() -> str:
    """Prompt the user to choose a platform when no flag is given."""
    print("\nSelect a platform:")
    print("  1. Charles Schwab  (stocks & ETFs)")
    print("  2. Polymarket      (prediction markets)")
    choice = input("Choice [1/2]: ").strip()
    if choice == "1":
        return "schwab"
    if choice == "2":
        return "polymarket"
    print("Invalid choice — defaulting to Schwab.")
    return "schwab"


def run_schwab() -> None:
    from auth import get_client
    from trader import Trader
    import cli

    print("Schwab Trading App — connecting...")
    client = get_client()
    trader = Trader(client)
    cli.run(trader)


def run_polymarket() -> None:
    from polymarket_auth import get_client
    from polymarket_trader import PolymarketTrader
    import polymarket_cli

    print("Polymarket Trading App — connecting...")
    client = get_client()
    trader = PolymarketTrader(client)
    polymarket_cli.run(trader)


def main() -> None:
    args = sys.argv[1:]

    if "--schwab" in args:
        mode = "schwab"
    elif "--polymarket" in args:
        mode = "polymarket"
    else:
        mode = _pick_mode()

    if mode == "polymarket":
        run_polymarket()
    else:
        run_schwab()


if __name__ == "__main__":
    main()
