from random import randint

from database.photos_table import Photo
from main import app, login_manager
from flask import render_template, redirect, request, abort
from database.all_for_session import create_session
from database.user_table import User
from flask_login import login_user, logout_user, login_required, current_user

db_session = create_session()


@login_manager.user_loader
def load_user(user):
    return db_session.query(User).get(user)


@app.route('/')
def main_page():
    users = db_session.query(User).all()
    return render_template('another_main_page.html', title='Главная', current_user=current_user, users=users)


@app.route('/all_photos')
def all_photos():
    photos = db_session.query(Photo).all()
    return render_template('main_page.html', title='Все работы', current_user=current_user, photos=photos)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        email = request.form.get("email")
        password = request.form.get("password")
        password2 = request.form.get("password2")
        name = request.form.get("name")

        if not name:
            return render_template('register.html', current_user=current_user, title='Регистрация',
                                   message='введите имя')

        if password != password2:
            return render_template('register.html', current_user=current_user, title='Регистрация',
                                   message='Пароли не совпадают')
        if len(password) < 6:
            return render_template('register.html', current_user=current_user, title='Регистрация',
                                   message='недопустимый пароль')

        if password.isdigit() or (password.isalpha() and (password.islower() or password.isupper())):
            return render_template('register.html', current_user=current_user, title='Регистрация',
                                   message="Ненадежный пароль")

        if password.islower() or password.isupper():
            return render_template('register.html', current_user=current_user, title='Регистрация',
                                   message="Слабый пароль")

        if db_session.query(User).filter(User.email == email).first():
            return render_template('register.html', current_user=current_user, title='Регистрация',
                                   message='Пользователь с таким email уже существует')

        user = User()
        user.email = email
        user.set_password(password)
        user.name = name

        db_session.add(user)
        db_session.commit()

        login_user(user)
        return redirect('/')

    return render_template('register.html', current_user=current_user, title='Регистрация')


@app.route('/delete/<int:photo_id>', methods=['GET', 'POST'])
@login_required
def delete_photo(photo_id):
    photo = db_session.query(Photo).get(photo_id)

    if photo is None or photo.user_id != current_user.id:
        abort(404)

    db_session.delete(photo)
    db_session.commit()
    return redirect(f'/profile/{current_user.id}')


def make_rows(arr):
    res = []
    for i in range(0, len(arr), 3):
        res.append(arr[i: min(len(arr), i + 3)])
    return res


def generate_name():
    letters, mod, length, res = 'abcdefghijklmnopqrstuvwxyz0123456789', 36, 20, ''
    for _ in range(length):
        res += letters[randint(0, mod - 1)]
    return res


@app.route('/profile/<int:user_id>', methods=["GET", "POST"])
def profile(user_id):

    # Если такого пользователя нет
    if db_session.query(User).get(user_id) is None:
        abort(404)

    # Получаем фотки и имя пользователя, чьи работы хотим посмотреть
    photos = list(db_session.query(User).get(user_id).photos)
    user_name = db_session.query(User).get(user_id).name

    if request.method == 'POST':

        # Загружаем фотку
        data = request.files['photo']
        if not data:  # Если пользователь не загрузил фотку
            return render_template('profile.html', user_name=user_name, current_user=current_user, title='Работы',
                                   photos=make_rows(photos), user_id=user_id, author_link=f'/profile/{user_id}',
                                   message='Файл не выбран')

        # Сохраняем фотку
        path = f'img/{generate_name()}.jpg'
        data.save('static/' + path)

        # Добавляем её в базу данных
        photo = Photo()
        photo.path = path
        photo.name = request.form['name']
        current_user.photos.append(photo)
        photos.append(photo)

        db_session.commit()

    return render_template('profile.html', user_name=user_name, current_user=current_user, title='Работы',
                           photos=make_rows(photos), user_id=user_id, author_link=f'/profile/{user_id}')


@app.route('/logout')
@login_required
def logout():
    """Выход из аккаунта"""

    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Обработчик для авторизации"""

    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        user = db_session.query(User).filter(User.email == email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect('/')

        return render_template("login.html", title='Вход', current_user=current_user,
                               message='Неправильный логин или пароль')

    return render_template("login.html", title='Вход', current_user=current_user)
