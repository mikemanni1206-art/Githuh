"""Interactive CLI for the Polymarket trading app."""

from __future__ import annotations

import sys
from tabulate import tabulate
from polymarket_trader import PolymarketTrader


# ──────────────────────────────────────────────────────────────
# Formatting helpers
# ──────────────────────────────────────────────────────────────

def _fmt_dollars(value) -> str:
    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)


def _fmt_pct(value) -> str:
    try:
        return f"{float(value):.1%}"
    except (TypeError, ValueError):
        return str(value)


def _confirm(prompt: str) -> bool:
    return input(f"{prompt} [y/N]: ").strip().lower() == "y"


def _trunc(text: str, width: int = 60) -> str:
    text = str(text)
    return text if len(text) <= width else text[: width - 3] + "..."


# ──────────────────────────────────────────────────────────────
# Display functions
# ──────────────────────────────────────────────────────────────

def show_balance(trader: PolymarketTrader) -> None:
    print("\nFetching balance...")
    balance = trader.get_balance()
    rows = [
        ["USDC Balance", _fmt_dollars(balance.get("balance", 0))],
    ]
    print(tabulate(rows, tablefmt="rounded_outline"))


def show_markets(trader: PolymarketTrader) -> None:
    print("\nFetching markets...")
    data = trader.get_markets()
    markets = data if isinstance(data, list) else data.get("data", [])
    if not markets:
        print("No active markets found.")
        return
    rows = []
    for m in markets[:20]:
        rows.append([
            _trunc(m.get("condition_id", "N/A"), 20),
            _trunc(m.get("question", "N/A"), 55),
            m.get("active", ""),
            m.get("closed", ""),
        ])
    print(tabulate(rows,
                   headers=["Condition ID", "Question", "Active", "Closed"],
                   tablefmt="rounded_outline"))
    if len(markets) > 20:
        print(f"  (showing first 20 of {len(markets)})")


def show_market_detail(trader: PolymarketTrader) -> None:
    condition_id = input("Enter condition ID: ").strip()
    if not condition_id:
        return
    print(f"\nFetching market {condition_id}...")
    market = trader.get_market(condition_id)
    if not market:
        print("Market not found.")
        return
    tokens = market.get("tokens", [])
    rows = [
        ["Question", _trunc(market.get("question", "N/A"), 70)],
        ["Condition ID", market.get("condition_id", "N/A")],
        ["Active", market.get("active", "N/A")],
        ["Closed", market.get("closed", "N/A")],
        ["Min Order Size", market.get("minimum_order_size", "N/A")],
        ["Min Tick Size", market.get("minimum_tick_size", "N/A")],
    ]
    print(tabulate(rows, tablefmt="rounded_outline"))
    if tokens:
        print("\nOutcome tokens:")
        tok_rows = [[t.get("outcome", ""), t.get("token_id", ""), t.get("price", "")] for t in tokens]
        print(tabulate(tok_rows, headers=["Outcome", "Token ID", "Price"], tablefmt="rounded_outline"))


def show_order_book(trader: PolymarketTrader) -> None:
    token_id = input("Enter token ID: ").strip()
    if not token_id:
        return
    print(f"\nFetching order book for {token_id[:20]}...")
    book = trader.get_order_book(token_id)
    if not book:
        print("No order book data found.")
        return
    bids = book.get("bids", [])[:10]
    asks = book.get("asks", [])[:10]
    print("\nTop 10 Bids:")
    if bids:
        print(tabulate([[b.get("price"), b.get("size")] for b in bids],
                       headers=["Price", "Size"], tablefmt="rounded_outline"))
    else:
        print("  No bids.")
    print("\nTop 10 Asks:")
    if asks:
        print(tabulate([[a.get("price"), a.get("size")] for a in asks],
                       headers=["Price", "Size"], tablefmt="rounded_outline"))
    else:
        print("  No asks.")


def show_open_orders(trader: PolymarketTrader) -> None:
    print("\nFetching open orders...")
    orders = trader.get_open_orders()
    if not orders:
        print("No open orders.")
        return
    rows = []
    for o in orders:
        rows.append([
            _trunc(o.get("id", "N/A"), 20),
            _trunc(o.get("asset_id", "N/A"), 20),
            o.get("side", "N/A"),
            o.get("price", "N/A"),
            o.get("original_size", "N/A"),
            o.get("size_matched", "N/A"),
            o.get("status", "N/A"),
        ])
    print(tabulate(rows,
                   headers=["Order ID", "Token ID", "Side", "Price", "Size", "Matched", "Status"],
                   tablefmt="rounded_outline"))


def show_trades(trader: PolymarketTrader) -> None:
    print("\nFetching recent trades...")
    trades = trader.get_trades()
    if not trades:
        print("No recent trades.")
        return
    rows = []
    for t in trades[:20]:
        rows.append([
            _trunc(t.get("id", "N/A"), 16),
            _trunc(t.get("asset_id", "N/A"), 20),
            t.get("side", "N/A"),
            _fmt_dollars(t.get("price")),
            t.get("size", "N/A"),
            t.get("status", "N/A"),
        ])
    print(tabulate(rows,
                   headers=["Trade ID", "Token ID", "Side", "Price", "Size", "Status"],
                   tablefmt="rounded_outline"))


# ──────────────────────────────────────────────────────────────
# Order entry
# ──────────────────────────────────────────────────────────────

def place_order_flow(trader: PolymarketTrader) -> None:
    print("\n--- Place Order ---")
    print("1. Buy limit (GTC)")
    print("2. Sell limit (GTC)")
    print("3. Buy market (FOK, spend USDC)")
    print("0. Back")
    choice = input("Choice: ").strip()

    if choice == "0":
        return

    token_id = input("Token ID: ").strip()
    if not token_id:
        return

    result = None

    if choice in ("1", "2"):
        try:
            price = float(input("Price (0.01 – 0.99): ").strip())
            size = float(input("Size (shares): ").strip())
            if not (0 < price < 1) or size <= 0:
                raise ValueError
        except ValueError:
            print("Invalid price or size.")
            return
        side = "BUY" if choice == "1" else "SELL"
        print(f"\n  {side} {size} shares @ {price:.4f}")
        if not _confirm("Confirm order?"):
            print("Order cancelled.")
            return
        if choice == "1":
            result = trader.buy_limit(token_id, price, size)
        else:
            result = trader.sell_limit(token_id, price, size)

    elif choice == "3":
        try:
            amount = float(input("Amount in USDC to spend: $").strip())
            if amount <= 0:
                raise ValueError
        except ValueError:
            print("Invalid amount.")
            return
        print(f"\n  Market BUY spending {_fmt_dollars(amount)} USDC on token {token_id[:20]}...")
        if not _confirm("Confirm order?"):
            print("Order cancelled.")
            return
        result = trader.buy_market(token_id, amount)

    else:
        print("Invalid choice.")
        return

    if result:
        print(f"\nOrder submitted successfully!")
        print(f"  Order ID : {result.get('orderID', result.get('id', 'N/A'))}")
        status = result.get("status", "N/A")
        if status:
            print(f"  Status   : {status}")


def cancel_order_flow(trader: PolymarketTrader) -> None:
    print("\n--- Cancel Order ---")
    print("1. Cancel by order ID")
    print("2. Cancel all open orders")
    print("0. Back")
    choice = input("Choice: ").strip()
    if choice == "0":
        return
    if choice == "1":
        order_id = input("Order ID: ").strip()
        if not order_id:
            return
        if not _confirm(f"Cancel order {order_id[:20]}?"):
            print("Cancelled.")
            return
        result = trader.cancel_order(order_id)
        print(f"Order cancelled. Response: {result}")
    elif choice == "2":
        if not _confirm("Cancel ALL open orders?"):
            print("Cancelled.")
            return
        result = trader.cancel_all_orders()
        print(f"All orders cancelled. Response: {result}")
    else:
        print("Invalid choice.")


# ──────────────────────────────────────────────────────────────
# Main menu
# ──────────────────────────────────────────────────────────────

MENU = """
╔══════════════════════════════════╗
║     Polymarket Trading App       ║
╠══════════════════════════════════╣
║  1. View Balance                 ║
║  2. Browse Markets               ║
║  3. View Market Detail           ║
║  4. View Order Book              ║
║  5. View Open Orders             ║
║  6. View Recent Trades           ║
║  7. Place Order                  ║
║  8. Cancel Order                 ║
║  0. Exit                         ║
╚══════════════════════════════════╝
"""


def run(trader: PolymarketTrader) -> None:
    while True:
        print(MENU)
        choice = input("Select option: ").strip()

        try:
            if choice == "1":
                show_balance(trader)
            elif choice == "2":
                show_markets(trader)
            elif choice == "3":
                show_market_detail(trader)
            elif choice == "4":
                show_order_book(trader)
            elif choice == "5":
                show_open_orders(trader)
            elif choice == "6":
                show_trades(trader)
            elif choice == "7":
                place_order_flow(trader)
            elif choice == "8":
                cancel_order_flow(trader)
            elif choice == "0":
                print("Goodbye.")
                sys.exit(0)
            else:
                print("Invalid option. Please try again.")
        except KeyboardInterrupt:
            print("\nReturning to menu...")
        except Exception as e:
            print(f"\nError: {e}")
