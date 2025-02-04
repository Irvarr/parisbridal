from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, TextAreaField, BooleanField, FloatField
from wtforms.validators import DataRequired, Email, Length, URL, Optional

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    wedding_date = DateField('Wedding Date', validators=[Optional()])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegistryForm(FlaskForm):
    title = StringField('Registry Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    is_public = BooleanField('Make Registry Public', default=True)

class RegistryItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    price = FloatField('Price', validators=[Optional()])
    amazon_url = StringField('Amazon URL', validators=[Optional(), URL()])
