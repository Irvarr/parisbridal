from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, DateField, TextAreaField, 
    BooleanField, SelectField, FloatField, SearchField, DateTimeField
)
from wtforms.validators import DataRequired, Email, Length, Optional, URL

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

    # Celebration Type Checkboxes
    is_wedding = BooleanField('I\'m getting married')
    is_quinceanera = BooleanField('I have a Quinceañera')
    is_party = BooleanField('I just like to party')

    # Optional Celebration Details
    celebration_date = SelectField('Celebration Date',
        choices=[
            ('tbd', 'Date Not Set (TBD)'),
            ('custom', 'I have a date in mind')
        ],
        default='tbd'
    )
    custom_date = DateField('Custom Date', validators=[Optional()])
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

class AppointmentForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    service_type = SelectField('Service Type', 
        choices=[
            ('bridal_gown', 'Bridal Gown Consultation'),
            ('quinceanera_dress', 'Quinceañera Dress Consultation'),
            ('tuxedo', 'Tuxedo Fitting'),
            ('alterations', 'Alterations'),
            ('planning', 'Event Planning'),
            ('general', 'General Inquiry')
        ],
        validators=[DataRequired()]
    )
    preferred_date = DateTimeField('Preferred Date and Time', 
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired()]
    )
    alternate_date = DateTimeField('Alternate Date and Time', 
        format='%Y-%m-%dT%H:%M',
        validators=[Optional()]
    )
    notes = TextAreaField('Additional Notes', 
        validators=[Optional(), Length(max=500)]
    )