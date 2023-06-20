# iGSE Energy Management System

## Table of Contents
- [Requirements](#requirements)
- [Environment Setup](#environment-setup)
  - [Windows](#windows)
  - [MacOS / Linux](#macos-/-linux)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Generating Tables from Models](#generating-tables-from-models)

## Requirements
- Python 3.x or higher
- For QR code detection, you will need to have a webcam connected to your computer and a webcam permission to access the webcam.



## Environment Setup
Create a new python environment using your preferred method, such as virtualenv.
Activate the environment.

### Windows
```cmd
$ python -m venv your-env
$ your-env\Scripts\activate
```

### MacOS / Linux
```bash
$ python3 -m venv your-env
$ source your-env/bin/activate
```

## Installation
Run the following command to install the necessary packages:
<caption style="text-style: italic; text-align: center; font-size: 11px;">
If you using macOS or Linux, you may need to use <code style="color:#0f0f14; background-color:a9b1d6; font-weight:bold">pip3</code> instead of <code style="color:#0f0f14; background-color:a9b1d6; font-weight:bold">pip</code>; just to avoid dependency issues if you have both Python 2 and Python 3 installed on your system.
</caption>

```bash
$ pip install -r requirements.txt
```


## Database Setup
Inside the `app.py` file, you will find the following line of code that defines the database connection at line 28:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://api_user:123456@localhost:3306/RestServiceInterface'
```
This line of code sets the database connection to a MySQL database with the following details:

- `api_user` as the username
- `123456` as the password
- `localhost:3306` as the host
- `RestServiceInterface` as the database name

><strong>NOTE:</strong> Before running the application, you will need to create the database called <b>RestServiceInterface</b> or give a custom database name and update the `app.py` file ([line 28](https://github.com/Esh07/energy-backend-api/blob/main/iGES_Open_Data_REST_API/app.py#LL28C1-L28C1)) with your own database credentials.

<caption style="text-align: center;">You can create the database using the following command: (it's one line query in MySQL)</caption>

```sql
CREATE DATABASE RestServiceInterface;
```
## Generating Tables from Models
To generate the necessary tables for the application, you will need to run the following command:

<caption style="text-align: center;">Only run this command once to initialize the database migrations</caption>

```bash
$ flask db init 
```


<caption style="text-align: center;">Run the following commands to generate the migration files for the database tables</caption>

```bash
$ flask db migrate
```

<caption style="text-align: center;">Run the following command to apply the migration files to the database tables and generate the tables in the database</caption>

```bash
$ flask db upgrade
```

## Running the Application

To start the application, run the following command:
```bash
$ Flask run
```
<blockquote style="border-left: 5px solid #f0ad4e; background-color: #fcf8e3; padding: 10px;">
  <p><strong>NOTE:</strong> If you set the <code style="color:#0f0f14; background-color:a9b1d6; font-weight:bold">FLASK_APP</code> environment variable, other than <code style="color:#0f0f14; background-color:a9b1d6; font-weight:bold">app.py</code>, you will need to configure the <code style="color:#0f0f14; background-color:a9b1d6; font-weight:bold">FLASK_APP</code> environment variable to <code style="color:#0f0f14; background-color:a9b1d6; font-weight:bold">app.py</code> before running the application.</p>
</blockquote>

You can also set the environment variable FLASK_APP and FLASK_DEBUG to run the application in debug mode:

<h5>MacOS / Linux </h5>

```bash
$ export FLASK_APP=app.py
$ export FLASK_DEBUG=1
``` 

<h5>Windows (temporary session)</h5>

```cmd
$ set FLASK_APP=app.py
$ set FLASK_DEBUG=1
```

<h5>Windows (permanent session)</h5>

```cmd
$ setx FLASK_APP app.py
$ setx FLASK_DEBUG 1
```
This will start the application on http://localhost:5000/

You should now be able to access the application in your browser by navigating to the specified URL. You can also access the application by entering the IP address of your machine on the network.


## API Documentation
The API documentation is available at http://localhost:5000/api/docs

| Endpoint | Method | Description |
| --- | --- | --- |
| `/` | GET | Home page |
| `/home` | GET | Home page |
| `/register` | GET POST | Register a new user |
| `/login` | GET POST | Login user |
| `/logout` | GET | Logout user |
| `/profile` | GET | View user profile |
| `/submit-meter-reading` | GET POST | Submit a meter reading |
| `view_latest_bill` | GET | View the latest bill |
| `/pay_bill/<int:bill_id>` | GET POST | Pay a bill |
| `top-up` | GET POST | Top up account |
| `/admin/register` | GET POST | Register a new admin user |
| `/admin/login` | GET POST | Login admin user |
| `/admin` | GET | Admin dashboard |
| `/admin/logout` | GET | Logout admin user |
| `/admin/set-tariffs` | GET POST | Set the tariffs |
| `admin/bills` | GET | View all bills |
| `/admin/bills/<int:bill_id>` | GET | View a specific bill |
| `/admin/meter-readings` | GET | View all submitted meter readings |
| `/admin/energy-statistics` | GET | View energy statistics |
| `/igse/propertycount` | GET | API endpoint to get the count of properties |
| `/igse/<property_type>/<num_bedrooms>` | GET | API endpoint to get the average energy consumption for a property type and number of bedrooms |
| `/check_email` | POST | API endpoint to check if an email address is already registered (AJAX) |
| `/check_evc_code` | POST | API endpoint to check if an EVC code is valid (AJAX) |
