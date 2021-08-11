from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, UserMixin, login_user, current_user


# создаем сервер и БД
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///question_forms.db?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ads2kh2kj3ch4xv8yu6neq1h4by372'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Класс БД для пользователей
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    login = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow,  onupdate=datetime.utcnow)
    question_forms = db.relationship('QuestionForm', backref='author')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.username)


class QuestionForm(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    questions = db.relationship('Form', backref='question_form')
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow,  onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer(), db.ForeignKey('users.id'))

    def __repr__(self):
        return "<{}>".format(self.id)


class Form(db.Model):
    __tablename__ = 'forms'
    id = db.Column(db.Integer(), primary_key=True)
    question = db.Column(db.String())
    answers = db.relationship('Answer', backref='form')
    question_form_id = db.Column(db.Integer(), db.ForeignKey('questions.id'))

    def __repr__(self):
        return "<{}>".format(self.id)


class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer(), primary_key=True)
    answer = db.Column(db.String())
    answer_count = db.Column(db.Integer())
    form_id = db.Column(db.Integer(), db.ForeignKey('forms.id'))

    def __repr__(self):
        return "<{}>".format(self.id)


# авторизация юзера
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


# Страница входа, бэк
@app.route('/login', methods=['POST', 'GET'])
@app.route('/')
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        try:
            user = db.session.query(User).filter(User.login == login).first()
            if user and user.check_password(password):
                login_user(user)
                load_user(user.id)
                return redirect(url_for('lk'))
            flash("Invalid username/password", 'error')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Что-то пошло не так ' + str(e), 'error')
            return redirect('/login')
    else:
        return render_template('login.html')


# Страница регистрации, бэк
@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        name = request.form['name']
        login = request.form['login']
        password = request.form['login']
        password_check = request.form['rep_psw']
        if password == password_check:
            user = User(name=name, login=login)
            user.set_password(password=password)
            try:
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))
            except Exception as e:
                flash("Error " + str(e), 'error')
                return redirect(url_for('registration'))
        else:
            flash("Пароли не совпадают", 'error')
            return redirect(url_for('registration'))
    else:
        return render_template('registration.html')


# Личный кабинет
@app.route('/lk')
@login_required
def lk():
    try:
        intro = QuestionForm.query.filter(QuestionForm.author_id == current_user.id).all()
    except:
        intro = ''
    try:
        return render_template('lk.html', intro=intro)
    except Exception as e:
        return "Exception ", e


@app.route('/new_quest', methods=['POST', 'GET'])
@login_required
def new_quest():
    if request.method == 'POST':
        name = request.form['name']
        quest_num = request.form['quest_num']
        quest = QuestionForm(name=name, author_id=current_user.id)
        for num in range(int(quest_num)):
            add_question(quest.id)
        db.session.add(quest)
        db.session.commit()
        return redirect(url_for(quest.id))

    else:
        return render_template('new_quest.html')

def add_question(id):
    quest = request.form['question']
    ans_num = request.form['ans_num']
    form = Form(question=quest, answer_id=id)
    for num in range(int(ans_num)):
        add_answer(form.id)
    db.session.add(form)
    db.session.commit()

def add_answer(id):
    answer = request.form['answer']
    ans = Answer(answer=answer, answer_count=0, form_id=id)
    db.session.add(ans)
    db.session.commit()


if __name__ == '__main__':
    app.run(debug=True)
