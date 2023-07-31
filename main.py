import telebot, requests, datetime, json
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = ''
url = "https://json.freeastrologyapi.com/match-making/ashtakoot-score"
API_KEY = ''
GEOCODER_URL = 'http://api.openweathermap.org/geo/1.0/direct'
GEOCODER_PARAMS = {
    'appid': API_KEY
}


def get_city_coords(city):
    GEOCODER_PARAMS['q'] = city
    json = requests.get(GEOCODER_URL, GEOCODER_PARAMS).json()
    lat, lon = json[0]['lat'], json[0]['lon']
    return lat, lon


def compatibility():
    try:
        fdfem = requests.get(
            f'http://api.timezonedb.com/v2.1/get-time-zone?key=&format=json&by=position&lat={latfem}&lng={lonfem}').json()
        zonefem = fdfem['gmtOffset'] / 3600

        fdmal = requests.get(
            f'http://api.timezonedb.com/v2.1/get-time-zone?key=&format=json&by=position&lat={latmal}&lng={lonmal}').json()
        zonemal = fdmal['gmtOffset'] / 3600

        payload = json.dumps({
            "female": {
                "year": datetimefem.year,
                "month": datetimefem.month,
                "date": datetimefem.day,
                "hours": 3,
                "minutes": 0,
                "seconds": 0,
                "latitude": latfem,
                "longitude": lonfem,
                "timezone": zonefem
            },
            "male": {
                "year": datetimemal.year,
                "month": datetimemal.month,
                "date": datetimemal.day,
                "hours": 3,
                "minutes": 0,
                "seconds": 0,
                "latitude": latmal,
                "longitude": lonmal,
                "timezone": zonemal
            }, "config": {
                "observation_point": "topocentric",
                "language": "te",
                "ayanamsha": "lahiri"
            }
        })
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': ''
        }
        response = requests.request("POST", url, headers=headers, data=payload).json()
        return response['output']['total_score']
    except Exception as e:
        return 'Error'


bot = telebot.TeleBot(TOKEN)

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton('Узнать совместимость'))
keyboard.add(KeyboardButton('О проекте'))


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Я бот, проверяющий совместимость! Для старта напишите "Узнать совместимость"',
                     reply_markup=keyboard)


@bot.message_handler(regexp=r'О проекте')
def city_fem(message):
    bot.send_message(message.chat.id,
                     'Чатбот "Compatibility" - быстрый способ узнать совместимость с человеком противоположного пола. Для определения результата требуется знать только город и дату рождения.')


@bot.message_handler(regexp=r'Узнать совместимость')
def city_fem(message):
    a = bot.send_message(message.chat.id, 'Введите данные женщины.')
    msg = bot.reply_to(a, 'Напишите город рождения.')
    bot.register_next_step_handler(msg, date_step_fem)


def date_step_fem(message):
    global cityfem
    cityfem = message.text
    msg = bot.reply_to(message, 'Напишите дату рождения в формате гггг.мм.дд.Например:09.09.1999')
    bot.register_next_step_handler(msg, city_mal)


def city_mal(message):
    try:
        global datetimefem
        datetimefem = datetime.datetime.strptime(message.text, '%d.%m.%Y')
        a = bot.send_message(message.chat.id, 'Введите данные мужчины.')
        msg = bot.reply_to(a, 'Напишите город рождения.')
        bot.register_next_step_handler(msg, date_step_mal)
    except Exception as e:
        msg = bot.reply_to(message,
                           'Неверный формат записи даты, начините заново. Для старта напишите"Узнать совместимость"')


def date_step_mal(message):
    global citymal
    citymal = message.text
    msg = bot.reply_to(message, 'Напишите дату рождения в формате гггг.мм.дд.Например:09.09.1999')
    bot.register_next_step_handler(msg, result)


def result(message):
    try:
        global datetimemal, latfem, lonfem, latmal, lonmal
        datetimemal = datetime.datetime.strptime(message.text, '%d.%m.%Y')
        bot.send_message(message.chat.id, 'Ожидайте результаты.')
        latfem, lonfem = get_city_coords(cityfem)
        latmal, lonmal = get_city_coords(citymal)
        s = compatibility()
        if s == 'Error':
            bot.send_message(message.chat.id,
                             'Определить совместимость не удалось, попробуйте другие даты. Для старта напишите"Узнать совместимость"')
        else:
            d = round(s / 36 * 100)
            bot.send_message(message.chat.id, f'Ваша совместимость: {s} из 36. Процент совместимости={d}%')
    except Exception as e:
        msg = bot.reply_to(message,
                           'Неверный формат записи даты, начините заново. Для старта напишите"Узнать совместимость"')


bot.infinity_polling()
