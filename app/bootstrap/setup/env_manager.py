from pathlib import Path

ENV_PATH = Path(".env")
REQUIRED_ENV_VARS = ["GOOGLE_AI_API_KEY", "EMAIL_ADDRESS", "EMAIL_APP_PASSWORD"]

def check_env(env_vars: dict):
    for req_var in REQUIRED_ENV_VARS:
        if req_var not in env_vars.keys():
            env_vars[req_var] = ""

def read_env():
    # Create .env if it doesn't exist yet
    if not ENV_PATH.exists():
        ENV_PATH.touch()

    # Read whatever's already in the .env into a dict
    with ENV_PATH.open() as f:
        lines = [line.strip() for line in f if "=" in line]
        env_vars = dict(line.split("=", 1) for line in lines)
        check_env(env_vars)
        return env_vars

def write_env(env_vars: dict):
    data = ""
    for key, value in env_vars.items():
        data += f"{key}={value}\n"

    with ENV_PATH.open("w") as f:
        f.write(data)