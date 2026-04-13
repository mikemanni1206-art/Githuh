"""
Interactive CLI for Polymarket prediction-market trading.
"""

from __future__ import annotations

import sys
from tabulate import tabulate
from polymarket_trader import PolymarketTrader


# ──────────────────────────────────────────────────────────────
# Formatting helpers
# ──────────────────────────────────────────────────────────────

def _fmt_price(value) -> str:
    try:
        pct = float(value) * 100
        return f"{pct:.1f}¢  ({float(value):.4f})"
    except (TypeError, ValueError):
        return str(value)


def _fmt_dollars(value) -> str:
    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)


def _confirm(prompt: str) -> bool:
    return input(f"{prompt} [y/N]: ").strip().lower() == "y"


# ──────────────────────────────────────────────────────────────
# Display functions
# ──────────────────────────────────────────────────────────────

def show_markets(trader: PolymarketTrader) -> None:
    print("\nFetching active markets (first page)...")
    page = trader.get_markets()
    markets = page.get("data", [])
    if not markets:
        print("No markets found.")
        return
    rows = []
    for m in markets[:20]:
        rows.append([
            m.get("condition_id", "")[:12] + "…",
            m.get("question", "N/A")[:60],
            "Yes" if m.get("active") else "No",
            m.get("end_date_iso", "N/A")[:10],
        ])
    print(tabulate(rows,
                   headers=["Condition ID", "Question", "Active", "End Date"],
                   tablefmt="rounded_outline"))


def search_markets(trader: PolymarketTrader) -> None:
    query = input("Search markets (keyword): ").strip()
    if not query:
        return
    print(f"\nSearching for '{query}'...")
    markets = trader.search_markets(query)
    if not markets:
        print("No matching markets found.")
        return
    rows = []
    for m in markets[:20]:
        rows.append([
            m.get("condition_id", ""),
            m.get("question", "N/A")[:70],
            "Yes" if m.get("active") else "No",
            m.get("end_date_iso", "N/A")[:10],
        ])
    print(tabulate(rows,
                   headers=["Condition ID", "Question", "Active", "End Date"],
                   tablefmt="rounded_outline"))


def show_market_detail(trader: PolymarketTrader) -> None:
    condition_id = input("Enter condition ID: ").strip()
    if not condition_id:
        return
    print(f"\nFetching market {condition_id}...")
    m = trader.get_market(condition_id)
    if not m:
        print("Market not found.")
        return

    print(f"\n  Question : {m.get('question', 'N/A')}")
    print(f"  Active   : {'Yes' if m.get('active') else 'No'}")
    print(f"  End Date : {m.get('end_date_iso', 'N/A')[:10]}")
    print(f"  Cond. ID : {m.get('condition_id', 'N/A')}")

    tokens = m.get("tokens", [])
    if tokens:
        rows = []
        for tok in tokens:
            token_id = tok.get("token_id", "N/A")
            outcome = tok.get("outcome", "N/A")
            mid = trader.get_midpoint(token_id)
            mid_str = _fmt_price(mid) if mid is not None else "N/A"
            rows.append([outcome, token_id[:16] + "…", mid_str])
        print()
        print(tabulate(rows, headers=["Outcome", "Token ID", "Mid Price"], tablefmt="rounded_outline"))


def show_orderbook(trader: PolymarketTrader) -> None:
    token_id = input("Enter token ID: ").strip()
    if not token_id:
        return
    print(f"\nFetching orderbook for {token_id[:20]}…")
    book = trader.get_orderbook(token_id)
    bids = book.get("bids", [])[:10]
    asks = book.get("asks", [])[:10]

    bid_rows = [[_fmt_price(b["price"]), b["size"]] for b in bids]
    ask_rows = [[_fmt_price(a["price"]), a["size"]] for a in asks]

    print("\n  Asks (best first):")
    print(tabulate(ask_rows[::-1], headers=["Price", "Size"], tablefmt="simple"))
    print("\n  Bids (best first):")
    print(tabulate(bid_rows, headers=["Price", "Size"], tablefmt="simple"))


def show_positions(trader: PolymarketTrader) -> None:
    print("\nFetching positions...")
    positions = trader.get_positions()
    if not positions:
        print("No open positions.")
        return
    rows = []
    for p in positions:
        rows.append([
            p.get("market", "N/A")[:14] + "…",
            p.get("outcome", "N/A"),
            p.get("size", "N/A"),
            _fmt_price(p.get("avgPrice", p.get("avg_price", "N/A"))),
            _fmt_dollars(p.get("value", p.get("currentValue", "N/A"))),
        ])
    print(tabulate(rows,
                   headers=["Market", "Outcome", "Size", "Avg Price", "Value"],
                   tablefmt="rounded_outline"))


def show_open_orders(trader: PolymarketTrader) -> None:
    print("\nFetching open orders...")
    orders = trader.get_open_orders()
    if not orders:
        print("No open orders.")
        return
    rows = []
    for o in orders:
        rows.append([
            o.get("id", "N/A")[:14] + "…",
            o.get("market", "N/A")[:14] + "…",
            o.get("outcome", o.get("side", "N/A")),
            o.get("side", "N/A"),
            _fmt_price(o.get("price", "N/A")),
            o.get("original_size", o.get("size", "N/A")),
            o.get("size_matched", "N/A"),
            o.get("status", "N/A"),
        ])
    print(tabulate(rows,
                   headers=["Order ID", "Market", "Outcome", "Side", "Price", "Size", "Filled", "Status"],
                   tablefmt="rounded_outline"))


def show_trades(trader: PolymarketTrader) -> None:
    print("\nFetching recent trades...")
    trades = trader.get_trades()
    if not trades:
        print("No trades found.")
        return
    rows = []
    for t in trades[:20]:
        rows.append([
            t.get("id", "N/A")[:12] + "…",
            t.get("market", "N/A")[:12] + "…",
            t.get("outcome", "N/A"),
            t.get("side", "N/A"),
            _fmt_price(t.get("price", "N/A")),
            t.get("size", "N/A"),
            _fmt_dollars(t.get("fee_rate_bps", "N/A")),
            (t.get("timestamp", t.get("created_at", "N/A")) or "")[:19].replace("T", " "),
        ])
    print(tabulate(rows,
                   headers=["Trade ID", "Market", "Outcome", "Side", "Price", "Size", "Fee bps", "Time"],
                   tablefmt="rounded_outline"))


# ──────────────────────────────────────────────────────────────
# Order entry
# ──────────────────────────────────────────────────────────────

def place_order_flow(trader: PolymarketTrader) -> None:
    print("\n--- Place Limit Order ---")
    print("1. Buy (GTC Limit)")
    print("2. Sell (GTC Limit)")
    print("0. Back")
    choice = input("Choice: ").strip()
    if choice == "0":
        return
    if choice not in ("1", "2"):
        print("Invalid choice.")
        return

    token_id = input("Token ID: ").strip()
    if not token_id:
        return

    try:
        price = float(input("Price (0.00 – 1.00, e.g. 0.65 for 65¢): ").strip())
        if not 0 < price < 1:
            raise ValueError
    except ValueError:
        print("Invalid price. Must be between 0 and 1 (exclusive).")
        return

    try:
        size = float(input("Size (number of shares): ").strip())
        if size <= 0:
            raise ValueError
    except ValueError:
        print("Invalid size.")
        return

    side = "BUY" if choice == "1" else "SELL"
    cost = price * size
    print(f"\n  {side} {size} shares @ {price:.4f} ({price*100:.1f}¢)  — est. cost: {_fmt_dollars(cost)}")
    if not _confirm("Confirm order?"):
        print("Order cancelled.")
        return

    if choice == "1":
        result = trader.buy_limit(token_id, price, size)
    else:
        result = trader.sell_limit(token_id, price, size)

    if result:
        print(f"\nOrder submitted!")
        print(f"  Order ID : {result.get('orderID', result.get('id', 'N/A'))}")
        print(f"  Status   : {result.get('status', 'N/A')}")


def cancel_order_flow(trader: PolymarketTrader) -> None:
    print("\n--- Cancel Order ---")
    print("1. Cancel a single order")
    print("2. Cancel ALL open orders")
    print("0. Back")
    choice = input("Choice: ").strip()
    if choice == "0":
        return
    if choice == "1":
        order_id = input("Order ID to cancel: ").strip()
        if not order_id:
            return
        if not _confirm(f"Cancel order {order_id}?"):
            print("Aborted.")
            return
        result = trader.cancel_order(order_id)
        print(f"Cancellation result: {result}")
    elif choice == "2":
        if not _confirm("Cancel ALL open orders?"):
            print("Aborted.")
            return
        result = trader.cancel_all_orders()
        print(f"Cancellation result: {result}")
    else:
        print("Invalid choice.")


# ──────────────────────────────────────────────────────────────
# Main menu
# ──────────────────────────────────────────────────────────────

MENU = """
╔══════════════════════════════════════╗
║     Polymarket Trading App           ║
╠══════════════════════════════════════╣
║  1. Browse Active Markets            ║
║  2. Search Markets                   ║
║  3. Market Detail & Prices           ║
║  4. View Orderbook                   ║
║  5. View My Positions                ║
║  6. View My Open Orders              ║
║  7. View My Trades                   ║
║  8. Place Order                      ║
║  9. Cancel Order(s)                  ║
║  0. Exit                             ║
╚══════════════════════════════════════╝
"""


def run(trader: PolymarketTrader) -> None:
    while True:
        print(MENU)
        choice = input("Select option: ").strip()

        try:
            if choice == "1":
                show_markets(trader)
            elif choice == "2":
                search_markets(trader)
            elif choice == "3":
                show_market_detail(trader)
            elif choice == "4":
                show_orderbook(trader)
            elif choice == "5":
                show_positions(trader)
            elif choice == "6":
                show_open_orders(trader)
            elif choice == "7":
                show_trades(trader)
            elif choice == "8":
                place_order_flow(trader)
            elif choice == "9":
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
