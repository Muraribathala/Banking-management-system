create table admin(a_id INT, name VARCHAR(10), pin int);
insert into admin values(101,'Deepali',1006),(102,'Bharadwaj',2580);

create table ifsc (ifsc_code VARCHAR(15) PRIMARY KEY, branch VARCHAR(20));
insert into ifsc values('BMSN0000847','Hyderabad Main'),('BMSN0001879','Charminar'),('BMSN0011744','Mehdipatnam'),('BMSN0032241','Kukatpally'),('BMSN0040479','Banjara Hills');

CREATE TABLE accounts (
    acc_no BIGINT  PRIMARY KEY AUTO_INCREMENT,
    ifsc_code VARCHAR(15),  
    branch VARCHAR(20),
    balance DECIMAL(10,2),
    acc_type VARCHAR(20),
    interest_rate decimal(5,2) Default 0.00,
    last_interest_date DATE,
    total_interest_earned DECIMAL(10,2),
    l_id BIGINT, 
    a_status VARCHAR(20) DEFAULT 'active',
    FOREIGN KEY (ifsc_code) REFERENCES ifsc(ifsc_code)
    ) AUTO_INCREMENT = 2501000001;

CREATE TABLE customers (
    c_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    c_name VARCHAR(40) NOT NULL,
    acc_no BIGINT,
    dob DATE,
    city VARCHAR(40),
    mobile BIGINT NOT NULL,
    email VARCHAR(40),
    c_pin INT NOT NULL,
    FOREIGN KEY (acc_no) REFERENCES accounts(acc_no)
    ) AUTO_INCREMENT = 2502000001;

CREATE TABLE transactions (
    t_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    acc_no BIGINT,
    amount DECIMAL(10,2),
    type VARCHAR(100),
    c_balance DECIMAL(10,2),
    t_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (acc_no) REFERENCES accounts(acc_no)
    ) AUTO_INCREMENT = 2503000001;

CREATE TABLE transfer_funds (
    tf_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sender_acc_no BIGINT NOT NULL,
    receiver_acc_no BIGINT NOT NULL,
    transfer_amount DECIMAL(10,2) NOT NULL,
    transfer_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    FOREIGN KEY(sender_acc_no) REFERENCES accounts(acc_no), 
    FOREIGN KEY(receiver_acc_no) REFERENCES accounts(acc_no)
    )AUTO_INCREMENT = 2504000001;

CREATE TABLE loans (
    l_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    acc_no BIGINT NULL,
    l_type VARCHAR(40) NULL,
    l_amount DECIMAL(10,2) NULL,
    interest_amount DECIMAL(10,2) NULL,
    duration INT NULL,
    status VARCHAR(20) NULL,
    total_paid DECIMAL(12,2) DEFAULT 0.00,
    emi DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    FOREIGN KEY (acc_no) REFERENCES accounts(acc_no)
    )AUTO_INCREMENT = 2505000001;
