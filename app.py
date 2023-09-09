from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, get_flashed_messages, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, FloatField, DateField, validators, SelectField, FormField, FieldList, Form, DecimalField
from wtforms.validators import Email, DataRequired, Length, EqualTo, NumberRange
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func


from .validator import IsInteger
import json
from flasgger import Swagger, Schema, fields
from flasgger.utils import swag_from
from flask_restful import Api, Resource


# import from forms.py
# from .forms import RegisterForm, LoginForm, MeterReadingForm
from datetime import datetime, date
from flask_migrate import Migrate
import secrets
import logging

valid_evc_codes = ['XTX2GZAD', 'NDA7SY2V', 'RVA7DZ2D', 'DM8LEESR']

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'iGSE Energy Management System API',
    'uiversion': 3
}
api = Api(app)
swagger = Swagger(app)


app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://api_user:123456@localhost:3306/RestServiceInterface'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False
db = SQLAlchemy(app)

logging.basicConfig(filename='app.log', level=logging.DEBUG)

login_manager = LoginManager()
login_manager.init_app(app)

# migrate
migrate = Migrate(app, db)

# login manager for fetching current user id


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class EnergyConsumption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    reading = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {'customer_id': self.customer_id, 'date': self.date, 'reading': self.reading}


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(150))
    address = db.Column(db.String(100))
    property_type = db.Column(db.String(100))
    num_bedrooms = db.Column(db.Integer)
    # EVC id from EVC table (FOREIGN KEY)
    evc = db.Column(db.Integer, db.ForeignKey('evc.id'))
    energy_credit = db.Column(db.Float, default=200)
    joined_on = db.Column(db.DateTime, default=datetime.utcnow)
    bill = db.relationship('Bill', back_populates='user', lazy=True)
    meter_readings = db.relationship(
        'MeterReading', back_populates='user', lazy=True)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, email, password, address, property_type, num_bedrooms, evc):
        self.email = email
        self.password = password
        self.address = address
        self.property_type = property_type
        self.num_bedrooms = num_bedrooms
        self.evc = evc
        self.energy_credit = 200
        self.is_admin = False

    def __repr__(self):
        return f'{self.email}'

    # set password hash
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # check password hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def validate_evc(self, evc):
        if evc in valid_evc_codes:
            self.energy_credit += 200
        return True

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'address': self.address,
            'property_type': self.property_type,
            'num_bedrooms': self.num_bedrooms,
            'evc': self.evc,
            'energy_credit': self.energy_credit
        }


class Admin(User):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    def __init__(self, email, password, address=None, property_type=None, num_bedrooms=None, evc=None):
        super().__init__(email, password, address, property_type, num_bedrooms, evc)
        self.is_admin = True

    def set_tariffs(self, electricity_day_per_kWh, electricity_night_per_kWh, gas_per_kWh, standing_charge_per_day):
        tariffs = Tariff.query.first()
        if tariffs:
            tariffs.electricity_day_per_kWh = electricity_day_per_kWh
            tariffs.electricity_night_per_kWh = electricity_night_per_kWh
            tariffs.gas_per_kWh = gas_per_kWh
            tariffs.standing_charge_per_day = standing_charge_per_day
        else:
            tariffs = Tariff(electricity_day_per_kWh=electricity_day_per_kWh, electricity_night_per_kWh=electricity_night_per_kWh,
                             gas_per_kWh=gas_per_kWh, standing_charge_per_day=standing_charge_per_day)
            db.session.add(tariffs)
        db.session.commit()

    def view_meter_readings(self):
        meter_readings = MeterReading.query.all()
        return meter_readings

    def view_energy_statistics(self):
        # code to calculate average gas and electricity consumption
        pass


class EVC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    evc = db.Column(db.String(8), unique=True, nullable=False)
    credit = db.Column(db.Float, default=200)
    used_by = db.relationship("User", backref="evc_code", lazy=True)
    topup_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, evc):
        self.evc = evc

    def __repr__(self):
        return f'{self.evc}'

    def to_dict(self):
        return {'evc': self.evc}


class Tariff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tariff_name = db.Column(db.String(100), unique=True, nullable=False)
    electricity_day_per_kWh = db.Column(db.Float, nullable=False)
    electricity_night_per_kWh = db.Column(db.Float, nullable=False)
    gas_per_kWh = db.Column(db.Float, nullable=False)
    standing_charge_per_day = db.Column(db.Float, nullable=False)

    def __init__(self, tariff_name, electricity_day_per_kWh, electricity_night_per_kWh, gas_per_kWh, standing_charge_per_day):
        self.tariff_name = tariff_name
        self.electricity_day_per_kWh = electricity_day_per_kWh
        self.electricity_night_per_kWh = electricity_night_per_kWh
        self.gas_per_kWh = gas_per_kWh
        self.standing_charge_per_day = standing_charge_per_day

    def __repr__(self):
        return f'{self.tariff_name}'

    def to_dict(self):
        return {
            'tariff_name': self.tariff_name,
            'electricity_day_per_kWh': self.electricity_day_per_kWh,
            'electricity_night_per_kWh': self.electricity_night_per_kWh,
            'gas_per_kWh': self.gas_per_kWh,
            'standing_charge_per_day': self.standing_charge_per_day
        }


class MeterReading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False, )
    user = db.relationship("User", back_populates="meter_readings")
    # date format YYYY-MM-DD and by default make it today's date
    date = db.Column(db.Date, nullable=False, default=datetime.today())
    electricity_day = db.Column(db.Float, nullable=False)
    electricity_night = db.Column(db.Float, nullable=False)
    gas = db.Column(db.Float, nullable=False)

    def __init__(self, customer_id, date, electricity_day, electricity_night, gas):
        self.customer_id = customer_id
        self.date = date
        self.electricity_day = electricity_day
        self.electricity_night = electricity_night
        self.gas = gas

    def __repr__(self):
        return f'{self.customer_id}'

    def validate_meter_reading(self, meter_reading):
        # check if meter reading is greater than 0
        if meter_reading['electricity_day'] < 0 or meter_reading['electricity_night'] < 0 or meter_reading['gas'] < 0:
            return False
        return True

    def to_dict(self):
        return {
            'customer_id': self.customer_id,
            'date': self.date,
            'electricity_day': self.electricity_day,
            'electricity_night': self.electricity_night,
            'gas': self.gas
        }


class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # customer_id = db.Column(db.Integer, nullable=False)
    customer_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship("User", back_populates="bill")
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    electricity_day_reading = db.Column(db.Float, nullable=False)
    electricity_night_reading = db.Column(db.Float, nullable=False)
    gas_reading = db.Column(db.Float, nullable=False)
    bill_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime)
    is_paid = db.Column(db.Boolean, default=False)

    def __init__(self, customer_id, start_date, end_date, electricity_day_reading, electricity_night_reading, gas_reading, bill_amount):
        self.customer_id = customer_id
        self.start_date = start_date
        self.end_date = end_date
        self.electricity_day_reading = electricity_day_reading
        self.electricity_night_reading = electricity_night_reading
        self.gas_reading = gas_reading
        self.bill_amount = bill_amount

    # def calculate_bill(customer_id, date):
    #     # Retrieve the latest meter reading for the customer
    #     latest_reading = MeterReading.query.filter_by(
    #         customer_id=customer_id, date=date).first()

    #     # Retrieve the previous meter reading for the customer
    #     previous_reading = MeterReading.query.filter(
    #         MeterReading.customer_id == customer_id, MeterReading.date < date).order_by(MeterReading.date.desc()).first()

    #     # Calculate the number of units used
    #     electricity_day_used = latest_reading.electricity_day - \
    #         previous_reading.electricity_day
    #     electricity_night_used = latest_reading.electricity_night - \
    #         previous_reading.electricity_night
    #     gas_used = latest_reading.gas - previous_reading.gas

    #     # Retrieve tariffs or set as constants
    #     electricity_day_tariff = 0.34
    #     electricity_night_tariff = 0.2
    #     gas_tariff = 0.1
    #     standing_charge = 0.74

    #     # Calculate the bill
    #     bill_amount = (electricity_day_used * electricity_day_tariff) + \
    #         (electricity_night_used * electricity_night_tariff) + \
    #         (gas_used * gas_tariff)

    #     # Add the standing charge
    #     bill_amount += standing_charge * \
    #         (latest_reading.date - previous_reading.date).days

    #     return bill_amount

    def create_bill(customer_id, date):
        # Retrieve the latest meter reading for the customer
        latest_reading = MeterReading.query.filter_by(
            customer_id=current_user.id).order_by(MeterReading.date.desc()).first()

        # Retrieve the previous meter reading for the customer
        previous_reading = MeterReading.query.filter(
            MeterReading.customer_id == current_user.id, MeterReading.date < latest_reading.date).order_by(MeterReading.date.desc()).first()

        # Retrieve the tariffs
        tariffs = Tariff.query.first()
        if not tariffs:
            # If there are no tariffs in the database, set them as constants
            electricity_day_tariff = 0.34
            electricity_night_tariff = 0.2
            gas_tariff = 0.1
            standing_charge = 0.74
        else:
            # If there are tariffs in the database, use those
            electricity_day_tariff = tariffs.electricity_day_per_kWh
            electricity_night_tariff = tariffs.electricity_night_per_kWh
            gas_tariff = tariffs.gas_per_kWh
            standing_charge = tariffs.standing_charge_per_day

         # Check if the previous bill is paid
        # previous_bill = Bill.query.filter_by(
        #     customer_id=customer_id, is_paid=False).order_by(Bill.created_at.desc()).first()
        # if previous_bill:
        #     # Deduct the unpaid amount from the customer's energy credit
        #     user = User.query.filter_by(id=customer_id).first()
        #     user.energy_credit -= previous_bill.bill_amount

        #     # Update the previous bill's payment status to paid
        #     previous_bill.is_paid = True
        #     previous_bill.paid_at = datetime.utcnow()
        #     db.session.commit()

        # Calculate the number of units used
        electricity_day_used = latest_reading.electricity_day - \
            previous_reading.electricity_day
        electricity_night_used = latest_reading.electricity_night - \
            previous_reading.electricity_night
        gas_used = latest_reading.gas - previous_reading.gas

        # Calculate the bill
        bill_amount = (electricity_day_used * electricity_day_tariff) + \
            (electricity_night_used * electricity_night_tariff) + \
            (gas_used * gas_tariff)

        # Add the standing charge
        bill_amount += standing_charge * \
            (latest_reading.date - previous_reading.date).days

       # retrieve the current user
        user = User.query.filter_by(id=current_user.id).first()
        # check if the previous bill is paid or not
        bill = Bill.query.filter_by(
            customer_id=current_user.id, is_paid=False).first()
        if bill:
            # if previous bill is not paid, deduct the bill amount from the user's energy credit
            flash('You have an unpaid bill, Please pay the bill first')
            return redirect(url_for('view_latest_bill'))
        # check if user have sufficient energy credit to pay the bill
        # if user.energy_credit >= bill_amount:
        #     # if user have sufficient energy credit, deduct the bill amount from the user's energy credit
        #     user.energy_credit -= bill_amount
        #     db.session.commit()
        #     flash('Bill paid successfully')
            # create the new bill
        bill = Bill(customer_id=current_user.id, start_date=previous_reading.date, end_date=latest_reading.date,
                    electricity_day_reading=electricity_day_used, electricity_night_reading=electricity_night_used, gas_reading=gas_used, bill_amount=bill_amount)
        db.session.add(bill)
        db.session.commit()
        flash('Bill created successfully')
        return redirect(url_for('view_latest_bill'))

# ==========---------- Tariff Form class ----------==========


class TariffForm(FlaskForm):
    electricity_day_per_kWh = DecimalField(
        'Electricity Day per kWh', validators=[DataRequired()])
    electricity_night_per_kWh = DecimalField(
        'Electricity Night per kWh', validators=[DataRequired()])
    gas_per_kWh = DecimalField('Gas per kWh', validators=[DataRequired()])
    standing_charge_per_day = DecimalField(
        'Standing Charge per day', validators=[DataRequired()])
    submit = SubmitField('Submit')


class MeterReadingForm(FlaskForm):
    # date = DateField('Submission date', validators=[DataRequired()])

    # i want to make date YYYY-MM-DD and by default make it today's date
    date = DateField('Submission date', format='%Y-%m-%d',
                     default=datetime.today())
    electricity_day = FloatField(
        'Electricity meter reading - Day', validators=[DataRequired(), NumberRange(min=0)])
    electricity_night = FloatField(
        'Electricity meter reading - Night', validators=[DataRequired(), NumberRange(min=0)])
    gas = FloatField('Gas meter reading', validators=[
        DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Submit')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(), Length(min=8, max=20)])
    confirm_password = PasswordField('Repeat Password', validators=[
        DataRequired(), EqualTo('password')])
    address = StringField('Address', validators=[DataRequired()])
    property_type = SelectField('Property Type', choices=[("detached", "detached"), ("semi-detached", "semi-detached"), ("terraced", "terraced"), ("flat", "flat"), ("cottage", "cottage"), (
        "bungalow", "bungalow"), ("mansion", "mansion")], validators=[validators.DataRequired(), validators.AnyOf(["detached", "semi-detached", "terraced", "flat", "cottage", "bungalow", "mansion"], message="Invalid property type.")])
    num_bedrooms = IntegerField('Number of Bedrooms', validators=[
        DataRequired(), NumberRange(min=1), IsInteger(message="Number of bedrooms must be an integer.")])
    evc = StringField('Energy Voucher Code', validators=[
        DataRequired(), validators.AnyOf(valid_evc_codes)])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class AdminRegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')


class AdminLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class TopUpForm(FlaskForm):
    # my token is a string of 8 digits
    evc = StringField('evc', validators=[
        DataRequired(), Length(min=8, max=8)])
    submit = SubmitField('Top Up')


@app.route('/register', methods=['GET', 'POST'], endpoint='register')
@swag_from('api/docs/register.yml', endpoint='register')
def register():
    """ Register a new user
    A new user can register by providing their email, password, address, property type, number of bedrooms and energy voucher code.
    """
    # // i will make ajax call to this route
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = RegisterForm()
        print("ajax call")
        # print form with tokens
        print(form.csrf_token)
        # print all form
        print(form.data)
        if not form.validate():
            return jsonify(success=False, email_error=form.email.errors, password_error=form.password.errors,
                           confirm_password_error=form.confirm_password.errors, address_error=form.address.errors,
                           property_type_error=form.property_type.errors, num_bedrooms_error=form.num_bedrooms.errors,
                           evc_error=form.evc.errors)

        if form.validate_on_submit():
            print("form validated")
            email = request.form.get('email')
            user = User.query.filter_by(email=email).first()
            if user:
                return jsonify({'status': 'error', 'message': 'Email address already exists'})
            else:
                return jsonify({'status': 'success', 'message': 'Email address is available'})

            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            print("password", password)
            print("confirm_password", confirm_password)
            if password != confirm_password:
                return jsonify({'status': 'error', 'message': 'Passwords do not match'})

            address = request.form.get('address')
            property_type = request.form.get('property_type')
            num_bedrooms = request.form.get('num_bedrooms')
            if not num_bedrooms.isdigit():
                return jsonify({'status': 'error', 'message': 'Number of bedrooms must be an integer.'})
            evc = request.form.get('evc')
            if evc not in valid_evc_codes:
                return jsonify({'status': 'error', 'message': 'Invalid energy voucher code.'})

            evc_code = EVCCode.query.filter_by(code=evc).first()
            if evc_code:
                return jsonify({'status': 'error', 'message': 'Energy voucher code has already been used.'})

            new_evc_code = EVC(evc=evc)
            db.session.add(new_evc_code)
            db.session.commit()
            user = User(email=email, password=password, address=address,
                        property_type=property_type, num_bedrooms=num_bedrooms, evc=new_evc_code.id)
            user.set_password(password)
            try:
                db.session.add(user)
                db.session.commit()
                flash('User created successfully')
                return redirect(url_for('login'))
            except IntegrityError as e:
                db.session.rollback()
                return jsonify({'status': 'error', 'message': 'Email address already exists'})
        else:
            return jsonify({'status': 'error', 'message': 'Form not validated'})
        # // get evc code from db and check if it exists
        # // if it exists, check if it has been used
    else:

        form = RegisterForm()
        print(form.errors)
        print(form.data)
        print(form)
        print("Register page")
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            address = form.address.data
            property_type = form.property_type.data
            num_bedrooms = int(form.num_bedrooms.data)
            evc = form.evc.data
            print("Form validated")
            try:
                user = User.query.filter_by(email=email).first()
                print("User found 1")
                if user:
                    # render the error saying the email already exists
                    form.email.errors.append("Email address already exists")
                    flash('Email address already exists')
                    return render_template('register.html', form=form)
            except:
                pass
            try:
                user = User.query.filter_by(evc=evc).first()
                if request.form['evc'] not in valid_evc_codes:
                    form.evc.errors.append("Invalid EVC voucher code")
                    flash('Invalid EVC')
                    return render_template('register.html', form=form)
            except:
                pass

            evc_code = EVC.query.filter_by(evc=evc).first()
            if evc_code:
                form.evc.errors.append("EVC code already used")
                flash('EVC code already used')
                return render_template('register.html', form=form)

            new_evc_code = EVC(evc=evc)
            db.session.add(new_evc_code)
            db.session.commit()
            user = User(email=email, password=password, address=address,
                        property_type=property_type, num_bedrooms=num_bedrooms, evc=new_evc_code.id)
            user.set_password(password)

            try:
                db.session.add(user)
                db.session.commit()
                flash('User created successfully')
                return redirect(url_for('login', type='success'))
            except IntegrityError as e:
                form.email.errors.append("Email address already exists")
                db.session.rollback()
                return render_template('register.html', form=form)
        else:
            # // print out the errors
            print(form.errors)
            print(form.errors.items())
            logging.debug(f'Form not valid')
            print("Form not valid - else clause")
    # return the form with the errors and bound data
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'], endpoint='login')
@swag_from("api/docs/login.yml", endpoint='login')
def login():
    """ Login page
    A user can login to the system using their email address and password.
    """
    form = LoginForm()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'POST':
            if form.validate_on_submit():
                email = form.email.data
                password = form.password.data
                user = User.query.filter_by(email=email).first()
                if user is None:
                    return jsonify(success=False, message='User does not exist', type='danger')
                if user is not None and not user.check_password(password):
                    return jsonify(success=False, message='Invalid email or password', type='danger')
                if user is not None and user.check_password(password):
                    login_user(user)
                    session['user'] = json.dumps(user.to_dict())
                    flash("You are logged in!")
                    return jsonify(success=True, message='You are logged in!', type='success')
            # fetch the error from the form.errors dictionary
            message = form.errors
            errors = []
            for key, value in message.items():
                errors.append(value[0])
            return jsonify(success=False, errors=errors, type='danger')
        return redirect(url_for('profile'))
    if request.method == 'POST':
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            user = User.query.filter_by(email=email).first()
            if user is not None and user.check_password(password):
                login_user(user)
                next_page = request.args.get('profile')
                session['user'] = json.dumps(user.to_dict())
                flash("You are logged in!")
                return redirect(url_for('profile'))
            if user is None:
                flash("User does not exist")
                form.email.errors.append("User does not exist")
                return render_template('login.html', form=form, type='danger')
            if user is not None and not user.check_password(password):
                flash("Invalid email or password")
                form.email.errors.append("Invalid email or password")
                return render_template('login.html', form=form, type='danger')
        else:
            print(form.errors)
            print(form.errors.items())
            logging.debug(f'Form not valid')
            print("Form not valid - else clause")
    return render_template('login.html', form=form)


@app.route('/reset-password', methods=['GET', 'POST'], endpoint='reset_password')
def reset_password():
    """ Reset password page
    A user can reset their password using their email address.
    ___
    tags:
        - Password Reset
    parameters:
        - name: email
          in: query
          type: string
          required: true
          description: The email address of the user
    responses:
        200:
            description: The password has been reset
        400:
            description: The email address is not valid
    """
    if request.method == 'POST':
        # Get the username and new password from the form
        username = request.form['username']
        new_password = request.form['new_password']

        # Hash the new password
        hashed_password = generate_password_hash(new_password)

        # Update the user's password in the database
        # Replace 'users', 'password_hash', and 'email' with the actual names of your table and columns
        sql = "UPDATE users SET password_hash = %s WHERE email = %s"
        db.engine.execute(sql, (hashed_password, username))

        flash('Your password has been reset.')
        return redirect(url_for('login'))

    return render_template('reset_password.html')


@app.route('/profile', methods=['GET'], endpoint='profile')
@login_required
# @swag_from("api/docs/profile.yml", endpoint='profile')
def profile():
    """ Profile page
    A user can view their profile page.
    """
    if current_user.is_authenticated:
        user = json.loads(session['user'])
    else:
        flash("You are not logged in")
        return redirect(url_for('login'))
    return render_template('profile.html', user=user)


@app.route('/logout', methods=['GET'], endpoint='logout')
@swag_from("api/docs/logout.yml", endpoint='logout')
def logout():
    """ Logout page
    A user can logout of the system.
    """
    if current_user.is_authenticated:
        logout_user()
        session.pop('user_id', None)
        flash("You are logged out!")
    return redirect(url_for('index'))


# @app.route('/', methods=['GET'])
# def index():
#     return render_template('index.html')

@ app.route('/home', methods=['GET'], endpoint='index')
def index():
    """ Home page
    A user can view the home page.
    ---
    tags:
        - Home
    responses:
        200:
            description: Home page
    """

    # get flash messages
    messages = get_flashed_messages()
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    return render_template('index.html', messages=messages)


@ app.route('/', methods=['GET'])
def root():
    """ Root page
    A user can view the root page.
    ---
    tags:
        - Root
    responses:
        200:
            description: Root page
    """

    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    return redirect(url_for('index'))


@ app.route('/submit-meter-reading', methods=['GET', 'POST'], endpoint='submit_meter_reading')
@ login_required
def submit_meter_reading():
    """ Submit meter reading page
    A user can submit their meter readings.
    ---
    tags:
        - Submit meter reading
    responses:
        200:
            description: Submit meter reading page
    """

    if current_user.is_authenticated:
        form = MeterReadingForm()
        print(form.errors)
        print(form.data)
        print(form)
        if form.validate_on_submit():
            date = form.date.data
            electricity_day = form.electricity_day.data
            electricity_night = form.electricity_night.data
            gas = form.gas.data
            # get the current user id
            user_id = current_user.id
            meter_reading = MeterReading(customer_id=user_id, date=date, electricity_day=electricity_day,
                                         electricity_night=electricity_night, gas=gas)
            try:
                db.session.add(meter_reading)
                db.session.commit()
                print("Meter reading added")
                flash('Meter readings submitted successfully')
                # call the function to calculate the meter readings
                # Retrieve the latest and previous meter readings

                latest_reading = MeterReading.query.filter_by(
                    customer_id=user_id, date=date).first()
                previous_reading = MeterReading.query.filter(
                    MeterReading.customer_id == user_id, MeterReading.date < date).order_by(MeterReading.date.desc()).first()
                if previous_reading:
                    # Calculate the energy consumption
                    # Create a new bill
                    Bill.create_bill(user_id, date)

                    flash('Bill created successfully')
                    return redirect(url_for('view_latest_bill'))
                else:
                    flash('No previous meter readings found')
                    return redirect(url_for('index'))
            except IntegrityError as e:
                print("Meter reading not added")
                db.session.rollback()
                return render_template('submit_meter_reading.html', form=form)
            # Your code to save the meter readings to the database
            flash('Meter readings submitted successfully')
            return redirect(url_for('profile'))
        else:
            print(form.errors)
            print(form.errors.items())
            logging.debug(f'Form not valid')
            print("Form not valid - else clause")
    else:
        flash("You are not logged in")
        return redirect(url_for('login'))
    return render_template('submit_meter_reading.html', form=form)


@ app.route('/energy-consumption', methods=['GET'], endpoint='energy_consumption')
def get_energy_consumption():
    """ Energy consumption page
    A user can view their energy consumption.
    ---
    tags:
        - Energy consumption
    responses:
        200:
            description: Energy consumption page
    """

    if current_user.is_authenticated:
        customer_id = request.args.get('customer_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        query = EnergyConsumption.query
        if customer_id:
            query = query.filter(EnergyConsumption.customer_id == customer_id)
        if start_date:
            query = query.filter(EnergyConsumption.date >= start_date)
        if end_date:
            query = query.filter(EnergyConsumption.date <= end_date)
        energy_consumption = query.all()
    else:
        flash("You are not logged in")
        return redirect(url_for('login'))
    return jsonify([energy_consumption.to_dict() for energy_consumption in energy_consumption])


@ app.route('/view_latest_bill', methods=['GET'], endpoint='view_latest_bill')
@ login_required
def view_latest_bill():
    """ View latest bill page
    A user can view their latest bill.
    ---
    tags:
        - View latest bill
    responses:
        200:
            description: View latest bill page
    """

    if current_user.is_authenticated:
        messages = get_flashed_messages()
        latest_bill = Bill.query.filter_by(
            customer_id=current_user.id, is_paid=False).first()

        print(latest_bill)
        if latest_bill:
            return render_template('view_bill.html', bill=latest_bill, messages=messages)
        else:
            flash('No unpaid bills found.')
            return redirect(url_for('index'))
    else:
        flash("You are not logged in")
        return redirect(url_for('login'))
    return render_template('view_bill.html', bill=latest_bill, messages=messages)


@ app.route('/pay_bill/<int:bill_id>', methods=['GET'], endpoint='pay_bill')
@ login_required
def pay_bill(bill_id):
    """ Pay bill page
    A user can pay their bill.
    ---
    tags:
        - Pay bill
    responses:
        200:
            description: Pay bill page
    """

    if current_user.is_authenticated:
        bill = Bill.query.filter_by(id=bill_id).first()
        if not bill:
            flash('Bill not found', 'danger')
            return redirect(url_for('view_latest_bill', type='danger'))
        if bill.customer_id != current_user.id:
            flash('Unauthorized access', 'danger')
            return redirect(url_for('view_latest_bill', type='danger'))
        if bill.is_paid:
            flash('Bill already paid', 'info')
            return redirect(url_for('view_latest_bill', type='info'))

        if current_user.energy_credit < bill.bill_amount:
            flash('Not enough credit to pay the bill', 'danger')
            return redirect(url_for('view_latest_bill'))
        current_user.energy_credit -= bill.bill_amount
        bill.is_paid = True
        bill.paid_at = datetime.utcnow()
        db.session.commit()
        flash('Bill paid successfully', 'success')
    else:
        flash("You are not logged in")
        return redirect(url_for('login'))
    return redirect(url_for('view_latest_bill', type='success'))


# top-up
@ app.route('/top-up', methods=['GET', 'POST'], endpoint='top_up')
@ login_required
def top_up():
    """ Top up page
    A user can top up their energy credit.
    ---
    tags:
        - Top up
    responses:
        200:
            description: Top up page
    """

    if current_user.is_authenticated:
        form = TopUpForm()
        if form.validate_on_submit():
            current_voucher = form.evc.data

            if current_voucher not in valid_evc_codes:
                form.evc.errors.append("Invalid EVC voucher code")
                flash('Invalid EVC')
                return render_template('top_up.html', form=form)
            # check if voucher is valid
            all_vouchers = EVC.query.all()
            voucher = EVC.query.filter_by(evc=current_voucher).first()
            if voucher:
                flash('Invalid voucher', 'danger')
                form.evc.errors.append('Invalid voucher - already used')
                return render_template('top_up.html', form=form)

            new_evc_code = EVC(evc=current_voucher)
            db.session.add(new_evc_code)
            db.session.commit()
            # add credit to user
            current_user.energy_credit += new_evc_code.credit
            db.session.commit()
            flash('Top up successful', 'success')
            # send success text
            session.message = "Top up successful"
            return redirect(url_for('index'))
    else:
        flash("You are not logged in")
        return redirect(url_for('login'))
    return render_template('top_up.html', form=form)


# =============------------- Admin Page -----------------==================
@ app.route('/admin/register', methods=['GET', 'POST'], endpoint='admin_register')
def admin_register():
    """ Admin register page
    An admin can register a new admin.
    ---
    tags:
        - Admin register
    responses:
        200:
            description: Admin register page
    """

    messages = get_flashed_messages()
    print("Admin register")
    # if current_user.is_authenticated:
    #     print("User is authenticated")
    #     flash("You are already logged in")
    #     return redirect(url_for('admin_dashboard'))

    form = AdminRegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            print("Form is validated")
            email = form.email.data
            password = form.password.data
            if email != "gse@shangrila.gov.un":
                flash('Invalid admin email. I will update with default admin email')
                email = "gse@shangrila.gov.un"
            if password != "gse@energy":
                flash('Invalid password. I am updating with default password')
                password = "gse@energy"
            if Admin.query.filter_by(email=email).first():
                flash('Admin account already exists')
                return redirect(url_for('admin_login'))
            admin = Admin(email=email, password=password)
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            flash('You are now a registered admin!')
            return redirect(url_for('admin_dashboard'))
    else:
        print("Form is not validated")
        return render_template('admin_register.html', form=form, messages=messages)
    return render_template('admin_register.html', form=form, messages=messages)


@ app.route('/admin/login', methods=['GET', 'POST'], endpoint='admin_login')
def admin_login():
    """ Admin login page
    An admin can login.
    ---
    tags:
        - Admin login
    responses:
        200:
            description: Admin login page
    """

    # if current_user.is_admin:
    #     return redirect(url_for('admin_dashboard'))
    # else:
    #     flash('You are not an admin')
    #     return redirect(url_for('index'))

    messages = get_flashed_messages()
    form = AdminLoginForm()
    print(form, "messages")
    # print all data from form
    print(form.email.data, "email")
    print(form.password.data, "password")
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        admin = Admin.query.filter_by(email=email).first()
        if admin is None:
            flash(
                f'This {email} is not registered as an admin. Please register first.')
            return redirect(url_for('admin_register'))
        if admin and admin.check_password(password):
            login_user(admin)
            flash('You are now logged in as admin.')
            print('You are now logged in as admin.')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password.')
    return render_template('admin_login.html', form=form, messages=messages)


@ app.route('/admin', endpoint='admin_dashboard')
def admin_dashboard():
    """ Admin dashboard page
    An admin can view the admin dashboard.
    ---
    tags:
        - Admin dashboard
    responses:
        200:
            description: Admin dashboard page
    """

    if not current_user.is_authenticated:
        flash('You must be logged in to access this page.')
        return redirect(url_for('admin_login'))
    if not current_user.is_admin:
        flash('You must be an admin to access this page.')
        return redirect(url_for('index'))
    messages = get_flashed_messages()
    print("checking if admin is logged in")
    if current_user.is_authenticated and current_user.is_admin:
        print('You are now logged in as admin.')
        return render_template('admin_dashboard.html', messages=messages)
    else:
        flash('You need to login as an admin first.')
        return redirect(url_for('admin_login', messages=messages))

# admin logout


@ app.route('/admin/logout', endpoint='admin_logout')
def admin_logout():
    """ Admin logout page
    An admin can logout.
    ---
    tags:
        - Admin logout
    responses:
        200:
            description: Admin logout page
    """

    logout_user()
    flash('You are now logged out.')
    return redirect(url_for('index'))


@ app.route('/admin/set-tariffs', methods=['GET', 'POST'], endpoint='set_tariffs')
@ login_required
def set_tariffs():
    """ Admin set tariffs page
    An admin can set tariffs.
    ---
    tags:
        - Admin set tariffs
    responses:
        200:
            description: Admin set tariffs page
    """

    if not current_user.is_authenticated:
        flash('You must be logged in to access this page.')
        return redirect(url_for('admin_login'))
    if not current_user.is_admin:

        return redirect(url_for('index'))
    if not current_user.is_admin:
        flash('You must be an admin to access this page.')
        return redirect(url_for('index'))
    form = TariffForm()
    if form.validate_on_submit():
        electricity_day_per_kWh = form.electricity_day_per_kWh.data
        electricity_night_per_kWh = form.electricity_night_per_kWh.data
        gas_per_kWh = form.gas_per_kWh.data
        standing_charge_per_day = form.standing_charge_per_day.data
        tariffs = Tariff.query.first()
        if tariffs:
            tariffs.electricity_day_per_kWh = electricity_day_per_kWh
            tariffs.electricity_night_per_kWh = electricity_night_per_kWh
            tariffs.gas_per_kWh = gas_per_kWh
            tariffs.standing_charge_per_day = standing_charge_per_day
        else:
            tariffs = Tariff(electricity_day_per_kWh=electricity_day_per_kWh,
                             electricity_night_per_kWh=electricity_night_per_kWh,
                             gas_per_kWh=gas_per_kWh,
                             standing_charge_per_day=standing_charge_per_day)
            db.session.add(tariffs)
        db.session.commit()
        flash('Tariffs set successfully')
        return redirect(url_for('admin_dashboard'))
    return render_template('set_tariffs.html', form=form)


@ app.route('/admin/bills', endpoint='admin_view_bills')
@ login_required
def admin_view_bills():
    """ Admin view bills page
    An admin can view bills.
    ---
    tags:
        - Admin view bills
    responses:
        200:
            description: Admin view bills page
    """

    if not current_user.is_authenticated:
        flash('You must be logged in to access this page.')
        return redirect(url_for('admin_login'))

    if not current_user.is_admin:
        flash('You must be an admin to access this page.')
        return redirect(url_for('index'))

    # check if there is parameter in url
    if request.args.get('bill_id'):
        bill_id = request.args.get('bill_id')
        bill = Bill.query.get_or_404(bill_id)
        return render_template('admin_view_bill.html', bill=bill)
    bills = Bill.query.all()
    return render_template('admin_view_bills.html', bills=bills)

# get the specific bill


@ app.route('/admin/bills/<int:bill_id>', endpoint='admin_view_bill')
@ login_required
def admin_view_bill(bill_id):
    """ Admin view bill page
    An admin can view a bill.
    ---
    tags:
        - Admin view bill
    responses:
        200:
            description: Admin view bill page
    """

    if not current_user.is_authenticated:
        flash('You must be logged in to access this page.')
        return redirect(url_for('admin_login'))
    if not current_user.is_admin:
        flash('You must be an admin to access this page.')
        return redirect(url_for('index'))
    bill = Bill.query.get_or_404(bill_id)
    return render_template('admin_view_bill.html', bill=bill)


# view all submitted meter readings
@ app.route('/admin/meter-readings', endpoint='admin_view_meter_readings')
@ login_required
def admin_view_meter_readings():
    """ Admin view meter readings page
    An admin can view meter readings.
    ---
    tags:
        - Admin view meter readings
    responses:
        200:
            description: Admin view meter readings page
    """

    if not current_user.is_authenticated:
        flash('You must be logged in to access this page.')
        return redirect(url_for('admin_login'))
    if not current_user.is_admin:
        flash('You must be an admin to access this page.')
        return redirect(url_for('index'))
    meter_readings = MeterReading.query.all()
    return render_template('admin_view_meter_readings.html', meter_readings=meter_readings)

# getting the  "Admin can view the energy statistics– show the average gas and electricity consumption (in kWh) per day for all customers based on their latest billing period."


@ app.route('/admin/energy-statistics', endpoint='admin_energy_statistics')
@ login_required
def admin_energy_statistics():
    """ Admin energy statistics page
    An admin can view energy statistics.
    ---
    tags:
        - Admin energy statistics
    responses:
        200:
            description: Admin energy statistics page
    """

    if not current_user.is_authenticated:
        flash('You must be logged in to access this page.')
        return redirect(url_for('admin_login'))
    if not current_user.is_admin:
        flash('You must be an admin to access this page.')
        return redirect(url_for('index'))
    bills = Bill.query.all()
    electricity_day_per_kWh = 0
    electricity_night_per_kWh = 0
    gas_per_kWh = 0
    standing_charge_per_day = 0
    for bill in bills:
        electricity_day_per_kWh += bill.electricity_day_reading
        electricity_night_per_kWh += bill.electricity_night_reading
        gas_per_kWh += bill.gas_reading
        # standing_charge_per_day += bill.standing_charge_per_day
    try:
        electricity_day_per_kWh = electricity_day_per_kWh / len(bills)
        electricity_night_per_kWh = electricity_night_per_kWh / len(bills)
        gas_per_kWh = gas_per_kWh / len(bills)
        print(len(bills))
        print(electricity_day_per_kWh)
        print(electricity_night_per_kWh)
        print(gas_per_kWh)

    except ZeroDivisionError:
        electricity_day_per_kWh = 0
        electricity_night_per_kWh = 0
        gas_per_kWh = 0
        return render_template('admin_energy_statistics.html', electricity_day_per_kWh=electricity_day_per_kWh, electricity_night_per_kWh=electricity_night_per_kWh, gas_per_kWh=gas_per_kWh, standing_charge_per_day=standing_charge_per_day)

    # standing_charge_per_day = standing_charge_per_day / len(bills)
    return render_template('admin_energy_statistics.html', electricity_day_per_kWh=electricity_day_per_kWh, electricity_night_per_kWh=electricity_night_per_kWh, gas_per_kWh=gas_per_kWh, standing_charge_per_day=standing_charge_per_day)


# ====------- Task 2 API -------====
@ app.route('/igse/propertycount', methods=['GET'], endpoint='get_property_count')
def get_property_count():
    """ Get property count
    An admin can view the number of properties of each type.
    ---
    tags:
        - Get property count
    responses:
        200:
            description: Get property count
    """

    if request.method == 'GET':
        print('get_property_count')
        # Query the database to group properties by type and count the number of properties in each group
        property_count = db.session.query(User.property_type, func.count(User.property_type)) \
            .filter(User.property_type != None) \
            .group_by(User.property_type) \
            .all()

        # Create a list to hold the property count data
        data = []

        # Loop through the property count data and add it to the list in the desired format
        for item in property_count:
            data.append({item[0]: item[1]})
            print(item[0])

    # Return the data in JSON format
    return jsonify(data)


@ app.route("/igse/<property_type>/<num_bedrooms>", methods=['GET'], endpoint='get_energy_usage_stats')
def energy_usage_stats(property_type, num_bedrooms):
    """ Get energy usage stats
    An admin can view the average energy usage per day for all customers based on their latest billing period.
    ---
    tags:
        - Get energy usage stats
    responses:
        200:
            description: Get energy usage stats
    """

    try:
        # Join the User and Bill tables and filter by property_type and num_bedrooms
        user_bills = db.session.query(User, Bill).join(Bill).filter(
            User.property_type == property_type, User.num_bedrooms == num_bedrooms).all()
        if not user_bills:
            raise ValueError(
                "No bills found for the specified property type and number of bedrooms.")
        total_electricity_gas_cost = 0
        num_bills = 0
        for user, bill in user_bills:
            # Calculate the number of days between the start and end date of the bill
            num_days = (bill.end_date - bill.start_date).days
            # Add the bill amount to the total cost
            total_electricity_gas_cost += bill.bill_amount
            num_bills += 1
        if num_bills == 0:
            raise ValueError(
                "No bills found for the specified property type and number of bedrooms.")
        try:
            # Divide the total cost by the number of days to get the average cost per day
            average_electricity_gas_cost_per_day = total_electricity_gas_cost / num_bills
        except ZeroDivisionError:
            average_electricity_gas_cost_per_day = 0

    except Exception as e:
        return jsonify({"error": "An unknown error occurred. Please try again later."})

    # Return the energy usage statistics in a JSON response
    return jsonify(
        {"type": property_type,
         "bedroom": num_bedrooms,
         "average_electricity_gas_cost_per_day": average_electricity_gas_cost_per_day,
         "unit": "pound"}
    )


@ app.route('/check_email', methods=['POST'], endpoint='check_email')
def check_email():
    """ Check email
    Check if email already exists in the database.
    ---
    tags:
        - Check email
    responses:
        200:
            description: Check email
        400:
            description: Email already exists

    parameters:
        - name: email
          in: formData
          type: string
          required: true
    definitions:
        exists:
            type: boolean
            description: True if email exists in the database, false otherwise

    """

    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify(exists=True)
    else:
        return jsonify(exists=False)

# check evc code is valid


@ app.route('/check_evc_code', methods=['POST'], endpoint='check_evc_code')
def check_evc_code():
    """ Check EVC code
    Check if EVC code is valid.
    ---
    tags:
        - Check EVC code
    responses:
        200:
            description: Check EVC code
        400:
            description: EVC code is invalid
    parameters:
        - name: energy_voucher_code
          in: formData
          type: string
          required: true
    definitions:
        exists:
            type: boolean
            description: True if EVC code exists in the database, false otherwise

    """
    evc_code = request.form.get('energy_voucher_code')
    print(evc_code)
    # check if evc code is valid in the evc table
    evc = EVC.query.filter_by(evc=evc_code).first()
    if evc is not None and evc.evc == evc_code:
        print('user exists')
        return jsonify(exists=True, message='EVC code is already used')
    if evc_code not in valid_evc_codes:
        return jsonify(not_valid_code=True, message='EVC code is invalid')


if __name__ == '__main__':
    # with open('openapi.json', 'w') as f:
    #     f.write(openapi.json())
    db.create_all()
    app.run(
        debug=False  # Allow verbose error reports
    )
