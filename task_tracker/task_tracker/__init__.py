import uvicorn

from .app import create_app
from .config import config


def main():
    app = create_app()
    host, port = config.host, config.port
    uvicorn.run(app, host=host or '0.0.0.0', port=int(port), access_log=True)
