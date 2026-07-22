from pathlib import Path

ENV_PATH = Path(".env")
REQUIRED_ENV_VARS = ["GOOGLE_AI_API_KEY", "EMAIL_ADDRESS", "EMAIL_APP_PASSWORD"]


def read_env():
    ENV_PATH.touch(exist_ok=True)
    env_vars = dict(
        line.strip().split("=", 1)
        for line in ENV_PATH.read_text().splitlines()
        if "=" in line
    )
    env_vars.update({key: "" for key in REQUIRED_ENV_VARS if key not in env_vars})
    return env_vars


def write_env(env_vars: dict):
    lines = [f"{key}={value}" for key, value in env_vars.items()]
    data = "\n".join(lines) + "\n"
    ENV_PATH.write_text(data)