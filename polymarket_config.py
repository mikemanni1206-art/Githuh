import os
from dotenv import load_dotenv

load_dotenv()


class PolymarketConfig:
    PRIVATE_KEY: str = os.getenv("POLYMARKET_PRIVATE_KEY", "")
    API_KEY: str = os.getenv("POLYMARKET_API_KEY", "")
    API_SECRET: str = os.getenv("POLYMARKET_API_SECRET", "")
    API_PASSPHRASE: str = os.getenv("POLYMARKET_API_PASSPHRASE", "")
    CHAIN_ID: int = int(os.getenv("POLYMARKET_CHAIN_ID", "137"))
    HOST: str = os.getenv("POLYMARKET_HOST", "https://clob.polymarket.com")

    @classmethod
    def has_api_creds(cls) -> bool:
        return bool(cls.API_KEY and cls.API_SECRET and cls.API_PASSPHRASE)

    @classmethod
    def validate(cls) -> None:
        if not cls.PRIVATE_KEY:
            raise EnvironmentError(
                "Missing required environment variable: POLYMARKET_PRIVATE_KEY\n"
                "Copy .env.example to .env and fill in your Polymarket credentials.\n"
                "Your private key is the Ethereum private key for your Polymarket wallet."
            )
