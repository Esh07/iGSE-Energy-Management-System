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

## Get the Code

To get the code, open your terminal and go to the directory where you want to download the code. Then run the following command:

```bash
git clone https://github.com/Esh07/iGSE-Energy-Management-System.git
```

## Environment Setup

> <strong>NOTE:</strong> It is recommended to use a virtual environment to run the application. This will allow you to install the required packages in an isolated environment without affecting your system's global packages. You can use any virtual environment manager of your choice, such as virtualenv, venv, pipenv, etc. For this guide, we will be using the built-in venv module.

You can create a python virtual environment anywhere but the recommended way is to create it inside the project directory.

Go to the project directory

```bash
cd iGSE-Energy-Management-System
```

Create a virtual environment.

> <strong>NOTE:</strong> You can replace `<your-env-name>` with any name you want.

##### Windows

```bash
 python -m venv <your-env-name>
```

##### MacOS / Linux

```bash
python3 -m venv <your-env-name>
```

Activate the environment.

##### Windows

```bash
<your-env-name>\Scripts\activate
```

##### MacOS / Linux

```bash
source <your-env-name>/bin/activate
```

## Installation

Run the following command to install the necessary packages:

> If you using macOS or Linux, you may need to use <code style="color:#0f0f14; background-color:a9b1d6; font-weight:bold">`pip3`</code> instead of <code style="color:#0f0f14; background-color:a9b1d6; font-weight:bold">`pip`</code>; just to avoid dependency issues if you have both Python 2 and Python 3 installed on your system.

```bash
pip install -r requirements.txt
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

> <strong>NOTE:</strong> Before running the application, you will need to create the database called <b>RestServiceInterface</b> or give a custom database name and update the `app.py` file ([line 28](https://github.com/Esh07/energy-backend-api/blob/main/iGES_Open_Data_REST_API/app.py#LL28C1-L28C1)) with your own database credentials.

### Creating the Database

You can create the database using the following command: (it's one line query in MySQL)

<i>Copy the following query and paste it in your MySQL Query Editor and run it. </i>

```sql
CREATE DATABASE RestServiceInterface;
```

To run queries in MySQL in Windows, press <kbd>ctrl</kbd> + <kbd>Enter</kbd> to run the query. In MacOS, press <kbd>command</kbd> + <kbd>Enter</kbd>.

or you can do it by GUI.
![Execute query in MySQL workbench](/docs/img/execture-query-in-workbench.png)
<i>Execute query in MySQL workbench</i>

### Generating Tables from Models

> <strong>NOTE:</strong> Make sure you're in the project directory and the virtual environment is activated. Otherwise, you will get an error.

To generate the necessary tables for the application, you will need to run the following command:

<caption style="text-align: center;">Only run this command once to initialize the database migrations</caption>

```bash
flask db init
```

<caption style="text-align: center;">Run the following commands to generate the migration files for the database tables</caption>

```bash
flask db migrate
```

<caption style="text-align: center;">Run the following command to apply the migration files to the database tables and generate the tables in the database</caption>

```bash
flask db upgrade
```

## Running the Application

<blockquote style="border-left: 5px solid #f0ad4e; background-color: #fcf8e3; padding: 10px;">
  <p><strong>NOTE:</strong> If you set the <code style="color:#0f0f14; background-color:a9b1d6; font-weight:bold">FLASK_APP</code> environment variable, other than <code style="color:#0f0f14; background-color:a9b1d6; font-weight:bold">app.py</code>, you will need to configure the <code style="color:#0f0f14; background-color:a9b1d6; font-weight:bold">FLASK_APP</code> environment variable to <code style="color:#0f0f14; background-color:a9b1d6; font-weight:bold">app.py</code> before running the application.</p>

  <p>For example, if you set the <code style="color:#0f0f14; background-color:a9b1d6; font-weight:bold">FLASK_APP</code> environment variable to <code style="color:#0f0f14; background-color:a9b1d6; font-weight:bold">app.py</code>, you will need to run the following command before running the application:</p>

##### Macos / Linux

  <pre><code style="color:#0f0f14; background-color:a9b1d6; font-weight:bold">export FLASK_APP=app.py</code></pre>
</blockquote>

To start the application, run the following command:

```bash
Flask run
```

You can also set the environment variable `FLASK_APP` and `FLASK_DEBUG` to run the application in debug mode:

> <strong>Note: </strong>A variable is only valid for the current terminal session. If you close the terminal, the variable will be removed. And you will need to set the variable again.

<h5>MacOS / Linux </h5>

```bash
export FLASK_APP=app.py
export FLASK_DEBUG=1 # 1 to disable debug mode, 0 to enable debug mode
```

<h5>Windows (temporary session)</h5>
```bash
set FLASK_APP=app.py
set FLASK_DEBUG=1
```

<h5>Windows (permanent session)</h5>
This will set the environment variable permanently in the system and you will not need to set the variable again. :smile:

```bash
setx FLASK_APP app.py
setx FLASK_DEBUG 1 # 1 to disable debug mode, 0 to enable debug mode
```

This will start the application on http://localhost:5000/

You should now be able to access the application in your browser by navigating to the specified URL. You can also access the application by entering the IP address of your machine on the network.

### Extra settings

#### Changing the port

To change the port, you can set the `FLASK_RUN_PORT` environment variable:

```bash
export FLASK_RUN_PORT=8000
```

You can set the following environment variables to configure the application:

| Environment Variable | Description                                                             |
| -------------------- | ----------------------------------------------------------------------- |
| `FLASK_APP`          | The name of the application file. Default: `app.py`                     |
| `FLASK_ENV`          | The environment to run the application in. Default: `production`        |
| `FLASK_DEBUG`        | Enable or disable debug mode. Default: `0`                              |
| `FLASK_RUN_HOST`     | The host to run the application on. Default: `localhost`                |
| `FLASK_RUN_PORT`     | The port to run the application on. Default: `5000`                     |
| `FLASK_RUN_CERT`     | The SSL certificate file to use to run the application. Default: `None` |

## API Documentation

The API documentation is available at http://localhost:5000/api/docs

| Endpoint                               | Method   | Description                                                                                   |
| -------------------------------------- | -------- | --------------------------------------------------------------------------------------------- |
| `/`                                    | GET      | Home page                                                                                     |
| `/home`                                | GET      | Home page                                                                                     |
| `/register`                            | GET POST | Register a new user                                                                           |
| `/login`                               | GET POST | Login user                                                                                    |
| `/logout`                              | GET      | Logout user                                                                                   |
| `/profile`                             | GET      | View user profile                                                                             |
| `/submit-meter-reading`                | GET POST | Submit a meter reading                                                                        |
| `view_latest_bill`                     | GET      | View the latest bill                                                                          |
| `/pay_bill/<int:bill_id>`              | GET POST | Pay a bill                                                                                    |
| `top-up`                               | GET POST | Top up account                                                                                |
| `/admin/register`                      | GET POST | Register a new admin user                                                                     |
| `/admin/login`                         | GET POST | Login admin user                                                                              |
| `/admin`                               | GET      | Admin dashboard                                                                               |
| `/admin/logout`                        | GET      | Logout admin user                                                                             |
| `/admin/set-tariffs`                   | GET POST | Set the tariffs                                                                               |
| `admin/bills`                          | GET      | View all bills                                                                                |
| `/admin/bills/<int:bill_id>`           | GET      | View a specific bill                                                                          |
| `/admin/meter-readings`                | GET      | View all submitted meter readings                                                             |
| `/admin/energy-statistics`             | GET      | View energy statistics                                                                        |
| `/igse/propertycount`                  | GET      | API endpoint to get the count of properties                                                   |
| `/igse/<property_type>/<num_bedrooms>` | GET      | API endpoint to get the average energy consumption for a property type and number of bedrooms |
| `/check_email`                         | POST     | API endpoint to check if an email address is already registered (AJAX)                        |
| `/check_evc_code`                      | POST     | API endpoint to check if an EVC code is valid (AJAX)                                          |
