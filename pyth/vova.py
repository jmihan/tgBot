import telebot
import sqlite3

# Ваш токен от BotFather
TOKEN = 'YOUR_TOKEN'
bot = telebot.TeleBot(TOKEN)

# Подключение к базе данных SQLite
conn = sqlite3.connect('answers.db', check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы для хранения результатов
cursor.execute('''
CREATE TABLE IF NOT EXISTS results (
    user_id INTEGER,
    question_number INTEGER,
    answer TEXT
)
''')
conn.commit()

# Список вопросов и ответов
questions = [
    ("Вопрос 1?", "да", "нет"),
    ("Вопрос 2?", "да", "нет"),
    ("Вопрос 3?", "да", "нет"),
    ("Вопрос 4?", "да", "нет"),
    ("Вопрос 5?", "да", "нет"),
    # Добавьте остальные 15 вопросов аналогично
]

user_data = {}

@bot.message_handler(commands=['start'])
def start_test(message):
    user_id = message.chat.id
    user_data[user_id] = {'current_question': 0, 'answers': []}
    ask_question(message)

def ask_question(message):
    user_id = message.chat.id
    current_question = user_data[user_id]['current_question']
    question, answer_a, answer_b = questions[current_question]
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(answer_a, answer_b)
    bot.send_message(user_id, question, reply_markup=markup)

@bot.message_handler(func=lambda message: message.chat.id in user_data)
def handle_answer(message):
    user_id = message.chat.id
    current_question = user_data[user_id]['current_question']
    answer = message.text

    # Сохранение ответа в базу данных
    cursor.execute('INSERT INTO results (user_id, question_number, answer) VALUES (?, ?, ?)',
                   (user_id, current_question + 1, answer))
    conn.commit()

    user_data[user_id]['answers'].append(answer)
    user_data[user_id]['current_question'] += 1

    if user_data[user_id]['current_question'] < len(questions):
        ask_question(message)
    else:
        bot.send_message(user_id, "Тест завершен. Спасибо за участие! Напишите /stats, чтобы получить статистику по тесту")
        del user_data[user_id]

@bot.message_handler(commands=['stats'])
def send_statistics(message):
    user_id = message.chat.id
    stats_message = "Статистика ответов других пользователей:\n\n"
    for i, question in enumerate(questions):
        cursor.execute('SELECT answer, COUNT(*) FROM results WHERE question_number = ? GROUP BY answer', (i + 1,))
        stats = cursor.fetchall()
        if stats:
            stats_message += f"{i + 1}. {question[0]}\n"
            for answer, count in stats:
                stats_message += f" {answer}: {count} ответов\n"
                stats_message += "\n"
        else:
            stats_message += f"{i + 1}. {question[0]}\n Нет данных\n\n"
    bot.send_message(user_id, stats_message)

bot.polling(none_stop=True)