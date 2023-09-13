# quiz_logic.py

from flask import current_app as app
import logging
import random
import tempfile
import asyncio
from gtts import gTTS
import pygame
from quiz_data import глаголы
import logging
from logging.handlers import RotatingFileHandler
from app import app

# Настройка логгирования
if app.config['DEBUG']:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Создаем обработчик для записи в файл quiz_logic.log
    handler = RotatingFileHandler('quiz_logic.log', maxBytes=1024*1024, backupCount=10)
    handler.setLevel(logging.INFO)

    # Формат лога
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Добавляем обработчик к логгеру
    logger.addHandler(handler)

# Функция для генерации вопроса и вариантов ответов
async def генерировать_вопрос_и_озвучивать(глаголы_для_теста, current_question):
    try:
        текущий_глагол = глаголы_для_теста[current_question]
        правильный_перевод = глаголы[текущий_глагол]
        
        варианты_ответов = [правильный_перевод]
        
        while len(варианты_ответов) < 4:
            случайный_вариант = random.choice(list(глаголы.values()))
            if случайный_вариант not in варианты_ответов:
                варианты_ответов.append(случайный_вариант)
        
        random.shuffle(варианты_ответов)

        # Отладочное сообщение для проверки
        if app.config['DEBUG']:
            print("Текущий глагол:", текущий_глагол)
            print("Варианты ответов:", варианты_ответов)

        return текущий_глагол, варианты_ответов

    except Exception as e:
        # В случае ошибки, записываем ошибку в лог и возвращаем None и пустой список
        if app.config['DEBUG']:
            logger.error(f"Произошла ошибка при генерации вопроса: {e}")
        return None, []


# Функция для озвучивания слова и прослушивания (асинхронная версия)
async def озвучить_и_прослушать_асинхронно(слово):
    try:
        tts = gTTS(text=слово, lang='en')

        # Создаем временный файл для аудио
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_audio.close()

        # Сохраняем аудио во временный файл
        tts.save(temp_audio.name)

        # Инициализируем Pygame и воспроизводим аудио асинхронно
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(temp_audio.name)
        pygame.mixer.music.play()

        # Ожидаем окончания воспроизведения асинхронно
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)

        # Закрываем временный файл после использования
        temp_audio.close()

    except Exception as e:
        # В случае ошибки, записываем ошибку в лог
        if app.config['DEBUG']:
            logger.error(f"Произошла ошибка при озвучивании слова: {e}")
