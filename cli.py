"""
Interactive CLI for the Schwab trading app.
"""

from __future__ import annotations

import sys
from tabulate import tabulate
from trader import Trader


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
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return str(value)


def _confirm(prompt: str) -> bool:
    return input(f"{prompt} [y/N]: ").strip().lower() == "y"


# ──────────────────────────────────────────────────────────────
# Display functions
# ──────────────────────────────────────────────────────────────

def show_accounts(trader: Trader) -> None:
    print("\nFetching accounts...")
    accounts = trader.get_accounts()
    rows = []
    for acct in accounts:
        inner = acct.get("securitiesAccount", {})
        balances = inner.get("currentBalances", {})
        rows.append([
            inner.get("accountNumber", "N/A"),
            inner.get("type", "N/A"),
            _fmt_dollars(balances.get("liquidationValue")),
            _fmt_dollars(balances.get("cashBalance")),
            _fmt_dollars(balances.get("buyingPower")),
        ])
    print(tabulate(rows, headers=["Account", "Type", "Total Value", "Cash", "Buying Power"], tablefmt="rounded_outline"))


def show_positions(trader: Trader) -> None:
    print("\nFetching positions...")
    positions = trader.get_positions()
    if not positions:
        print("No open positions.")
        return
    rows = []
    for pos in positions:
        inst = pos.get("instrument", {})
        rows.append([
            inst.get("symbol", "N/A"),
            inst.get("description", ""),
            pos.get("longQuantity", 0),
            _fmt_dollars(pos.get("averagePrice")),
            _fmt_dollars(pos.get("marketValue")),
            _fmt_dollars(pos.get("currentDayProfitLoss")),
            _fmt_pct(pos.get("currentDayProfitLossPercentage")),
        ])
    print(tabulate(rows,
                   headers=["Symbol", "Description", "Qty", "Avg Cost", "Mkt Value", "Day P/L", "Day P/L %"],
                   tablefmt="rounded_outline"))


def show_quote(trader: Trader) -> None:
    symbol = input("Enter symbol: ").strip().upper()
    if not symbol:
        return
    print(f"\nFetching quote for {symbol}...")
    quote = trader.get_quote(symbol)
    if not quote:
        print(f"No data found for {symbol}.")
        return
    ref = quote.get("reference", {})
    q = quote.get("quote", {})
    rows = [
        ["Symbol", symbol],
        ["Description", ref.get("description", "N/A")],
        ["Last Price", _fmt_dollars(q.get("lastPrice"))],
        ["Bid", _fmt_dollars(q.get("bidPrice"))],
        ["Ask", _fmt_dollars(q.get("askPrice"))],
        ["Open", _fmt_dollars(q.get("openPrice"))],
        ["Close (prev)", _fmt_dollars(q.get("closePrice"))],
        ["Day High", _fmt_dollars(q.get("highPrice"))],
        ["Day Low", _fmt_dollars(q.get("lowPrice"))],
        ["Volume", q.get("totalVolume", "N/A")],
        ["52w High", _fmt_dollars(ref.get("week52High"))],
        ["52w Low", _fmt_dollars(ref.get("week52Low"))],
    ]
    print(tabulate(rows, tablefmt="rounded_outline"))


def show_orders(trader: Trader) -> None:
    print("\nFetching recent orders...")
    orders = trader.get_all_orders()
    if not orders:
        print("No recent orders.")
        return
    rows = []
    for o in orders:
        legs = o.get("orderLegCollection", [{}])
        leg = legs[0] if legs else {}
        inst = leg.get("instrument", {})
        rows.append([
            o.get("orderId", "N/A"),
            inst.get("symbol", "N/A"),
            leg.get("instruction", "N/A"),
            o.get("quantity", "N/A"),
            o.get("price", "MARKET"),
            o.get("orderType", "N/A"),
            o.get("status", "N/A"),
            o.get("enteredTime", "N/A")[:19].replace("T", " ") if o.get("enteredTime") else "N/A",
        ])
    print(tabulate(rows,
                   headers=["Order ID", "Symbol", "Side", "Qty", "Price", "Type", "Status", "Entered"],
                   tablefmt="rounded_outline"))


# ──────────────────────────────────────────────────────────────
# Order entry
# ──────────────────────────────────────────────────────────────

def place_order_flow(trader: Trader) -> None:
    print("\n--- Place Order ---")
    print("1. Buy (Market)")
    print("2. Buy (Limit)")
    print("3. Sell (Market)")
    print("4. Sell (Limit)")
    print("0. Back")
    choice = input("Choice: ").strip()

    if choice == "0":
        return

    symbol = input("Symbol: ").strip().upper()
    if not symbol:
        return

    try:
        qty = int(input("Quantity (shares): ").strip())
        if qty <= 0:
            raise ValueError
    except ValueError:
        print("Invalid quantity.")
        return

    result = None

    if choice in ("1", "3"):
        # Market order — fetch live quote for confirmation
        quote = trader.get_quote(symbol)
        last = quote.get("quote", {}).get("lastPrice", "unknown")
        side = "BUY" if choice == "1" else "SELL"
        print(f"\n  {side} {qty} shares of {symbol} at MARKET (last: {_fmt_dollars(last)})")
        if not _confirm("Confirm order?"):
            print("Order cancelled.")
            return
        if choice == "1":
            result = trader.buy_market(symbol, qty)
        else:
            result = trader.sell_market(symbol, qty)

    elif choice in ("2", "4"):
        try:
            price = float(input("Limit price: $").strip())
            if price <= 0:
                raise ValueError
        except ValueError:
            print("Invalid price.")
            return
        side = "BUY" if choice == "2" else "SELL"
        print(f"\n  {side} {qty} shares of {symbol} @ LIMIT ${price:.2f}")
        if not _confirm("Confirm order?"):
            print("Order cancelled.")
            return
        if choice == "2":
            result = trader.buy_limit(symbol, qty, price)
        else:
            result = trader.sell_limit(symbol, qty, price)
    else:
        print("Invalid choice.")
        return

    if result:
        print(f"\nOrder submitted successfully!")
        print(f"  Order ID : {result.get('order_id', 'N/A')}")
        print(f"  Symbol   : {result['symbol']}")
        print(f"  Side     : {result['side']}")
        print(f"  Type     : {result['type']}")
        print(f"  Quantity : {result['quantity']}")
        if "price" in result:
            print(f"  Price    : ${result['price']:.2f}")


def cancel_order_flow(trader: Trader) -> None:
    print("\n--- Cancel Order ---")
    order_id = input("Enter Order ID to cancel: ").strip()
    if not order_id:
        return
    if not _confirm(f"Cancel order {order_id}?"):
        print("Cancelled.")
        return
    success = trader.cancel_order(order_id)
    if success:
        print(f"Order {order_id} cancelled successfully.")
    else:
        print(f"Failed to cancel order {order_id}. It may already be filled or cancelled.")


# ──────────────────────────────────────────────────────────────
# Main menu
# ──────────────────────────────────────────────────────────────

MENU = """
╔══════════════════════════════════╗
║     Schwab Trading App           ║
╠══════════════════════════════════╣
║  1. View Accounts & Balances     ║
║  2. View Positions               ║
║  3. Get Quote                    ║
║  4. View Orders                  ║
║  5. Place Order                  ║
║  6. Cancel Order                 ║
║  0. Exit                         ║
╚══════════════════════════════════╝
"""


def run(trader: Trader) -> None:
    while True:
        print(MENU)
        choice = input("Select option: ").strip()

        try:
            if choice == "1":
                show_accounts(trader)
            elif choice == "2":
                show_positions(trader)
            elif choice == "3":
                show_quote(trader)
            elif choice == "4":
                show_orders(trader)
            elif choice == "5":
                place_order_flow(trader)
            elif choice == "6":
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
