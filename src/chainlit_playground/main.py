import os

from chainlit.utils import mount_chainlit
from fastapi import FastAPI

from chainlit_playground import hello

APPS: dict[str, str] = {
    "hello": hello.app.__file__,
}


def app() -> FastAPI:
    target = APPS.get(os.getenv("TARGET", "hello"))
    if target is None:
        msg = f"Unknown target: {target}. Available targets: {', '.join(APPS.keys())}"
        raise ValueError(msg)

    app = FastAPI()
    mount_chainlit(app, target, path="/")
    return app
