import sys
import logging


def create_logger():
    """
    Function that creates a logger that outputs to stdout with a logging level of debug.
    :return: Logger that outputs to stdout
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(filename)s: '
                                  '%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


LOGGER = create_logger()
