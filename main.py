import telebot
import requests
from telebot import types
from datetime import datetime

bot_token = '6310054769:AAFmc_juovAVh3bDUjU9b9ukxYsdqUOLCCs'
bot = telebot.TeleBot(bot_token)
channel_id = '@kdtdjtytyjtydtjydjtydjdty'
cart = {}
user_carts = {}

# Головне меню
main_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
button_1 = types.KeyboardButton('🍣 Зробити замовлення')
button_2 = types.KeyboardButton('📱 Контакти')
checkout_back = types.KeyboardButton('📦 Оформити замовлення')
button_back = types.KeyboardButton('🚪 Головне меню')
button_cart = types.KeyboardButton('🛒 Кошик')
empty_cart_button = types.KeyboardButton('🗑️ Опустошити кошик') 
main_markup.add(button_1, button_2, button_back, checkout_back, button_cart, empty_cart_button) 

food_choice_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
food_button = types.KeyboardButton('🍔 їжа')
drink_button = types.KeyboardButton('🍹 Напої')
button_back = types.KeyboardButton('🚪 Головне меню')
food_choice_markup.add(food_button, drink_button, button_back)

# Меню зі стравами
order_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
dishes = {
    'Кебаб': {'price': 250, 'image_path': 'images/kebab.jpg', 'type': 'food'},
    'Шаурма': {'price': 250, 'image_path': 'images/shaurma.jpg', 'type': 'food'},
    'Бургер телятина': {'price': 360, 'image_path': 'images/burger_telyatina.jpg', 'type': 'food'},

    'Бургер курятина': {'price': 340, 'image_path': 'images/burger_chicken.jpg'},
    'Салат фірмовий': {'price': 190, 'image_path': 'images/salad_firm.png'},
    'Цезар з куркою': {'price': 240, 'image_path': 'images/caesar_chicken.jpg'},
    'Салат грецький': {'price': 220, 'image_path': 'images/salad_greek.jpg'},
    'Борщ': {'price': 120, 'image_path': 'images/borscht.jpg'},
    # 'Курячий бульйон': {'price': 100, 'image_path': 'images/chicken_soup.png'},
    # 'Паста 1': {'price': 170, 'image_path': 'images/pasta_1.png'},
    # 'Паста 2': {'price': 185, 'image_path': 'images/pasta_2.png'},

    'Горілка Nemiroff 40% Original 0,5 л.': {'price': 130, 'image_path': 'images/gor_nemyriv.jpg', 'type': 'drink'},
    'Горілка Nemiroff 40% Original 0,7 л.': {'price': 130, 'image_path': 'images/gor_nemyriv.jpg', 'type': 'drink'},
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
    bot.send_message(message.chat.id, '🙂 Вибери тип страв: ', reply_markup=food_choice_markup)


@bot.message_handler(func=lambda message: message.text == '🍔 їжа')
def show_food_menu(message):
    for dish, details in dishes.items():
        if details.get('type') == 'food':
            photo_path = details['image_path']
            price = details['price']
            caption = f'{dish}: {price} грн.'
            with open(photo_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo, caption=caption, reply_markup=create_add_to_cart_keyboard(dish))

@bot.message_handler(func=lambda message: message.text == '🍹 Напої')
def show_drink_menu(message):
    for dish, details in dishes.items():
        if details.get('type') == 'drink':
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
    user_id = message.chat.id
    if user_id not in user_carts or not user_carts[user_id]:
        bot.send_message(user_id, 'Ваш кошик порожній.')
    else:
        # Вартість доставки
        delivery_cost = 370
        
        # Обчислення загальної суми без урахування доставки
        total_price_without_delivery = sum(dishes[dish]['price'] * quantity for dish, quantity in user_carts[user_id].items())
        
        # Додавання вартості доставки до загальної суми
        total_price_with_delivery = total_price_without_delivery + delivery_cost
        
        # Формування повідомлення з вмістом кошика і загальною сумою
        cart_items = '\n'.join([f'{dish}: {quantity} шт. - {dishes[dish]["price"] * quantity} грн.' for dish, quantity in user_carts[user_id].items()])
        message_text = f'Вміст вашого кошика:\n\n{cart_items}\n\n💰 Загальна сума без доставки: {total_price_without_delivery} грн.\n💰 Загальна сума з доставкою: {total_price_with_delivery} грн.'

        bot.send_message(user_id, message_text)

@bot.message_handler(func=lambda message: message.text == '🗑️ Опустошити кошик')
def empty_cart(message):
    user_id = message.chat.id
    if user_id in user_carts:
        user_carts[user_id] = {}  # Опустошити кошик користувача
        bot.send_message(user_id, '🗑️ Кошик успішно опустошено! ', reply_markup=main_markup)
    else:
        bot.send_message(user_id, 'Ваш кошик вже порожній.', reply_markup=main_markup)

@bot.callback_query_handler(func=lambda call: call.data in dishes.keys())
def add_to_cart(call):
    selected_dish = call.data
    user_id = call.message.chat.id
    # Перевірка, чи користувач вже має кошик
    if user_id not in user_carts:
        user_carts[user_id] = {}
    # Додавання товару до кошика користувача
    if selected_dish in user_carts[user_id]:
        user_carts[user_id][selected_dish] += 1
    else:
        user_carts[user_id][selected_dish] = 1
    bot.send_message(user_id, f'✅ Страва додана до вашого кошика! \n\nНазва: {selected_dish}')

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == '📦 Оформити замовлення':
        checkout(message)
    else:
        echo(message)

@bot.message_handler(func=lambda message: True)
def echo(message):
    if message.text == '📱 Контакти':
        bot.send_message(message.chat.id, "📱Телефони : +380123456789\n+380123456788\n+380123456777\n⌛️ Приймання замовлень: Без вихідних з 22:00 до 05:00")
    elif message.text == '🚪 Головне меню':
        bot.send_message(message.chat.id, 'Ви повернулись до головного меню.', reply_markup=main_markup)

@bot.message_handler(func=lambda message: message.text == '📦 Оформити замовлення')
def checkout(message):
    user_id = message.chat.id
    # Перевірка, чи кошик користувача не порожній
    if user_id not in user_carts or not user_carts[user_id]:
        bot.send_message(user_id, 'Ваш кошик порожній. Додайте товари перед оформленням замовлення.')
        return

    # Попросити користувача ввести адресу та номер телефону
    bot.send_message(user_id, 'Введіть вашу адресу:')
    if message.text == '🚪 Головне меню':
        bot.send_message(message.chat.id, 'Ви повернулись до головного меню.', reply_markup=main_markup)
        return
    bot.register_next_step_handler(message, ask_address)

def ask_address(message):
    address = message.text
    
    if address == '🚪 Головне меню':  
        bot.send_message(message.chat.id, 'Ви повернулись до головного меню.', reply_markup=main_markup)
        return
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        reg_button = types.KeyboardButton(text="Надати номер телефону", request_contact=True)
        main_menu_button = types.KeyboardButton('🚪 Головне меню')  # Додано кнопку "🚪 Головне меню"
        keyboard.add(reg_button, main_menu_button)  # Додано кнопку до клавіатури
        
        bot.send_message(message.chat.id, 'Залишіть свій номер телефону, щоб з вами зв\'язались', reply_markup=keyboard) 

        # Перевірка чи введена адреса не порожня
        if address:
            bot.register_next_step_handler(message, confirm_order, address)
        else:
            bot.send_message(message.chat.id, 'Будь ласка, введіть адресу доставки або виберіть "🚪 Головне меню".')


def confirm_order(message, address):

    phone_number = message.text
    if phone_number == '🚪 Головне меню':  
        bot.send_message(message.chat.id, 'Ви повернулись до головного меню.', reply_markup=main_markup)
        return

    username = message.from_user.username
    if username is None:
        username = message.from_user.first_name  # Використовуємо ім'я користувача, якщо нікнейм відсутній

    if message.contact:
        phone_number = message.contact.phone_number
        
    user_id = message.chat.id  # Отримуємо ID користувача
    if user_id in user_carts:
        user_cart = user_carts[user_id]  # Отримуємо кошик користувача
    else:
        user_cart = {}  # Якщо кошика немає, створюємо новий пустий кошик

    current_datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    delivery_cost = 370  # Вартість доставки
    total_price = sum(dishes[dish]['price'] * quantity for dish, quantity in user_cart.items()) + delivery_cost
    message = f'Отримано нове замовлення!\nДата та час: {current_datetime}\n\nКористувач: {username} (ID: {user_id})\nАдреса: {address}\nНомер телефону: {phone_number}\n\nЗамовлення:'
    for dish, quantity in user_cart.items():
        dish_price = dishes[dish]['price']
        message += f'\n{dish}: {quantity} шт. - {dish_price * quantity} грн.'
    message += f'\n\nВартість доставки: {delivery_cost} грн.'
    message += f'\nЗагальна сума з доставкою: {total_price} грн.'

    
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    params = {
        'chat_id': channel_id,
        'text': message
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        print('Дані успішно відправлені на канал!')
    else:
        print('Сталася помилка при відправленні даних на канал.')

    # Обчислення загальної суми замовлення
    total_price = sum(dishes[dish]['price'] * quantity for dish, quantity in user_cart.items())
    # Додавання вартості доставки
    total_price += 370

    order_text = f'Дякуємо за замовлення!\n\n'
    order_text += 'Ваше замовлення:\n'
    for dish, quantity in user_cart.items():
        dish_price = dishes[dish]['price']
        order_text += f'{dish}: {quantity} шт. - {dish_price * quantity} грн.\n'
    order_text += f'\nАдреса: {address}\n'
    order_text += f'Номер телефону: {phone_number}\n'
    order_text += f'Доставка: 370 грн.\n'
    order_text += f'Загальна сума: {total_price} грн.\n'
    order_text += '\nОчікуйте нашого оператора найближчим часом.\n'
    order_text += 'Дякуємо, що обрали нас!'


        
    bot.send_message(user_id, order_text, reply_markup=main_markup)
    user_carts[user_id] = {}

if __name__ == '__main__':
    bot.polling()