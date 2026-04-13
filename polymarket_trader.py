"""Polymarket trading operations via the CLOB API."""

from __future__ import annotations

from typing import Optional
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType, MarketOrderArgs


class PolymarketTrader:
    def __init__(self, client: ClobClient) -> None:
        self.client = client

    # ------------------------------------------------------------------
    # Account
    # ------------------------------------------------------------------

    def get_balance(self) -> dict:
        """Return USDC balance information for the connected wallet."""
        return self.client.get_balance()

    # ------------------------------------------------------------------
    # Markets
    # ------------------------------------------------------------------

    def get_markets(self, next_cursor: str = "MA==") -> dict:
        """Return a page of active prediction markets."""
        return self.client.get_markets(next_cursor=next_cursor)

    def get_market(self, condition_id: str) -> dict:
        """Return a single market by its condition ID."""
        return self.client.get_market(condition_id)

    def get_order_book(self, token_id: str) -> dict:
        """Return the order book for a market outcome token."""
        return self.client.get_order_book(token_id)

    # ------------------------------------------------------------------
    # Orders
    # ------------------------------------------------------------------

    def get_open_orders(self) -> list[dict]:
        """Return all open orders for the connected account."""
        resp = self.client.get_orders()
        return resp if isinstance(resp, list) else []

    def get_trades(self) -> list[dict]:
        """Return recent trades for the connected account."""
        resp = self.client.get_trades()
        return resp if isinstance(resp, list) else []

    def buy_limit(self, token_id: str, price: float, size: float) -> dict:
        """Place a limit buy (YES) order."""
        order_args = OrderArgs(
            token_id=token_id,
            price=price,
            size=size,
            side="BUY",
        )
        signed = self.client.create_order(order_args)
        return self.client.post_order(signed, OrderType.GTC)

    def sell_limit(self, token_id: str, price: float, size: float) -> dict:
        """Place a limit sell order."""
        order_args = OrderArgs(
            token_id=token_id,
            price=price,
            size=size,
            side="SELL",
        )
        signed = self.client.create_order(order_args)
        return self.client.post_order(signed, OrderType.GTC)

    def buy_market(self, token_id: str, amount: float) -> dict:
        """Place a market buy order spending `amount` USDC."""
        order_args = MarketOrderArgs(
            token_id=token_id,
            amount=amount,
        )
        signed = self.client.create_market_order(order_args)
        return self.client.post_order(signed, OrderType.FOK)

    def cancel_order(self, order_id: str) -> dict:
        """Cancel an open order by ID."""
        return self.client.cancel(order_id)

    def cancel_all_orders(self) -> dict:
        """Cancel all open orders."""
        return self.client.cancel_all()
