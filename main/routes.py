from flask import render_template, url_for, flash, redirect, request, abort
from main import app, db, bcrypt
from main.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from main.models import User, Post, PostImage
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from os import abort
from PIL import Image


# posts = [
#     {
#         'title': 'Վաճառվում է բնակարան',
#         'price' : '80.000$',
#         'adress': 'ք․երևան, Բաբաջանյան 160'
#     },
# {
#         'title': 'Վաճառվում է Honda Accord մակնիշի ավտոմեքենա',
#         'price' : '15.000$',
#         'adress': 'ք․երևան, Ուլնեցի 10'
#     },
# {
#         'title': 'Վաճառվում է Կլառնետ',
#         'price' : '10,000$',
#         'adress': 'ք․երևան, Գուգուշի նրբանցք 6'
#     }
# ]


@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Ձեր էջը ստեղծված է! Այժմ կարող է մուտք գործել', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Սխալ տվյալներ. Խնդրում ենք ստուգել էլ․հասցեն կամ գաղտնաբառը', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture, folder):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static', folder, picture_fn)

    # output_size = (125, 125)
    # i = Image.open(form_picture)
    # i.thumbnail(output_size)
    # i.save(picture_path)

    form_picture.save(picture_path)

    return picture_fn

#
# def save_pictureP(form_picture):
#     random_hex = secrets.token_hex(8)
#     _, f_ext = os.path.splitext(form_picture.filename)
#     picture_fn = random_hex + f_ext
#     picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
#
#     output_size = (125, 125)
#     i = Image.open(form_picture)
#     i.thumbnail(output_size)
#     i.save(picture_path)
#
#     return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 'profile_pics')
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Ваш профиль был успешно обновлен!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    image_file = 'default.jpg'
    if form.validate_on_submit():
        if form.image.data:
            image_file = save_picture(form.image.data, 'post_images')
        else:
            image_file = 'default.jpg'

        post = Post(title=form.title.data, content=form.content.data,
                    price=form.price.data, phone_number=form.phone_number.data, address=form.address.data,
                    image_file=image_file, author=current_user)

        db.session.add(post)
        db.session.commit()
        flash('Ձեր հայտարարությունը ստեղծված է!', 'success')
        return redirect(url_for('home'))

    return render_template('create_post.html', title='New Post',
                           form=form, legend='Նոր հայտարարություն', image_file=image_file)






@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        form.content.data = post.content
        post.content = form.content.data
        db.session.commit()
        flash('Ձեր հայտարարությունը թարմացվել է!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.price.data = post.price
        form.content.data = post.content


    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Թարմացնել հայտարարություն')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Ձեր հայտարարությունը ջնջվել է!', 'success')
    return redirect(url_for('home'))