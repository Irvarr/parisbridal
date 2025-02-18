from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, TextAreaField, BooleanField, FloatField, SearchField, SelectField
from wtforms.validators import DataRequired, Email, Length, URL, Optional

class RegisterForm(FlaskForm):
    partner1_name = StringField('Partner 1 Name', validators=[DataRequired(), Length(min=2, max=100)])
    partner2_name = StringField('Partner 2 Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    wedding_date = DateField('Wedding Date', validators=[DataRequired()])
    wedding_location = StringField('Wedding Location (Optional)', validators=[Optional(), Length(max=200)])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegistryForm(FlaskForm):
    title = StringField('Registry Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    is_public = BooleanField('Make Registry Public', default=True)

class RegistryItemForm(FlaskForm):
    name = StringField('Gift Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    item_type = SelectField(
        'Gift Type',
        choices=[
            ('physical', 'Physical Gift'),
            ('cash', 'Cash Fund'),
            ('experience', 'Experience')
        ],
        default='physical'
    )
    price = FloatField('Price (for physical gifts)', validators=[Optional()])
    target_amount = FloatField('Target Amount (for cash funds)', validators=[Optional()])
    amazon_url = StringField('Amazon URL (for physical gifts)', validators=[Optional(), URL()])
    experience_date = DateField('Experience Date (optional)', validators=[Optional()])
    experience_location = StringField('Experience Location (optional)', validators=[Optional()])

class RegistrySearchForm(FlaskForm):
    search = SearchField('Search by couple name or email', validators=[DataRequired()])

class PurchaseForm(FlaskForm):
    purchased_by = StringField('Your Name', validators=[DataRequired()])
    delivery_choice = StringField('Delivery Method', validators=[DataRequired()])
    ship_to_couple = BooleanField('Ship to Couple', default=True)
    bring_to_wedding = BooleanField('I will bring this gift to the wedding', default=False)
    shipping_address = TextAreaField('Shipping Address', validators=[Optional()])