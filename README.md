# iGSE Energy Management System - Webapp

iGSE Energy Management System: A tool for managing energy consumption and bills, featuring a web interface and a REST API.

For detailed documentation, please refer to the [:book: Documentation](./DOCUMENTATION.md) file.

For screenshots of the web interface, please refer to the [:camera: Screenshots](./Screenshots.md) file.

## :computer: Technologies Used

- **Programming Languages**: Python, HTML, CSS, JavaScript
- **Frameworks**: Flask, Bootstrap
- **Libraries**: Jinja2, jQuery, QRCode.js
- **Database**: SQLite
- **API Testing**: Postman

## :bulb: Features
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

## :climbing: Challenges Faced

1. <b>User Authentication</b>

2. <b>QR Code Scanning</b>

3. <b>Data Management</b>

4. <b>Error Handling</b>

## :trophy: Achievements

By completing this project, I accomplished the following:

- Developed a fully functional web interface for iGSE Energy Management System, allowing customers to submit meter readings, view bills, and pay bills using energy vouchers.
- Implemented user registration and authentication functionality, ensuring secure access to customer accounts.
- Integrated QR code scanning feature for easy registration and verification of energy vouchers.
- Created an administrative dashboard for GSE admins to manage unit prices, view customer bills, and generate energy usage statistics.
- Implemented robust error handling mechanisms to provide meaningful error messages for various scenarios.
