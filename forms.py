from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, TextAreaField, BooleanField, FloatField, SearchField, SelectField, RadioField
from wtforms.validators import DataRequired, Email, Length, URL, Optional, NumberRange

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
    name = StringField('Gift Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    item_type = RadioField(
        'Gift Type',
        choices=[
            ('physical', 'Physical Gift'),
            ('cash', 'Cash Fund'),
            ('experience', 'Experience Gift')
        ],
        default='physical'
    )
    price = FloatField('Price', validators=[Optional()])
    target_amount = FloatField('Target Amount', validators=[Optional()])
    amazon_url = StringField('Amazon URL', validators=[Optional(), URL()])
    priority_level = SelectField(
        'Priority Level',
        choices=[
            ('must-have', 'Must Have'),
            ('normal', 'Normal'),
            ('nice-to-have', 'Nice to Have')
        ],
        default='normal'
    )
    experience_date = DateField('Experience Date', validators=[Optional()])
    experience_location = StringField('Experience Location', validators=[Optional()])

class RegistrySearchForm(FlaskForm):
    search = SearchField('Search by couple name or email', validators=[DataRequired()])

class PurchaseForm(FlaskForm):
    purchased_by = StringField('Your Name', validators=[DataRequired()])
    delivery_choice = StringField('Delivery Method', validators=[DataRequired()])
    ship_to_couple = BooleanField('Ship to Couple', default=True)
    bring_to_wedding = BooleanField('I will bring this gift to the wedding', default=False)
    shipping_address = TextAreaField('Shipping Address', validators=[Optional()])
    contribution_amount = FloatField('Contribution Amount', validators=[Optional(), NumberRange(min=1)])