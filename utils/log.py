import logging
from logging.handlers import RotatingFileHandler


def gen_logger(log_name, file_name):
    logger = logging.getLogger(log_name)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_handler = RotatingFileHandler(file_name)
    log_handler.setLevel(logging.ERROR)
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
    return logger