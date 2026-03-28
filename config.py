import os
from dotenv import load_dotenv

load_dotenv()


class Config:
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
