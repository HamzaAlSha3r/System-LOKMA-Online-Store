from flask import Flask, redirect, url_for, render_template, request, session, flash
import pymysql
import mysql.connector
from mysql.connector import IntegrityError, Error
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from markupsafe import escape
from decimal import Decimal, InvalidOperation
import re

app = Flask(__name__)
app.secret_key = "hello"

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2710",
    database="LOKMA"
)
mycursor_tuple = conn.cursor()
mycursor_dict = conn.cursor(dictionary=True)

# ------------------------------- input handling helpers (added)
def _clean_str(val, max_len=255):
    if val is None:
        return ""
    val = str(val).strip()
    # remove control chars
    val = re.sub(r"[\x00-\x1f\x7f]", "", val)
    if len(val) > max_len:
        val = val[:max_len]
    return val

def _to_int(val, default=None):
    try:
        return int(str(val).strip())
    except (ValueError, TypeError):
        return default

def _to_float(val, default=None):
    try:
        return float(str(val).strip())
    except (ValueError, TypeError):
        return default

def _to_decimal(val, default=None):
    try:
        return Decimal(str(val).strip())
    except (InvalidOperation, ValueError, TypeError):
        return default

def _to_bool01(val):
    if val is None:
        return '0'
    s = str(val).strip().lower()
    return '1' if s in {'1','true','on','yes','y'} else '0'

def _enum(val, allowed, default=None):
    v = _clean_str(val)
    return v if v in allowed else default

def _ymd(val):
    s = _clean_str(val)
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return s
    except ValueError:
        return None

def _session_int(key):
    return _to_int(session.get(key), None)

def _session_str(key, max_len=255):
    return _clean_str(session.get(key), max_len=max_len)

# ----------------------------------------------------------------

@app.route('/index')
def hello():
    return render_template("index.html")

@app.route('/')
def home():
    session.clear()
    return render_template("index.html",sweetsL=get_sweets(),hotDrinksL=get_hot_drinks(),smothiesL=get_smothies(),milksL=get_milks())

def get_sweets():
    try:
        mycursor_tuple.execute("SELECT p.product_id, p.product_name, p.price, s.nuts_type, s.chocolate_type FROM Products p, Sweets s WHERE p.product_id = s.product_id")
        sweets = mycursor_tuple.fetchall()
        sweetsL = []
        sweetsL.clear()
        for s in sweets:
            img_name = str(s[1]).replace(" ", "").replace("_", "")
            stu_der = {
                "product_id": s[0],
                "product_name": s[1],
                "price": s[2],
                "nuts_type": s[3],
                "chocolate_type": s[4],
                "img": img_name
            }
            sweetsL.append(stu_der)
        print('Access')
        return sweetsL
    except Exception as ex :
        return []

def get_hot_drinks():
    try:
        mycursor_tuple.execute("""
        SELECT p.product_id, p.product_name, p.price, d.state, d.is_sugar_free
        FROM Products p, Drinks d
        WHERE p.product_id = d.product_id AND d.state LIKE 'Hot'
        """)
        hotDrinks = mycursor_tuple.fetchall()
        hotDrinksL= []
        hotDrinksL.clear()
        for s in hotDrinks:
            img_name = str(s[1]).replace(" ", "").replace("_", "")
            hot_der = {
                "product_id": s[0],
                "product_name": s[1],
                "price": s[2],
                "state": s[3],
                "is_sugar_free": s[4],
                "img": img_name
            }
            hotDrinksL.append(hot_der)
        print('Access')
        return hotDrinksL
    except Exception as e:
        return []

def get_smothies():
    try:
        mycursor_tuple.execute("""
        SELECT p.product_id, p.product_name, p.price, d.state, d.is_sugar_free
        FROM Products p, Drinks d
        WHERE p.product_id = d.product_id AND d.state LIKE 'Smothie'
        """)
        smothies = mycursor_tuple.fetchall()
        smothiesL= []
        smothiesL.clear()
        for s in smothies:
            img_name = str(s[1]).replace(" ", "").replace("_", "")
            smo_der = {
                "product_id": s[0],
                "product_name": s[1],
                "price": s[2],
                "state": s[3],
                "is_sugar_free": s[4],
                "img": img_name
            }
            smothiesL.append(smo_der)
        print('Access')
        return smothiesL
    except Exception as ex:
        return []

def get_milks():
    try:
        mycursor_tuple.execute("""
        SELECT p.product_id, p.product_name, p.price, d.state, d.is_sugar_free
        FROM Products p, Drinks d
        WHERE p.product_id = d.product_id AND d.state LIKE 'Milk Shake'
        """)
        milks = mycursor_tuple.fetchall()
        milksL = []
        milksL.clear()
        for s in milks:
            img_name = str(s[1]).replace(" ", "").replace("_", "")
            mil_der = {
                "product_id": s[0],
                "product_name": s[1],
                "price": s[2],
                "state": s[3],
                "is_sugar_free": s[4],
                "img": img_name
            }
            milksL.append(mil_der)
        print('Access')
        return milksL
    except Exception as ex:
        return []

# ------------------------------------------------------------------------------------- customer
@app.route('/Customer')
def customer():
    if session.get('user_type') != 'Customer':
        flash("Unauthorized access. Please log in.")
        return render_template('login.html')
    
    # gets the cached lists from session or fetch them if not available
    sweetsL = session.get('sweetsL', get_sweets())
    hotDrinksL = session.get('hotDrinksL', get_hot_drinks())
    smothiesL = session.get('smothiesL', get_smothies())
    milksL = session.get('milksL', get_milks())
    customer_id = _session_int('customer_id')
    customer_name = get_customer_name(customer_id)
    
    return render_template('customerHome.html', sweetsL=sweetsL, hotDrinksL=hotDrinksL, smothiesL=smothiesL, milksL=milksL, customerName=customer_name)

@app.route('/cart',methods=['GET'])
def cart():
    # this query gets the products in the current cart (order) for the current loged in customer
    cid = _session_int('customer_id')
    oid = _session_int('order_id')
    if cid is None or oid is None:
        flash("Please log in first.")
        return render_template('login.html')

    getProductsQuery = '''SELECT P.product_id,P.product_name,OP.quantity,OP.sub_price,P.price
                          FROM Orders O
                          JOIN Order_Product OP ON O.order_id = OP.order_id
                          JOIN Products P ON OP.product_id = P.product_id
                          WHERE O.customer_id = %s AND O.order_id = %s'''
    mycursor_tuple.execute(getProductsQuery, (cid, oid))
    products = mycursor_tuple.fetchall()
    productsL = []
    for s in products:
        prod_der = {
            "product_id" : s[0],
            "product_name" : s[1],
            "quantity" : s[2],
            "oneitemprice" : s[4],
            "price" : s[3]
        }
        productsL.append(prod_der)
    # this query uses the sum function in the SQL to cart price to pay 
    getTotalPrice = '''SELECT sum(OP.sub_price)
                          FROM Orders O
                          JOIN Order_Product OP ON O.order_id = OP.order_id
                          JOIN Products P ON OP.product_id = P.product_id
                          WHERE O.customer_id = %s AND O.order_id = %s;'''
    mycursor_tuple.execute(getTotalPrice, (cid, oid))
    totalPrice =  mycursor_tuple.fetchone()[0]
    if not totalPrice:
        totalPrice = 0
    # query to update the total_amount of the order , but still not payed
    updateOrderDetailsQuery = 'UPDATE Orders SET total_amount = %s WHERE order_id = %s'
    mycursor_tuple.execute(updateOrderDetailsQuery, (totalPrice, oid))
    # this query checks if there is old cards the current customer added and payed with 
    checkIfThereisOldPayMethodQuery = """Select pm.PaymentMethodID, cd.cardNum
                                         From PaymentMethod pm, CardDetails cd
                                         Where pm.PaymentMethodID = cd.PaymentMethodID AND pm.MethodType Like 'Credit Card' AND pm.customer_id=%s"""
    mycursor_tuple.execute(checkIfThereisOldPayMethodQuery, (cid,))
    methods = mycursor_tuple.fetchall()
    methodsL = []
    for m in methods:
        payM_der={
            'PaymentMethodID' : m[0],
            'cardNum' : m[1]
        }
        methodsL.append(payM_der)

    conn.commit()
    return render_template('customerCart.html',order_id=oid,productsL=productsL,totalPrice=totalPrice,methodsL=methodsL)

@app.route('/cart/pay',methods=['POST'])
def payOrder():
    # this query just to make sure the cart is not empty , so it dont make since to pay a empty cart 
    cid = _session_int('customer_id')
    oid = _session_int('order_id')
    if cid is None or oid is None:
        flash("Please log in first.")
        return render_template('login.html')

    checkIfCartEmptyQuery = '''SELECT P.product_id
                               FROM Orders O
                               JOIN Order_Product OP ON O.order_id = OP.order_id
                               JOIN Products P ON OP.product_id = P.product_id
                               WHERE O.customer_id = %s AND O.order_id = %s'''
    mycursor_tuple.execute(checkIfCartEmptyQuery, (cid, oid))
    checkresult = mycursor_tuple.fetchall()
    if not checkresult:
        flash("Your Cart is Empty, nothing to pay for ")
        return redirect(url_for('cart'))
    # now getting the choosed paymentMethod form the customer to pay with  
    payMethod_raw = request.form.get('payment_method', '')
    payMethod = _enum(payMethod_raw, {'Cash','Credit Card'}, None)
    if payMethod == 'Cash':
        # inserting the payment to the PaymentMethod tabel and get the payment id
        addPaymentQuery = 'Insert into PaymentMethod (customer_id, MethodType) values (%s,"Cash")'
        mycursor_tuple.execute(addPaymentQuery, (cid,))
        getPayMethodIDQuery = """Select PaymentMethodID 
                                From PaymentMethod 
                                Where MethodType like %s and customer_id = %s
                                Order by PaymentMethodID DESC"""
        mycursor_tuple.execute(getPayMethodIDQuery, (payMethod, cid))
        payMethodID = mycursor_tuple.fetchone()[0]
        print(payMethodID)
        mycursor_tuple.fetchall() # just to clear the cursor
    elif payMethod == 'Credit Card': 
        # this for adding a new card to pay with ,getting the card data and insert it to PaymentMethod and CardDetails tabels
        cardNum = _clean_str(request.form.get('card_number'), max_len=32)
        expiryDate = _clean_str(request.form.get('expiry_date'), max_len=10)
        cvv = _clean_str(request.form.get('cvv'), max_len=4)
        addPaymentQuery = 'Insert Into PaymentMethod (customer_id, MethodType) values (%s,"Credit Card")'
        mycursor_tuple.execute(addPaymentQuery, (cid,))
        addCardDeailsQuery = """Insert Into CardDetails (cardNum,cardcvv,expiryDate,paymentMethodID) values (%s,%s,%s,LAST_INSERT_ID())"""
        mycursor_tuple.execute(addCardDeailsQuery, (cardNum, cvv, expiryDate))
        getPayMethodIDQuery ="""Select pm.PaymentMethodID 
                                From PaymentMethod pm,CardDetails cd 
                                Where pm.paymentMethodID = cd.paymentMethodID AND pm.MethodType like %s and pm.customer_id = %s and cd.cardnum=%s"""
        mycursor_tuple.execute(getPayMethodIDQuery, (payMethod, cid, cardNum))
        payMethodID = mycursor_tuple.fetchone()[0]
        print(payMethodID)
        mycursor_tuple.fetchall()
    else : # this for paying with an old card , payMethodID stored in the html as a input
        payMethodID = _to_int(payMethod_raw, None)
        if payMethodID is None:
            flash("Invalid payment method.")
            return redirect(url_for('cart'))

    # adding the payment record to  Payments_order tabel to , mark this order as a payed order 
    total_price_str = request.form.get('totalPrice')
    total_price = _to_decimal(total_price_str, Decimal('0'))
    payTheOrderQuery = "INSERT INTO Payments_order (OrderID, PaymentMethodID, PaymentDate, Amount) VALUES (%s, %s, CURDATE(), %s);"
    mycursor_tuple.execute(payTheOrderQuery, (oid, payMethodID, str(total_price)))
    customerRating = _to_int(request.form.get("rate"), None)
    customerRatingQuery = 'UPDATE Orders SET rating = %s WHERE order_id = %s'
    mycursor_tuple.execute(customerRatingQuery, (customerRating, oid))
    conn.commit()
    # creating a new order (cart) for the current customer 
    create_order(cid)
    getOrderIDQuery = 'Select order_id From Orders Where customer_id = %s Order by order_id DESC'
    mycursor_tuple.execute(getOrderIDQuery,(cid,))
    orderID = mycursor_tuple.fetchone()[0]
    mycursor_tuple.fetchall()
    session['order_id'] = orderID
    return redirect(url_for('cart'))

@app.route('/orders_history')
def customerOrdersHistory():
    # join with Payments_order, PaymentMethod, CardDetails to get all the information of the order that was placed using Cards (not Cash)
    cid = _session_int('customer_id')
    if cid is None:
        flash("Please log in first.")
        return redirect(url_for('login'))

    getCustOrdersWithCardQuery = """SELECT o.order_id, o.total_amount, o.rating, po.PaymentDate, p.MethodType, cd.cardnum
                            FROM Orders o
                            JOIN Payments_order po ON o.order_id = po.OrderID
                            JOIN PaymentMethod p ON po.PaymentMethodID = p.PaymentMethodID
                            JOIN CardDetails cd ON cd.PaymentMethodID = p.PaymentMethodID
                            WHERE o.customer_id = %s 
                            Order by po.PaymentDate"""
    mycursor_tuple.execute(getCustOrdersWithCardQuery,(cid,))
    orders = mycursor_tuple.fetchall()
    ordersL = []
    for o in orders:
        ord_der={
            'order_id': o[0],
            'total_amount': o[1],
            'rating' : o[2],
            'PaymentDate' : o[3],
            'MethodType' : o[4],
            'cardnum' : o[5]
        }
        ordersL.append(ord_der)
        # join with Payments_order, PaymentMethod to get all the information of the order that was placed using Cash
    getCustOrdersWithCashQuery = """SELECT o.order_id, o.total_amount, o.rating, po.PaymentDate, p.MethodType
                            FROM Orders o
                            JOIN Payments_order po ON o.order_id = po.OrderID
                            JOIN PaymentMethod p ON po.PaymentMethodID = p.PaymentMethodID
                            WHERE o.customer_id = %s AND p.MethodType Like 'Cash'
                            Order by po.PaymentDate"""
    mycursor_tuple.execute(getCustOrdersWithCashQuery,(cid,))
    orders2 = mycursor_tuple.fetchall()
    for o in orders2:
        ord_der={
            'order_id': o[0],
            'total_amount': o[1],
            'rating' : o[2],
            'PaymentDate' : o[3],
            'MethodType' : o[4],
            'cardnum' : '---'
        }
        ordersL.append(ord_der)
    return render_template('customerOrdersHistory.html',customerName=session.get('customer_name'),ordersL=ordersL)

@app.route('/employee/add_new_product')
def addNewProduct():
    if session.get('user_type') != 'Employee':
        flash("Unauthorized access. Only employees can add sweets.")
        return render_template('error.html')
    else:
        empID = _session_int('employee_id')
        query = "SELECT emp_name FROM Employees WHERE emp_id=%s"
        mycursor_tuple.execute(query, (empID,))
        empName = mycursor_tuple.fetchone()[0]
        flash(f"{empName}")
        return render_template('insertProduct.html', empName=empName,empID=empID)

@app.route('/employee/add_sweet', methods=['GET','POST'])
def insert_sweet():
    if session.get('user_type') != 'Employee':
        flash("Unauthorized access. Only employees can add sweets.")
        return render_template('error.html')
    
    if request.method == 'GET':
        return render_template('insertProduct.html')
    # getting the product data from the html form 
    if request.method == 'POST':
        product_id = _to_int(request.form.get('product_id'), None)
        product_name = _clean_str(request.form.get('product_name'), max_len=120)
        price = _to_decimal(request.form.get('price'), Decimal('0'))
        nuts_type = _clean_str(request.form.get('nuts_type'), max_len=64)
        chocolate_type = _clean_str(request.form.get('chocolate_type', '0'), max_len=64)  
        emp_id = _session_int('employee_id')

        if product_id is None or product_name == "" or price is None:
            flash("Invalid product input.")
            return render_template('insertProduct.html')

        # inserting the sweet
        mycursor_tuple.execute('''INSERT INTO Products (product_id,product_name, price) 
                            VALUES (%s, %s, %s)''', 
                        (product_id, product_name, str(price)))
        conn.commit()
        mycursor_tuple.execute('''INSERT INTO Sweets (product_id, nuts_type, chocolate_type) 
                        VALUES (%s, %s, %s)''', 
                        (product_id, nuts_type, chocolate_type))
        conn.commit()
        # inserting a record for the employee that inserted this sweet
        mycursor_tuple.execute('''INSERT INTO Product_Employee (product_id, emp_id) 
                        VALUES (%s, %s)''', 
                        (product_id, emp_id))
        conn.commit()
        return redirect(url_for('employeeHome'))  
    
# employee add new drink to the system 
@app.route('/employee/add_drink', methods=['GET','POST'])
def insert_drink():
    # Ensure user is an employee
    if session.get('user_type') != 'Employee':
        flash("Unauthorized access. Only employees can add drinks.")
        return render_template('error.html')
    if request.method == 'GET':
        flash("Only Employees allowed to insert new Drinks")
        return render_template('insertProduct.html')
    # getting new drink information from the html form 
    if request.method == 'POST':
        product_id = _to_int(request.form.get('product_id'), None)
        product_name = _clean_str(request.form.get('product_name'), max_len=120)
        price = _to_decimal(request.form.get('price'), Decimal('0'))
        state = _enum(request.form.get('state'), {'Hot','Smothie','Milk Shake','Cold'}, None)
        isSugarFree = _to_bool01(request.form.get('is_sugar_free', '0'))  
        emp_id = _session_int('employee_id')

        if product_id is None or product_name == "" or price is None or state is None:
            flash("Invalid drink input.")
            return render_template('insertProduct.html')

        # add the new Drink
        mycursor_tuple.execute('''INSERT INTO Products (product_id,product_name, price) 
                            VALUES (%s, %s, %s)''', 
                        (product_id, product_name, str(price)))
        conn.commit()
        mycursor_tuple.execute('''INSERT INTO Drinks (product_id, state, is_Sugar_Free) 
                        VALUES (%s, %s, %s)''', 
                        (product_id, state, isSugarFree))
        conn.commit()
        # inserting a record for the employee that inserted this drink
        mycursor_tuple.execute('''INSERT INTO Product_Employee (product_id, emp_id) 
                        VALUES (%s, %s)''', 
                        (product_id, emp_id))
        conn.commit()
        return redirect(url_for('employeeHome'))

@app.route('/employee/OrderFromSupplier', methods=['GET','POST'])
def buy_from_supplier():
    if session.get('user_type') != 'Employee':
        flash("Unauthorized access. Only employees can add sweets.")
        return render_template('error.html')
    empID = _session_int('employee_id')
    query = "SELECT emp_name FROM Employees WHERE emp_id=%s"
    mycursor_tuple.execute(query, (empID,))
    empName = mycursor_tuple.fetchone()[0]
    getSupliersQuery="""Select supplier_id, SupplierName
                        From Suppliers   """
    mycursor_tuple.execute(getSupliersQuery)
    suppliers = mycursor_tuple.fetchall()
    suppliersL =[]
    for s in suppliers:
        sup_der={
            'supplier_id' : s[0],
            'SupplierName' : s[1]
        }
        suppliersL.append(sup_der)
    session['suppliersL'] = suppliersL
    if request.method == 'GET':
        flash(f"{empName}")
        return render_template('buyFromSupplier.html',empName=empName,empID=empID,suppliersL=suppliersL)

@app.route('/employee/getSupplierProducts',methods=['POST'])
def getSelectedSupplierProducts():
    supplierID = _to_int(request.form.get('supplierName'), None)
    if supplierID is None:
        flash("Invalid supplier.")
        return redirect(url_for('buy_from_supplier'))
    getSelectedSupplierProductsQuery = """Select product_name 
                                          From Supplier_Products
                                          Where supplier_id = %s"""
    mycursor_tuple.execute(getSelectedSupplierProductsQuery,(supplierID,))
    products = mycursor_tuple.fetchall()
    productsL =[]
    for p in products:
        der={
            'product_name' : p[0]
        }
        productsL.append(der)
    print(productsL)
    empID = _session_int('employee_id')
    query = "SELECT emp_name FROM Employees WHERE emp_id=%s"
    mycursor_tuple.execute(query, (empID,))
    empName = mycursor_tuple.fetchone()[0]
    return render_template('buyFromSupplierAfter.html',empName=empName,empID=empID,suppliersL=session.get('suppliersL',[]),productsL=productsL,supplierID=supplierID)

@app.route('/employee/PlaceOrderFromSupplier',methods=['POST'])
def placeOrderFromSupplier():
    if request.method == 'POST':
        supplierID = _to_int(request.form.get('supplierName'), None)
        quantity = _to_int(request.form.get('quantity'), None)
        productName = _clean_str(request.form.get('product_name'), max_len=120)
        emp_id = _session_int('employee_id')
        if supplierID is None or quantity is None or productName == "":
            flash("Invalid supplier order input.")
            return redirect(url_for('buy_from_supplier'))
        # employee buying operations from suplliers recorded in the Suppliers_Buy tabel
        addingTheBuyQuery = """INSERT INTO Suppliers_Buy (quantity, emp_id, buy_date, supplier_id) 
                                VALUES (%s,%s,CURDATE(),%s)"""
        mycursor_tuple.execute(addingTheBuyQuery, (quantity, emp_id, supplierID))
        conn.commit()
        return redirect(url_for('buy_from_supplier'))

@app.route('/Customer/add_sweet_to_cart' ,methods=['GET','POST'])
def addSweetToCustomerCart() :
    if request.method == 'POST':
        if session.get('user_type',None) != 'Customer':
            flash("You need to login before you add to your cart,.")
            return render_template('login.html')
        orderID = _session_int('order_id')
        if not orderID:
            flash("No active order found. Please start a new order.")
            return render_template('login.html')
        
        quantity = _to_int(request.form.get('quantity'), None)
        productID = _to_int(request.form.get('product_id'), None)
        if quantity is None or productID is None:
            flash('Invalid item input.')
            return redirect(url_for('customer'))

        checkIfInCartQuery = """ Select quantity 
                                 From Order_Product 
                                 Where order_id= %s AND product_id= %s """
        mycursor_tuple.execute(checkIfInCartQuery,(orderID,productID))
        quantityInCart = mycursor_tuple.fetchone()
        if quantityInCart :
            existingQuantity = quantityInCart[0]
            newQuantity = existingQuantity + int(quantity)
            productPrice = _to_decimal(request.form.get('price'), None)
            if productPrice is not None:
                subPrice = float(productPrice) * newQuantity
            else:
                subPrice = 0  

            updateQuantityQuery = """UPDATE Order_Product
                                     SET quantity = %s, sub_price = %s
                                     WHERE order_id = %s AND product_id = %s"""
            mycursor_tuple.execute(updateQuantityQuery, (newQuantity, subPrice, orderID, productID))
            conn.commit()
            flash('Product is already in the Cart , we increased the Quantity only')
            return redirect(url_for('customer'))
        else:
            if productID:
                productPrice = _to_decimal(request.form.get('price'), None)
                print('productPrice = ')
                print(productPrice)
                subPrice = 0
                if productPrice is not None and quantity is not None:
                    subPrice = float(productPrice) * int(quantity)
                else:
                    subPrice = 0  
                orderID = _session_int('order_id')
                addSweetToCartQuery='INSERT INTO Order_Product (order_id, product_id, sub_price, quantity) Values (%s, %s, %s, %s)'
                print('added to CART')
                mycursor_tuple.execute(addSweetToCartQuery,(orderID,productID,subPrice,quantity))
                conn.commit()
                flash('Product addded to your cart')
                return redirect(url_for('customer'))

@app.route('/Customer/add_drink_to_cart' ,methods=['GET','POST'])
def addDrinkToCustomerCart() :
    if request.method == 'POST':
        if session.get('user_type',None) != 'Customer':
            flash("You need to login before you add to your cart,.")
            return render_template('login.html')
        orderID = _session_int('order_id')
        if not orderID:
            flash("No active order found. Please start a new order.")
            return render_template('login.html')

        quantity = _to_int(request.form.get('quantity'), None)
        productID = _to_int(request.form.get('product_id'), None)
        if quantity is None or productID is None:
            flash('Invalid item input.')
            return redirect(url_for('customer'))

        checkIfInCartQuery = """ Select quantity 
                                 From Order_Product 
                                 Where order_id= %s AND product_id= %s """
        mycursor_tuple.execute(checkIfInCartQuery,(orderID,productID))
        quantityInCart = mycursor_tuple.fetchone()
        if quantityInCart :
            existingQuantity = quantityInCart[0]
            newQuantity = existingQuantity + int(quantity)
            productPrice = _to_decimal(request.form.get('price'), None)
            if productPrice is not None:
                subPrice = float(productPrice) * newQuantity
            else:
                subPrice = 0  

            updateQuantityQuery = """UPDATE Order_Product
                                     SET quantity = %s, sub_price = %s
                                     WHERE order_id = %s AND product_id = %s"""
            mycursor_tuple.execute(updateQuantityQuery, (newQuantity, subPrice, orderID, productID))
            conn.commit()
            flash('Product is already in the Cart , we increased the Quantity only')
            return redirect(url_for('customer'))
        else:
            if productID:
                productPrice = _to_decimal(request.form.get('price'), None)
                print('productPrice = ')
                print(productPrice)
                subPrice = 0
                if productPrice is not None and quantity is not None:
                    subPrice = float(productPrice) * int(quantity)
                else:
                    subPrice = 0  
                orderID = _session_int('order_id')
                addSweetToCartQuery='INSERT INTO Order_Product (order_id, product_id, sub_price, quantity) Values (%s, %s, %s, %s)'
                print('added to CART')
                mycursor_tuple.execute(addSweetToCartQuery,(orderID,productID,subPrice,quantity))
                flash('Product addded to your cart')
                conn.commit()

                return redirect(url_for('customer'))

@app.route('/Customer/remove_from_cart', methods=['POST'])
def removeProductFromCart():
    if session.get('user_type', None) != 'Customer':
        flash("You need to log in to modify your cart.")
        return render_template('login.html')

    orderID = _session_int('order_id')
    if not orderID:
        flash("No active order found.")
        return render_template('login.html')

    productID = _to_int(request.form.get('product_id'), None)
    if not productID:
        flash("Product ID is required to remove an item from the cart.")
        return redirect(url_for('cart'))

    removeFromCartQuery = 'DELETE FROM Order_Product WHERE order_id = %s AND product_id = %s'
    try:
        mycursor_tuple.execute(removeFromCartQuery, (orderID, productID))
        conn.commit()
        flash("Product removed from cart successfully.")
    except Exception as e:
        flash(f"An error occurred: {str(e)}")
    
    return redirect(url_for('cart'))
# -------------------------------------------------------------------------------- employee
@app.route('/employee')
def employeeHome():
    if session.get('user_type') != 'Employee':
        flash("Unauthorized access. Only employees can add sweets.")
        return render_template('error.html')
    else:
        empID = _session_int('employee_id')
        empName = session.get('employee_name')
        salary = session.get('salary')
        getSweetsQuery = """Select p.product_id,p.product_name,p.price,s.nuts_type,s.chocolate_type 
                            From Products p ,Sweets s, Product_Employee pe 
                            Where p.product_id=s.product_id AND p.product_id = pe.product_id AND pe.emp_id=%s """
        mycursor_tuple.execute(getSweetsQuery, (empID,))
        sweets = mycursor_tuple.fetchall()
        sweetsL = []
        for s in sweets:
            stu_der = {
                "product_id" : s[0],
                "product_name" : s[1],
                "price" : s[2],
                "nuts_type" : s[3],
                "chocolate_type" : s[4]
            }
            sweetsL.append(stu_der)
        getDrinksQuery = """Select p.product_id,p.product_name,p.price,d.state,d.is_sugar_free 
                            From Products p ,Drinks d, Product_Employee pe 
                            Where p.product_id=d.product_id AND p.product_id = pe.product_id AND pe.emp_id=%s """
        mycursor_tuple.execute(getDrinksQuery, (empID,))
        drinks = mycursor_tuple.fetchall()
        drinksL = []
        for s in drinks:
            dri_der = {
                "product_id" : s[0],
                "product_name" : s[1],
                "price" : s[2],
                "state" : s[3],
                "is_sugar_free" : s[4]
            }
            drinksL.append(dri_der)
        getOrdersQuery = """Select s.supplier_id, s.SupplierName, s.phone, sp.product_Name, sb.buy_date, sb.quantity, sp.price 
                            From Suppliers s ,Suppliers_Buy sb ,Supplier_Products sp
                            Where s.supplier_id = sb.supplier_id AND sp.supplier_id = s.supplier_id AND sb.emp_id= %s"""
        mycursor_tuple.execute(getOrdersQuery, (empID,))
        orders = mycursor_tuple.fetchall()
        ordersL = []
        for s in orders:
            ord_der = {
                "supplier_id" : s[0],
                "SupplierName" : s[1],
                "phone" : s[2],
                "product_name" : s[3],
                "buy_date" : s[4],
                "quantity" : s[5],
                "price" : int(s[5])*int(s[6])
            }
            ordersL.append(ord_der)
        return render_template('employeeHome.html',empName=empName,empID=empID,salary=salary,sweetsL=sweetsL,drinksL=drinksL,ordersL=ordersL)


# ------------------------------------------------------ manger with login
@app.route('/needToLogin',methods=['GET'])
def needToLogin() :
    if request.method == 'GET':
        flash("You need to login before you add to your cart,.")
        return render_template('login.html')
    
@app.route('/login', methods=['GET','POST'])
def login():
    session.clear() 
    if request.method == 'GET':
        return render_template('login.html')
    email = _clean_str(request.form.get('email'))
    password = _clean_str(request.form.get('password'))

    if not conn:
        flash("Database connection error.")
        return render_template('error.html')
    user = get_user_by_email(email)
    if user is None:
        flash("User not found.")
        return redirect(url_for('login'))
    storedPassword= user['PasswordHash']
    if password == storedPassword: # if the enterd passwod dont equal the one from database then pasword is error
        setup_user_session(user)#setting the current session values for the user who loged in ,(this method spacifi the type of the user to redirct to correct pages)
        print(user)
        if user['UserType'] == 'Manager': 
            flash("Login successful! Welcome, Manager!")
            return redirect(url_for('manager_dashboard')) 
        elif user['UserType'] == 'Employee': 
            query1 = "SELECT emp_name FROM Employees WHERE emp_id=%s"
            mycursor_tuple.execute(query1, (user['EmployeeID'],))
            session['employee_name'] = mycursor_tuple.fetchone()[0]
            query2 = "SELECT salary FROM Employees WHERE emp_id=%s"
            mycursor_tuple.execute(query2, (user['EmployeeID'],))
            session['salary'] = mycursor_tuple.fetchone()[0]
            flash("Login successful! Welcome, Employee !")
            return redirect(url_for('employeeHome')) 
        elif user['UserType'] == 'Customer':
            session['sweetsL'] = get_sweets()
            session['hotDrinksL'] = get_hot_drinks()
            session['smothiesL'] = get_smothies()
            session['milksL'] = get_milks()
            oldCart = checkIfThereIsUnpayedCart()
            if oldCart == None:  
                create_order(user['CustomerID'])
                customerID = user['CustomerID']
                getOrderIDQuery = 'SELECT order_id FROM Orders WHERE customer_id = %s ORDER BY order_id DESC'
                mycursor_tuple.execute(getOrderIDQuery,(customerID,))
                orderID = mycursor_tuple.fetchone()[0]
                mycursor_tuple.fetchall()
                session['order_id'] = orderID 
            else:
                session['order_id'] = oldCart
            flash("Login successful! Welcome, Customer!")
            return redirect(url_for('customer')) 
        else:
            flash("Error in the UserType in the Login.")
            return redirect(url_for('hello'))
    else:
        flash("enterd email or password has error")
        return render_template('login.html')
    
@app.route('/manager_dashboard')
def manager_dashboard():
    employee_id = _session_int('employee_id')
    if not employee_id:
        flash("Manager information is missing.")
        return redirect(url_for('login'))
    try:
        query = "SELECT emp_name FROM Employees WHERE emp_id = %s"
        mycursor_dict.execute(query, (employee_id,))
        result = mycursor_dict.fetchone()
        if result:
            # result is a dictionary => result['emp_name']
            manager_name = result['emp_name']
        else:
            flash("Manager not found.")
            return redirect(url_for('login'))
    except Exception as e:
        print(f"Error occurred in manager_dashboard: {e}")
        flash(f"An error occurred: {e}")
        return render_template('error.html')

    return render_template('MangerHome.html',
                           email=session.get('email'),
                           manager_name=manager_name)

from datetime import datetime

@app.route('/manager_dashboard/order_management', methods=['GET', 'POST'])
def order_management():
    from datetime import date, datetime
    search_type = request.form.get('search_type', 'current_date')
    search_value_raw = request.form.get('search_value', '')
    search_value = _clean_str(search_value_raw, max_len=128)

    base_query = """
        SELECT 
            Payments_order.PaymentID,
            Payments_order.OrderID,
            Customers.customer_name,
            Payments_order.PaymentDate,
            Payments_order.Amount,
            Orders.rating,
            PaymentMethod.MethodType
        FROM Payments_order
        JOIN Orders ON Payments_order.OrderID = Orders.order_id
        JOIN Customers ON Orders.customer_id = Customers.customer_id
        JOIN PaymentMethod ON Payments_order.PaymentMethodID = PaymentMethod.PaymentMethodID
    """

    conditions = []
    params = []

    if search_type == 'current_date':
        current_date = date.today().strftime("%Y-%m-%d")
        conditions.append("Payments_order.PaymentDate = %s")
        params.append(current_date)

    elif search_type == 'all':
        pass

    elif search_type == 'date':
        sv_date = _ymd(search_value)
        if sv_date:
            conditions.append("Payments_order.PaymentDate = %s")
            params.append(sv_date)
        else:
            flash("Invalid date format. Use YYYY-MM-DD.")
            return render_template('order_management.html',
                                   orders=[], total_orders=0, total_amount=0)

    elif search_type == 'payment_method':
        pm = _enum(search_value, {'Cash','Credit Card'}, None)
        if pm is None:
            flash("Invalid payment method.")
            return render_template('order_management.html',
                                   orders=[], total_orders=0, total_amount=0)
        conditions.append("PaymentMethod.MethodType = %s")
        params.append(pm)

    elif search_type == 'customer_name':
        conditions.append("Customers.customer_name LIKE %s")
        params.append(f"%{search_value}%")

    elif search_type == 'max_total_amount':
        conditions.append("Payments_order.Amount = (SELECT MAX(Amount) FROM Payments_order)")

    elif search_type == 'min_total_amount':
        conditions.append("Payments_order.Amount = (SELECT MIN(Amount) FROM Payments_order)")

    elif search_type == 'greater_than':
        val = _to_float(search_value, None)
        if val is None:
            flash("Invalid value for Greater Than search. Please enter a numeric value.")
            return render_template('order_management.html',
                                   orders=[], total_orders=0, total_amount=0)
        conditions.append("Payments_order.Amount > %s")
        params.append(val)

    elif search_type == 'less_than':
        val = _to_float(search_value, None)
        if val is None:
            flash("Invalid value for Less Than search. Please enter a numeric value.")
            return render_template('order_management.html',
                                   orders=[], total_orders=0, total_amount=0)
        conditions.append("Payments_order.Amount < %s")
        params.append(val)

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    base_query += " ORDER BY Payments_order.PaymentDate DESC"

    mycursor_tuple.execute(base_query, params)
    results = mycursor_tuple.fetchall() or []

    total_amount = sum(float(row[4]) for row in results)

    enriched_results = []
    for row in results:
        order_id = row[1]
        product_query = """
            SELECT Products.product_name, Order_Product.quantity
            FROM Order_Product
            INNER JOIN Products ON Order_Product.product_id = Products.product_id
            WHERE Order_Product.order_id = %s
        """
        mycursor_tuple.execute(product_query, (order_id,))
        products = mycursor_tuple.fetchall()

        product_details = ", ".join(f"{p[0]} (x{p[1]})" for p in products) if products else "No products"
        enriched_results.append(row + (product_details,))

    return render_template(
        'order_management.html',
        orders=enriched_results,
        total_orders=len(enriched_results),
        total_amount=total_amount
    )


@app.route('/manager_dashboard/employee_management', methods=['GET', 'POST'])
def employee_management():
    if request.method == 'POST':
        emp_name = _clean_str(request.form.get('emp_name'), max_len=120)
        phone = _clean_str(request.form.get('phone'), max_len=32)
        address = _clean_str(request.form.get('address'), max_len=255)
        salary_str = _clean_str(request.form.get('salary'), max_len=16)
        email = _clean_str(request.form.get('email'), max_len=255)
        password = _clean_str(request.form.get('password'), max_len=255)

        if not emp_name or not phone or not address or not salary_str or not email or not password:
            flash("All fields are required to add a new employee.")
            return redirect(url_for('employee_management'))

        salary = _to_int(salary_str, None)
        if salary is None:
            flash("Salary must be an integer.")
            return redirect(url_for('employee_management'))

        insert_emp_query = """
            INSERT INTO Employees (emp_name, phone, address, emp_role, salary)
            VALUES (%s, %s, %s, %s, %s)
        """
        mycursor_tuple.execute(insert_emp_query, (emp_name, phone, address, 'Employee', salary))
        conn.commit()
        new_emp_id = mycursor_tuple.lastrowid 

        insert_login_query = """
            INSERT INTO EmployeeLogin (Email, PasswordHash,EmployeeID)
            VALUES (%s, %s, %s)
        """
        mycursor_tuple.execute(insert_login_query, (email, password, new_emp_id))
        conn.commit()

        flash(f"New Employee '{emp_name}' added successfully!")
        return redirect(url_for('employee_management'))

    select_emp_query = """
        SELECT emp_id, emp_name, phone, address, salary
        FROM Employees
        WHERE emp_role = 'Employee'
        ORDER BY emp_id DESC
    """
    mycursor_tuple.execute(select_emp_query)
    employees = mycursor_tuple.fetchall()

    count_emp_query = "SELECT COUNT(*) FROM Employees WHERE emp_role = 'Employee'"
    mycursor_tuple.execute(count_emp_query)
    total_employees = mycursor_tuple.fetchone()[0]

    sum_salary_query = "SELECT SUM(salary) FROM Employees WHERE emp_role = 'Employee'"
    mycursor_tuple.execute(sum_salary_query)
    sum_salary_result = mycursor_tuple.fetchone()[0]
    total_salary = sum_salary_result if sum_salary_result else 0

    return render_template(
        'employee_management.html',
        employees=employees,
        total_employees=total_employees,
        total_salary=total_salary
    )

@app.route('/manager_dashboard/employee_management/delete/<int:emp_id>', methods=['POST'])
def delete_employee(emp_id):
    try:
        check_employee_query = "SELECT emp_id FROM Employees WHERE emp_id = %s"
        mycursor_tuple.execute(check_employee_query, (emp_id,))
        employee = mycursor_tuple.fetchone()
        if not employee:
            flash(f"Employee ID {emp_id} does not exist.")
            return redirect(url_for('employee_management'))

        delete_related_records_query = "DELETE FROM Suppliers_Buy WHERE emp_id = %s"
        mycursor_tuple.execute(delete_related_records_query, (emp_id,))

        delete_login_query = "DELETE FROM EmployeeLogin WHERE EmployeeID = %s"
        mycursor_tuple.execute(delete_login_query, (emp_id,))

        delete_employee_query = "DELETE FROM Employees WHERE emp_id = %s"
        mycursor_tuple.execute(delete_employee_query, (emp_id,))

        conn.commit()

        flash(f"Employee ID {emp_id} has been deleted.")
    except Exception as e:
        conn.rollback()
        flash(f"Error deleting Employee ID {emp_id}: {e}")
    return redirect(url_for('employee_management'))


@app.route('/manager_dashboard/employee_management/update_salary/<int:emp_id>', methods=['POST'])
def update_employee_salary(emp_id):
    new_salary_str = _clean_str(request.form.get('new_salary'), max_len=16)
    if not new_salary_str:
        flash("Please enter a salary to update.")
        return redirect(url_for('employee_management'))
    
    new_salary = _to_int(new_salary_str, None)
    if new_salary is None:
        flash("Salary must be an integer.")
        return redirect(url_for('employee_management'))
    
    update_query = "UPDATE Employees SET salary = %s WHERE emp_id = %s"
    mycursor_tuple.execute(update_query, (new_salary, emp_id))
    conn.commit()
    
    flash(f"Employee ID {emp_id} salary updated to {new_salary}.")
    return redirect(url_for('employee_management'))


@app.route('/manager_dashboard/supplier_management', methods=['GET', 'POST'])
def supplier_management():
    if request.form.get('action') == 'add_supplier':
        supplier_name = _clean_str(request.form.get('supplier_name'), max_len=120)
        product_name = _clean_str(request.form.get('product_name'), max_len=120)
        product_price = _to_decimal(request.form.get('product_price'), None)
        phone = _clean_str(request.form.get('phone'), max_len=32)
        address = _clean_str(request.form.get('address'), max_len=255)

        if not supplier_name or not product_name or not phone or not address or product_price is None:
            flash("All fields are required.")
            return redirect(url_for('supplier_management'))

        try:
            insert_supplier_query = """
                INSERT INTO Suppliers (SupplierName, Phone, address)
                VALUES (%s, %s, %s)
            """
            mycursor_tuple.execute(insert_supplier_query, (supplier_name, phone, address))
            conn.commit()
            new_supplier_id = mycursor_tuple.lastrowid

            insert_product_query = """
                INSERT INTO Supplier_Products (supplier_id, product_name, price)
                VALUES (%s, %s, %s)
            """
            mycursor_tuple.execute(insert_product_query, (new_supplier_id, product_name, str(product_price)))
            conn.commit()

            flash(f"New Supplier '{supplier_name}' and Product '{product_name}' added successfully!")
        except Exception as e:
            flash(f"Error adding supplier: {e}")
        return redirect(url_for('supplier_management'))

    if request.form.get('action') == 'update_supplier':
        supp_id = _to_int(request.form.get('supp_id'), None)
        new_phone = _clean_str(request.form.get('new_phone'), max_len=32)
        new_address = _clean_str(request.form.get('new_address'), max_len=255)
        new_product_name = _clean_str(request.form.get('new_product_name'), max_len=120)
        new_product_price = _to_decimal(request.form.get('new_product_price'), None)

        if not supp_id:
            flash("Invalid supplier ID.")
            return redirect(url_for('supplier_management'))

        try:
            set_clauses = []
            params = []
            if new_phone:
                set_clauses.append("Phone = %s")
                params.append(new_phone)
            if new_address:
                set_clauses.append("address = %s")
                params.append(new_address)
            if set_clauses:
                update_supplier_query = "UPDATE Suppliers SET " + ", ".join(set_clauses) + " WHERE supplier_id = %s"
                params.append(supp_id)
                mycursor_tuple.execute(update_supplier_query, params)
                conn.commit()

            if new_product_name and new_product_price is not None:
                insert_product_query = """
                    INSERT INTO Supplier_Products (supplier_id, product_name, price)
                    VALUES (%s, %s, %s)
                """
                mycursor_tuple.execute(insert_product_query, (supp_id, new_product_name, str(new_product_price)))
                conn.commit()
        except Exception as e:
            flash(f"Error updating supplier: {e}")
        return redirect(url_for('supplier_management'))

    # Search Parameters
    search_type = request.form.get('search_type', 'all')
    search_value = _clean_str(request.form.get('search_value', ''), max_len=128)

    base_query = """
        SELECT 
            sb.supplier_id,
            s.SupplierName,
            sp.product_name,
            sb.quantity,
            sp.price,
            sb.emp_id,
            COALESCE(e.emp_name, 'N/A') AS emp_name,
            sb.buy_date
        FROM Suppliers_Buy sb
        JOIN Suppliers s ON sb.supplier_id = s.supplier_id
        JOIN Supplier_Products sp ON sb.supplier_id = sp.supplier_id
        LEFT JOIN Employees e ON sb.emp_id = e.emp_id
    """

    # Add Search Conditions
    conditions = []
    params = []

    if search_type == 'supplier_name':
        conditions.append("s.SupplierName LIKE %s")
        params.append(f"%{search_value}%")
    elif search_type == 'employee_name':
        conditions.append("e.emp_name LIKE %s")
        params.append(f"%{search_value}%")
    elif search_type == 'max_total':
        conditions.append("(sb.quantity * sp.price) = (SELECT MAX(sb.quantity * sp.price) FROM Suppliers_Buy sb JOIN Supplier_Products sp ON sb.supplier_id = sp.supplier_id)")
    elif search_type == 'min_total':
        conditions.append("(sb.quantity * sp.price) = (SELECT MIN(sb.quantity * sp.price) FROM Suppliers_Buy sb JOIN Supplier_Products sp ON sb.supplier_id = sp.supplier_id)")

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    base_query += " ORDER BY sb.buy_date DESC"

    mycursor_tuple.execute(base_query, params)
    movements = mycursor_tuple.fetchall() or []

    enriched_movements = []
    for row in movements:
        supplier_id, supplier_name, product_name, quantity, price, emp_id, emp_name, buy_date = row
        total = float(quantity) * float(price) if quantity and price else 0.0
        enriched_movements.append((supplier_id, supplier_name, product_name, quantity, price, emp_id, emp_name, buy_date, total))

    all_suppliers_query = """
        SELECT s.supplier_id, s.SupplierName, sp.product_name, sp.price, s.Phone, s.address
        FROM Suppliers s
        LEFT JOIN Supplier_Products sp ON s.supplier_id = sp.supplier_id
        ORDER BY s.supplier_id DESC
    """
    mycursor_tuple.execute(all_suppliers_query)
    all_suppliers = mycursor_tuple.fetchall() or []

    grand_total = sum(row[-1] for row in enriched_movements)

    return render_template(
        'supplier_management.html',
        movements=enriched_movements,
        suppliers=all_suppliers,
        grand_total=grand_total
    )

@app.route('/manager_dashboard/Report', methods=['GET', 'POST'])
def Report_of_Store():
    avg_salary_query = """
        SELECT AVG(salary) 
        FROM Employees
    """
    mycursor_tuple.execute(avg_salary_query)
    avg_salary_result = mycursor_tuple.fetchone()[0]
    avg_salary = float(avg_salary_result) if avg_salary_result else 0.0

    avg_order_query = """
        SELECT AVG(Amount)
        FROM Payments_order
    """
    mycursor_tuple.execute(avg_order_query)
    avg_order_result = mycursor_tuple.fetchone()[0]
    avg_order_amount = float(avg_order_result) if avg_order_result else 0.0

    avg_supplier_query = """
        SELECT AVG(sb.quantity * sp.price)
        FROM Suppliers_Buy sb
        JOIN Supplier_Products sp ON sb.supplier_id = sp.supplier_id
    """
    mycursor_tuple.execute(avg_supplier_query)
    avg_supplier_result = mycursor_tuple.fetchone()[0]
    avg_supplier_amount = float(avg_supplier_result) if avg_supplier_result else 0.0

    total_income_query = """
        SELECT SUM(Amount)
        FROM Payments_order
    """
    mycursor_tuple.execute(total_income_query)
    total_income_result = mycursor_tuple.fetchone()[0]
    total_income = float(total_income_result) if total_income_result else 0.0

    sum_salary_query = "SELECT SUM(salary) FROM Employees"
    mycursor_tuple.execute(sum_salary_query)
    sum_salary_result = mycursor_tuple.fetchone()[0]
    sum_salaries = float(sum_salary_result) if sum_salary_result else 0.0

    sum_suppliers_query = """
        SELECT SUM(sb.quantity * sp.price)
        FROM Suppliers_Buy sb
        JOIN Supplier_Products sp ON sb.supplier_id = sp.supplier_id
    """
    mycursor_tuple.execute(sum_suppliers_query)
    sum_suppliers_result = mycursor_tuple.fetchone()[0]
    sum_suppliers_buys = float(sum_suppliers_result) if sum_suppliers_result else 0.0

    total_outcome = sum_salaries + sum_suppliers_buys

    arrow_income_up = total_income > total_outcome
    arrow_outcome_up = total_outcome > total_income

    income_color = "green-text" if arrow_income_up else "red-text"
    outcome_color = "green-text" if arrow_outcome_up else "red-text"

    return render_template(
        'Report.html',
        avg_salary=round(avg_salary, 2),
        avg_order_amount=round(avg_order_amount, 2),
        avg_supplier_amount=round(avg_supplier_amount, 2),
        total_income=round(total_income, 2),
        total_outcome=round(total_outcome, 2),
        arrow_income_up=arrow_income_up,
        arrow_outcome_up=arrow_outcome_up,
        income_color=income_color,
        outcome_color=outcome_color
    )

@app.route('/SignUp', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('SignUp.html')
    else:
        name = _clean_str(request.form.get('name'))
        phone = _clean_str(request.form.get('phoneNum'))
        address = _clean_str(request.form.get('address'))
        email = _clean_str(request.form.get('email'))
        password = _clean_str(request.form.get('pass'))
        
        if not conn:
            flash("Database connection error.")
            return redirect(url_for('hello'))
        
        try:
            customer_query = """
                INSERT INTO Customers (customer_name, phone, address)
                VALUES (%s, %s, %s)
            """
            mycursor_tuple.execute(customer_query, (name, phone, address))
            conn.commit()  
            customer_id = mycursor_tuple.lastrowid  
            
            login_query = """
                INSERT INTO CustomerLogin (Email, PasswordHash, CustomerID)
                VALUES (%s, %s, %s)
            """
            mycursor_tuple.execute(login_query, (email, password, customer_id))
            conn.commit()  

            flash("Sign-up successful! You can now log in.")
            session['logged_in'] = True
            session['email'] = email
            session['user_type'] = 'Customer'
            session['customer_id'] = customer_id

            return redirect(url_for('login'))
        except Exception as e:
            conn.rollback()  
            flash(f"Error during sign-up: {e}")
            return redirect(url_for('signup'))


@app.route('/logout')
def logout():
    session.clear()
    return render_template("index.html",sweetsL=get_sweets(),hotDrinksL=get_hot_drinks(),smothiesL=get_smothies(),milksL=get_milks())      
#------------------------------------------ functions 
def setup_user_session(user):
    session['email'] = user['Email']
    session['user_type'] = user['UserType']
    session['employee_id'] = user['EmployeeID']
    session['customer_id'] = user['CustomerID']

def get_user_by_email(email):
    email = _clean_str(email)
    checkIfManagerQuery = """SELECT el.Email,el.PasswordHash,el.EmployeeID,e.emp_name,e.emp_role
                            FROM EmployeeLogin el
                            JOIN Employees e ON el.EmployeeID = e.emp_id
                            WHERE el.Email = %s AND e.emp_role = 'Manager';
                        """
    mycursor_dict.execute(checkIfManagerQuery, (email,))
    manager_result = mycursor_dict.fetchone()
    if manager_result:
        role = manager_result['emp_role']
        if role == 'Manager':
            return{
            'Email': manager_result['Email'],
            'PasswordHash': manager_result['PasswordHash'],
            'UserType': 'Manager',
            'EmployeeID': manager_result['EmployeeID'],
            'CustomerID': None,  
        }
        
    employee_query = """
        SELECT Email, PasswordHash, EmployeeID 
        FROM EmployeeLogin
        WHERE Email = %s
    """
    mycursor_dict.execute(employee_query, (email,))
    employee_result = mycursor_dict.fetchone()

    if employee_result:
        return {
            'Email': employee_result['Email'],
            'PasswordHash': employee_result['PasswordHash'],
            'UserType': 'Employee',
            'EmployeeID': employee_result['EmployeeID'],
            'CustomerID': None,  # Not applicable for Employee
        }

    customer_query = """
        SELECT Email, PasswordHash, CustomerID 
        FROM CustomerLogin
        WHERE Email = %s
    """
    mycursor_dict.execute(customer_query, (email,))
    customer_result = mycursor_dict.fetchone()

    if customer_result:
        return {
            'Email': customer_result['Email'],
            'PasswordHash': customer_result['PasswordHash'],
            'UserType': 'Customer',
            'EmployeeID': None,  
            'CustomerID': customer_result['CustomerID'],
        }

    return None


def create_order(customer_id):
    query = "INSERT INTO Orders (customer_id, total_amount) VALUES (%s, 0)"
    mycursor_tuple.execute(query, (customer_id,))
    conn.commit()

def get_customer_name(customer_id):
    if customer_id is None:
        return None
    query = "SELECT customer_name FROM Customers WHERE customer_id = %s"
    mycursor_tuple.execute(query, (customer_id,))
    result = mycursor_tuple.fetchone()
    session['customer_name'] = result[0] if result else None
    return result[0] if result else None

def checkIfThereIsUnpayedCart():
    cid = _session_int('customer_id')
    if cid is None:
        return None
    checkIfThereIsUnPayedCartQuery = """ SELECT o.order_id
                                         FROM Orders o
                                         WHERE o.customer_id = %s AND o.order_id NOT IN (SELECT OrderID FROM Payments_order)
                                         order by o.order_id DESC"""
    mycursor_tuple.execute(checkIfThereIsUnPayedCartQuery, (cid,))
    result = mycursor_tuple.fetchone()
    mycursor_tuple.fetchall()
    if not result :
        return None
    else:
        return result[0]


if __name__ == "__main__":
    app.run(debug=True)
