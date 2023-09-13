# app.py

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_wtf import FlaskForm
from wtforms import RadioField
from wtforms.validators import InputRequired
from config import Config
import asyncio
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

# Настройка уровня логирования только в режиме отладки
if app.config['DEBUG']:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Создаем обработчик для записи в файл app.log
    handler = RotatingFileHandler('app.log', maxBytes=1024*1024, backupCount=10)
    handler.setLevel(logging.INFO)

    # Формат лога
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Добавляем обработчик к логгеру
    logger.addHandler(handler)

class QuizForm(FlaskForm):
    answer = RadioField('Answer', validators=[InputRequired()])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/quiz', methods=['GET', 'POST'])
async def quiz():
    from quiz_logic import генерировать_вопрос_и_озвучивать, озвучить_и_прослушать_асинхронно
    from quiz_data import глаголы

    if 'score' not in session:
        session['score'] = 0

    current_question = session.get('current_question', 0)  # Получаем значение current_question из сессии
    form = QuizForm()

    глаголы_для_теста = list(глаголы.keys())
    answer_feedback = None

    try:
        if request.method == 'POST':
            user_answer = form.answer.data
            current_verb = глаголы_для_теста[current_question]
            correct_answer = глаголы.get(current_verb)

            if user_answer == correct_answer:
                session['score'] += 1
                answer_feedback = "Правильно!"
            else:
                answer_feedback = f"Неверно. Правильный ответ: {correct_answer}"

            current_question += 1
            session['current_question'] = current_question

        if current_question >= len(глаголы_для_теста):
            total_questions = len(глаголы_для_теста)
            correct_answers = session['score']
            percent_correct = (correct_answers / total_questions) * 100
            status = get_status(percent_correct)
            
            session['score'] = 0  # Сбросить счет после завершения теста
            session['current_question'] = 0  # Сбросить текущий вопрос

            return render_template('quiz_completed.html', 
                total_questions=total_questions, 
                correct_answers=correct_answers, 
                percent_correct=percent_correct, 
                status=status)
        else:
            # Сбросить текущий вопрос только если тест еще не завершен
            session['current_question'] = current_question
            session['score'] = session.get('score', 0)  # Если score не установлен, установите его в 0

        правильный_ответ, варианты_ответов = await генерировать_вопрос_и_озвучивать(глаголы_для_теста, current_question)  # Передаем current_question
        await озвучить_и_прослушать_асинхронно(правильный_ответ)

        form.answer.choices = [(вариант, вариант) for вариант in варианты_ответов]

        return render_template('quiz.html', question=правильный_ответ, form=form, answer_feedback=answer_feedback)

    except Exception as e:
        if app.config['DEBUG']:
            logger.error(f"Произошла ошибка: {e}")
        return f"Произошла ошибка."

def get_status(percent_correct):
    if percent_correct < 10:
        return "Слабак"
    elif percent_correct >= 10 and percent_correct <= 50:
        return "Ты на правильном пути"
    elif percent_correct > 50 and percent_correct <= 90:
        return "Гений"
    else:
        return "Сверхразум"

@app.route('/restart_quiz', methods=['GET', 'POST'])
def restart_quiz():
    session['score'] = 0
    session['current_question'] = 0
    return redirect(url_for('quiz'))

if __name__ == '__main__':
    app.run(debug=True)