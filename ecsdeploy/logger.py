import logging
import sys

class Logger(logging.getLoggerClass()):
    def __init__(self, **kwargs):

        # Defaults
        default_log_level = logging.INFO
        default_date_format = '%Y-%m-%d %H:%M:%S'
        default_log_format = (
            '%(asctime)s [%(levelname)s] %(name)s: '
            #'[%(filename)s: %(lineno)d:%(funcName)s] '
            '%(message)s'
        )
        log_name = kwargs['name']
        log_level = kwargs.get('log_level', default_log_level)
        log_format = kwargs.get('fmt', default_log_format)
        date_format = kwargs.get('datefmt', default_date_format)

        log_formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

        # Handlers
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(log_formatter)

        # Configure root logger
        logging.basicConfig(
            format=log_format,
            datefmt=date_format,
            level=log_level,
            handlers=[handler])

        super(Logger, self).__init__(name=log_name)
        self.setLevel(log_level)
        self.addHandler(handler)

    def __get__(self):
        return self
