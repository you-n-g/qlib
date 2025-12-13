import typer
from dotenv import set_key
from pathlib import Path


env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
print(env_path)

app = typer.Typer()


@app.command()
def set_timeout_expanding(debug_hours: float =1.0, full_hours: float = 3.0):
    set_key(str(env_path), "DS_DEBUG_TIMEOUT", f"{int(3600 * debug_hours)}")
    set_key(str(env_path), "DS_FULL_TIMEOUT", f"{int(3600 * full_hours)}")

if __name__ == "__main__":
    app()
