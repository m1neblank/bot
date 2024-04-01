import telebot
import requests
from telebot import types
from flask import Flask, request
import threading
from werkzeug.serving import make_server
import json 

bot = telebot.TeleBot('6310054769:AAFmc_juovAVh3bDUjU9b9ukxYsdqUOLCCs')
cart = {}
app = Flask(__name__)

@app.route('/', methods=['POST'])
def receive_order():
    data = request.form
    user_id = data.get('user_id')
    order = data.get('order')
    decoded_json = json.loads(order)
    username = data.get('username')
    address = data.get('address')
    phone_number = data.get('phone_number')
    print(f"Отримано замовлення від користувача.\nКористувач: {user_id} \nСтрави: {decoded_json} \nНазва користувача: {username} \nАдреса: {address} \nНомер телефону: {phone_number}")
    return 'OK'

# Головне меню
main_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
button_1 = types.KeyboardButton('🍣 Зробити замовлення')
button_2 = types.KeyboardButton('📱 Контакти')
checkout_back = types.KeyboardButton('📦 Оформити замовлення')
button_back = types.KeyboardButton('🚪 Головне меню')
button_cart = types.KeyboardButton('🛒 Кошик')
empty_cart_button = types.KeyboardButton('🗑️ Опустошити кошик') 
main_markup.add(button_1, button_2, button_back, checkout_back, button_cart, empty_cart_button) 


# Меню зі стравами
order_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
dishes = ['Кебаб', 'Шаурма', 'Бургер телятина', 'Бургер курятина', 'Салат фірмовий', 'Цезар з куркою', 'Салат грецький', 'Борщ', 'Курячий бульйон', 'Паста 1', 'Паста 2']  # Список страв
dishes_prices = {
    'Кебаб': {'price': 250, 'image_path': 'images/kebab.png'},
    'Шаурма': {'price': 250, 'image_path': 'images/kebab.png'},
    'Бургер телятина': {'price': 360, 'image_path': 'images/kebab.png'},
    'Бургер курятина': {'price': 340, 'image_path': 'images/kebab.png'},
    'Салат фірмовий': {'price': 190, 'image_path': 'images/kebab.png'},
    'Цезар з куркою': {'price': 240, 'image_path': 'images/kebab.png'},
    'Салат грецький': {'price': 220, 'image_path': 'images/kebab.png'},
    'Борщ': {'price': 120, 'image_path': 'images/kebab.png'},
    'Курячий бульйон': {'price': 100, 'image_path': 'images/kebab.png'},
    'Паста 1': {'price': 170, 'image_path': 'images/kebab.png'},
    'Паста 2': {'price': 185, 'image_path': 'images/kebab.png'},
}

for dish in dishes:
    order_markup.add(types.KeyboardButton(dish))
button_back = types.KeyboardButton('🚪 Головне меню')
order_markup.add(button_back)

# Змінна для зберігання вибраної страви
selected_dish = None

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Давай зробимо замовлення 😎', reply_markup=main_markup)

@bot.message_handler(func=lambda message: message.text == '🍣 Зробити замовлення')
def show_menu(message):
    for dish, details in dishes_prices.items():
        photo_path = details['image_path']
        price = details['price']
        caption = f'{dish}: {price} грн.'
        with open(photo_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption=caption, reply_markup=create_add_to_cart_keyboard(dish))

def create_add_to_cart_keyboard(dish):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Додати до кошика", callback_data=dish))
    return keyboard

@bot.message_handler(func=lambda message: message.text == '🛒 Кошик')
def view_cart(message):
    if not cart:
        bot.send_message(message.chat.id, 'Ваш кошик порожній.')
    else:
        total_price = sum(dishes_prices[dish]['price'] * quantity for dish, quantity in cart.items())
        cart_items = '\n'.join([f'{dish}: {quantity} шт. - {dishes_prices[dish]["price"] * quantity} грн.' for dish, quantity in cart.items()])
        bot.send_message(message.chat.id, f'Вміст вашого кошика:\n\n{cart_items}\n\n💰 До сплати: {total_price} грн.')

@bot.message_handler(func=lambda message: message.text == '🗑️ Опустошити кошик')
def empty_cart(message):
    global cart  # Зробити кошик глобальним, щоб мати до нього доступ
    cart = {}  # Опустошити кошик
    bot.send_message(message.chat.id, '🗑️ Кошик успішно опустошено! ', reply_markup=main_markup)


@bot.callback_query_handler(func=lambda call: call.data in dishes_prices.keys())
def add_to_cart(call):
    selected_dish = call.data
    # Перевірка, чи страва вже є у кошику
    if selected_dish in cart:
        cart[selected_dish] += 1
    else:
        cart[selected_dish] = 1
    bot.send_message(call.message.chat.id, f'✅ Страва додана до кошика! \n\nНазва: {selected_dish}')

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == '📦 Оформити замовлення':
        checkout(message)
    else:
        echo(message)

@bot.message_handler(func=lambda message: True)
def echo(message):
    global selected_dish
    if message.text == '📱 Контакти':
        bot.send_message(message.chat.id, "📱Телефони : +380123456789\n+380123456788\n+380123456777\n⌛️ Приймання замовлень: Без вихідних з 22:00 до 05:00")
    elif message.text == '🚪 Головне меню':
        bot.send_message(message.chat.id, 'Ви повернулись до головного меню.', reply_markup=main_markup)

@bot.message_handler(func=lambda message: message.text == '📦 Оформити замовлення')
def checkout(message):
    # Перевірка, чи кошик не порожній
    if not cart:
        bot.send_message(message.chat.id, 'Ваш кошик порожній. Додайте товари перед оформленням замовлення.')
        return

    # Попросити користувача ввести адресу та номер телефону
    bot.send_message(message.chat.id, 'Введіть вашу адресу:')
    bot.register_next_step_handler(message, ask_address)


def ask_address(message):
    address = message.text
    # bot.send_message(message.chat.id, 'Дякуємо за адресу! Тепер введіть ваш номер телефону:')
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    reg_button = types.KeyboardButton(text="Надати номер телефону", request_contact=True)
    keyboard.add(reg_button)
    bot.send_message(message.chat.id, 'Залишіть свій номер телефону, щоб з вами зв\'язались', reply_markup=keyboard) 
    bot.register_next_step_handler(message, confirm_order, address)


def confirm_order(message, address):
    phone_number = message.text

    username = message.from_user.username
    if username is None:
        username = message.from_user.first_name  # Використовуємо ім'я користувача, якщо нікнейм відсутній

    if message.contact:
        phone_number = message.contact.phone_number
        
    send_order_to_server(message.chat.id, message.from_user.username, cart, address, phone_number)
    
    # Підготовка тексту для відправлення користувачеві
    order_text = f'Дякуємо за замовлення!\n\n'
    order_text += 'Ваше замовлення:\n'
    for dish, quantity in cart.items():
        order_text += f'{dish}: {quantity} шт.\n'
    order_text += f'\nАдреса: {address}\n'
    order_text += f'Номер телефону: {phone_number}\n'
    order_text += '\nОчікуйте нашого оператора найближчим часом.\n'
    order_text += 'Дякуємо, що обрали нас!'
    
    bot.send_message(message.chat.id, order_text, reply_markup=main_markup)

def send_order_to_server(user_id, username, order, address, phone_number):
    url = 'http://127.0.0.1:5000'  # URL вашого сервера
    order_json = json.dumps(order)  # Перетворення масиву у JSON-рядок
    data = {'user_id': user_id, 'username': username, 'order': order_json, 'address': address, 'phone_number': phone_number}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print('Замовлення успішно відправлене на сервер!')
    else:
        print('Сталася помилка при відправленні замовлення на сервер.')

def flask_thread():
    server = make_server('localhost', 5000, app)
    server.serve_forever()

def telegram_thread():
    bot.polling()

if __name__ == '__main__':
    flask_t = threading.Thread(target=flask_thread)
    telegram_t = threading.Thread(target=telegram_thread)

    flask_t.start()
    telegram_t.start()

    flask_t.join()
    telegram_t.join()