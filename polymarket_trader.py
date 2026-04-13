"""
Polymarket CLOB trading operations: markets, orderbook, positions, orders.
"""

from __future__ import annotations

from typing import Optional

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.constants import BUY, SELL


class PolymarketTrader:
    def __init__(self, client: ClobClient) -> None:
        self.client = client

    # ------------------------------------------------------------------
    # Markets
    # ------------------------------------------------------------------

    def get_markets(self, next_cursor: str = "") -> dict:
        """Return a page of active markets."""
        return self.client.get_markets(next_cursor=next_cursor)

    def get_market(self, condition_id: str) -> dict:
        """Return details for a single market by condition ID."""
        return self.client.get_market(condition_id)

    def search_markets(self, query: str) -> list[dict]:
        """Return markets whose question contains *query* (case-insensitive)."""
        results: list[dict] = []
        cursor = ""
        while True:
            page = self.client.get_markets(next_cursor=cursor)
            for market in page.get("data", []):
                if query.lower() in market.get("question", "").lower():
                    results.append(market)
            cursor = page.get("next_cursor", "LTE=")
            # "LTE=" is the sentinel value indicating the last page
            if not cursor or cursor == "LTE=":
                break
            # Limit to first 5 pages to avoid very long waits
            if len(results) >= 50:
                break
        return results

    # ------------------------------------------------------------------
    # Orderbook & prices
    # ------------------------------------------------------------------

    def get_orderbook(self, token_id: str) -> dict:
        """Return the current orderbook for an outcome token."""
        return self.client.get_order_book(token_id)

    def get_midpoint(self, token_id: str) -> Optional[float]:
        """Return the midpoint price (0–1) for an outcome token, or None."""
        book = self.get_orderbook(token_id)
        bids = book.get("bids", [])
        asks = book.get("asks", [])
        best_bid = float(bids[0]["price"]) if bids else None
        best_ask = float(asks[0]["price"]) if asks else None
        if best_bid is not None and best_ask is not None:
            return (best_bid + best_ask) / 2
        return best_bid or best_ask

    # ------------------------------------------------------------------
    # Account positions & trades
    # ------------------------------------------------------------------

    def get_positions(self) -> list[dict]:
        """Return open positions for the authenticated wallet."""
        resp = self.client.get_positions()
        if isinstance(resp, list):
            return resp
        return resp.get("data", [])

    def get_trades(self, condition_id: str = "") -> list[dict]:
        """Return recent trades, optionally filtered by market condition ID."""
        kwargs = {}
        if condition_id:
            kwargs["market"] = condition_id
        resp = self.client.get_trades(**kwargs)
        if isinstance(resp, list):
            return resp
        return resp.get("data", [])

    # ------------------------------------------------------------------
    # Open orders
    # ------------------------------------------------------------------

    def get_open_orders(self, condition_id: str = "") -> list[dict]:
        """Return open orders, optionally filtered by market condition ID."""
        kwargs = {}
        if condition_id:
            kwargs["market"] = condition_id
        resp = self.client.get_orders(**kwargs)
        if isinstance(resp, list):
            return resp
        return resp.get("data", [])

    # ------------------------------------------------------------------
    # Order placement & cancellation
    # ------------------------------------------------------------------

    def buy_limit(self, token_id: str, price: float, size: float) -> dict:
        """Place a GTC limit buy order."""
        order = self.client.create_order(
            OrderArgs(
                token_id=token_id,
                price=price,
                size=size,
                side=BUY,
            )
        )
        return self.client.post_order(order, OrderType.GTC)

    def sell_limit(self, token_id: str, price: float, size: float) -> dict:
        """Place a GTC limit sell order."""
        order = self.client.create_order(
            OrderArgs(
                token_id=token_id,
                price=price,
                size=size,
                side=SELL,
            )
        )
        return self.client.post_order(order, OrderType.GTC)

    def cancel_order(self, order_id: str) -> dict:
        """Cancel a single open order by ID."""
        return self.client.cancel(order_id)

    def cancel_all_orders(self) -> dict:
        """Cancel all open orders."""
        return self.client.cancel_all()
