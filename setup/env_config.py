from pathlib import Path
from setup.ui.display import display_banner
from setup.ui.input_helpers import confirm_action

# ===== CONSTANTS =====

WIDTH = 64

# ===== .ENV FUNCTIONS =====

ENV_PATH = Path(".env")
REQUIRED_ENV_VARS = {
    "GEMINI_API_KEY": "Enter your Gemini API key",
    "EMAIL_ADDRESS": "Enter sender email address",
    "EMAIL_APP_PASSWORD": "Enter email app password",
}


def ensure_env():
    """Ensure .env file exists and all required variables are configured."""
    if not ENV_PATH.exists():
        ENV_PATH.touch()

    existing_env_vars = {}

    with ENV_PATH.open() as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                existing_env_vars[k] = v

    with ENV_PATH.open("a") as f:
        while True:
            display_banner("NEWSLETTER BOT SETUP")

            new_env_dict = {}
            accounted = True
            
            for key, prompt in REQUIRED_ENV_VARS.items():
                if key not in existing_env_vars:
                    accounted = False
                    value = input(f"{prompt}: ").strip()
                    new_env_dict[key] = value

            if accounted:
                return
            
            display_banner("CONFIRM ENVIRONMENT CONFIGURATION")
            print("The following values will be added:\n")

            for key, value in new_env_dict.items():
                print(f"  {key:<20} - {value}")

            print("\n" + "-" * WIDTH)

            if confirm_action("Proceed with these values?"):
                for key, value in new_env_dict.items():
                    f.write(f"\n{key}={value}")
                return

