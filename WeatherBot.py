import telebot
import pyowm
import gptkey
import secretWeather
import openai
import owmToken
import random
from telebot import types
bot = telebot.TeleBot(token=secretWeather.botToken)

openai.api_key = (gptkey.gptToken)

owm = pyowm.OWM(owmToken.token)

mgr = owm.weather_manager()

#движок ChatGPT

engine = 'text-davinci-003'

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'Список команд:\n-Кнопка "Отправить местоположение" отправит вашу геолокацию и бот расскажет вам о погоде в вашем городе, и сам ChatGPT подскажет вам что надеть)\n'
                                      '-Кнопка /city позволит вам ввести город вручную и узнать ту же информацию)')

@bot.message_handler(commands=['start'])
def text(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=False)
    but1 = types.KeyboardButton('/city')
    but2 = types.KeyboardButton('/help')
    get_location = types.KeyboardButton("Отправить местоположение", request_location=True)
    keyboard.add(get_location, but1, but2)
    bot.send_message(message.chat.id, "Привет! Чтобы узнать погоду и рекомендацию по одежде от ChatGPT - нажми на кнопку и передай мне свое местоположение или введи /city чтобы ввести название города вручную", reply_markup=keyboard)

#хендлер команды отправки геолокации

@bot.message_handler(content_types=["location"])
def locatWeather(message):
    if message.location is not None:
        lat = message.location.latitude
        lon = message.location.longitude
        observation = mgr.weather_at_coords(lat, lon)
        w = observation.weather
        weathercondRus = {'clear sky': 'ясно', 'few clouds': 'мало-облачно', 'scattered clouds': 'несколько облачно',
                          'broken clouds': 'облачно', 'shower rain': 'ливень',
                          'rain': 'дождь', 'thunderstorm': 'гроза', 'snow': 'идет снег', 'mist': 'туманно'}
        w.detailed_status = weathercondRus[w.detailed_status]
        wind = w.wind()['speed']
        feel = int(w.temperature('celsius')['feels_like'])
        temp = int(w.temperature('celsius')['temp'])
        prompt = f"Скажи что одеть в {w.detailed_status} погоду в 1 предложении при температуре {feel} градусов"
        completion = openai.Completion.create(engine=engine, prompt=prompt, temperature=0.5, max_tokens=1000)
        completionG = completion.choices[0]['text']
        bot.send_message(message.chat.id, f'В вашем городе сейчас {w.detailed_status} \nТемпература {temp} градусов. Ощущается как {feel} градусов. Ветер {wind} м/с. {completionG}')

#хендлер команды /city

@bot.message_handler(commands=['city'])
def city(message):
    city = message.text
    bot.send_message(message.chat.id, "Введи название города")
    bot.register_next_step_handler(message, cityWeather)
def cityWeather(message):
    try:
        bot.send_message(message.chat.id, 'Ищу погоду в городе {city}'.format(city=message.text))
        data = message.text
        observation = mgr.weather_at_place(data)
        w = observation.weather
        wind = w.wind()['speed']
        temp = int(w.temperature('celsius')['temp'])
        weathercondRus = {'clear sky': 'ясно', 'few clouds': 'мало-облачно', 'scattered clouds': 'несколько облачно',
                          'broken clouds': 'облачно', 'shower rain': 'ливень',
                          'rain': 'дождь', 'thunderstorm': 'гроза', 'snow': 'идет снег', 'mist': 'туманно'}
        w.detailed_status = weathercondRus[w.detailed_status]
        feel = int(w.temperature('celsius')['feels_like'])
        prompt = f"Скажи что одеть в {w.detailed_status} погоду в 1 предложении при температуре {feel} градусов"
        completion = openai.Completion.create(engine=engine, prompt=prompt, temperature=0.5, max_tokens=1000)
        completionG = completion.choices[0]['text']
        bot.send_message(message.chat.id,
                         f'В городе {message.text} сейчас {w.detailed_status} \nТемпература {temp} градусов. Ощущается как {feel} градусов. Ветер {wind} м/с {completionG}')
    except Exception as error:
        bot.send_message(message.chat.id, 'Я не нашел такого города, попробуйте еще раз)')

#хендлер рандомных сообщений

@bot.message_handler(content_types=['text'])
def text_handler(message):
    bot.send_message(message.chat.id, "Я вас не понял! Если хотите узнать погоду - введите команду /city, или отправьте геолокацию! ")
    pass

bot.polling(none_stop=True)

# def city(message):
#     bot.send_message(message.chat.id, 'Ищу погоду в вашем городе')
#     time.sleep(2)
#
#     #data = message.text
#     observation = mgr.weather_at_coords(lat, lon)
#     w = observation.weather
#     wind = w.wind()
#     temp = w.temperature('celsius')['temp']
#     max_temp = w.temperature('celsius')['temp_max']
#     min_temp = w.temperature('celsius')['temp_min']
#     feel = w.temperature('celsius')['feels_like']
#     bot.send_message(message.chat.id, f'В вашем городе сейчас {w.detailed_status} \nМаксимальная температура {max_temp} градусов, а минимальная температура {min_temp} градусов. Ощущается как {feel} градусов')






# @bot.message_handler(commands=['city'])
# def cmd_city(message):
#     send = bot.send_message(message.chat.id, 'Введи город')
#     bot.register_next_step_handler(send, city)
#
#
# def city(message):
#     bot.send_message(message.chat.id, 'Ищу погоду в городе {city}'.format(city=message.text))
#     time.sleep(2)
#
#     data = message.text
#     observation = mgr.weather_at_place(data)
#     w = observation.weather
#     wind = w.wind()
#     temp = w.temperature('celsius')['temp']
#     max_temp = w.temperature('celsius')['temp_max']
#     min_temp = w.temperature('celsius')['temp_min']
#     feel = w.temperature('celsius')['feels_like']
#     bot.send_message(message.chat.id, f'В городе {message.text} сейчас {w.detailed_status} \nМаксимальная температура {max_temp} градусов, а минимальная температура {min_temp} градусов. Ощущается как {feel} градусов')

    # det = w.detailed_status()
    #hum = w.humidity()

    # wnd = json.dumps(wind, sort_keys=True, indent=4)
    # tmp = json.dumps(temp, sort_keys=True, indent=4)
    # pwnd = json.loads(wnd)
    # ptmp = json.loads(tmp)
    # winds = pwnd['speed']
    # tmp = ptmp['temp']
    # tmpx = ptmp['temp_max']
    # tmpn = ptmp['temp_min']


    # bot.send_message(message.chat.id,
    #                  'В  {city}: \n 🌡 Сейчас: {tmp}°C \n 🌡 Максимум: {tmpx}°C \n 🌡 Минимум: {tmpn}°C \n 💨 Ветер: {wind} м/с \n 💧 Влажность: {humidity}%'.format(
    #                      city=message.text,
    #                      tmp=(tmp), tmpx=(tmpx), tmpn=(tmpn),
    #                      humidity=(hum), wind=(winds)))


 # def get_location(lat, lon):
#     url = f"https://yandex.ru/pogoda/maps/nowcast?lat={lat}&lon={lon}&via=hnav&le_Lightning=1"
#     return url
#
#
# def weather(city: str):
#     owm = OWM('5626e8fbf656b5e2eac0cb473f525efa')
#     mgr = owm.weather_manager()
#     observation = mgr.weather_at_place(city)
#     weather = observation.weather
#     location = get_location(observation.location.lat, observation.location.lon)
#     temperature = weather.temperature("celsius")
#     return temperature, location
#
# @bot.message_handler(commands=['weather'])
# def get_text_messages(message):
#     bot.send_message(message.chat.id, "Введите название города)")
#     bot.register_next_step_handler(message, get_weather)
#
# def get_weather(message):
#     city = message.text
#     try:
#         w = weather(city)
#         bot.send_message(message.chat.id, f'В городе {city} сейчас {round(w[0]["temp"])} градусов' f'чувствуется как{round(w[0]["feels_like"])} градусов')
#         bot.send_message(message.chat.id, w[1])
#         bot.send_message(message.chat.id, "Введите название города")
#         bot.register_next_step_handler(message, get_weather)
#     except Exception:
#         bot.send_message(message.chat.id, "Упс... Такого города нет в базе, попробуйте еще раз")
#         bot.send_message(message.chat.id, "Введите название города")
#         bot.register_next_step_handler(message, get_weather)

