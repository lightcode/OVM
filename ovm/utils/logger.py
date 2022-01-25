import logging

__all__ = ["logger"]


BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

COLORS = {
    "WARNING": YELLOW,
    "INFO": WHITE,
    "DEBUG": BLUE,
    "CRITICAL": RED,
    "ERROR": RED,
}


RESET_SEQ = "\033[0m"


def color_string(text, color):
    return "\033[1;3{0}m{1}{2}".format(color, text, RESET_SEQ)


class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color=True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        if self.use_color and record.levelname in COLORS:
            record.levelname = color_string(record.levelname, COLORS[record.levelname])
        return logging.Formatter.format(self, record)


class ColoredLogger(logging.Logger):
    FORMAT = "%(levelname)-18s  %(message)s   (%(filename)s:%(lineno)d)"

    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.DEBUG)

        color_formatter = ColoredFormatter(self.FORMAT)

        console = logging.StreamHandler()
        console.setFormatter(color_formatter)
        self.addHandler(console)


logging.setLoggerClass(ColoredLogger)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
