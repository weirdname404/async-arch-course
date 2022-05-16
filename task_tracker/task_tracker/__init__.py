import uvicorn

from . import config
from .app import create_app


def main():
    app = create_app()
    uvicorn.run(app, host=config.HOST, port=int(config.PORT), access_log=True)
