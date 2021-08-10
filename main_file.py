from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy

# создаем сервер и БД
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///question_forms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'adskhkjchxvyuneq1h4by372'
db = SQLAlchemy(app)


# Класс БД для пользователей
class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(40), nullable=False)
    name = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        return '<Users %r>' % self.user_id


# Страница входа, бэк
@app.route('/login', methods=['POST', 'GET'])
@app.route('/')
def main():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        try:
            intro = Users.query.order_by(Users.login).all()
            for el in intro:
                if el.login == login and el.password == password:
                    return render_template('lk.html', user=el.user_id)
            flash('login or password not found', 'error')
            return redirect('/login')
        except Exception as e:
            flash('Что-то пошло не так' + str(e), 'error')
            return redirect('/login')
    else:
        return render_template('login.html')


# Страница регистрации, бэк
@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        repeat_password = request.form['rep_psw']
        name = request.form['name']

        user = Users(login=login, password=password, name=name)

        if password == repeat_password:
            try:
                db.session.add(user)
                db.session.commit()

                return redirect('/')
            except:
                flash('exsisting login')
                return redirect('/registration')
        else:
            flash("Password isn't match", 'error')
            return redirect('/registration')
    else:
        return render_template('registration.html')


# Личный кабинет
@app.route('/lk')
def lk():
    intro = Users.query.order_by(Users.login).all()
    try:
        return render_template('lk.html', intro=intro)
    except Exception as e:
        return "Exception ", e


if __name__ == '__main__':
    app.run(debug=True)
