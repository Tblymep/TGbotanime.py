import requests
import random
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = TeleBot('7274640935:AAFcDczqp-gMA_7AYCAXNa1fqsN9kLjUHWs')

# Функция для получения случайного факта об аниме
def get_random_fact():
    facts = [
        "Слово 'аниме' происходит от английского слова 'animation'.",
        "Первое аниме было создано в 1907 году.",
        "Аниме стало популярным во всем мире, начиная с 1980-х годов.",
        "Многие известные аниме-сериалы основаны на манге.",
        "Аниме имеет множество жанров, включая экшен, романтику, фэнтези и др."
    ]
    return random.choice(facts)

# Функция для получения информации о манге
def get_manga_info(title):
    url = f'https://api.jikan.moe/v4/manga?q={title}&limit=1'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка статуса запроса
        manga_data = response.json().get('data', [])
        if manga_data:
            manga = manga_data[0]
            image_url = manga['images']['jpg']['large_image_url']
            title = manga['title']
            synopsis = manga['synopsis']
            return image_url, title, synopsis
    except requests.RequestException as e:
        print(f"Error fetching manga information: {e}")
    return None, None, None

# Функция для получения случайной манги
def get_random_manga():
    url = 'https://api.jikan.moe/v4/random/manga'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка статуса запроса
        manga = response.json()['data']
        title = manga['title']
        synopsis = manga['synopsis']
        image_url = manga['images']['jpg']['large_image_url']
        return image_url, title, synopsis
    except requests.RequestException as e:
        print(f"Error fetching random manga: {e}")
    return None, None, None

# Функция для получения случайного аниме
def get_anime_image():
    url = 'https://api.jikan.moe/v4/random/anime'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка статуса запроса
        data = response.json()
        image_url = data['data']['images']['jpg']['large_image_url']
        title = data['data']['title']
        synopsis = data['data']['synopsis']
        genres = ', '.join(genre['name'] for genre in data['data']['genres'])
        return image_url, title, synopsis, genres
    except requests.RequestException as e:
        print(f"Error fetching anime image: {e}")
        return None, None, None, None

# Функция для создания клавиатуры
def create_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Получить случайное аниме", callback_data='anime_button'))
    markup.add(InlineKeyboardButton("Поиск манги по названию", callback_data='manga_button'))
    markup.add(InlineKeyboardButton("Случайная манга", callback_data='random_manga_button'))
    markup.add(InlineKeyboardButton("Случайный факт об аниме", callback_data='fact_button'))
    markup.add(InlineKeyboardButton("Информация о боте", callback_data='info_button'))
    markup.add(InlineKeyboardButton("Перезапуск", callback_data='restart_button'))
    return markup

# Команда /start
@bot.message_handler(commands=['start'])
def start_command(message):
    markup = create_keyboard()
    bot.send_message(message.chat.id, "Привет! Я аниме бот. Выберите действие:", reply_markup=markup)

# Обработка нажатия на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'anime_button':
        bot.send_message(call.message.chat.id, "Получаем случайное аниме...")
        image_url, title, synopsis, genres = get_anime_image()
        if image_url:
            response_text = f"<b>{title}</b>\n\n<em>{synopsis}</em>\n\nЖанры: {genres}"
            bot.send_photo(call.message.chat.id, image_url, caption=response_text, parse_mode='HTML')
        else:
            bot.send_message(call.message.chat.id, "Не удалось получить аниме-картинку.")

    elif call.data == 'fact_button':
        fact = get_random_fact()
        bot.send_message(call.message.chat.id, f"Вот случайный факт об аниме: {fact}")

    elif call.data == 'manga_button':
        bot.send_message(call.message.chat.id, "Введите название манги для поиска:")
        bot.register_next_step_handler(call.message, process_manga_info)

    elif call.data == 'random_manga_button':
        bot.send_message(call.message.chat.id, "Получаем случайную мангу...")
        image_url, title, synopsis = get_random_manga()
        if image_url:
            response_text = f"<b>{title}</b>\n\n<em>{synopsis}</em>"
            bot.send_photo(call.message.chat.id, image_url, caption=response_text, parse_mode='HTML')
        else:
            bot.send_message(call.message.chat.id, "Не удалось получить случайную мангу.")

    elif call.data == 'info_button':
        bot.send_message(call.message.chat.id, "Этот бот может показывать случайное аниме, факты об аниме и информацию о манге.")

    elif call.data == 'restart_button':
        start_command(call.message)

    bot.answer_callback_query(call.id, "Вы выбрали действие!")
    # После обработки события, снова отправляем кнопки
    markup = create_keyboard()
    bot.send_message(call.message.chat.id, "Выберите действие:", reply_markup=markup)

# Функция обработки ввода названия манги
def process_manga_info(message):
    title = message.text.strip()
    image_url, title, synopsis = get_manga_info(title)
    if image_url:
        response_text = f"<b>{title}</b>\n\n<em>{synopsis}</em>"
        bot.send_photo(message.chat.id, image_url, caption=response_text, parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, "Не удалось найти информацию о манге с таким названием.")

if __name__ == "__main__":
    bot.polling(none_stop=True)
