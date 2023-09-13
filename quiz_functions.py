# quiz_functions.py

from quiz_logic import генерировать_вопрос_и_озвучивать, озвучить_и_прослушать_асинхронно
import logging
from logging.handlers import RotatingFileHandler
from app import app

# Настройка логгирования
if app.config['DEBUG']:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Создаем обработчик для записи в файл quiz_functions.log
    handler = RotatingFileHandler('quiz_functions.log', maxBytes=1024*1024, backupCount=10)
    handler.setLevel(logging.INFO)

    # Формат лога
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Добавляем обработчик к логгеру
    logger.addHandler(handler)

# Проверка, если скрипт выполняется напрямую
if __name__ == "__main__":
    # Пример использования функции генерации вопроса
    глагол, варианты = asyncio.run(генерировать_вопрос_и_озвучивать(глаголы))
    print(f"Вопрос: Как переводится глагол '{глагол}'?")
    print("Варианты ответов:", варианты)
