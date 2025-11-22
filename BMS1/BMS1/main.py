# Modules
import mysql.connector
import re 
from decimal import Decimal, getcontext
getcontext().prec = 10
import csv
from tabulate import tabulate 
import schedule
import time

current_customer = {
    "mobile": None,
    "name": None,
    "acc_no": None
}

savings_account= {
    "interest" : Decimal('3.5')
}

minimum_balance = {
    "savings":5000,
    "current":10000,
}

loan_interest_rate = {
    "home": Decimal('8.0'),
    "personal": Decimal('10.0'),
    "education": Decimal('14.0')
}
# Database Connection
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
# CUSTOMER INTERFACE
def create_account():   
    print("For creating an account please enter the required details......")
    try:
        def validate_email():
            while True:
                email = input("Enter Email Id :")   
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if re.match(pattern,email):
                    return email
                print("Invalid email.....Please enter a valid email")

        def validate_mobile():
            while True:
                mobile = input("Enter the Mobile Number :")
                if mobile.isdigit() and len(mobile) == 10 :
                    return int(mobile) 
                print("Invalid mobile......Please enter a valid mobile number")

        def validate_balance():
            while True:    
                balance = Decimal(input("Enter opening balance:"))
                if balance >= minimum_balance["savings"] and acc_type == "savings":
                    return balance
                elif balance >= minimum_balance["current"] and acc_type == "current":
                    return balance
                else:
                    print("Enter valid balance again...!")

        def validate_dob():
            while True:
                dob = input("Enter the date of birth (YYYY-MM-DD) :")
                pattern = r'^(\d{4})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$'
                if re.match(pattern, dob):
                    return dob 
                print("Enter correct date format")

        def validate_pin():
            while True:
                c_pin = input("Set your pin :")
                if c_pin.isdigit() and len(c_pin) == 4 :
                    return int(c_pin) 
                print("Invalid...... pin should contain only 4 digits")

        def select_branch():
            branches = {
                "1": ("Hyderabad Main", "BMSN0000847"),
                "2": ("Charminar", "BMSN0001879"),
                "3": ("Mehdipatnam", "BMSN0011744"),
                "4": ("Kukatpally", "BMSN0032241"),
                "5": ("Banjara Hills", "BMSN0040479")
            }

            print("\nSelect Branch:")
            for k, v in branches.items():
                print(f"{k}. {v[0]}")

            while True:
                choice = input("Enter branch number: ")
                if choice in branches:
                    branch, ifsc = branches[choice]
                    print(f"Selected: {branch} ({ifsc})")
                    return branch, ifsc
                else:
                    print("Invalid choice! Please enter a number from 1 to 5.")

        # --- Input Section ---
        c_name = input("Enter your Full Name: ") 
        dob = validate_dob()
        city = input("Enter your City: ")
        mobile = validate_mobile()
        email = validate_email()
        acc_type = input("Enter the Account Type (Savings/Current): ").lower()
        balance = validate_balance()
        c_pin = validate_pin()
        branch_name, ifsc_code = select_branch()
    
    except Exception as e :
        print("Invalid input",e)

    # --- Insert into accounts safely ---
    try:
        query1 = "INSERT INTO accounts (ifsc_code, branch,balance, acc_type) VALUES (%s,%s,%s,%s)"
        values1 = (ifsc_code, branch_name,balance, acc_type)
        mycursor.execute(query1, values1)
        conn.commit()
        acc_no = mycursor.lastrowid

        if not acc_no:  # Fallback if lastrowid fails
            mycursor.execute("SELECT MAX(acc_no) FROM accounts")
            acc_no = mycursor.fetchone()[0]

        print("Account created successfully!!!!")
        print(f"Account Number: {acc_no}")
        print("Your login credentials are: ")
        print(f"Mobile: {mobile}")
        print(f"PIN: {c_pin}")
        
        if acc_type == 'savings':
            query = "Update accounts SET interest_rate = 3.50 WHERE acc_no = %s"
            values = (acc_no,)
            mycursor.execute(query, values)
            conn.commit()

        # --- Insert into customers ---
        query2 = "INSERT INTO  customers (c_name, mobile, email, city, dob, acc_no, c_pin) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        values2 = (c_name, mobile, email, city, dob, acc_no, c_pin)
        mycursor.execute(query2, values2)
        conn.commit()    

    except mysql.connector.Error as e:
        print("ERROR", e)
        conn.rollback()
    conn.commit()
def deposit():
    try:
        acc_no = current_customer["acc_no"]
        query = "SELECT a_status FROM accounts WHERE acc_no = %s"
        mycursor.execute(query, (acc_no,))
        result = mycursor.fetchone()

        if result == "block" or result == "deactivate":
            print("Account is block or deactivate !")
            return
        
        amount = Decimal(input("Enter amount to deposit: "))

        if amount <= 0:
            print("Amount must be greater than 0!")
            return

        # Get current balance
        query = "SELECT balance FROM accounts WHERE acc_no = %s"
        mycursor.execute(query, (acc_no,))
        result = mycursor.fetchone()

        if result is None:
            print("Account not found!")
            return

        current_balance = result[0]
        new_balance = current_balance + amount

        # Update balance
        query2 = "UPDATE accounts SET balance = %s WHERE acc_no = %s"
        mycursor.execute(query2, (new_balance, acc_no))
        conn.commit()

        # Insert into transactions
        query3 = "INSERT INTO transactions (acc_no, amount, type, c_balance) VALUES (%s, %s, %s, %s)"
        values = (acc_no, amount, 'deposit', new_balance)
        mycursor.execute(query3, values)
        conn.commit()

        print("\nDeposit successfull!")
        print(f"Amount Deposited: ₹{amount}")
        print(f"Current Balance: ₹{new_balance}")

    except Exception as e:
        print("ERROR while deposit", e)
        conn.rollback()
def withdraw():
    try:
        acc_no = current_customer["acc_no"]
        query = "SELECT a_status FROM accounts WHERE acc_no = %s"
        mycursor.execute(query, (acc_no,))
        result = mycursor.fetchone()

        if result == "block" or result == "deactivate":
            print("Account is block or deactivate !")
            return
        amount = Decimal(input("Enter amount to withdraw: "))

        if amount <= 0:
            print("Amount must be greater than 0!")
            return
        

        # Fetch current balance
        query = "SELECT balance FROM accounts WHERE acc_no = %s"
        mycursor.execute(query, (acc_no,))
        result = mycursor.fetchone()

        if result is None:
            print("Account not found!")
            return

        current_balance = result[0]
        print(f"\nCurrent Balance: ₹{current_balance}")

        # Check balance
        if current_balance >= amount:
            new_balance = current_balance - amount

            # Update balance
            query2 = "UPDATE accounts SET balance = %s WHERE acc_no = %s"
            mycursor.execute(query2, (new_balance, acc_no))
            conn.commit()

            # Insert transaction
            query3 = "INSERT INTO transactions (acc_no, amount, type, c_balance) VALUES (%s, %s, %s, %s)"
            values = (acc_no, amount, 'withdraw', new_balance)
            mycursor.execute(query3, values)
            conn.commit()

            print("\nWithdrawal successfull!")
            print(f"Amount Withdrawn: ₹{amount}")
            print(f"New Balance: ₹{new_balance}")

        else:
            print("Insufficient funds")

    except Exception as e:
        print("ERROR while withdraw", e)
        conn.rollback()
def transfer_funds():
    try:
        sender_acc_no = current_customer["acc_no"]
        acc_no = current_customer["acc_no"]
        query = "SELECT a_status FROM accounts WHERE acc_no = %s"
        mycursor.execute(query, (acc_no,))
        result = mycursor.fetchone()

        if result == "block" or result == "deactivate":
            print("Account is block or deactivate !")
            return
        
        receiver_acc_no = int(input("Enter Receiver's Account Number: "))
        amount = Decimal(input("Enter amount to transfer: "))

        if amount <= 0:
            print("Amount must be greater than 0!")
            return

        # Fetch sender balance
        mycursor.execute("SELECT balance FROM accounts WHERE acc_no = %s", (sender_acc_no,))
        result1 = mycursor.fetchone()
        if result1 is None:
            print("Sender account not found!")
            return
        sender_balance = Decimal(result1[0])

        # Fetch receiver balance
        mycursor.execute("SELECT balance FROM accounts WHERE acc_no = %s", (receiver_acc_no,))
        result2 = mycursor.fetchone()
        if result2 is None:
            print("Receiver account not found!")
            return
        receiver_balance = Decimal(result2[0])

        # Check sufficient balance
        if sender_balance < amount:
            print("Insufficient balance to transfer!")
            return

        # Update balances
        new_sender_balance = sender_balance - amount
        new_receiver_balance = receiver_balance + amount

        mycursor.execute("UPDATE accounts SET balance = %s WHERE acc_no = %s",
                         (new_sender_balance, sender_acc_no))
        mycursor.execute("UPDATE accounts SET balance = %s WHERE acc_no = %s",
                         (new_receiver_balance, receiver_acc_no))

        # Insert into transactions table
        mycursor.execute("INSERT INTO transactions(acc_no, amount, type, c_balance) VALUES (%s, %s, %s, %s)",
                         (sender_acc_no, amount, 'transfer_sent', new_sender_balance))
        mycursor.execute("INSERT INTO transactions(acc_no, amount, type, c_balance) VALUES (%s, %s, %s, %s)",
                         (receiver_acc_no, amount, 'transfer_received', new_receiver_balance))

        # Insert into transfer_funds table
        mycursor.execute("INSERT INTO transfer_funds(sender_acc_no, receiver_acc_no, transfer_amount) VALUES (%s, %s, %s)",
        (sender_acc_no, receiver_acc_no, amount))

        conn.commit()

        print(f"₹{amount} transferred successfully from your account {sender_acc_no} to {receiver_acc_no}!")
        print(f"Your new balance: ₹{new_sender_balance:.2f}")

    except Exception as e:
        conn.rollback()
        print("ERROR while transfer", e)
def view_balance():
    acc_no = current_customer["acc_no"]
    query ="SELECT balance FROM accounts WHERE acc_no = %s"
    mycursor.execute(query, (acc_no,))
    result = mycursor.fetchone()
    if result is None:
        print("Account not found!")
        return
    else:
        balance = result[0]
        print(f"Your current balance is : {balance}")
def show_transactions(acc_no = None):
   if acc_no is None:
       acc_no = current_customer["acc_no"]
   query = "select * from transactions where acc_no = %s limit 5"
   values=(acc_no,)
   mycursor.execute(query,values)
   result = mycursor.fetchall()
   if result is None:
       print("No transactions found")
       return
   print(f"----- Last 5 transaction details of account {acc_no} -----")
   for x in result:
        print(f"Transaction ID   : {x[0]}")
        print(f"Account Number   : {x[1]}")
        print(f"Amount           : ₹{x[2]:.2f}")
        print(f"Type             : {x[3]}")
        print(f"Current Balance  : ₹{x[4]:.2f}")
        print(f"Transaction Date : {x[5]}")
        print("-"*15)
def update_profile():
    acc_no = current_customer["acc_no"]
    query = "SELECT a_status FROM accounts WHERE acc_no = %s"
    mycursor.execute(query, (acc_no,))
    result = mycursor.fetchone()

    if result == "block" or result == "deactivate":
        print("Account is block or deactivate !")
        return
    print(" Update Profile Menu ")
    print("1. Update Mobile Number")
    print("2. Update Email")
    print("3. Update City/Address")
    print("4. Back")

    choice = input("Enter your choice: ")

    if choice == '1':
        new_mobile = input("Enter new mobile number: ")
        query1 = "UPDATE customers SET mobile = %s WHERE acc_no = %s"
        mycursor.execute(query1,(new_mobile, acc_no))
        conn.commit()
        print("Mobile number updated successfully!")

    elif choice == '2':
        new_email = input("Enter new email address: ")
        query2 = "UPDATE customers SET email = %s WHERE acc_no = %s"
        mycursor.execute(query2, (new_email, acc_no))
        conn.commit()
        print("Email updated successfully!")

    elif choice == '3':
        new_city = input("Enter new city/address: ")
        query3 = "UPDATE customers SET city = %s WHERE acc_no = %s"
        mycursor.execute(query3, (new_city, acc_no))
        conn.commit()
        print("City/Address updated successfully!")

    elif choice == '4':
        profile_management()
    else:
        print("Invalid choice!")
def change_pin():
    acc_no = current_customer["acc_no"]
    query = "SELECT a_status FROM accounts WHERE acc_no = %s"
    mycursor.execute(query, (acc_no,))
    result = mycursor.fetchone()

    if result == "block" or result == "deactivate":
        print("Account is block or deactivate !")
        return
    while True:
        old_pin = int(input("Enter your current PIN: "))

        query1 = "SELECT c_pin FROM customers WHERE acc_no = %s"
        mycursor.execute(query1, (acc_no,))
        result = mycursor.fetchone()
        if result is None:
            print("Account not found.")
            return
        stored_pin = result[0]
        
        if old_pin != stored_pin:
            print("Incorrect current PIN! Please try again.")
            continue

        new_pin = int(input("Enter your new PIN: "))
        confirm_pin = int(input("Re-enter your new PIN: "))
        
        if new_pin != confirm_pin:
            print("PINs do not match! Try again......")
            continue
        elif new_pin == old_pin:
            print("New PIN cannot be the same as old PIN!!")
            continue
        
        query2 = "UPDATE customers SET c_pin = %s WHERE acc_no = %s"
        mycursor.execute(query2, (new_pin, acc_no))
        conn.commit()
        
        print("Your PIN has been updated successfully!")
        break   
def profile_management():
    while True:
        acc_no = current_customer["acc_no"]
        query = "SELECT a_status FROM accounts WHERE acc_no = %s"
        mycursor.execute(query, (acc_no,))
        result = mycursor.fetchone()

        if result == "block" or result == "deactivate":
            print("Account is block or deactivate !")
            return
        print("------- PROFILE MANAGEMENT -------")
        print("1. Update Profile (Phone/Email/Address)")
        print("2. Change customer pin")
        print("3. Back to customer menu")

        choice = input("Enter your choice: ")

        if choice == '1':
            update_profile()
        elif choice == '2':
            change_pin()
        elif choice == '3':
            customer_menu()
            break
        else:
            print("Invalid choice!")
def loan_application():
    try:
        acc_no = current_customer["acc_no"]
        query = "SELECT a_status FROM accounts WHERE acc_no = %s"
        mycursor.execute(query, (acc_no,))
        result = mycursor.fetchone()

        if result == "block" or result == "deactivate":
            print("Account is block or deactivate !")
            return

        def calculate_emi(principal, annual_rate, months):
            principal = Decimal(principal)
            monthly_rate = Decimal(annual_rate) / Decimal('1200')
            emi = (principal * monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
            return emi.quantize(Decimal('0.01'))


        print("====== Loan Processing System ======")
        loan_type = input("Enter Loan Type (home/education/personal): ").lower()
        principal = Decimal(input("Enter Loan Amount (in ₹): "))
        years = int(input("Enter Loan Tenure (in years): "))
        months = years * 12

        rate = loan_interest_rate[loan_type]
        


        emi = calculate_emi(principal, rate, months)
        total_payment = emi * months
        total_interest = total_payment - principal

        print("\n--- Loan Summary ---")
        print(f"Loan Type          : {loan_type.capitalize()}")
        print(f"Principal Amount   : ₹{principal:,.2f}")
        print(f"Interest Rate      : {rate}% per annum")
        print(f"Loan Tenure        : {years} years ({months} months)")
        print(f"Monthly EMI        : ₹{emi:,.2f}")
        print(f"Total Payment      : ₹{total_payment:,.2f}")
        print(f"Total Interest     : ₹{total_interest:,.2f}")

        proceed = input("Enter 1 to apply or 0 to cancel: ")
        if proceed != '1':
            print("Your loan application has been cancelled!")
            return

        # Insert into loans table
        query = "INSERT INTO loans (acc_no, l_type, l_amount, interest_amount, duration, emi, total_paid, status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
        values = (acc_no, loan_type, principal, total_interest, months, emi, Decimal('0.00'), 'Pending')
        mycursor.execute(query, values)
        conn.commit()

        l_id = mycursor.lastrowid
        print(f"Loan application submitted successfully! Loan ID: {l_id}")

        # Update account with latest loan id
        update_query = "UPDATE accounts SET l_id = %s WHERE acc_no = %s"
        mycursor.execute(update_query, (l_id, acc_no))
        conn.commit()

    except Exception as e:
        print("ERROR", e)
        conn.rollback()
def repay_loan():
    try:
        acc_no = current_customer["acc_no"]
        query = "SELECT a_status FROM accounts WHERE acc_no = %s"
        mycursor.execute(query, (acc_no,))
        result = mycursor.fetchone()

        if result == "block" or result == "deactivate":
            print("Account is block or deactivate !")
            return

        # Fetch all ongoing loans for this account
        query = "SELECT l_id, l_amount, total_paid, emi, status FROM loans WHERE acc_no=%s AND status='ongoing'"
        mycursor.execute(query, (acc_no,))
        loans = mycursor.fetchall()

        if not loans:
            print("No ongoing loans found for your account.")
            return

        print("Your ongoing loans:")
        for l in loans:
            print(f"Loan ID: {l[0]}, Loan Amount: ₹{l[1]:.2f}, Total Paid: ₹{l[2]:.2f}, EMI: ₹{l[3]:.2f}")

        loan_id = int(input("Enter Loan ID you want to repay: "))

        # Fetch loan details
        mycursor.execute("SELECT l_amount, total_paid, emi FROM loans WHERE l_id=%s", (loan_id,))
        loan = mycursor.fetchone()
        if not loan:
            print("Loan not found!")
            return

        loan_amount, total_paid, emi = loan
        emi = Decimal(emi)

        # Fetch current balance
        mycursor.execute("SELECT balance FROM accounts WHERE acc_no=%s", (acc_no,))
        balance = Decimal(mycursor.fetchone()[0])

        if emi > balance:
            print("Insufficient balance to repay EMI!")
            return

        # Deduct EMI from account
        enter_emi   = Decimal(input("Enter amount of emi: "))
        payment = enter_emi 
        if enter_emi > emi :
            new_balance = balance - payment
            mycursor.execute("UPDATE accounts SET balance=%s WHERE acc_no=%s", (new_balance, acc_no))
        else :
            print(f"{emi} repaid ")
            new_balance = balance - payment
            mycursor.execute("UPDATE accounts SET balance=%s WHERE acc_no=%s", (new_balance, acc_no))
        

        new_total_paid = Decimal(total_paid) + payment
        status = 'closed' if new_total_paid >= Decimal(loan_amount) else 'ongoing'
        mycursor.execute("UPDATE loans SET total_paid=%s, status=%s WHERE l_id=%s", (new_total_paid, status, loan_id))

        # Record transaction
        mycursor.execute(
            "INSERT INTO transactions (acc_no, amount, type, c_balance) VALUES (%s, %s, %s, %s)",
            (acc_no, payment, 'loan_repayment', new_balance))
        conn.commit()
        print(f"₹{payment:.2f} repaid successfully! New balance: ₹{new_balance:.2f}")
        if status == 'closed':
            print("Loan fully repaid! ")

    except Exception as e:
        conn.rollback()
        print("ERROR during loan repayment", e)
def loan_repayment_history():
    acc_no = current_customer["acc_no"]
    
    query = """
    SELECT 
        l.l_id,
        l.acc_no,
        l.l_type,
        l.l_amount,
        l.status,
        t.amount AS emi,
        t.type AS transaction_type,
        t.t_time AS transaction_time
    FROM loans l
    JOIN transactions t ON l.acc_no = t.acc_no
    WHERE l.acc_no = %s AND t.type = 'loan_repayment'
    ORDER BY t.t_time DESC
    """
    
    mycursor.execute(query, (acc_no,))
    result = mycursor.fetchall()
    
    headers = ["Loan id", "Account no", "Loan type", "Loan amount", "Status", "EMI", "Transaction", "Time and date"]
    
    # Format numbers nicely
    formatted_results = []
    for row in result:
        formatted_row = (
            row[0],                      # Loan id
            row[1],                      # Account no
            row[2],                      # Loan type
            f"{row[3]:,.2f}",            # Loan amount
            row[4],                      # Status
            f"{row[5]:,.2f}",            # EMI
            row[6],                      # Transaction type
            row[7].strftime("%Y-%m-%d %H:%M:%S")  # Time formatted
        )
        formatted_results.append(formatted_row)
    
    print(tabulate(formatted_results, headers=headers, tablefmt="fancy_grid"))

# CUSTOMER LOGIN AND MENU
def customer_menu():
    while True:
        print("=" * 30)
        print("-------CUSTOMER MENU-------")
        print("=" * 30)
        print("---- Enter Choice ----")
        print("1. Deposit Money ")
        print("2. Withdraw Money ")
        print("3. Transfer Funds ")
        print("4. View Balance ") 
        print("5. View Transactions ")
        print("6. Loan Services ")
        print("7. Profile management ")
        print("8. Repay loan ")
        print("9. Repayment history ")
        print("10. Logout ")
        
        print("=" * 30)

        choice = input("Enter your choice: ")

        if choice == '1':
            deposit()
        elif choice == '2':
            withdraw()
        elif choice == '3':
            transfer_funds()
        elif choice == '4':
            view_balance()
        elif choice == '5':
            show_transactions()
        elif choice == '6':
            loan_application()
        elif choice == '7':
            profile_management()
        elif choice == '8':
            repay_loan()
        elif choice == '9':
            loan_repayment_history()
        elif choice == '10':
            print("You have been logged out!")
            break
        else:
            print("Invalid choice. Please try again.")
def customer_login():
    global current_customer
    
    print("-----CUSTOMER LOGIN PAGE-----")
    mobile = input("Enter mobile number : ")

    query = "SELECT c_name, mobile , c_pin, acc_no, dob FROM customers WHERE mobile = %s"
    mycursor.execute(query, (mobile,))
    result = mycursor.fetchone()

    if result is None:
        print("No customer found....Try again")
        return
    
    while True:
        c_pin_input = input("Enter your PIN (or type 'forgot' to reset): ")

        if c_pin_input.lower() == "forgot":
        
            dob = input("Enter your Date of Birth (YYYY-MM-DD) to verify your identity: ")
            if dob == str(result[4]):
                print("Identity verified.")
                new_pin = input("Enter your new 4-digit PIN: ")
                confirm_pin = input("Re-enter your new PIN: ")

                if not (new_pin.isdigit() and len(new_pin) == 4):
                    print("PIN must contain exactly 4 digits.")
                    continue

                if new_pin != confirm_pin:
                    print("PINs do not match! Try again....")
                    continue

                query2 = "UPDATE customers SET c_pin = %s WHERE mobile = %s"
                mycursor.execute(query2, (int(new_pin), mobile))
                conn.commit()
                print("PIN updated successfully! Please log in again with your new PIN.")
                return
            else:
                print("Verification failed. Date of Birth does not match.")
                return
        elif c_pin_input.isdigit():
            c_pin = int(c_pin_input)
            if result[2] == c_pin:
                print(f"Hi {result[0]}! You have been logged in successfully.")
                current_customer["mobile"] = result[1]
                current_customer["name"] = result[0]
                current_customer["acc_no"] = result[3]
                customer_menu()
                break
            else:
                print("Invalid pin...Try again or type 'forgot' to reset PIN.\n")
        else:
            print("Invalid input...")

# ADMIN INTERFACE
def view_all_customer_accounts():
    query = "SELECT c.acc_no, c.c_name, c.dob, c.mobile, c.c_pin, a.acc_type, a.branch, a.balance from customers c join accounts a on c.acc_no = a.acc_no "
    mycursor.execute(query)
    results = mycursor.fetchall()
    headers = ["Account No.", "Name", "DOB", "Mobile", "PIN", "Account Type", "Branch", "Balance"]

    formatted_results = [
    row[:-1] + (f"{row[-1]:,.2f}",)  # last column is balance
    for row in results
    ]
    print(tabulate(formatted_results, headers=headers, tablefmt="fancy_grid"))
def deactivate_block_account():
    acc_no = int(input("Enter the account number :"))
    query = "SELECT acc_no FROM accounts WHERE acc_no = %s"
    mycursor.execute(query, (acc_no,))
    result = mycursor.fetchone()
    a_status = ""
    if result is None:
        print("Account not found!")
        return
    choice = int(input("Enter 1 for 'Deactivate' , 2 for 'Block' and 3 for 'Activate' : "))
    if choice == 1:
        a_status = "deactivate"
    elif choice == 2:
        a_status = "block"
    elif choice == 3:
        a_status = "activate"
    else:
        print("Not a valid choice")
    
    query = "UPDATE accounts set a_status = %s where acc_no = %s"
    mycursor.execute(query,(a_status,acc_no))
    conn.commit()
    print(f"the account {acc_no} is {a_status}")
def update_profile():
        acc_no = int(input("Enter the account number :")) 
        query = "SELECT a_status FROM accounts WHERE acc_no = %s"
        mycursor.execute(query, (acc_no,))
        result = mycursor.fetchone()

        if result == "block" or result == "deactivate":
            print("Account is block or deactivate !")
            return
        print(" Update Profile Menu ")
        print("1. Update Mobile Number")
        print("2. Update Email")
        print("3. Update City/Address")
        print("4. Back")

        choice = input("Enter your choice: ")

        if choice == '1':
            new_mobile = input("Enter new mobile number: ")
            query1 = "UPDATE customers SET mobile = %s WHERE acc_no = %s"
            mycursor.execute(query1,(new_mobile, acc_no))
            conn.commit()
            print("Mobile number updated successfully!")

        elif choice == '2':
            new_email = input("Enter new email address: ")
            query2 = "UPDATE customers SET email = %s WHERE acc_no = %s"
            mycursor.execute(query2, (new_email, acc_no))
            conn.commit()
            print("Email updated successfully!")

        elif choice == '3':
            new_city = input("Enter new city/address: ")
            query3 = "UPDATE customers SET city = %s WHERE acc_no = %s"
            mycursor.execute(query3, (new_city, acc_no))
            conn.commit()
            print("City/Address updated successfully!")

        elif choice == '4':
            profile_management()
        else:
            print("Invalid choice!")
def manage_accounts():
    choice = int(input("1. View all accounts \n2. Activate/Deactivate/Block \n3. Update customer details : "))
    if choice == 1:
        view_all_customer_accounts()
    elif choice == 2:
        deactivate_block_account()
    elif choice == 3:
        update_profile()
    else:
        print("Not a valid choice")
def update_savings_interest_rate():
    """
    Update interest rate for all Savings accounts and store it in savings_account dict.
    """
    global savings_account
    try:
        rate = Decimal(input("Set savings account interest rate in %: "))
        savings_account["interest"] = rate

        # Update all Savings accounts in DB
        update_query = "UPDATE accounts SET interest_rate=%s WHERE acc_type='Savings'"
        mycursor.execute(update_query, (rate,))
        conn.commit()

        print(f"Savings account interest rate updated to {rate}% successfully!")

    except Exception as e:
        conn.rollback()
        print("ERROR", e)
def add_savings_interest():
    """
    Add 1 month interest to all Savings accounts using stored interest rate.
    """
    global savings_account
    try:
        rate = savings_account.get("interest")
        if rate is None:
            print("Interest rate not set! Please update it first.")
            return

        # Fetch all Savings accounts
        query = "SELECT acc_no, balance, total_interest_earned FROM accounts WHERE acc_type='Savings'"
        mycursor.execute(query)
        accounts = mycursor.fetchall()

        for acc_no, balance, total_interest in accounts:
            # Calculate monthly interest
            interest = balance * (rate / 100) / 12
            new_balance = balance + interest
            total_interest = (total_interest or 0) + interest

            # Update account
            update_query = """
                UPDATE accounts
                SET balance=%s, last_interest_date=CURDATE(), total_interest_earned=%s
                WHERE acc_no=%s
            """
            mycursor.execute(update_query, (new_balance, total_interest, acc_no))
            conn.commit()

            # Record transaction
            insert_query = "INSERT INTO transactions (acc_no, amount, type, c_balance) VALUES (%s, %s, %s, %s)"
            mycursor.execute(insert_query, (acc_no, interest, 'Interest_credit', new_balance))
            conn.commit()

            print(f"Account {acc_no}: Interest ₹{interest:.2f} added. New balance ₹{new_balance:.2f}")

        print("\nMonthly interest credited to all Savings accounts successfully!")

    except Exception as e:
        conn.rollback()
        print("ERROR ", e)
def add_interest_job():
    add_savings_interest()

    # Schedule to run at 00:01 on 1st of every month
    schedule.every().month.at("00:01").do(add_interest_job)
    while True:
        schedule.run_pending()
        time.sleep(60) 
def set_loan_interest():
    global loan_interest_rate  # make sure we are modifying the global dict
    try:
        for loan_type in loan_interest_rate:
            # Show current rate and get user input
            rate_input = input(f"Enter interest rate for {loan_type} (current {loan_interest_rate[loan_type]}%): ").strip()
            if rate_input:  # if user entered a value
                loan_interest_rate[loan_type] = Decimal(rate_input)  # update the dict

        print("\nUpdated loan interest rates:")
        for lt, r in loan_interest_rate.items():
            print(f"{lt.capitalize()}: {r}%")

    except Exception as e:
        print("ERROR", e)
def approve_loans():
    query = "select * from loans where status = 'pending'"
    mycursor.execute(query)
    rows = mycursor.fetchall()
    columns = [desc[0] for desc in mycursor.description]
    formatted_rows = []
    for row in rows:
        formatted_row = list(row)
        # Convert 3rd and 4th index to float and format
        for i in [3, 4]:  # l_amount and interest_amount
            value = row[i]
            if isinstance(value, Decimal):
                value = float(value)
            formatted_row[i] = f"{value:,.2f}"
        formatted_rows.append(formatted_row)

    print(tabulate(formatted_rows, headers=columns, tablefmt="fancy_grid"))

    l_id = int(input("Enter loan id :"))
    choice = int(input("1. Approve\n2. Reject \n"))
    if choice == 1:
        # Fatch loan amount
        mycursor.execute("select l_amount,acc_no from loans where l_id = %s",(l_id,))
        result = mycursor.fetchone()
        amount = result[0]
        acc_no = result[1]
        # Update loan status 
        mycursor.execute("update loans set status = 'ongoing' where l_id = %s",(l_id,))
        #Credit loan amount
        mycursor.execute("SELECT balance FROM accounts WHERE acc_no = %s", (acc_no,))
        current_balance = mycursor.fetchone()[0]
        new_balance = current_balance + amount
        mycursor.execute("update accounts set balance = %s where acc_no = %s",(new_balance,acc_no))
        mycursor.execute("insert into transactions (acc_no,amount,type,c_balance) values (%s,%s,%s,%s)",(acc_no,amount,"loan approval",new_balance))
        conn.commit()
        print(f"Loan has been approved amount {amount} credited in account {acc_no}.")
    elif choice == 2:
        query1 = "update loans set status = 'rejected' where l_id = %s"
        values = (l_id,)
        mycursor.execute(query1,values)
        conn.commit()
        print("Loan has been rejected please visit bank ")
    else :
        print("Invalid choice")
def generate_reports():
    def mothly_deposit_withdrawal():
        query = """
        SELECT 
            acc_no,
            YEAR(t_time) as year,
            MONTH(t_time) as month,
            SUM(CASE WHEN type='deposit' THEN amount ELSE 0 END) as total_deposit,
            SUM(CASE WHEN type='withdraw' THEN amount ELSE 0 END) as total_withdraw
        FROM transactions
        GROUP BY acc_no, YEAR(t_time), MONTH(t_time)
        ORDER BY acc_no, YEAR(t_time), MONTH(t_time)
        """
        mycursor.execute(query)
        monthly_summary = mycursor.fetchall()

        # --- Write to CSV ---
        with open("monthly_transactions.csv", "w", newline="") as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(["Acc No", "Year", "Month", "Total Deposit", "Total Withdraw"])
            # Write data
            writer.writerows(monthly_summary)

        print("CSV file 'monthly_transactions.csv' created successfully!")

    def loan_summary():
        #  Total loan amount
        query_disbursed = "SELECT SUM(l_amount) FROM loans"
        mycursor.execute(query_disbursed)
        total_disbursed = mycursor.fetchone()[0]

        #  Total loan recovered 
        query_recovered = "SELECT SUM(total_paid) FROM loans"
        mycursor.execute(query_recovered)
        total_recovered = mycursor.fetchone()[0]

        print(f"Total Loan Disbursed: {total_disbursed}")
        print(f"Total Loan Recovered: {total_recovered}")

    def interest_earned_paid():
        query_interest_earned = "SELECT SUM(total_interest_earned) FROM accounts"
        mycursor.execute(query_interest_earned)
        total_interest_earned = mycursor.fetchone()[0]

        # --- Total interest to be paid by customers ---
        query_interest_paid = "SELECT SUM(interest_amount) FROM loans"
        mycursor.execute(query_interest_paid)
        total_interest_to_be_paid = mycursor.fetchone()[0]

        print(f"Total Interest Earned by Bank: {total_interest_earned}")
        print(f"Total Interest to be Paid by Customers: {total_interest_to_be_paid}")

    def most_active_customer():
        query = """
        SELECT c.c_name, c.acc_no, COUNT(t.t_id) AS transaction_count
        FROM customers c
        JOIN transactions t ON c.acc_no = t.acc_no
        GROUP BY c.acc_no, c.c_name
        ORDER BY transaction_count DESC
        LIMIT 1
        """
        mycursor.execute(query)
        most_active = mycursor.fetchone()

        if most_active:
            print(f"Most Active Customer: {most_active[0]} (Account: {most_active[1]})")
            print(f"Number of Transactions: {most_active[2]}")
        else:
            print("No transactions found.")

    def highest_lowest():
        mycursor.execute("""
        SELECT a.acc_no, c.c_name, a.balance, a.acc_type
        FROM accounts a
        JOIN customers c ON a.acc_no = c.acc_no
        ORDER BY a.balance DESC
        LIMIT 1
        """)
        highest = mycursor.fetchone()

        mycursor.execute("""
        SELECT a.acc_no, c.c_name, a.balance, a.acc_type
        FROM accounts a
        JOIN customers c ON a.acc_no = c.acc_no
        ORDER BY a.balance ASC
        LIMIT 1
        """)
        lowest = mycursor.fetchone()

        print("------ Account Balances ------")
        print(f"Highest Balance Account: {highest[0]} | Customer: {highest[1]} | Balance: {highest[2]} | Type: {highest[3]}")
        print(f"Lowest Balance Account: {lowest[0]} | Customer: {lowest[1]} | Balance: {lowest[2]} | Type: {lowest[3]}")

    while True:
        print("=" * 30)
        print("--------REPORTS MENU--------")
        print("=" * 30)
        print("---- Enter Choice ----")
        print("1. onthly deposit and withdrwals ")
        print("2. Loans summary")
        print("3. Interest earned and paid ")
        print("4. Most active customer ")
        print("5. Highest and lowest balance account ")
        print("6. Return to menu ")
        print("=" * 30)

        choice = input("Enter your choice: ")

        if choice == '1':
            mothly_deposit_withdrawal()
        elif choice == '2':
            loan_summary()
        elif choice == '3':
            interest_earned_paid()
        elif choice == '4':
            most_active_customer()
        elif choice == '5':
            highest_lowest()
        elif choice == '6':
            break
        else:
            print("Invalid choice. Please try again.")
def analysis():
    def branch_wise_deposit():
        try:
            query = """
                SELECT 
                    i.branch AS Branch,
                    SUM(a.balance) AS Total_Deposit
                FROM accounts a
                JOIN ifsc i ON a.ifsc_code = i.ifsc_code
                GROUP BY i.branch
                ORDER BY Total_Deposit DESC;
            """
            mycursor.execute(query)
            data = mycursor.fetchall()

            with open("branch_wise_deposits.csv", "w", newline="") as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(["Branch", "Total_Deposit"])
                # Write data
                writer.writerows(data)

            print("Branch-wise deposit report exported to 'branch_wise_deposits.csv' successfully!")

        except Exception as e:
            print("Error exporting branch-wise deposit report:", e)

    def avg_balance_by_account_type():
        """
        Exports the average account balance for each account type to a CSV file.
        """
        try:
            query = """
                SELECT 
                    acc_type AS Account_Type,
                    ROUND(AVG(balance), 2) AS Average_Balance
                FROM accounts
                GROUP BY acc_type
                ORDER BY Average_Balance DESC;
            """
            mycursor.execute(query)
            data = mycursor.fetchall()

            # --- Export to CSV ---
            with open("average_balance_per_account_type.csv", "w", newline="") as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(["Account_Type", "Average_Balance"])
                # Write data
                writer.writerows(data)

            print("Average balance by account type exported successfully to 'average_balance_per_account_type.csv'!")

        except Exception as e:
            print("Error exporting average balance per account type:", e)

    def top_customers_by_balance(limit=5):

            query = """
                SELECT c.c_id, c.c_name, a.acc_no, a.acc_type, a.balance
                FROM accounts a
                JOIN customers c ON a.acc_no = c.acc_no
                ORDER BY a.balance DESC
                LIMIT %s
            """
            mycursor.execute(query, (limit,))
            data = mycursor.fetchall()

            with open("top_customers_by_balance.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Customer ID", "Customer Name", "Account No", "Account Type", "Balance"])
                writer.writerows(data)
 
            print(f"Top {limit} customers by balance exported to 'top_customers_by_balance.csv'!")

    def loan_distribution_by_type():

        """
        Count total loans and sum of loan amounts by loan type.
        """
        query = """
            SELECT l_type, COUNT(*) AS total_loans, SUM(l_amount) AS total_amount
            FROM loans
            GROUP BY l_type
            ORDER BY total_amount DESC
        """
        mycursor.execute(query)
        data = mycursor.fetchall()

        with open("loan_distribution_by_type.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Loan Type", "Total Loans", "Total Loan Amount"])
            writer.writerows(data)
    
        print("Loan distribution by type exported to 'loan_distribution_by_type.csv'!")
    
    def interest_collected_per_loan_type():
        """
        Sum of interest collected per loan type.
        """
        query = """
            SELECT l_type, SUM(interest_amount) AS total_interest
            FROM loans
            GROUP BY l_type
            ORDER BY total_interest DESC
        """
        mycursor.execute(query)
        data = mycursor.fetchall()

        with open("interest_collected_per_loan_type.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Loan Type", "Total Interest Collected"])
            writer.writerows(data)
        
        print("Interest collected per loan type exported to 'interest_collected_per_loan_type.csv'!")
    
    while True:
        print("=" * 30)
        print("--------Analysis--------")
        print("=" * 30)
        print("---- Enter Choice ----")
        print("1. Branch wise deposit ")
        print("2. Avg balance by account type ")
        print("3. Top customers by balance ")
        print("4. Loan distribution by type ")
        print("5. Interest collected per loan type ") 
        print("6. Back to menu ")
        print("=" * 30)

        choice = input("Enter your choice: ")

        if choice == '1':
            branch_wise_deposit()
        elif choice == '2':
            avg_balance_by_account_type()
        elif choice == '3':
            top_customers_by_balance()
        elif choice == '4':
            loan_distribution_by_type()
        elif choice == '5':
            interest_collected_per_loan_type()
        elif choice == '6':
            break
        else:
            print("Invalid choice. Please try again.")

# ADMIN LOGIN AND MENU
def admin_menu():
    while True:
        print("=" * 30)
        print("--------ADMIN MENU--------")
        print("=" * 30)
        print("---- Enter Choice ----")
        print("1. Manage Accounts ")
        print("2. Approve Loans ")
        print("3. Set Interest Rates ")
        print("4. View Transactions ")
        print("5. Generate Reports ") 
        print("6. Analysis  ") 
        print("7. Logout ")
        print("=" * 30)

        choice = input("Enter your choice: ")

        if choice == '1':
            manage_accounts()
        elif choice == '2':
            approve_loans()
        elif choice == '3':
            set_loan_interest()
        elif choice == '4':
            acc_no = int(input("Enter Account Number to view transactions: "))
            show_transactions(acc_no)
        elif choice == '5':
            generate_reports()
        elif choice == '6':
            analysis()
        elif choice == '7':
            print("You have been logged out")
            break
        else:
            print("Invalid choice. Please try again.")
def admin_login():
    print("=" * 30)
    print("-----ADMIN LOGIN PAGE-----")
    print("=" * 30)
    a_id = input("Enter your Id: ")

    query = "SELECT name , pin FROM admin WHERE a_id = %s"
    mycursor.execute(query, (a_id,))
    result = mycursor.fetchone()

    if result is None:
        print("Admin not found")
        return
    
    while True:
        pin = int(input("Enter your pin: "))
        if result[1] == pin:
            print("HI",result[0],"....!")
            admin_menu()
            break
        else:
            print("Invalid pin...Try again")

def main():
    while True:
        print("=" * 30)
        print("BANKING MANAGEMENT SYSTEM")
        print("=" * 30)
        print("---- Choose an option ----")
        print("1. Admin Login ")
        print("2. Customer login ")
        print("3. New Registration (Account Creation) ")
        print("4. Exit ")
        print("=" * 30)

        choice = input("Enter your choice: ")

        if choice == '1':
            admin_login()
        elif choice == '2':
            customer_login()
        elif choice == '3':
            create_account()
        elif choice == '4':
            print("Thank you for using the Banking Management System.")
            conn.close()
            break
        else:
            print("Invalid choice. Please try again.")

main()
