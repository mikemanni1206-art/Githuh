"""Handles Polymarket CLOB API authentication via py-clob-client."""

import os
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from polymarket_config import PolymarketConfig


def get_client() -> ClobClient:
    """
    Return an authenticated Polymarket CLOB client.

    Authentication uses two levels:
      L1 — wallet private key only (used to derive API credentials)
      L2 — API key + secret + passphrase (used for order placement)

    On first run, L1 is used to generate and print API credentials that you
    should save to your .env file.  On subsequent runs, L2 credentials are
    loaded directly from the environment.
    """
    PolymarketConfig.validate()

    if PolymarketConfig.has_api_creds():
        # L2 auth — full trading access
        creds = ApiCreds(
            api_key=PolymarketConfig.API_KEY,
            api_secret=PolymarketConfig.API_SECRET,
            api_passphrase=PolymarketConfig.API_PASSPHRASE,
        )
        client = ClobClient(
            PolymarketConfig.HOST,
            key=PolymarketConfig.PRIVATE_KEY,
            chain_id=PolymarketConfig.CHAIN_ID,
            creds=creds,
        )
        print("Connected to Polymarket (L2 — full API access).")
        return client

    # L1 auth — derive API credentials from wallet
    print("\n--- Polymarket First-Time Setup ---")
    print("No API credentials found. Generating them from your wallet private key...")

    client = ClobClient(
        PolymarketConfig.HOST,
        key=PolymarketConfig.PRIVATE_KEY,
        chain_id=PolymarketConfig.CHAIN_ID,
    )

    creds = client.create_api_key()

    print("\nAPI credentials generated successfully!")
    print("Add these to your .env file to skip this step next time:\n")
    print(f"  POLYMARKET_API_KEY={creds.api_key}")
    print(f"  POLYMARKET_API_SECRET={creds.api_secret}")
    print(f"  POLYMARKET_API_PASSPHRASE={creds.api_passphrase}")

    # Upgrade to L2 client using freshly generated creds
    client = ClobClient(
        PolymarketConfig.HOST,
        key=PolymarketConfig.PRIVATE_KEY,
        chain_id=PolymarketConfig.CHAIN_ID,
        creds=creds,
    )
    print("\nConnected to Polymarket (L2 — full API access).\n")
    return client
