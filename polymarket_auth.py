"""Handles Polymarket CLOB API authentication and credential management."""

import json
import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds

from config import PolymarketConfig


def _load_cached_creds(path: str) -> ApiCreds | None:
    """Return cached L2 API credentials from disk, or None if unavailable."""
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            data = json.load(f)
        return ApiCreds(
            api_key=data["api_key"],
            api_secret=data["api_secret"],
            api_passphrase=data["api_passphrase"],
        )
    except (KeyError, json.JSONDecodeError):
        return None


def _save_creds(path: str, creds: ApiCreds) -> None:
    """Persist L2 API credentials to disk."""
    with open(path, "w") as f:
        json.dump(
            {
                "api_key": creds.api_key,
                "api_secret": creds.api_secret,
                "api_passphrase": creds.api_passphrase,
            },
            f,
            indent=2,
        )


def get_client() -> ClobClient:
    """
    Return an authenticated Polymarket CLOB client.

    Authentication flow:
      1. If L2 credentials exist (env vars, cached file), use them directly.
      2. Otherwise derive them from the wallet private key (L1 → derive L2),
         cache the result, and return an L2-authenticated client.
    """
    PolymarketConfig.validate()

    private_key = PolymarketConfig.PRIVATE_KEY
    host = PolymarketConfig.HOST
    chain_id = PolymarketConfig.CHAIN_ID
    creds_path = PolymarketConfig.CREDS_PATH

    # 1. Try credentials from environment variables first
    if PolymarketConfig.API_KEY and PolymarketConfig.API_SECRET and PolymarketConfig.API_PASSPHRASE:
        creds = ApiCreds(
            api_key=PolymarketConfig.API_KEY,
            api_secret=PolymarketConfig.API_SECRET,
            api_passphrase=PolymarketConfig.API_PASSPHRASE,
        )
        return ClobClient(host=host, key=private_key, chain_id=chain_id, creds=creds)

    # 2. Try cached credentials file
    creds = _load_cached_creds(creds_path)
    if creds is not None:
        return ClobClient(host=host, key=private_key, chain_id=chain_id, creds=creds)

    # 3. Derive L2 credentials from wallet (L1 auth) and cache them
    print("\n--- Polymarket API Key Derivation ---")
    print("No saved credentials found. Deriving API keys from your wallet...")
    print("(This requires a signed request to Polymarket — no browser needed.)\n")

    l1_client = ClobClient(host=host, key=private_key, chain_id=chain_id)
    creds = l1_client.create_or_derive_api_creds()

    _save_creds(creds_path, creds)
    print(f"API credentials derived and saved to: {creds_path}")
    print("You may also copy these into your .env to skip derivation next time:")
    print(f"  POLYMARKET_API_KEY={creds.api_key}")
    print(f"  POLYMARKET_API_SECRET={creds.api_secret}")
    print(f"  POLYMARKET_API_PASSPHRASE={creds.api_passphrase}\n")

    return ClobClient(host=host, key=private_key, chain_id=chain_id, creds=creds)
