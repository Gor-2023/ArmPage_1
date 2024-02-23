from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from main.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Անվանում', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Էլ․հասցե', validators=[DataRequired(), Email()])
    password = PasswordField('Գաղտնաբառ', validators=[DataRequired()])
    confirm_password = PasswordField('Հաստատել գաղտնաբառը', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Գրանցում')



    def validate_username(self, username):

            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError('Այդ անվանումը զբաղված է. Խնդրում ենք ընտրել մեկ այլը.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Այդ էլ․հասցեն զբաղված է. Խնդրում ենք ընտրել մեկ այլը.')


class LoginForm(FlaskForm):
    email = StringField('Էլ․հասցե', validators=[DataRequired(), Email()])
    password = PasswordField('Գաղտնաբառ', validators=[DataRequired()])
    remember = BooleanField('Հիշել')
    submit = SubmitField('Մուտք')


class UpdateAccountForm(FlaskForm):
    username = StringField('Անվանում', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Էլ․հասցե', validators=[DataRequired(), Email()])
    picture = FileField('Թարմացնել էջի նկարը', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Թարմացնել')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Այդ անվանումը զբաղված է. Խնդրում ենք ընտրել մեկ այլը.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Այդ էլ․հասցեն զբաղված է. Խնդրում ենք ընտրել մեկ այլը.')


class PostForm(FlaskForm):
    title = StringField('Վերնագիր', validators=[DataRequired()])
    price = StringField('Արժեք', validators=[DataRequired()])
    address = TextAreaField('Հասցե', validators=[DataRequired()])
    phone_number = TextAreaField('Հեռախոսահամար', validators=[DataRequired()])
    content = TextAreaField('Նկարագիր', validators=[DataRequired()])
    image = FileField('Ավելացնել նկար', validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Տեղադրել')
