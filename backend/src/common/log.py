import logging


def setup_logging() -> logging.Logger:
    """
    로깅 설정
    """
    _logger = logging.getLogger("pattern_service")
    _logger.setLevel(logging.INFO)

    # 기존 핸들러 제거(중복 방지)
    _logger.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)
    return _logger
