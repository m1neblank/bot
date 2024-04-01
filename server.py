from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def receive_order():
    data = request.form
    user_id = data.get('user_id')
    order = data.get('order')
    username = data.get('username')
    address = data.get('address')
    phone_number = data.get('phone_number')
    print(f"Отримано замовлення від користувача.\nКористувач: {user_id} \nСтрави: {order} \nНазва користувача: {username} \nАдреса: {address} \nНомер телефону: {phone_number}")
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True)