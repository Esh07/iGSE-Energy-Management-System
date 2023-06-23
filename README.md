# iGSE Energy Management System - Webapp

The iGSE Energy Management System aims to provide Shangri-La residents with a platform to manage their energy consumption and bills. It includes a web interface and a REST API.

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

1. <b>User Authentication</b>: Implementing a secure and reliable user authentication system was a significant challenge. I had to ensure that customer passwords were stored securely and that only authorized users could access their accounts.

2. <b>QR Code Scanning</b>: Integrating QR code scanning functionality posed a challenge. I had to research and implement a suitable library or API to read QR codes, validate them, and associate them with customer accounts.

3. <b>Data Management</b>: Storing and managing customer information, meter readings, and energy consumption data required careful consideration of database design and data handling. Ensuring data integrity and efficient retrieval was crucial.

4. <b>Error Handling</b>: Designing an effective error handling system was crucial to providing a smooth user experience. I had to anticipate possible errors and develop error pages or AJAX messages to display meaningful feedback to users.

## :trophy: Achievements

By completing this project, I accomplished the following:

- Developed a fully functional web interface for iGSE Energy Management System, allowing customers to submit meter readings, view bills, and pay bills using energy vouchers.
- Implemented user registration and authentication functionality, ensuring secure access to customer accounts.
- Integrated QR code scanning feature for easy registration and verification of energy vouchers.
- Designed and implemented REST API endpoints to provide open access to energy consumption data and statistics.
- Created an administrative dashboard for GSE admins to manage unit prices, view customer bills, and generate energy usage statistics.
- Implemented robust error handling mechanisms to provide meaningful error messages for various scenarios.

## :key: Key Takeaways

The completion of this project provided me with the following crucial learning experiences:

1. <b>Web Development Skills</b>: I gained practical experience in developing web applications using modern technologies and frameworks (Flask). This included frontend development (Jinja2 template engine), backend programming, and integrating various components (QR scanning and DB) to create a cohesive system.

2. <b>User Interface Design</b>: Designing a user-friendly interface required a deep understanding of user needs and effective UI/UX design principles. I learned to create intuitive interfaces that enhance user experience and simplify complex tasks.

3. <b>API Design and Development</b>: Designing and implementing RESTful APIs helped me understand the importance of clear specifications, request/response handling, and proper data structuring. I even take use of Postman for testing and checking endpoints. I learned to create APIs that are efficient, scalable, and adhere to industry best practices.

4. <b>Database Management</b>: Working with a database required me to design appropriate database schemas, handle data efficiently, and ensure data integrity. I learned valuable skills in structuring and querying databases to store and retrieve information accurately.

5. <b>Error Handling and Debugging</b>: Dealing with errors and bugs in the development process taught me the importance of error handling and effective debugging techniques. I learned to identify and resolve issues, improving the overall stability and reliability of the system.
