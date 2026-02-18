import logging
import logging.config
import logging.handlers
from os import path
import pathlib
import json
import atexit


def setup_logging():
    script_dir = pathlib.Path(__file__).parent
    config_file = script_dir / "config.json"

    with open(config_file) as f_in:
        config = json.load(f_in)

    logging.config.dictConfig(config)
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)
