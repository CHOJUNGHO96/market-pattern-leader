import logging


def setup_logging() -> logging.Logger:
    """
    로깅 설정
    """
    _logger = logging.getLogger("crawler_sevice")
    _logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)
    return _logger
