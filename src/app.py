from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
import os
import requests

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'  

USERS_FILE = 'users.json'


def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as file:
                return json.load(file)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Ошибка загрузки пользователей: {e}")
        return {}
    return {}


def save_users(users):
    try:
        with open(USERS_FILE, 'w') as file:
            json.dump(users, file)
    except IOError as e:
        print(f"Ошибка сохранения пользователей: {e}")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        if username in users:
            return "Пользователь уже существует!", 400
        users[username] = {'password': password, 'favorites': []}
        save_users(users)
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        if username in users and users[username]['password'] == password:
            session['current_user'] = username  
            return redirect(url_for('index'))
        return "Неверный логин или пароль!", 401
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('current_user', None)
    return redirect(url_for('index'))


@app.route('/random_cat')
def random_cat():
    try:
        response = requests.get('https://api.thecatapi.com/v1/images/search', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0 and 'url' in data[0]:
                return jsonify({'url': data[0]['url']})
            else:
                return jsonify({'error': 'Пустой ответ от API'}), 502
        elif 400 <= response.status_code < 500:
            return jsonify({'error': f'Ошибка клиента: {response.status_code}'}), response.status_code
        elif 500 <= response.status_code < 600:
            return jsonify({'error': 'Ошибка сервера внешнего API'}), 502
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса к API: {e}")
        return jsonify({'error': 'Ошибка запроса к внешнему API'}), 503


@app.route('/favorites', methods=['GET', 'POST'])
def favorites():
    if 'current_user' not in session:
        return redirect(url_for('login'))

    users = load_users()
    username = session['current_user']

    if username not in users:
        return "Пользователь не найден!", 404

    favorites = users[username].get('favorites', [])

    if request.method == 'POST':
        cat_url = request.json.get('cat_url')
        if cat_url and cat_url not in favorites:
            favorites.append(cat_url)
            users[username]['favorites'] = favorites
            save_users(users)
        return jsonify({'status': 'added'})

    return render_template('favorites.html', favorites=favorites)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
