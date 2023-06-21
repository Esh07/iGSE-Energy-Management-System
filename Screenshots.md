# Introduction

In this section, it's all about system screenshots. I will list down all the screenshots of the webapp webpages.

## Table of Contents

- [Introduction](#introduction)
- [Table of Contents](#table-of-contents)
- [:unlock: Open webpages](#open-webpages)

  - [Home Page](#home-page)
  - [Login Page](#login-page)
  - [Register Page](#register-page)
  - [Reset Password Page](#reset-password-page)

- [:closed_lock_with_key: Authenticated webpages (normal users)](#authenticated-webpages-normal-users)

  - [Dashboard Page](#dashboard-page)
  - [Submit Meter Reading Page](#submit-meter-reading-page)
  - [View Last Bill Page](#view-last-bill-page)
  - [Top-up Account Page](#top-up-account-page)

- [:closed_lock_with_key: Authenticated webpages (admin users)](#authenticated-webpages-admin-users)

  - [Admin Dashboard Page](#admin-dashboard-page)
  - [Set/Update Tariff Page](#setupdate-tariff-page)
  - [View All meter readings Page](#view-all-meter-readings-page)
  - [View All Bills Page](#view-all-bills-page)
  - [View Single Bill Page](#view-single-bill-page)

- [:closed_lock_with_key: Auth Webpage (normal & admin users)](#authenticated-webpages-normal--admin-users)
  - [Logout Page](#logout-page)

## Open webpages

<details>
<summary>Home Page</summary>

## Home Page

![Home Page](docs/img/webpage-screenshots/homepage.png)
<b>Home Page</b>
On the homepage, if user is anonymous, it will show session information and a login button. If user is logged in, it will show the user's information and a logout button.

</details>

<details>
<summary>Login Page</summary>

## Login Page

![Login Page](docs/img/webpage-screenshots/login-page.png)

<b>Login Page</b>
A page only accessible to anonymous users. It's a simple form which has instant AJAX validation.

</details>

<details>
<summary>Register Page</summary>

## Register Page

![Register Page](docs/img/webpage-screenshots/register-page.png)
<b>Register Page</b>
A register page for new users to register into the system. It's a simple form which has instant AJAX validation.

It has features like:

- The interesting part is, if you select the "Enter Voucher Code" input field and click on "Scan QR Code" button and scan the QR code, the voucher code will be automatically filled in the input field. This is done using the [QR Code Scanner](https://cdn.jsdelivr.net/npm/jsqr@1.0.4/dist/jsQR.min.js).

- Check if the voucher code is valid instantly using AJAX.
- Check if the username is available instantly using AJAX.
</details>

<details>
<summary>Reset Password Page</summary>

## Reset Password Page

![Reset Password Page](docs/img/webpage-screenshots/reset-password-page.png)

<b>Reset Password Page</b>
A page for users to reset their password.

</details>

## Authenticated webpages (normal users)

<details>
<summary>Dashboard Page</summary>

## Dashboard Page

![Dashboard page](docs/img/webpage-screenshots/dashboard-page.png)
<b>Dashboard Page</b>
A dashboard page for users to view their information and their vouchers. It also has a button, submit meter reading,view last bill, top-up account, and logout.

</details>

<details>
<summary>Submit Meter Reading Page</summary>

## Submit Meter Reading Page

![Submit meter reading page](docs/img/webpage-screenshots/submit-meter-reading-page.png)
<b>Submit Meter Reading Page</b>
A page for users to submit their meter reading. It has a form which has instant AJAX validation.

</details>

<details>
<summary>View Last Bill Page</summary>

## View Last Bill Page

![View last bill](docs/img/webpage-screenshots/view-last-bill-page.png)

<b>View Last Bill Page</b>
A page for users to view their last bill. It has a table which shows the last bill information.

An action button, Pay, is also available for users to pay their last bill.

</details>

<details>
<summary>Top-up Account Page</summary>

## Top-up Account Page

![Top up account page](docs/img/webpage-screenshots/top-up-account-page.png)
<b>Top-up Account Page</b>
A page for users to top-up their account.

It has features like:

- Scan QR Code to fill in the voucher code automatically into the input field (same as register page)

- Validate voucher code instantly using AJAX.
</details>

## Authenticated webpages (admin users)

<details>
<summary>Admin Dashboard Page</summary>

## Admin Dashboard Page

![Admin dashboard page](docs/img/webpage-screenshots/admin/admin-dashboard-page.png)

<b>Admin Dashboard Page</b>
A dashboard page for admin users to view their information and their vouchers. It also has a button, submit meter reading,view last bill, top-up account, and logout.

</details>

<details>
<summary>Set/Update Tariff Page</summary>

## Set/Update Tariff Page

![Set/Update Tariff Page](docs/img/webpage-screenshots/admin/set-update-tariff-page.png)

<b>Set/Update Tariff Page</b>
A page for admin users to set/update tariff.

</details>

<details>
<summary>View All meter readings Page</summary>

## View All meter readings Page

![View All meter readings Page](docs/img/webpage-screenshots/admin/view-all-meter-readings-page.png)

<b>View All meter readings Page</b>
A page for admin users to view all meter readings submitted by users.

</details>

<details>
<summary>View All Bills Page</summary>

## View All Bills Page

![View All Bills Page](docs/img/webpage-screenshots/admin/view-all-bills-page.png)

<b>View All Bills Page</b>
A page for admin users to view all bills generated by the system.

</details>

<details>
<summary>View Single Bill Page</summary>

## View Single Bill Page

![View Single Bill Page](docs/img/webpage-screenshots/admin/view-single-bill-page.png)

<b>View Single Bill Page</b>
A page for admin users to view a single bill.

</details>

<details>
<summary>View statistics Page</summary>

## View statistics Page

![View statistics Page](docs/img/webpage-screenshots/admin/view-statistics-page.png)
<b>View statistics Page</b>
A page for admin users to view statistics of the system.

</details>

## Authenticated webpages (normal & admin users)

<details>
<summary>Logout Page</summary>

## Logout Page

![Logout page](docs/img/webpage-screenshots/log-out-account-page.png)

<b>Logout Page</b>
A page for users to logout of their account.

</details>
