"""Handles Schwab OAuth2 authentication via schwab-py."""

import os
import schwab
from config import Config


def get_client() -> schwab.client.Client:
    """
    Return an authenticated Schwab client.

    On first run, opens a browser for OAuth login and saves the token.
    On subsequent runs, loads the saved token and refreshes it if needed.
    """
    Config.validate()

    token_path = Config.TOKEN_PATH

    if os.path.exists(token_path):
        try:
            client = schwab.auth.client_from_token_file(
                token_path,
                Config.APP_KEY,
                Config.APP_SECRET,
            )
            return client
        except Exception:
            # Token invalid or expired — fall through to re-authenticate
            print("Saved token is invalid or expired. Re-authenticating...")
            os.remove(token_path)

    # First-time / re-authentication: browser-based OAuth flow
    print("\nOpening browser for Schwab login...")
    print(f"After logging in, you will be redirected to: {Config.CALLBACK_URL}")
    print("Paste the full redirect URL here when prompted.\n")

    client = schwab.auth.client_from_login_flow(
        Config.APP_KEY,
        Config.APP_SECRET,
        Config.CALLBACK_URL,
        token_path,
    )
    print("Authentication successful. Token saved.\n")
    return client
