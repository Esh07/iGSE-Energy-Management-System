from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, get_flashed_messages, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, FloatField, DateField, validators, SelectField, FormField, FieldList, Form, DecimalField
from wtforms.validators import Email, DataRequired, Length, EqualTo, NumberRange
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError

from .validator import IsInteger
import json

# import from forms.py
# from .forms import RegisterForm, LoginForm, MeterReadingForm

from flask import session
from datetime import datetime, date
from flask_migrate import Migrate
import secrets
import logging

valid_evc_codes = ['XTX2GZAD', 'NDA7SY2V', 'RVA7DZ2D', 'DM8LEESR']

app = Flask(__name__)

app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://api_user:123456@localhost:3306/RestServiceInterface'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
    bills = db.relationship('Bill', backref='users', lazy=True)
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
    customer_id = db.Column(db.Integer, nullable=False)
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
    user = db.relationship("User", back_populates="bills")
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

# ==========---------- Tarric Form class ----------==========


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

    # iwant to make date YYYY-MM-DD and by deault make it today's date
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
    # my toekn is a string of 8 digits
    evc = StringField('evc', validators=[
        DataRequired(), Length(min=8, max=8)])
    submit = SubmitField('Top Up')


@ app.route('/register', methods=['GET', 'POST'])
def register():
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
            return redirect(url_for('login'))
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


@ app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user is not None and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            session['user'] = json.dumps(user.to_dict())
            flash("You are logged in!")
            # rendder template with current_user
            return redirect(next_page or url_for('profile'))
        if user is None:
            flash("User does not exist")
            form.email.errors.append("User does not exist")
        if user is not None and not user.check_password(password):
            flash("Incorrect password")
            form.password.errors.append("Incorrect password")
    return render_template('login.html', form=form)


@ app.route('/profile')
@ login_required
def profile():
    user = json.loads(session['user'])
    return render_template('profile.html', user=user)


@ app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You are logged out!")
    return redirect(url_for('index'))


# @app.route('/', methods=['GET'])
# def index():
#     return render_template('index.html')

@ app.route('/home', methods=['GET'])
def index():
    messages = get_flashed_messages()
    return render_template('index.html', messages=messages)


@ app.route('/')
def root():
    print("/")
    return redirect(url_for('index'))


@ app.route('/submit-meter-reading', methods=['GET', 'POST'])
@ login_required
def submit_meter_reading():
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
    return render_template('submit_meter_reading.html', form=form)


@ app.route('/energy-consumption', methods=['GET'])
def get_energy_consumption():
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
    return jsonify([energy_consumption.to_dict() for energy_consumption in energy_consumption])


@ app.route('/view_latest_bill')
@ login_required
def view_latest_bill():
    messages = get_flashed_messages()
    latest_bill = Bill.query.filter_by(
        customer_id=current_user.id, is_paid=False).first()

    print(latest_bill)
    if latest_bill:
        return render_template('view_bill.html', bill=latest_bill, messages=messages)
    else:
        flash('No unpaid bills found.')
        return redirect(url_for('index'))


@ app.route('/pay_bill/<int:bill_id>')
@ login_required
def pay_bill(bill_id):
    bill = Bill.query.filter_by(id=bill_id).first()
    if not bill:
        flash('Bill not found', 'danger')
        return redirect(url_for('view_latest_bill'))
    if bill.customer_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('view_latest_bill'))
    if bill.is_paid:
        flash('Bill already paid', 'info')
        return redirect(url_for('view_latest_bill'))

    if current_user.energy_credit < bill.bill_amount:
        flash('Not enough credit to pay the bill', 'danger')
        return redirect(url_for('view_latest_bill'))
    current_user.energy_credit -= bill.bill_amount
    bill.is_paid = True
    bill.paid_at = datetime.utcnow()
    db.session.commit()
    flash('Bill paid successfully', 'success')
    return redirect(url_for('view_latest_bill'))


# top-up
@ app.route('/top-up', methods=['GET', 'POST'])
@ login_required
def top_up():
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
    return render_template('top_up.html', form=form)


# =============------------- Admin Page -----------------==================
@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    messages = get_flashed_messages()
    form = AdminRegisterForm()
    if form.validate_on_submit():
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
    return render_template('admin_register.html', form=form, messages=messages)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
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


@ app.route('/admin')
def admin_dashboard():
    messages = get_flashed_messages()
    print("checking if admin is logged in")
    if current_user.is_authenticated and current_user.is_admin:
        print('You are now logged in as admin.')
        return render_template('admin_dashboard.html', messages=messages)
    else:
        flash('You need to login as an admin first.')
        return redirect(url_for('admin_login', messages=messages))


@ app.route('/admin/set-tariffs', methods=['GET', 'POST'])
@ login_required
def set_tariffs():
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


@app.route('/admin/bills')
@login_required
def admin_view_bills():
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


@app.route('/admin/bills/<int:bill_id>')
@login_required
def admin_view_bill(bill_id):
    if not current_user.is_admin:
        flash('You must be an admin to access this page.')
        return redirect(url_for('index'))
    bill = Bill.query.get_or_404(bill_id)
    return render_template('admin_view_bill.html', bill=bill)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=False)
