<div align="center">

# ⚡ iGSE Energy Management System

**A full-stack energy billing platform built with Python, Flask, SQLite, and REST API design**

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)](https://sqlite.org)
[![Swagger](https://img.shields.io/badge/Swagger-85EA2D?logo=swagger&logoColor=173647)](https://swagger.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

iGSE is a web-based energy management platform that allows customers to submit meter readings, manage bills, and top up energy credit, while giving administrators full control over pricing, billing data, and usage statistics.

Built as a university coursework project, it demonstrates real-world patterns including REST API design, role-based access control, QR voucher integration, and structured database management.


For detailed documentation, please refer to the [:book: Documentation](./DOCUMENTATION.md) file.

For screenshots of the web interface, please refer to the [:camera: Screenshots](./Screenshots.md) file.

## ✨ Features

| Area | Capability |
|---|---|
| 👤 Customer | Submit meter readings, view & pay bills, top up energy credit via QR vouchers |
| 🛡️ Admin | Set unit prices, view all customer bills, generate energy usage statistics |
| 🔐 Auth | Secure registration & login with session management |
| 📡 REST API | Open endpoints for energy consumption data and statistics |
| 📷 QR Codes | Voucher scanning for credit verification and registration |
| ⚠️ Errors | Structured error handling with meaningful HTTP responses |

### Customer
1. A customer can submit new meter readings, which consists of four parts:
    - Submission date (e.g. 2022-11-05, default value: today)
    - Electricity meter reading - Day (e.g. 100 kWh)
     - Electricity meter reading - Night (e.g. 250 kWh)
     - Gas meter reading (e.g. 800 kWh)
3. A customer can view and pay the latest unpaid bill with energy credit.
4. A customer can top up the credit with a <a href="./Screenshots.md#evc-energy-voucher-code">valid EVC*</a>.

### Admin 
> <b> iGSE admin account:</b> there is only one pre-defined GSE admin account (due to requirement), which has a login name
“gse@shangrila.gov.un” and a default password “gse@energy”. 
1. Admin can set the price per kWh (or unit cost) for the electricity (day/night) and gas.
2. Admin can access meter readings submitted by all customers.
3. Admin can view the energy statistics– show the average gas and electricity consumption (in kWh)
per day for all customers based on their latest billing period.

### System
- Integration of QR code scanning for easy registration and verification of energy vouchers.
- REST API endpoints to provide open access to energy consumption data and statistics.
- Robust error handling mechanisms for providing meaningful error messages.

---

## 🛠 Tech Stack

- **Backed**: Python, Flask
- **Frontend**: HTML5, CSS3, JavaScript (jQuery, QRCode.js), Jinja2 templates, Bootstrap 
- **Database**: SQLite API,
- **RESTful**: Auth, Session-based authentication, QR Codes (QR voucher generation and scanning)
- **API Testing**: Postman

Follow Documentation is: [Docs](/DOCUMENTATION.md)
