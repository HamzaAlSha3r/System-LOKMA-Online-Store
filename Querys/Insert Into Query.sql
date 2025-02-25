-- Inserting products

insert into Employees (emp_name, manger_id,phone, address,emp_role) values ("yahya" , 1,"05982600008" , "Hebron", "Manger");
INSERT INTO Login (Email, PasswordHash, UserType, EmployeeID, CustomerID) VALUES ('yahya@lokma.com', '2004', 'Manger', 1, NULL);

INSERT INTO Products (product_id, product_name, price, emp_id) VALUES (1, 'Lokma Meal Small', 20.0 , null);
INSERT INTO Products (product_id, product_name, price, emp_id) VALUES (2, 'Lokma Meal Small', 20.0 , null);
INSERT INTO Products (product_id, product_name, price, emp_id) VALUES (3, 'Lokma Meal Small', 20.0 , null);
INSERT INTO Products (product_id, product_name, price, emp_id) VALUES (4, 'Lokma Family Meal ', 35.0 , null);
INSERT INTO Products (product_id, product_name, price, emp_id) VALUES (5, 'Lokma Family Meal ', 35.0 , null);
INSERT INTO Products (product_id, product_name, price, emp_id) VALUES (6, 'Lokma Family Meal ', 35.0 , null);
INSERT INTO Products (product_id, product_name, price, emp_id) VALUES (7, 'Crape', 18.0 , null);
INSERT INTO Products (product_id, product_name, price, emp_id) VALUES (8, 'Pan cake', 20.0 , null);
INSERT INTO Sweets (product_id, nuts_type, chocolate_Type) VALUES (1, 'Pistashio', "nutella");
INSERT INTO Sweets (product_id, nuts_type, chocolate_Type) VALUES (2, 'Pistashio', "white");
INSERT INTO Sweets (product_id, nuts_type, chocolate_Type) VALUES (3, 'peanut', "nutella");
INSERT INTO Sweets (product_id, nuts_type, chocolate_Type) VALUES (4, 'Pistashio', "nutella");
INSERT INTO Sweets (product_id, nuts_type, chocolate_Type) VALUES (5, 'dried coconut', "Loutes");
INSERT INTO Sweets (product_id, nuts_type, chocolate_Type) VALUES (6, 'none', "white");
INSERT INTO Sweets (product_id, nuts_type, chocolate_Type) VALUES (7, 'peanut', "nutella and white");
INSERT INTO Sweets (product_id, nuts_type, chocolate_Type) VALUES (8, 'Pistashio', "honey");

INSERT INTO Products (product_id, product_name, price, emp_id) VALUES (9, 'esspresso', 6 , null);
INSERT INTO Products (product_id, product_name, price, emp_id) VALUES (10, 'latte', 10 , null);
INSERT INTO Products (product_id, product_name, price, emp_id) VALUES (11, 'hot oreo', 10 , null);
INSERT INTO Drinks (product_id, state, is_Sugar_Free) VALUES (9, 'Hot', "yes");
INSERT INTO Drinks (product_id, state, is_Sugar_Free) VALUES (10, 'Hot', "yes");
INSERT INTO Drinks (product_id, state, is_Sugar_Free) VALUES (11, 'Hot', "no");

INSERT INTO Products (product_id, product_name, price, emp_id) VALUES (12, 'Mango', 12 , null);
INSERT INTO Products (product_id, product_name, price, emp_id) VALUES (13, 'Grape and Watermelon', 14, null);
INSERT INTO Products (product_id, product_name, price, emp_id) VALUES (14, 'Lemon and Mint', 10 , null);
INSERT INTO Drinks (product_id, state, is_Sugar_Free) VALUES (12, 'Smothie', "yes");
INSERT INTO Drinks (product_id, state, is_Sugar_Free) VALUES (13, 'Smothie', "no");
INSERT INTO Drinks (product_id, state, is_Sugar_Free) VALUES (14, 'Smothie', "yes");

INSERT INTO Products (product_id, product_name, price, emp_id) VALUES (15, 'Oreo MilkShake', 12, null);
INSERT INTO Products (product_id, product_name, price, emp_id) VALUES (16, 'Corneto MilkShake', 14, null);
INSERT INTO Products (product_id, product_name, price, emp_id) VALUES (17, 'Pistashio MilkShake', 15, null);
INSERT INTO Drinks (product_id, state, is_Sugar_Free) VALUES (15, 'Milk Shake', "no");
INSERT INTO Drinks (product_id, state, is_Sugar_Free) VALUES (16, 'Milk Shake', "no");
INSERT INTO Drinks (product_id, state, is_Sugar_Free) VALUES (17, 'Milk Shake', "no");






