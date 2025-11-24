import typer
from dotenv import set_key
from pathlib import Path


env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
print(env_path)

app = typer.Typer()


@app.command()
def set_timeout_expanding():
    set_key(str(env_path), "DS_DEBUG_TIMEOUT", "3600")
    set_key(str(env_path), "DS_FULL_TIMEOUT", "10800")

if __name__ == "__main__":
    app()
