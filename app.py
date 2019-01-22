# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, session, flash
import config
from models import User, Question, Comment
from exts import db
from decorators import log_required


app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)


@app.route('/')
def index():
    context = {
        'questions': Question.query.order_by('-create_time').all()
    }
    return render_template('index.html', **context)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        # print(telephone)
        # print(password)
        user = User.query.filter(User.telephone == telephone, User.password == password).first()
        # print(user)
        # return telephone

        if user:
            # print("hello")
            session['user_id'] = user.id
            session.permanent = True
            flash('You have logged in!')
            return redirect(url_for('index'))
        else:
            return "手机号码或者密码输入错误"


@app.route('/logout')
def logout():
    # session.clear()
    session.pop('user_id', None)
    flash('You have logged out!')
    return redirect(url_for('index'))

# @app.route('/logout/')
# def logout():
#     session.clear()
#     return redirect(url_for('login'))


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter(User.telephone == telephone).first()
        if user:
            return "该手机号码已经注册，请更换手机号码"
        else:
            if password1 != password2:
                return "两次输入密码不一致，请检查"
            else:
                user = User(telephone=telephone, username=username, password=password1)
                db.session.add(user)
                db.session.commit()
                flash("You've registered! Please login in")
                return redirect(url_for('login'))


@app.route('/question/', methods=['GET', 'POST'])
@log_required
def question():
    if request.method == 'GET':
        return render_template('question.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        question = Question(title=title, content=content)
        user_id = session.get('user_id')
        user = User.query.filter(User.id == user_id).first()
        question.author = user
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('index'))


@app.route('/detail/<question_id>')
def detail(question_id):
    question_model = Question.query.filter(Question.id == question_id).first()
    return render_template('detail.html', question=question_model)


@app.route('/add_comment/', methods=['POST'])
@log_required
def add_comment():
    content = request.form.get('content')
    question_id = request.form.get('question_id')

    comment = Comment(content=content)
    user_id = session['user_id']
    user = User.query.filter(User.id == user_id).first()
    comment.author = user
    question = Question.query.filter(Question.id == question_id).first()
    comment.question = question
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('detail', question_id=question_id))


if __name__ == '__main__':
    app.debug = True
    app.run()
