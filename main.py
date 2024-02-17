import telebot
from telebot import types
import pymysql
from config import TOKEN, HOST, USER, PASSWORD, PORT, DATABASE

bot = telebot.TeleBot(TOKEN)

username = None
username_call = None

connection = pymysql.connect(
    host=HOST,
    user=USER,
    password=PASSWORD,
    port=PORT,
    database=DATABASE
)
cursor = connection.cursor()

@bot.message_handler(commands=['start'])
def start(message: str) -> None:
    cht = message.chat.id

    # cursor.execute("DROP TABLE stats")
    cursor.execute("CREATE TABLE IF NOT EXISTS stats (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50), q INT DEFAULT 0)")

    bot.send_message(cht, f'Дурак? Який смоук бот?')

@bot.message_handler(commands=['perekur'])
def perekur(message: str) -> None:
    cursor.execute("SELECT * FROM stats WHERE username = %s", (message.from_user.username))
    data = cursor.fetchall()
    if len(data) == 0:
        cursor.execute("INSERT INTO stats (username) VALUES (%s)", (message.from_user.username))
        connection.commit()

    global username_call

    cht = message.chat.id

    text = message.text

    if text == '/perekur':
        bot.send_message(cht, 'Схоже, ти забув вказати свого братка чи залу засідань 😞')
        print('1')
    else:
        try:
            cursor.execute("SELECT q FROM stats WHERE username = %s", (message.from_user.username))
            q_data = cursor.fetchone()
            q = int(q_data[0]) + 1

            cursor.execute("UPDATE stats SET q = %s WHERE username = %s", (q, message.from_user.username))
            connection.commit()
        except Exception as ex:
            bot.send_message(cht, ex)

        text = text.split(' ')
        username_call = text[1].replace('@', '')

        markup = types.InlineKeyboardMarkup(row_width=2)
        no = types.InlineKeyboardButton('Нііі 🤨', callback_data='no')
        yes = types.InlineKeyboardButton('Го 😺', callback_data='yes')
        markup.add(no, yes)

        try:
            bot.send_message(cht, f'Курязі <b>@{message.from_user.username}</b> дуже самотньо. Він терміново викликає колєгу по цеху, <b>{text[1]}</b>, або хоча б когось на перекур до зали засідань на <b>{text[2]}</b> поверсі', reply_markup=markup, parse_mode='HTML')
        except Exception as ex:
            bot.send_message(cht, 'Схоже, ти забув вказати свого братка чи залу засідань 😞')
            print(f'{ex}')

@bot.message_handler(commands=['stats'])
def stats(message: str) -> None:
    cht = message.chat.id

    cursor.execute("SELECT username, q FROM stats")
    all_users = cursor.fetchall()

    medals = ['🥇', '🥈', '🥉']

    # Створюємо відсортований список all_users за другим елементом (рахунком)
    sorted_users = sorted(all_users, key=lambda x: x[1], reverse=True)

    stats_list = ''
    for k, (user, score) in enumerate(sorted_users[:3], 1):
        stats_list += f'{medals[k-1]} @{user} - {score}\n'

    for k, (user, score) in enumerate(sorted_users[3:], 4):
        stats_list += f'{k}. @{user} - {score}\n'



    bot.send_message(cht, f'<b><i>Статистика куряг чату за кількістю запропонованих перекурів:</i></b>\n\n{stats_list}', parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: True)
def callback(call: str) -> None:
    global username

    cht = call.message.chat.id

    if call.data == 'yes':
        username = call.from_user.username
        print(username)
        bot.send_message(cht, f'Вельмишановний <b>@{username_call}</b>, я, @{username}, залишаю усі свої "важливі" справи та прямую до тебе!', parse_mode='HTML')
    elif call.data == 'no':
        bot.send_message(cht, f'-')

bot.polling()