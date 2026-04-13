import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Schwab
    APP_KEY: str = os.getenv("SCHWAB_APP_KEY", "")
    APP_SECRET: str = os.getenv("SCHWAB_APP_SECRET", "")
    CALLBACK_URL: str = os.getenv("SCHWAB_CALLBACK_URL", "https://127.0.0.1")
    TOKEN_PATH: str = os.getenv("SCHWAB_TOKEN_PATH", "token.json")

    @classmethod
    def validate(cls) -> None:
        missing = [k for k, v in {"SCHWAB_APP_KEY": cls.APP_KEY, "SCHWAB_APP_SECRET": cls.APP_SECRET}.items() if not v]
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                "Copy .env.example to .env and fill in your Schwab API credentials.\n"
                "Register at https://developer.schwab.com"
            )


class PolymarketConfig:
    PRIVATE_KEY: str = os.getenv("POLYMARKET_PRIVATE_KEY", "")
    # Derived L2 API credentials (auto-populated on first run; can also be set manually)
    API_KEY: str = os.getenv("POLYMARKET_API_KEY", "")
    API_SECRET: str = os.getenv("POLYMARKET_API_SECRET", "")
    API_PASSPHRASE: str = os.getenv("POLYMARKET_API_PASSPHRASE", "")
    CREDS_PATH: str = os.getenv("POLYMARKET_CREDS_PATH", "polymarket_creds.json")
    HOST: str = os.getenv("POLYMARKET_HOST", "https://clob.polymarket.com")
    CHAIN_ID: int = int(os.getenv("POLYMARKET_CHAIN_ID", "137"))

    @classmethod
    def validate(cls) -> None:
        if not cls.PRIVATE_KEY:
            raise EnvironmentError(
                "Missing required environment variable: POLYMARKET_PRIVATE_KEY\n"
                "Copy .env.example to .env and fill in your Polygon wallet private key.\n"
                "This is the private key of the wallet linked to your Polymarket account."
            )
