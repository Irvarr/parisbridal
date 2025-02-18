from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, TextAreaField, BooleanField, FloatField, SearchField, SelectField, RadioField
from wtforms.validators import DataRequired, Email, Length, URL, Optional

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    celebration_type = RadioField('Celebration Type', 
        choices=[('wedding', 'Wedding'), ('quinceanera', 'Quinceañera')],
        validators=[DataRequired()]
    )
    # Wedding-specific fields
    partner1_name = StringField('Partner 1 Name', validators=[Optional(), Length(min=2, max=100)])
    partner2_name = StringField('Partner 2 Name', validators=[Optional(), Length(min=2, max=100)])
    # Quinceañera-specific fields
    celebrant_name = StringField('Celebrant Name', validators=[Optional(), Length(min=2, max=100)])
    # Common Fields
    celebration_date = DateField('Celebration Date', validators=[DataRequired()])
    celebration_location = StringField('Location (Optional)', validators=[Optional(), Length(max=200)])

class CreateWeddingForm(FlaskForm):
    partner1_name = StringField('Partner 1 Name', validators=[DataRequired(), Length(min=2, max=100)])
    partner2_name = StringField('Partner 2 Name', validators=[DataRequired(), Length(min=2, max=100)])
    celebration_date = DateField('Celebration Date', validators=[DataRequired()])
    celebration_location = StringField('Location (Optional)', validators=[Optional(), Length(max=200)])

class CreateQuinceaneraForm(FlaskForm):
    celebrant_name = StringField('Celebrant Name', validators=[DataRequired(), Length(min=2, max=100)])
    celebration_date = DateField('Celebration Date', validators=[DataRequired()])
    celebration_location = StringField('Location (Optional)', validators=[Optional(), Length(max=200)])

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
    bring_to_wedding = BooleanField('I will bring this gift to the celebration', default=False)
    shipping_address = TextAreaField('Shipping Address', validators=[Optional()])

class GuestForm(FlaskForm):
    name = StringField('Guest Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    number_of_guests = StringField('Number of Guests', validators=[DataRequired()])
    table_assignment = StringField('Table Assignment', validators=[Optional(), Length(max=50)])
    meal_choice = SelectField('Meal Preference',
        choices=[
            ('no_preference', 'No Preference'),
            ('chicken', 'Chicken'),
            ('salmon', 'Salmon'),
            ('steak', 'Steak'),
            ('vegan', 'Vegan')
        ],
        default='no_preference',
        validators=[Optional()]
    )
    dietary_restrictions = TextAreaField('Dietary Restrictions')
    notes = TextAreaField('Additional Notes')

class WeddingPartyMemberForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    role_type = SelectField('Role Type', 
        choices=[
            ('bridesmaid', 'Bridesmaid'),
            ('groomsman', 'Groomsman'),
            ('sponsor', 'Padrino/Madrina/Sponsor')
        ],
        validators=[DataRequired()]
    )
    role_title = StringField('Special Title (e.g., Maid of Honor, Best Man)', validators=[Optional(), Length(max=50)])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    table_assignment = StringField('Table Assignment', validators=[Optional(), Length(max=50)])
    meal_choice = SelectField('Meal Preference',
        choices=[
            ('no_preference', 'No Preference'),
            ('chicken', 'Chicken'),
            ('salmon', 'Salmon'),
            ('steak', 'Steak'),
            ('vegan', 'Vegan')
        ],
        default='no_preference',
        validators=[Optional()]
    )
    notes = TextAreaField('Notes')