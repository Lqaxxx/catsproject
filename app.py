from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
import os
import requests

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'  

USERS_FILE = 'users.json'


def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as file:
            return json.load(file)
    return {}


def save_users(users):
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file)

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
            return "Пользователь уже существует!"
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
        return "Неверный логин или пароль!"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('current_user', None)
    return redirect(url_for('index'))

@app.route('/random_cat')
def random_cat():
    response = requests.get('https://api.thecatapi.com/v1/images/search')
    if response.status_code == 200:
        return jsonify(response.json()[0]['url'])
    return jsonify({'error': 'Не удалось получить котика'})

@app.route('/favorites', methods=['GET', 'POST'])
def favorites():
    if 'current_user' not in session:
        return redirect(url_for('login'))

    users = load_users()
    username = session['current_user']
    favorites = users[username].get('favorites', [])

    if request.method == 'POST':
        cat_url = request.json.get('cat_url')
        if cat_url and cat_url not in favorites:
            favorites.append(cat_url)
            users[username]['favorites'] = favorites
            save_users(users)
        return jsonify({'status': 'added'})

    return render_template('favorites.html', favorites=favorites)

if __name__ == '__main__':
    app.run(debug=True)
