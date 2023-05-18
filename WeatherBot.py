import telebot
import pyowm
import gptkey
import secretWeather
import openai
import owmToken
import random
from telebot import types

#токен тг бота

bot = telebot.TeleBot(token=secretWeather.botToken)

#токен ChatGPT

openai.api_key = (gptkey.gptToken)

#токен OWM

owm = pyowm.OWM(owmToken.token)

mgr = owm.weather_manager()

#движок ChatGPT

engine = 'text-davinci-003'

#создаём клавиатуру, кнопка get_location отправляет геолокацию пользователя, а так же делаем хендлер команды /start

@bot.message_handler(commands=['start'])
def text(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=False)
    but1 = types.KeyboardButton('Погода☀')
    but2 = types.KeyboardButton('Помощь🆘')
    get_location = types.KeyboardButton("📍Отправить геолокацию", request_location=True)
    keyboard.add(get_location, but1, but2)
    bot.send_message(message.chat.id, "Привет! Чтобы узнать погоду и рекомендацию по одежде от ChatGPT - нажми на кнопку '📍Отправить геолокацию' и передай мне свое местоположение или нажми на кнопку 'Погода☀' чтобы ввести название города вручную", reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == 'Помощь🆘')
def help(message):
    if message.text == 'Помощь🆘':
        bot.send_message(message.chat.id, 'Список команд:\n-Кнопка '📍Отправить геолокацию' отправит вашу геолокацию и бот расскажет вам о погоде в вашем городе, и сам ChatGPT подскажет вам что надеть)\n'
                         '-Кнопка 'Погода☀' позволит вам ввести город вручную и узнать ту же информацию)')


#хендлер команды отправки геолокации, ищем город по переменным широты lat и долготы lon, а так же делаем запросы к ChatGPT через переменные prompt и completion

@bot.message_handler(content_types=["location"])
def locatWeather(message):
    if message.location is not None:
        bot.send_message(message.chat.id, '☀Ищу погоду в вашем городе...')
        lat = message.location.latitude
        lon = message.location.longitude
        observation = mgr.weather_at_coords(lat, lon)
        w = observation.weather
        weathercondRus = {'clear sky': 'ясно☀', 'few clouds': 'мало-облачно⛅', 'scattered clouds': 'несколько облачно🌤️',
                          'broken clouds': 'облачно☁', 'shower rain': 'ливень💦',
                          'rain': 'дождь🌧️', 'thunderstorm': 'гроза🌩️', 'snow': 'идет снег🌨️', 'mist': 'туманно🌫️', 'overcast clouds': 'облачно☁'}
        w.detailed_status = weathercondRus[w.detailed_status]
        wind = w.wind()['speed']
        feel = int(w.temperature('celsius')['feels_like'])
        temp = int(w.temperature('celsius')['temp'])
        prompt = f"Скажи что одеть при {feel} градусов. Предложение должно быть в дружеском стиле"
        completion = openai.Completion.create(engine=engine, prompt=prompt, temperature=0.5, max_tokens=1000)
        completionG = completion.choices[0]['text']
        bot.send_message(message.chat.id, f'☀В вашем городе сейчас {w.detailed_status} \n🌡️Температура {temp} градусов. Ощущается как {feel} градусов. 💨Ветер {wind} м/с. {completionG}-Совет от ChatGPT🤓')

#хендлер команды /city, в первой функции обрабатываем название города, а во второй пробуем найти этот город в OWM, и говорим что не нашли такой город, если его неккоректно ввели, или если его нет на OWM
#запросы к ChatGPT через переменные prompt и completion

@bot.message_handler(func=lambda message: message.text == 'Погода☀')
def city(message):
    city = message.text
    bot.send_message(message.chat.id, "🌇Введи название города")
    bot.register_next_step_handler(message, cityWeather)
def cityWeather(message):
    try:
        bot.send_message(message.chat.id, '☀Ищу погоду в городе {city}'.format(city=message.text))
        data = message.text
        observation = mgr.weather_at_place(data)
        w = observation.weather
        wind = w.wind()['speed']
        temp = int(w.temperature('celsius')['temp'])
        weathercondRus = {'clear sky': 'ясно☀', 'few clouds': 'мало-облачно⛅',
                          'scattered clouds': 'несколько облачно🌤️',
                          'broken clouds': 'облачно☁', 'shower rain': 'ливень💦',
                          'rain': 'дождь🌧️', 'thunderstorm': 'гроза🌩️', 'snow': 'идет снег🌨️', 'mist': 'туманно🌫️', 'overcast clouds': 'облачно☁'}
        w.detailed_status = weathercondRus[w.detailed_status]
        feel = int(w.temperature('celsius')['feels_like'])
        #prompt = f"Скажи что одеть в {w.detailed_status} погоду в 1 предложении и неформальном стиле при температуре {feel} градусов"
        prompt = f"Скажи что одеть при {feel} градусов. Предложение должно быть в дружеском стиле"
        completion = openai.Completion.create(engine=engine, prompt=prompt, temperature=0.5, max_tokens=1000)
        completionG = completion.choices[0]['text']
        bot.send_message(message.chat.id,
                         f'☀В городе {message.text} сейчас {w.detailed_status} \n🌡️Температура {temp} градусов. Ощущается как {feel} градусов. 💨Ветер {wind} м/с {completionG}-Совет от ChatGPT🤓')
    except Exception as error:
        bot.send_message(message.chat.id, 'Я не нашел такого города, попробуйте еще раз)')

#хендлер рандомных сообщений

@bot.message_handler(content_types=['text'])
def text_handler(message):
    bot.send_message(message.chat.id, "Я вас не понял! Если хотите узнать погоду - введите команду 'Погода☀', или отправьте геолокацию! ")
    pass

bot.polling(none_stop=True)
