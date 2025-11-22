import mysql.connector
from random import randint, choice, uniform
from faker import Faker
from decimal import Decimal

# Use Indian locale
fake = Faker('en_IN')  # English, India

conn = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "root",
    port = 3306,
    connection_timeout = 5,
    use_pure = True,
    database = "bms1"
)
mycursor = conn.cursor()

# --- Branch IFSC Codes ---
branches = [
    ("Hyderabad Main", "BMSN0000847"),
    ("Charminar", "BMSN0001879"),
    ("Mehdipatnam", "BMSN0011744"),
    ("Kukatpally", "BMSN0032241"),
    ("Banjara Hills", "BMSN0040479")
]

# --- 10 Accounts & Customers ---
account_numbers = []

for _ in range(10):
    branch_name, ifsc_code = choice(branches)
    acc_type = choice(["Savings", "Current"])
    balance = round(uniform(5000, 100000), 2)
    
    # Insert into accounts
    mycursor.execute(
        "INSERT INTO accounts (ifsc_code, branch, acc_type, balance) VALUES (%s,%s,%s,%s)",
        (ifsc_code, branch_name, acc_type, balance)
    )
    conn.commit()
    acc_no = mycursor.lastrowid
    account_numbers.append(acc_no)
    
    # Insert into customers
    c_name = fake.name()  # Indian name
    dob = fake.date_of_birth(minimum_age=18, maximum_age=60)
    city = fake.city()  # Indian city
    mobile = randint(9000000000, 9999999999)
    email = f"{c_name.replace(' ', '').lower()}{randint(1,100)}@example.com"
    c_pin = randint(1000, 9999)
    
    mycursor.execute(
        "INSERT INTO customers (c_name, acc_no, dob, city, mobile, email, c_pin) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (c_name, acc_no, dob, city, mobile, email, c_pin)
    )
    conn.commit()

print("10 Indian accounts and customers added successfully!")

# --- 50 Transactions ---
transaction_types = ["deposit", "withdraw"]

for _ in range(50):
    acc_no = choice(account_numbers)
    t_type = choice(transaction_types)
    amount = round(uniform(500, 20000), 2)
    
    # Get current balance
    mycursor.execute("SELECT balance FROM accounts WHERE acc_no=%s", (acc_no,))
    balance = Decimal(mycursor.fetchone()[0])
    
    # Update balance
    if t_type == "deposit":
        new_balance = balance + Decimal(amount)
    else:
        if balance < amount:
            continue  # skip if insufficient funds
        new_balance = balance - Decimal(amount)
    
    mycursor.execute("UPDATE accounts SET balance=%s WHERE acc_no=%s", (new_balance, acc_no))
    mycursor.execute(
        "INSERT INTO transactions (acc_no, amount, type, c_balance) VALUES (%s,%s,%s,%s)",
        (acc_no, amount, t_type, new_balance)
    )
    conn.commit()

print("50 Indian transactions added successfully!")

# --- 30 Fund Transfers ---
for _ in range(30):
    sender, receiver = choice(account_numbers), choice(account_numbers)
    if sender == receiver:
        continue
    amount = round(uniform(500, 10000), 2)
    
    # Check sender balance
    mycursor.execute("SELECT balance FROM accounts WHERE acc_no=%s", (sender,))
    sender_balance = Decimal(mycursor.fetchone()[0])
    
    if sender_balance < amount:
        continue
    
    mycursor.execute("SELECT balance FROM accounts WHERE acc_no=%s", (receiver,))
    receiver_balance = Decimal(mycursor.fetchone()[0])
    
    # Update balances
    sender_new = sender_balance - Decimal(amount)
    receiver_new = receiver_balance + Decimal(amount)
    
    mycursor.execute("UPDATE accounts SET balance=%s WHERE acc_no=%s", (sender_new, sender))
    mycursor.execute("UPDATE accounts SET balance=%s WHERE acc_no=%s", (receiver_new, receiver))
    
    # Insert into transactions
    mycursor.execute("INSERT INTO transactions (acc_no, amount, type, c_balance) VALUES (%s,%s,%s,%s)",
                     (sender, amount, 'transfer_sent', sender_new))
    mycursor.execute("INSERT INTO transactions (acc_no, amount, type, c_balance) VALUES (%s,%s,%s,%s)",
                     (receiver, amount, 'transfer_received', receiver_new))
    
    # Insert into transfer_funds
    mycursor.execute("INSERT INTO transfer_funds (sender_acc_no, receiver_acc_no, transfer_amount) VALUES (%s,%s,%s)",
                     (sender, receiver, amount))
    conn.commit()

print("30 Indian fund transfers added successfully!")

conn.close()
