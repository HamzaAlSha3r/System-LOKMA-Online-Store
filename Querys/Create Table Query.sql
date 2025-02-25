drop database if exists LOKMA;
create database LOKMA;
use LOKMA;

create Table Employees (
emp_id int primary key AUTO_INCREMENT ,
manger_id int ,
emp_name varchar (20) ,
phone varchar (15) ,
address TEXT ,
emp_role  varchar (32),
salary int );

create Table Customers (
customer_id int primary key AUTO_INCREMENT, 
customer_name varchar (20) ,
phone varchar (15) ,
address TEXT );

CREATE TABLE EmployeeLogin (
    LoginID INT PRIMARY KEY AUTO_INCREMENT,
    Email VARCHAR(100) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    EmployeeID INT NOT NULL,
    FOREIGN KEY (EmployeeID) REFERENCES Employees(emp_id) ON DELETE CASCADE
);

CREATE TABLE CustomerLogin (
    LoginID INT PRIMARY KEY AUTO_INCREMENT,
    Email VARCHAR(100) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    CustomerID INT NOT NULL,
    FOREIGN KEY (CustomerID) REFERENCES Customers(customer_id) ON DELETE CASCADE
);

CREATE TABLE Products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(32),
    price DOUBLE
);

CREATE TABLE Product_Employee (
    product_id INT NOT NULL,
    emp_id INT NOT NULL,
    PRIMARY KEY (product_id, emp_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (emp_id) REFERENCES Employees(emp_id) ON DELETE CASCADE
);

create table Sweets (
product_id int primary key ,
nuts_Type varchar (32) ,
 chocolate_Type varchar (32) ,
foreign key (product_id) references products (product_id) on delete cascade ); 

create table Drinks (
product_id int primary key ,
 state varchar (32) ,
is_Sugar_Free VARCHAR(3) DEFAULT NULL CHECK (is_Sugar_Free IN ('yes', 'no')), 
foreign key (product_id) references products (product_id) on delete cascade );

CREATE TABLE Orders (
order_id INT PRIMARY KEY AUTO_INCREMENT, 
customer_id INT ,
total_amount DOUBLE NOT NULL CHECK (total_amount >= 0), -- * 
rating INT DEFAULT NULL CHECK (rating BETWEEN 1 AND 5),
FOREIGN KEY (customer_id) REFERENCES Customers(customer_id) ON UPDATE CASCADE ON DELETE SET NULL
);

create Table Order_Product (
order_id int not null, 
product_id int not null ,
sub_price DOUBLE NOT NULL CHECK (sub_price >= 0),
quantity INT NOT NULL CHECK (quantity > 0),  
primary key (order_id,product_id),
foreign key (order_id) references Orders (order_id) on update cascade on delete cascade ,
foreign key (product_id) references Products (product_id) on update cascade on delete cascade );

CREATE TABLE PaymentMethod (
    PaymentMethodID INT PRIMARY KEY AUTO_INCREMENT,
    MethodType VARCHAR(32) NOT NULL,
    customer_id INT,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id) ON DELETE CASCADE
);

-- new 
CREATE TABLE CardDetails (
    CardID INT PRIMARY KEY AUTO_INCREMENT,
    cardnum VARCHAR(32) NOT NULL,
    cardcvv VARCHAR(16) NOT NULL,
    expiryDate VARCHAR(16) NOT NULL,
    PaymentMethodID INT NOT NULL,
    FOREIGN KEY (PaymentMethodID) REFERENCES PaymentMethod(PaymentMethodID) ON DELETE CASCADE
);

CREATE TABLE Payments_order (
PaymentID INT PRIMARY KEY AUTO_INCREMENT,
OrderID INT NOT NULL,
PaymentMethodID INT NOT NULL,
PaymentDate DATE NOT NULL,
Amount DECIMAL(10, 2) NOT NULL,
FOREIGN KEY (OrderID) REFERENCES Orders(order_id) ON DELETE CASCADE,
FOREIGN KEY (PaymentMethodID) REFERENCES PaymentMethod(PaymentMethodID) ON DELETE CASCADE
);

CREATE TABLE Suppliers (
    supplier_id INT PRIMARY KEY AUTO_INCREMENT,
    SupplierName VARCHAR(100) NOT NULL,
    Phone VARCHAR(15),
    address VARCHAR(30)
);

CREATE TABLE Suppliers_Buy (
    quantity INT,
    buy_date DATE,
    emp_id INT NOT NULL,
    supplier_id INT NOT NULL,
    FOREIGN KEY (emp_id) REFERENCES Employees(emp_id) ON UPDATE CASCADE ON DELETE NO ACTION,
    FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Supplier_Products (
    supplier_id INT NOT NULL,
    product_name VARCHAR(100) NOT NULL, 
    price INT,
    PRIMARY KEY (supplier_id, product_name),
    FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id) ON DELETE CASCADE
);

-- Insert Products
INSERT INTO Products (product_id, product_name, price) 
VALUES 
(1, 'Lokma Meal Small', 20.0),
(2, 'Lokma Meal Small', 20.0),
(3, 'Lokma Meal Small', 20.0),
(4, 'Lokma Family Meal', 35.0),
(5, 'Lokma Family Meal', 35.0),
(6, 'Lokma Family Meal', 35.0),
(7, 'Crape', 18.0),
(8, 'Pan Cake', 20.0),
(9, 'Espresso', 6),
(10, 'Latte', 10),
(11, 'Hot Oreo', 10),
(12, 'Mango', 12),
(13, 'Grape and Watermelon', 14),
(14, 'Lemon and Mint', 10),
(15, 'Oreo MilkShake', 12),
(16, 'Corneto MilkShake', 14),
(17, 'Pistachio MilkShake', 15);

-- Insert Sweets
INSERT INTO Sweets (product_id, nuts_type, chocolate_Type) 
VALUES 
(1, 'Pistachio', 'Nutella'),
(2, 'Pistachio', 'White'),
(3, 'Peanut', 'Nutella'),
(4, 'Pistachio', 'Nutella'),
(5, 'Dried Coconut', 'Loutes'),
(6, 'None', 'White'),
(7, 'Peanut', 'Nutella and White'),
(8, 'Pistachio', 'Honey');

-- Insert Drinks
INSERT INTO Drinks (product_id, state, is_Sugar_Free) 
VALUES 
(9, 'Hot', 'Yes'),
(10, 'Hot', 'Yes'),
(11, 'Hot', 'No'),
(12, 'Smoothie', 'Yes'),
(13, 'Smoothie', 'No'),
(14, 'Smoothie', 'Yes'),
(15, 'Milk Shake', 'No'),
(16, 'Milk Shake', 'No'),
(17, 'Milk Shake', 'No');

-- Insert Employees
INSERT INTO Employees (emp_name, manger_id, phone, address, emp_role, salary) 
VALUES 
('Yahya', 1, '05982600008', 'Hebron', 'Manager', 9999),
('David Smith', null, '2233445566', '5678 Oak Street', 'Employee', 3000),
('Emily Davis', null, '3344556677', '9101 Pine Street', 'Employee', 3200),
('James Taylor', null, '4455667788', '3456 Maple Street', 'Employee', 2800);

-- Insert Customers
INSERT INTO Customers (customer_id, customer_name, phone, address) 
VALUES 
(1, 'John Doe', '1234567890', '123 Main St'),
(2, 'Jane Smith', '9876543210', '456 Elm St'),
(3, 'Alice Johnson', '1122334455', '789 Oak St'),
(4, 'Bob Brown', '5566778899', '101 Pine St');

-- Insert EmployeeLogin
INSERT INTO EmployeeLogin (Email, PasswordHash, EmployeeID) 
VALUES 
('yahya@lokma.com', '2004', 1),
('david.smith@lokma.com', '0000', 2),
('emily.davis@lokma.com', '0000', 3),
('james.taylor@lokma.com', '0000', 4);

-- Insert CustomerLogin
INSERT INTO CustomerLogin (Email, PasswordHash, CustomerID) 
VALUES 
('john.doe@example.com', '0000', 1),
('jane.smith@example.com', '0000', 2),
('alice.johnson@example.com', '0000', 3),
('bob.brown@example.com', '0000', 4);

-- Insert PaymentMethod
INSERT INTO PaymentMethod (MethodType, customer_id) 
VALUES 
('Credit Card', 1),
('Credit Card', 2),
('Cash', 3),
('Cash', 4),
('Debit Card', 2);

-- Insert CardDetails
INSERT INTO CardDetails (cardnum, cardcvv, expiryDate, PaymentMethodID) 
VALUES 
('1234567812345678', '123', '2025-01-01', 1),
('9876543210987654', '456', '2024-03-01', 2),
('2233445566778899', '654', '2027-09-01', 5);

-- Insert Orders
INSERT INTO Orders (customer_id, total_amount, rating) 
VALUES 
(1, 5000.00, 5),
(2, 20000.00, 4),
(3, 350.00, 5),
(4, 280.00, 3),
(1, 600.00, 5),
(3, 1500.00, NULL);

-- Insert Payments_order
INSERT INTO Payments_order (OrderID, PaymentMethodID, PaymentDate, Amount) 
VALUES 
(1, 1, '2025-01-01', 5000.00),
(2, 2, '2025-01-02', 20000.00),
(3, 3, '2025-01-03', 350.00),
(4, 4, '2025-01-06', 280.00),
(5, 5, '2025-01-07', 1500.00),
(1, 1, '2025-01-08', 600.00);

-- Insert Suppliers
INSERT INTO Suppliers (SupplierName, Phone, address) 
VALUES 
('Sweet Treats Co', '1234567890', '123 Sweet Street'),
('Nutty Supplier', '0987654321', '456 Nut Lane'),
('Dairy Dreams', '5678901234', '789 Flour Road'),
('Supplier Milk', '6789012345', '321 Milk Avenue');

-- Insert Supplier_Products
INSERT INTO Supplier_Products (supplier_id, product_name, price) 
VALUES 
(1, 'Chocolates', 500),
(2, 'Nuts', 200),
(3, 'Flour', 100),
(4, 'Milk', 150);

-- Insert Suppliers_Buy
INSERT INTO Suppliers_Buy (quantity, buy_date, emp_id, supplier_id) 
VALUES 
(100, '2024-12-09', 1, 1),
(200, '2024-12-20', 2, 2),
(150, '2024-12-29', 3, 3),
(250, '2024-12-15', 4, 4);

SELECT * FROM Suppliers;
SELECT * FROM Supplier_Products;
select * from EmployeeLogin;
SELECT * from Employees;

