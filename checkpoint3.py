import sqlite3

def connect_to_database(db_file):
    """Connect to the SQLite3 database."""
    try:
        conn = sqlite3.connect(db_file)
        print("Database connection successful!")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def display_menu(is_admin):
    """Display the menu based on user type."""
    print("\nMenu:")
    if is_admin:
        print("1. View All Users")
    print("2. View Cart")
    print("3. Add Product to Cart")
    print("4. Create Order")
    print("5. View Orders")
    print("6. View Order Details")
    print("7. Add Review")
    print("8. Remove Item from Cart")
    print("9. View Reviews")  # New menu option
    print("10. Exit")

def view_all_users(conn):
    """Retrieve and display all users (Admin only)."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, is_admin FROM User")
        rows = cursor.fetchall()

        if rows:
            print("\n=== Users ===")
            print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Admin':<6}")
            print("-" * 65)
            for user_id, username, email, is_admin in rows:
                admin_status = "Yes" if is_admin else "No"
                print(f"{user_id:<5} {username:<20} {email:<30} {admin_status:<6}")
        else:
            print("No users found.")
    except sqlite3.Error as e:
        print(f"Error retrieving users: {e}")

def view_cart(conn, user_id):
    """View the cart for the logged-in user."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Cart.id, Product.name, Cart.quantity
            FROM Cart
            JOIN Product ON Cart.product_id = Product.id
            WHERE Cart.user_id = ?
        """, (user_id,))
        rows = cursor.fetchall()

        if rows:
            print("\n=== Your Cart ===")
            print(f"{'ID':<5} {'Product Name':<30} {'Quantity':<10}")
            print("-" * 50)
            total_items = 0
            for cart_id, product_name, quantity in rows:
                print(f"{cart_id:<5} {product_name:<30} {quantity:<10}")
                total_items += quantity
            print("-" * 50)
            print(f"Total Items: {total_items}")
        else:
            print("No items in cart.")
    except sqlite3.Error as e:
        print(f"Error retrieving cart: {e}")

def add_product_to_cart(conn, user_id):
    """Add a product to the cart for the logged-in user."""
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, price FROM Product")
        products = cursor.fetchall()

        if not products:
            print("No products available to add to cart.")
            return

        print("\n=== Available Products ===")
        for idx, (product_id, product_name, product_price) in enumerate(products, start=1):
            print(f"{idx}. {product_name} (Price: ${product_price:.2f})")

        # Prompt user to select a product
        choice = int(input("Enter the number of the product you want to add to your cart: ").strip())
        if 1 <= choice <= len(products):
            selected_product = products[choice - 1]
            product_id = selected_product[0]
            product_name = selected_product[1]

            quantity = int(input(f"Enter quantity for '{product_name}': ").strip())

            cursor.execute("""
                INSERT INTO Cart (user_id, product_id, quantity)
                VALUES (?, ?, ?)
            """, (user_id, product_id, quantity))
            conn.commit()
            print(f"Product '{product_name}' added to cart successfully!")
        else:
            print("Invalid choice.")
    except sqlite3.Error as e:
        print(f"Error adding product to cart: {e}")

def create_order_with_details(conn, user_id):
    """Create a new order and populate the OrderDetails table."""
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT Cart.product_id, Product.price, Cart.quantity
            FROM Cart
            JOIN Product ON Cart.product_id = Product.id
            WHERE Cart.user_id = ?
        """, (user_id,))
        cart_items = cursor.fetchall()

        if not cart_items:
            print("No items in the cart for this user.")
            return

        total_amount = sum(price * quantity for _, price, quantity in cart_items)

        name = input("Enter name: ").strip()
        email = input("Enter email: ").strip()
        address = input("Enter address: ").strip()
        address2 = input("Enter address line 2 (optional): ").strip() or None
        city = input("Enter city: ").strip()
        state = input("Enter state: ").strip()
        zip_code = input("Enter zip code: ").strip()
        country = input("Enter country: ").strip()

        cursor.execute("""
            INSERT INTO Orders (user_id, name, email, address, address2, city, state, zip_code, country, total_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, name, email, address, address2, city, state, zip_code, country, total_amount))
        conn.commit()

        order_id = cursor.lastrowid

        for product_id, price, quantity in cart_items:
            cursor.execute("""
                INSERT INTO OrderDetails (order_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            """, (order_id, product_id, quantity, price))
        conn.commit()

        # Clear the user's cart after creating the order
        cursor.execute("""
            DELETE FROM Cart WHERE user_id = ?
        """, (user_id,))
        conn.commit()

        print(f"Order created successfully! Total amount: ${total_amount:.2f}")
        print(f"Order ID: {order_id}")
        print("Order details have been recorded, and your cart has been cleared.")
    
    except sqlite3.Error as e:
        print(f"Error creating order with details: {e}")

def view_orders(conn, user_id):
    """View all orders for the logged-in user."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, total_amount, paid, name, city, state
            FROM Orders
            WHERE user_id = ?
        """, (user_id,))
        rows = cursor.fetchall()
        
        if rows:
            print("\n=== Your Orders ===")
            for order in rows:
                order_id, total_amount, paid, name, city, state = order
                print(f"Order ID: {order_id}")
                print(f"Recipient Name: {name}")
                print(f"Shipping Address: {city}, {state}")
                print(f"Total Amount: ${total_amount:.2f}")
                print(f"Paid: {'Yes' if paid else 'No'}")
                print("-" * 30)
        else:
            print("No orders found.")
    except sqlite3.Error as e:
        print(f"Error retrieving orders: {e}")

def add_review(conn):
    """Add an anonymous text review for a product."""
    print("\n=== Select a Product to Review ===")
    
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM Product")
    products = cursor.fetchall()
    
    if products:
        for idx, (product_id, product_name) in enumerate(products, start=1):
            print(f"{idx}. {product_name}")
        
        choice = int(input("Enter the number of the product you want to review: ").strip())
        if 1 <= choice <= len(products):
            selected_product = products[choice - 1]
            product_id = selected_product[0]
            product_name = selected_product[1]
            
            text_review = input(f"Enter your text review for the product '{product_name}': ").strip()

            try:
                cursor.execute("""
                    INSERT INTO Review (product_id, text_review)
                    VALUES (?, ?)
                """, (product_id, text_review))
                conn.commit()
                print("Review added successfully!")
            except sqlite3.Error as e:
                print(f"Error adding review: {e}")
        else:
            print("Invalid choice.")
    else:
        print("No products available to review.")
        
def remove_item_from_cart(conn, user_id):
    """Remove an item from the cart for the logged-in user."""
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT Cart.id, Product.name, Cart.quantity
            FROM Cart
            JOIN Product ON Cart.product_id = Product.id
            WHERE Cart.user_id = ?
        """, (user_id,))
        cart_items = cursor.fetchall()

        if not cart_items:
            print("No items in the cart to remove.")
            return

        print("\n=== Your Cart ===")
        for idx, (cart_id, product_name, quantity) in enumerate(cart_items, start=1):
            print(f"{idx}. {product_name} (Quantity: {quantity})")

        item_number = int(input("\nEnter the number of the item you want to remove: ").strip())
        
        if 1 <= item_number <= len(cart_items):
            cart_id = cart_items[item_number - 1][0]  # Get the Cart ID
            cursor.execute("DELETE FROM Cart WHERE id = ?", (cart_id,))
            conn.commit()
            print("Item removed from cart successfully!")
        else:
            print("Invalid item number.")
    except sqlite3.Error as e:
        print(f"Error removing item from cart: {e}")

def login(conn):
    """Prompt the user to log in."""
    username = input("Enter your username: ").strip()
    password = input("Enter your password: ").strip()

    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash, is_admin FROM User WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user is None:
        print("Username not found.")
        return None, None

    user_id, _, password_hash, is_admin = user
    if password != password_hash:
        print("Incorrect password.")
        return None, None

    print(f"Welcome {username}!")
    return user_id, is_admin


def view_order_details(conn, user_id):
    """View the details of a specific order."""
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, total_amount
            FROM Orders
            WHERE user_id = ?
        """, (user_id,))
        orders = cursor.fetchall()

        if not orders:
            print("No orders found.")
            return

        print("\n=== Your Orders ===")
        for idx, (order_id, total_amount) in enumerate(orders, start=1):
            print(f"{idx}. Order ID: {order_id}, Total: ${total_amount:.2f},")

        choice = int(input("\nEnter the number of the order to view details: ").strip())

        if 1 <= choice <= len(orders):
            selected_order_id = orders[choice - 1][0]
            
            cursor.execute("""
                SELECT Product.name, OrderDetails.quantity, OrderDetails.price
                FROM OrderDetails
                JOIN Product ON OrderDetails.product_id = Product.id
                WHERE OrderDetails.order_id = ?
            """, (selected_order_id,))
            order_details = cursor.fetchall()

            if order_details:
                print(f"\n=== Details for Order ID: {selected_order_id} ===")
                for product_name, quantity, price in order_details:
                    print(f"- {product_name}: Quantity {quantity}, Price: ${price:.2f}")
            else:
                print("No details found for this order.")
        else:
            print("Invalid choice.")
    except sqlite3.Error as e:
        print(f"Error retrieving order details: {e}")

def view_reviews(conn):
    """Retrieve and display all reviews."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                Review.id,
                Product.name AS product_name,
                Review.text_review
            FROM Review
            JOIN Product ON Review.product_id = Product.id
        """)
        rows = cursor.fetchall()
        
        if rows:
            print("\n=== Reviews ===")
            for review in rows:
                review_id, product_name, text_review = review
                print(f"Review ID: {review_id}")
                print(f"Product: {product_name}")
                print(f"Review: {text_review}")
                print("-" * 30)
        else:
            print("No reviews found.")
    except sqlite3.Error as e:
        print(f"Error retrieving reviews: {e}")


def main():
    """Main function to run the application."""
    database = "Checkpoint2-dbase.sqlite3"
    conn = connect_to_database(database)
    if conn is None:
        return
    
    user_id, is_admin = login(conn)
    if user_id is None:
        return

    while True:
        display_menu(is_admin)
        choice = input("Enter your choice (1-10): ").strip()

        if choice == "1" and is_admin:
            view_all_users(conn)
        elif choice == "2":
            view_cart(conn, user_id)
        elif choice == "3":
            add_product_to_cart(conn, user_id)
        elif choice == "4":
            create_order_with_details(conn, user_id)
        elif choice == "5":
            view_orders(conn, user_id)
        elif choice == "6":
            view_order_details(conn, user_id)  
        elif choice == "7":
            add_review(conn)
        elif choice == "8":
            remove_item_from_cart(conn, user_id)
        elif choice == "9":
            view_reviews(conn) 
        elif choice == "10":
            print("Exiting the application. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
    
    conn.close()

if __name__ == "__main__":
    main()