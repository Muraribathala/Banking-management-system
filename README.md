# Banking-management-system
Banking Management System

A Python + MySQL based mini-project designed to digitalize and automate core banking operations.
This system provides separate modules for Admin and Customer, enabling secure, structured, and efficient handling of banking transactions, account management, loan services, and report generation.

📌 Features
👤 Customer Module

Create new bank accounts

Deposit & Withdraw money

Transfer funds between accounts

Apply for loans

EMI repayment

View transaction history

Forgot PIN functionality

Secure PIN-based authentication

🛠️ Admin Module

Manage customer accounts

Approve / reject loan requests

Update interest rate

Track loan EMI details

Generate branch-wise and account-wise reports

View top customers

Access SQL-based analytics

🗄️ Database Structure

The system uses MySQL with properly designed relational tables:

✔ Tables

accounts – Core account details, balance, interest, status

customers – Customer personal info & linked account

transactions – Records deposits, withdrawals, transfers

transfer_funds – Logs inter-account transfers

loans – Loan details, EMI, repayments & status

admin – Admin login credentials

ifsc – Bank branch information

✔ Relationships

customers.acc_no → accounts.acc_no

loans.acc_no → accounts.acc_no

transactions.acc_no → accounts.acc_no

transfer_funds.sender_acc_no → accounts.acc_no

ifsc.ifsc_code → accounts.ifsc_code

The complete SQL schema (CREATE, INSERT, SELECT, UPDATE queries) is included in the project.

📊 ER Diagram Summary

The Entity-Relationship model connects key modules of the system such as Customers, Accounts, Loans, Transactions, IFSC, and Admin.
The Accounts table acts as the central node, linking customers, loans, and financial activities.

🧩 SQL Highlights

Here are some useful SQL operations included in the project:

Analytics Using JOIN, GROUP BY, HAVING

Branch-wise deposits

Average balance by account type

Monthly deposits & withdrawals

Most active customer

Customer with highest balance

Loan distribution by type

Interest collected per loan type

These help generate real-time banking insights.

🚀 Tech Stack
Component	Technology
Backend	Python (Procedural / OOP in scripts)
Database	MySQL
UI	Terminal-based interface
Tools	MySQL Connector / Python
📁 Project Structure (Suggested)
/Banking-Management-System
│
├── main.py
├── admin/
│   ├── admin_functions.py
│
├── customer/
│   ├── customer_functions.py
│
├── database/
│   ├── schema.sql
│   ├── connection.py
│
├── README.md
└── BMS_REPORT(final).docx

📦 How to Run the Project
1. Install Dependencies
pip install mysql-connector-python

2. Import the SQL Schema

Run the SQL commands from schema.sql or from your report file.

3. Update MySQL Credentials in connection.py
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_mysql_password",
    database="banking_system"
)

4. Start the Application
python main.py

🧑‍💻 Team Members

Bharadwaj

Deepali

Umang

Murari

Biswajit

Shankar

📜 License

This project is for educational use (Mini Project / Semester Project).
Feel free to modify and enhance it.
