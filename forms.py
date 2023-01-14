from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, FloatField, DateField, validators, SelectField
from wtforms.validators import Email, DataRequired, Length, EqualTo, NumberRange
from werkzeug.security import generate_password_hash, check_password_hash


# class MeterReadingForm(FlaskForm):
#     date = DateField('Submission date', validators=[DataRequired()])
#     electricity_day = FloatField(
#         'Electricity meter reading - Day', validators=[DataRequired(), NumberRange(min=0)])
#     electricity_night = FloatField(
#         'Electricity meter reading - Night', validators=[DataRequired(), NumberRange(min=0)])
#     gas = FloatField('Gas meter reading', validators=[
#                      DataRequired(), NumberRange(min=0)])
#     submit = SubmitField('Submit')


# class RegisterForm(FlaskForm):
#     email = StringField('Email', validators=[
#         DataRequired(), Email()])
#     password = PasswordField('Password', validators=[
#         DataRequired(), Length(min=8, max=20)])
#     confirm_password = PasswordField('Repeat Password', validators=[
#         DataRequired(), EqualTo('password')])
#     address = StringField('Address', validators=[DataRequired()])
#     property_type = SelectField('Property Type', choices=[("detached", "detached"), ("semi-detached", "semi-detached"), ("terraced", "terraced"), ("flat", "flat"), ("cottage", "cottage"), (
#         "bungalow", "bungalow"), ("mansion", "mansion")], validators=[validators.DataRequired(), validators.AnyOf(["detached", "semi-detached", "terraced", "flat", "cottage", "bungalow", "mansion"], message="Invalid property type.")])
#     num_bedrooms = IntegerField('Number of Bedrooms', validators=[
#         DataRequired(), NumberRange(min=1), IsInteger(message="Number of bedrooms must be an integer.")])
#     evc = StringField('Energy Voucher Code', validators=[
#         DataRequired(), validators.AnyOf(valid_evc_codes)])
#     submit = SubmitField('Register')


# class LoginForm(FlaskForm):
#     email = StringField('Email', validators=[DataRequired(), Email()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     submit = SubmitField('Login')
