DROP DATABASE IF EXISTS LOKMA;
CREATE DATABASE LOKMA;
USE LOKMA;

-- =========================
-- Lookup / reference tables
-- =========================
CREATE TABLE EmpRoles (
  role_id INT PRIMARY KEY AUTO_INCREMENT,
  role_name VARCHAR(32) UNIQUE NOT NULL
);

CREATE TABLE DrinkStates (
  state_id INT PRIMARY KEY AUTO_INCREMENT,
  state_name VARCHAR(32) UNIQUE NOT NULL
);

CREATE TABLE PaymentMethodTypes (
  method_type_id INT PRIMARY KEY AUTO_INCREMENT,
  method_type_name VARCHAR(32) UNIQUE NOT NULL
);

CREATE TABLE NutsTypes (
  nuts_type_id INT PRIMARY KEY AUTO_INCREMENT,
  nuts_type_name VARCHAR(32) UNIQUE NOT NULL
);

CREATE TABLE ChocolateTypes (
  chocolate_type_id INT PRIMARY KEY AUTO_INCREMENT,
  chocolate_type_name VARCHAR(32) UNIQUE NOT NULL
);

-- Seed lookups
INSERT INTO EmpRoles (role_name) VALUES ('Manager'), ('Employee');

INSERT INTO DrinkStates (state_name) VALUES
  ('Hot'), ('Cold'), ('Smoothie'), ('Milk Shake');

INSERT INTO PaymentMethodTypes (method_type_name) VALUES
  ('Cash'), ('Credit Card'), ('Debit Card');

INSERT INTO NutsTypes (nuts_type_name) VALUES
  ('Pistachio'), ('Peanut'), ('Dried Coconut'), ('None');

INSERT INTO ChocolateTypes (chocolate_type_name) VALUES
  ('Nutella'), ('White'), ('Loutes'), ('Nutella and White'), ('Honey');

-- =========================
-- Core entities
-- =========================
CREATE TABLE Employees (
  emp_id INT PRIMARY KEY AUTO_INCREMENT,
  manager_id INT NULL,
  emp_name VARCHAR(50) NOT NULL,
  phone VARCHAR(20),
  address VARCHAR(100),
  role_id INT NOT NULL,
  salary INT NOT NULL CHECK (salary >= 0),
  CONSTRAINT fk_emp_role   FOREIGN KEY (role_id) REFERENCES EmpRoles(role_id),
  CONSTRAINT fk_emp_mgr    FOREIGN KEY (manager_id) REFERENCES Employees(emp_id) ON DELETE SET NULL
);

CREATE TABLE Customers (
  customer_id INT PRIMARY KEY AUTO_INCREMENT,
  customer_name VARCHAR(50) NOT NULL,
  phone VARCHAR(20),
  address VARCHAR(100)
);

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
  product_name VARCHAR(64) NOT NULL,
  price DECIMAL(10,2) NOT NULL CHECK (price >= 0)
);

-- Which employee introduced/owns which product (many-to-many)
CREATE TABLE Product_Employee (
  product_id INT NOT NULL,
  emp_id INT NOT NULL,
  PRIMARY KEY (product_id, emp_id),
  FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE CASCADE,
  FOREIGN KEY (emp_id) REFERENCES Employees(emp_id) ON DELETE CASCADE
);

-- Product subtypes (1:1 with Products)
CREATE TABLE Sweets (
  product_id INT PRIMARY KEY,
  nuts_type_id INT NOT NULL,
  chocolate_type_id INT NOT NULL,
  FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE CASCADE,
  FOREIGN KEY (nuts_type_id) REFERENCES NutsTypes(nuts_type_id),
  FOREIGN KEY (chocolate_type_id) REFERENCES ChocolateTypes(chocolate_type_id)
);

CREATE TABLE Drinks (
  product_id INT PRIMARY KEY,
  state_id INT NOT NULL,
  is_sugar_free TINYINT(1) NOT NULL DEFAULT 0, -- 1=true, 0=false
  FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE CASCADE,
  FOREIGN KEY (state_id) REFERENCES DrinkStates(state_id)
);

-- Orders & payments
CREATE TABLE Orders (
  order_id INT PRIMARY KEY AUTO_INCREMENT,
  customer_id INT,
  total_amount DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (total_amount >= 0),
  rating INT DEFAULT NULL CHECK (rating BETWEEN 1 AND 5),
  FOREIGN KEY (customer_id) REFERENCES Customers(customer_id) ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE Order_Items (
  order_id INT NOT NULL,
  product_id INT NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
  quantity INT NOT NULL CHECK (quantity > 0),
  sub_price DECIMAL(10,2) AS (unit_price * quantity) STORED,
  PRIMARY KEY (order_id, product_id),
  FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES Products(product_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE PaymentMethod (
  PaymentMethodID INT PRIMARY KEY AUTO_INCREMENT,
  method_type_id INT NOT NULL,
  customer_id INT,
  FOREIGN KEY (method_type_id) REFERENCES PaymentMethodTypes(method_type_id),
  FOREIGN KEY (customer_id) REFERENCES Customers(customer_id) ON DELETE CASCADE
);

CREATE TABLE CardDetails (
  CardID INT PRIMARY KEY AUTO_INCREMENT,
  cardnum VARCHAR(32) NOT NULL,
  cardcvv VARCHAR(8) NOT NULL,
  expiryDate DATE NOT NULL,
  PaymentMethodID INT NOT NULL UNIQUE,
  FOREIGN KEY (PaymentMethodID) REFERENCES PaymentMethod(PaymentMethodID) ON DELETE CASCADE
);

CREATE TABLE Payments_order (
  PaymentID INT PRIMARY KEY AUTO_INCREMENT,
  OrderID INT NOT NULL,
  PaymentMethodID INT NOT NULL,
  PaymentDate DATE NOT NULL,
  Amount DECIMAL(10,2) NOT NULL CHECK (Amount >= 0),
  FOREIGN KEY (OrderID) REFERENCES Orders(order_id) ON DELETE CASCADE,
  FOREIGN KEY (PaymentMethodID) REFERENCES PaymentMethod(PaymentMethodID) ON DELETE CASCADE
);

-- Suppliers & procurement
CREATE TABLE Suppliers (
  supplier_id INT PRIMARY KEY AUTO_INCREMENT,
  SupplierName VARCHAR(100) NOT NULL,
  Phone VARCHAR(20),
  address VARCHAR(100)
);

CREATE TABLE Supplier_Products (
  supplier_product_id INT PRIMARY KEY AUTO_INCREMENT,
  supplier_id INT NOT NULL,
  product_name VARCHAR(100) NOT NULL,
  price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
  FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id) ON DELETE CASCADE,
  UNIQUE (supplier_id, product_name)
);

CREATE TABLE Suppliers_Buy (
  buy_id INT PRIMARY KEY AUTO_INCREMENT,
  supplier_product_id INT NOT NULL,
  quantity INT NOT NULL CHECK (quantity > 0),
  buy_date DATE NOT NULL,
  emp_id INT NOT NULL,
  FOREIGN KEY (supplier_product_id) REFERENCES Supplier_Products(supplier_product_id) ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (emp_id) REFERENCES Employees(emp_id) ON UPDATE CASCADE ON DELETE NO ACTION
);

-- =========================
-- Seed data
-- =========================

-- Employees (use role_id from EmpRoles)
INSERT INTO Employees (emp_name, manager_id, phone, address, role_id, salary) VALUES
  ('Yahya', NULL, '05982600008', 'Hebron', (SELECT role_id FROM EmpRoles WHERE role_name='Manager'), 9999),
  ('David Smith', NULL, '2233445566', '5678 Oak Street', (SELECT role_id FROM EmpRoles WHERE role_name='Employee'), 3000),
  ('Emily Davis', NULL, '3344556677', '9101 Pine Street', (SELECT role_id FROM EmpRoles WHERE role_name='Employee'), 3200),
  ('James Taylor', NULL, '4455667788', '3456 Maple Street', (SELECT role_id FROM EmpRoles WHERE role_name='Employee'), 2800);

-- Make Yahya his own manager logically null, and others report to Yahya
UPDATE Employees SET manager_id = emp_id WHERE role_id = (SELECT role_id FROM EmpRoles WHERE role_name='Manager');
UPDATE Employees SET manager_id = (SELECT emp_id FROM Employees WHERE emp_name='Yahya') WHERE emp_name IN ('David Smith','Emily Davis','James Taylor');

-- Customers
INSERT INTO Customers (customer_name, phone, address) VALUES
  ('John Doe', '1234567890', '123 Main St'),
  ('Jane Smith', '9876543210', '456 Elm St'),
  ('Alice Johnson', '1122334455', '789 Oak St'),
  ('Bob Brown', '5566778899', '101 Pine St');

-- Logins
INSERT INTO EmployeeLogin (Email, PasswordHash, EmployeeID) VALUES
  ('yahya@lokma.com', '2004', (SELECT emp_id FROM Employees WHERE emp_name='Yahya')),
  ('david.smith@lokma.com', '0000', (SELECT emp_id FROM Employees WHERE emp_name='David Smith')),
  ('emily.davis@lokma.com', '0000', (SELECT emp_id FROM Employees WHERE emp_name='Emily Davis')),
  ('james.taylor@lokma.com', '0000', (SELECT emp_id FROM Employees WHERE emp_name='James Taylor'));

INSERT INTO CustomerLogin (Email, PasswordHash, CustomerID) VALUES
  ('john.doe@example.com', '0000', 1),
  ('jane.smith@example.com', '0000', 2),
  ('alice.johnson@example.com', '0000', 3),
  ('bob.brown@example.com', '0000', 4);

-- Products
INSERT INTO Products (product_name, price) VALUES
  ('Lokma Meal Small', 20.00),
  ('Lokma Family Meal', 35.00),
  ('Crape', 18.00),
  ('Pan Cake', 20.00),
  ('Espresso', 6.00),
  ('Latte', 10.00),
  ('Hot Oreo', 10.00),
  ('Mango', 12.00),
  ('Grape and Watermelon', 14.00),
  ('Lemon and Mint', 10.00),
  ('Oreo MilkShake', 12.00),
  ('Corneto MilkShake', 14.00),
  ('Pistachio MilkShake', 15.00);

-- Sweets (map to product rows above)
-- Choose products that are sweets: Lokma Meal Small, Lokma Family Meal, Crape, Pan Cake
INSERT INTO Sweets (product_id, nuts_type_id, chocolate_type_id) VALUES
  ((SELECT product_id FROM Products WHERE product_name='Lokma Meal Small' LIMIT 1),
    (SELECT nuts_type_id FROM NutsTypes WHERE nuts_type_name='Pistachio'),
    (SELECT chocolate_type_id FROM ChocolateTypes WHERE chocolate_type_name='Nutella')),
  ((SELECT product_id FROM Products WHERE product_name='Lokma Family Meal' LIMIT 1),
    (SELECT nuts_type_id FROM NutsTypes WHERE nuts_type_name='Pistachio'),
    (SELECT chocolate_type_id FROM ChocolateTypes WHERE chocolate_type_name='Nutella')),
  ((SELECT product_id FROM Products WHERE product_name='Crape' LIMIT 1),
    (SELECT nuts_type_id FROM NutsTypes WHERE nuts_type_name='Peanut'),
    (SELECT chocolate_type_id FROM ChocolateTypes WHERE chocolate_type_name='Nutella and White')),
  ((SELECT product_id FROM Products WHERE product_name='Pan Cake' LIMIT 1),
    (SELECT nuts_type_id FROM NutsTypes WHERE nuts_type_name='Pistachio'),
    (SELECT chocolate_type_id FROM ChocolateTypes WHERE chocolate_type_name='Honey'));

-- Drinks
INSERT INTO Drinks (product_id, state_id, is_sugar_free) VALUES
  ((SELECT product_id FROM Products WHERE product_name='Espresso'), (SELECT state_id FROM DrinkStates WHERE state_name='Hot'), 1),
  ((SELECT product_id FROM Products WHERE product_name='Latte'), (SELECT state_id FROM DrinkStates WHERE state_name='Hot'), 1),
  ((SELECT product_id FROM Products WHERE product_name='Hot Oreo'), (SELECT state_id FROM DrinkStates WHERE state_name='Hot'), 0),
  ((SELECT product_id FROM Products WHERE product_name='Mango'), (SELECT state_id FROM DrinkStates WHERE state_name='Smoothie'), 1),
  ((SELECT product_id FROM Products WHERE product_name='Grape and Watermelon'), (SELECT state_id FROM DrinkStates WHERE state_name='Smoothie'), 0),
  ((SELECT product_id FROM Products WHERE product_name='Lemon and Mint'), (SELECT state_id FROM DrinkStates WHERE state_name='Smoothie'), 1),
  ((SELECT product_id FROM Products WHERE product_name='Oreo MilkShake'), (SELECT state_id FROM DrinkStates WHERE state_name='Milk Shake'), 0),
  ((SELECT product_id FROM Products WHERE product_name='Corneto MilkShake'), (SELECT state_id FROM DrinkStates WHERE state_name='Milk Shake'), 0),
  ((SELECT product_id FROM Products WHERE product_name='Pistachio MilkShake'), (SELECT state_id FROM DrinkStates WHERE state_name='Milk Shake'), 0);

-- Payment Methods (using lookup)
INSERT INTO PaymentMethod (method_type_id, customer_id) VALUES
  ((SELECT method_type_id FROM PaymentMethodTypes WHERE method_type_name='Credit Card'), 1),
  ((SELECT method_type_id FROM PaymentMethodTypes WHERE method_type_name='Credit Card'), 2),
  ((SELECT method_type_id FROM PaymentMethodTypes WHERE method_type_name='Cash'), 3),
  ((SELECT method_type_id FROM PaymentMethodTypes WHERE method_type_name='Cash'), 4),
  ((SELECT method_type_id FROM PaymentMethodTypes WHERE method_type_name='Debit Card'), 2);

-- CardDetails only for card methods (dates normalized to DATE)
INSERT INTO CardDetails (cardnum, cardcvv, expiryDate, PaymentMethodID) VALUES
  ('1234567812345678', '123', '2025-01-01', 1),
  ('9876543210987654', '456', '2024-03-01', 2),
  ('2233445566778899', '654', '2027-09-01', 5);

-- Orders
INSERT INTO Orders (customer_id, total_amount, rating) VALUES
  (1, 5000.00, 5),
  (2, 20000.00, 4),
  (3, 350.00, 5),
  (4, 280.00, 3),
  (1, 600.00, 5),
  (3, 1500.00, NULL);

-- Order Items (snapshot unit_price; compute sub_price)
-- Example items for order 1 and 2 to be consistent with totals
INSERT INTO Order_Items (order_id, product_id, unit_price, quantity) VALUES
  (1, (SELECT product_id FROM Products WHERE product_name='Lokma Family Meal'), 35.00, 50), -- 1750
  (1, (SELECT product_id FROM Products WHERE product_name='Oreo MilkShake'), 12.00, 50),    -- 600
  (1, (SELECT product_id FROM Products WHERE product_name='Latte'), 10.00, 265),            -- 2650  -> total 5000
  (2, (SELECT product_id FROM Products WHERE product_name='Lokma Meal Small'), 20.00, 500), -- 10000
  (2, (SELECT product_id FROM Products WHERE product_name='Corneto MilkShake'), 14.00, 300),-- 4200
  (2, (SELECT product_id FROM Products WHERE product_name='Pistachio MilkShake'), 15.00, 400); -- 6000 -> total 20200 (example)

-- Payments (leave as provided)
INSERT INTO Payments_order (OrderID, PaymentMethodID, PaymentDate, Amount) VALUES
  (1, 1, '2025-01-01', 5000.00),
  (2, 2, '2025-01-02', 20000.00),
  (3, 3, '2025-01-03', 350.00),
  (4, 4, '2025-01-06', 280.00),
  (5, 5, '2025-01-07', 1500.00),
  (1, 1, '2025-01-08', 600.00);

-- Suppliers
INSERT INTO Suppliers (SupplierName, Phone, address) VALUES
  ('Sweet Treats Co', '1234567890', '123 Sweet Street'),
  ('Nutty Supplier', '0987654321', '456 Nut Lane'),
  ('Dairy Dreams', '5678901234', '789 Flour Road'),
  ('Supplier Milk', '6789012345', '321 Milk Avenue');

-- Supplier Products (normalized, unique per supplier)
INSERT INTO Supplier_Products (supplier_id, product_name, price) VALUES
  ((SELECT supplier_id FROM Suppliers WHERE SupplierName='Sweet Treats Co'), 'Chocolates', 500.00),
  ((SELECT supplier_id FROM Suppliers WHERE SupplierName='Nutty Supplier'), 'Nuts', 200.00),
  ((SELECT supplier_id FROM Suppliers WHERE SupplierName='Dairy Dreams'), 'Flour', 100.00),
  ((SELECT supplier_id FROM Suppliers WHERE SupplierName='Supplier Milk'), 'Milk', 150.00);

-- Purchases (now reference specific supplier_product_id)
INSERT INTO Suppliers_Buy (supplier_product_id, quantity, buy_date, emp_id) VALUES
  ((SELECT supplier_product_id FROM Supplier_Products sp JOIN Suppliers s ON sp.supplier_id=s.supplier_id WHERE s.SupplierName='Sweet Treats Co' AND sp.product_name='Chocolates'), 100, '2024-12-09', (SELECT emp_id FROM Employees WHERE emp_name='Yahya')),
  ((SELECT supplier_product_id FROM Supplier_Products sp JOIN Suppliers s ON sp.supplier_id=s.supplier_id WHERE s.SupplierName='Nutty Supplier' AND sp.product_name='Nuts'), 200, '2024-12-20', (SELECT emp_id FROM Employees WHERE emp_name='David Smith')),
  ((SELECT supplier_product_id FROM Supplier_Products sp JOIN Suppliers s ON sp.supplier_id=s.supplier_id WHERE s.SupplierName='Dairy Dreams' AND sp.product_name='Flour'), 150, '2024-12-29', (SELECT emp_id FROM Employees WHERE emp_name='Emily Davis')),
  ((SELECT supplier_product_id FROM Supplier_Products sp JOIN Suppliers s ON sp.supplier_id=s.supplier_id WHERE s.SupplierName='Supplier Milk' AND sp.product_name='Milk'), 250, '2024-12-15', (SELECT emp_id FROM Employees WHERE emp_name='James Taylor'));
