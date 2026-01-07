import secrets

token = secrets.token_hex(64)

with open(".env", "w") as fp:
    fp.write(f"FLASK_SECRET={token}\n" f"VIDEO_SOURCE=1")
