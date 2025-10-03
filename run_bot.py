"""Утилита для запуска MerchantBot из командной строки."""

import logging

from MerchantBot import main as run_merchant_bot


def main() -> None:
    """Точка входа для запуска Telegram-бота."""
    try:
        run_merchant_bot()
    except KeyboardInterrupt:
        logging.getLogger(__name__).info("Остановка по запросу пользователя")


if __name__ == "__main__":
    main()
