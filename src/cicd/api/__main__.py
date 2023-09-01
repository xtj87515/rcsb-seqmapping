import os
from pathlib import Path

from hypercorn import Config
from hypercorn.run import run


def _get_config() -> str:
    e = os.environ.get("HYPERCORN_CONFIG")
    if e and Path(e).exists():
        return e
    elif e:
        msg = f"Config file {e} not found"
        raise FileNotFoundError(msg)
    p = Path("hypercorn_config.toml")
    if p.exists():
        return p.name
    msg = f"Default config file {p} not found and $HYPERCORN_CONFIG not set (cwd={Path.cwd()}"
    raise FileNotFoundError(msg)


config = Config.from_object(_get_config())
run(config)
