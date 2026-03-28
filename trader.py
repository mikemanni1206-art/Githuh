"""
Schwab trading operations: quotes, account info, orders.
"""

from __future__ import annotations

from typing import Optional
import schwab
import schwab.orders.equities as eq
from schwab.orders.common import Duration, Session


class Trader:
    def __init__(self, client: schwab.client.Client) -> None:
        self.client = client
        self._account_hash: Optional[str] = None

    # ------------------------------------------------------------------
    # Account helpers
    # ------------------------------------------------------------------

    def get_account_hash(self) -> str:
        """Return the first linked account's encrypted hash."""
        if self._account_hash:
            return self._account_hash
        resp = self.client.get_account_numbers()
        resp.raise_for_status()
        accounts = resp.json()
        if not accounts:
            raise RuntimeError("No accounts found linked to this Schwab login.")
        self._account_hash = accounts[0]["hashValue"]
        return self._account_hash

    def get_accounts(self) -> list[dict]:
        """Return all linked accounts with balances."""
        resp = self.client.get_accounts(fields=[self.client.Account.Fields.POSITIONS])
        resp.raise_for_status()
        return resp.json()

    def get_positions(self) -> list[dict]:
        """Return current positions for the primary account."""
        accounts = self.get_accounts()
        for acct in accounts:
            inner = acct.get("securitiesAccount", {})
            if inner.get("hashValue") == self.get_account_hash() or True:
                return inner.get("positions", [])
        return []

    def get_orders(self, max_results: int = 20) -> list[dict]:
        """Return recent open/working orders."""
        resp = self.client.get_orders_for_account(
            self.get_account_hash(),
            max_results=max_results,
            status=self.client.Order.Status.WORKING,
        )
        resp.raise_for_status()
        return resp.json()

    def get_all_orders(self, max_results: int = 25) -> list[dict]:
        """Return recent orders regardless of status."""
        resp = self.client.get_orders_for_account(
            self.get_account_hash(),
            max_results=max_results,
        )
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Quotes
    # ------------------------------------------------------------------

    def get_quote(self, symbol: str) -> dict:
        resp = self.client.get_quote(symbol.upper())
        resp.raise_for_status()
        data = resp.json()
        return data.get(symbol.upper(), {})

    def get_quotes(self, symbols: list[str]) -> dict:
        resp = self.client.get_quotes([s.upper() for s in symbols])
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Order placement
    # ------------------------------------------------------------------

    def buy_market(self, symbol: str, quantity: int) -> dict:
        """Place a market buy order."""
        order = (
            eq.equity_buy_market(symbol.upper(), quantity)
            .set_duration(Duration.DAY)
            .set_session(Session.NORMAL)
            .build()
        )
        resp = self.client.place_order(self.get_account_hash(), order)
        resp.raise_for_status()
        order_id = resp.headers.get("Location", "").split("/")[-1]
        return {"status": "submitted", "order_id": order_id, "side": "BUY", "type": "MARKET",
                "symbol": symbol.upper(), "quantity": quantity}

    def sell_market(self, symbol: str, quantity: int) -> dict:
        """Place a market sell order."""
        order = (
            eq.equity_sell_market(symbol.upper(), quantity)
            .set_duration(Duration.DAY)
            .set_session(Session.NORMAL)
            .build()
        )
        resp = self.client.place_order(self.get_account_hash(), order)
        resp.raise_for_status()
        order_id = resp.headers.get("Location", "").split("/")[-1]
        return {"status": "submitted", "order_id": order_id, "side": "SELL", "type": "MARKET",
                "symbol": symbol.upper(), "quantity": quantity}

    def buy_limit(self, symbol: str, quantity: int, price: float) -> dict:
        """Place a limit buy order."""
        order = (
            eq.equity_buy_limit(symbol.upper(), quantity, price)
            .set_duration(Duration.DAY)
            .set_session(Session.NORMAL)
            .build()
        )
        resp = self.client.place_order(self.get_account_hash(), order)
        resp.raise_for_status()
        order_id = resp.headers.get("Location", "").split("/")[-1]
        return {"status": "submitted", "order_id": order_id, "side": "BUY", "type": "LIMIT",
                "symbol": symbol.upper(), "quantity": quantity, "price": price}

    def sell_limit(self, symbol: str, quantity: int, price: float) -> dict:
        """Place a limit sell order."""
        order = (
            eq.equity_sell_limit(symbol.upper(), quantity, price)
            .set_duration(Duration.DAY)
            .set_session(Session.NORMAL)
            .build()
        )
        resp = self.client.place_order(self.get_account_hash(), order)
        resp.raise_for_status()
        order_id = resp.headers.get("Location", "").split("/")[-1]
        return {"status": "submitted", "order_id": order_id, "side": "SELL", "type": "LIMIT",
                "symbol": symbol.upper(), "quantity": quantity, "price": price}

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order. Returns True on success."""
        resp = self.client.cancel_order(order_id, self.get_account_hash())
        return resp.status_code in (200, 204)
