from loguru import logger
import os
import time

class Logger:
    log_dir = None

    def __init__(self):
        current_time = time.strftime('%Y-%m-%d-%H-%M-%S')
        self.log_dir = 'output/' + current_time
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        log_file = os.path.join(self.log_dir, f'{current_time}.log')
        logger.add(log_file, format='{time} {level} {message}', level='INFO')

    @staticmethod
    def info(message, customDepth=1):
        logger.opt(depth=customDepth).info(message)

    @staticmethod
    def error(message):
        logger.opt(depth=1).error(message)