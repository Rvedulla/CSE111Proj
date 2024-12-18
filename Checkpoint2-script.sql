DROP TABLE IF EXISTS Cart;
DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Review;
DROP TABLE IF EXISTS Product;
DROP TABLE IF EXISTS OrderDetails;
DROP TABLE IF EXISTS Category;


CREATE TABLE User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT 0
);

CREATE TABLE Product (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    stock INTEGER NOT NULL
);

CREATE TABLE Cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (product_id) REFERENCES Product(id)
);

CREATE TABLE Orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    address TEXT NOT NULL,
    address2 TEXT,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    zip_code TEXT NOT NULL,
    country TEXT NOT NULL,
    total_amount REAL NOT NULL,
    paid BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES User(id)
);

CREATE TABLE OrderDetails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(id),
    FOREIGN KEY (product_id) REFERENCES Product(id)
);

CREATE TABLE Review (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER NOT NULL,
    text_review TEXT,
    FOREIGN KEY (order_id) REFERENCES Orders(id),
    FOREIGN KEY (product_id) REFERENCES Product(id)
);

-- Insert data into tables
INSERT INTO User (id, username, email, password_hash, is_admin) VALUES
(1, 'johndoe', 'johndoe@example.com', 'john', 0),
(2, 'janedoe', 'janedoe@example.com', 'jane', 0),
(3, 'adminuser', 'admin@example.com', 'admin', 1);

INSERT INTO Product (id, name, description, price, stock) VALUES
(1, 'Laptop', 'new laptop', 1200.00, 10),
(2, 'Phone', 'new smartphone', 800.00, 20);

INSERT INTO Cart (id, user_id, product_id, quantity) VALUES
(1, 1, 1, 1),
(2, 1, 2, 2);

INSERT INTO Orders (user_id, name, email, address, address2, city, state, zip_code, country, total_amount, paid) VALUES
(1, 'John Doe', 'johndoe@example.com', '123 Main St', NULL, 'Anytown', 'State', '12345', 'Country', 2000.00, 1);

INSERT INTO OrderDetails (order_id, product_id, quantity, price) VALUES
(1, 1, 1, 1200.00),
(1, 2, 2, 800.00);

INSERT INTO Review (order_id, product_id, text_review) VALUES
(1, 1, 'Excellent product!'),
(2, 2, 'Great value for the price.');

-- -- 2-3 select -- ADD JOIN QUERIES
-- SELECT 
--     Orders.id AS order_id,
--     User.username AS customer_name,
--     Product.name AS product_name,
--     Product.price AS product_price,
--     Cart.quantity AS product_quantity,
--     (Cart.quantity * Product.price) AS total_product_cost,
--     Orders.total_amount AS order_total
-- FROM Orders
-- JOIN User ON Orders.user_id = User.id
-- JOIN Cart ON Cart.product_id = Product.id 
-- JOIN Product ON Cart.product_id = Product.id;

-- SELECT 
--     User.id AS user_id,
--     User.username AS customer_name,
--     User.email AS customer_email,
--     COUNT(Orders.id) AS total_orders
-- FROM User
-- LEFT JOIN Orders ON User.id = Orders.user_id
-- GROUP BY User.id, User.username, User.email
-- ORDER BY total_orders DESC;

-- -- 1 update
-- UPDATE Product
-- SET stock = stock - 1
-- WHERE id = 1;

-- -- 1 delete
-- DELETE FROM Cart
-- WHERE ROWID = 1;