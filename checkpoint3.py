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

def display_menu():
    """Display the main menu."""
    print("\n=== Main Menu ===")
    print("1. View all users")
    print("2. View all products")
    print("3. View cart for a user")
    print("4. Add a product to the cart")
    print("5. Create an order")
    print("6. View orders")
    print("7. Add a review for a product in an order")
    print("8. Exit")

def view_all_users(conn):
    """Retrieve and display all users."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User")
        rows = cursor.fetchall()
        if rows:
            print("\n=== Users ===")
            for row in rows:
                print(row)
        else:
            print("No users found.")
    except sqlite3.Error as e:
        print(f"Error retrieving users: {e}")

def view_all_products(conn):
    """Retrieve and display all products."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Product")
        rows = cursor.fetchall()
        if rows:
            print("\n=== Products ===")
            for row in rows:
                print(row)
        else:
            print("No products found.")
    except sqlite3.Error as e:
        print(f"Error retrieving products: {e}")

def view_cart(conn):
    """View the cart for a specific user."""
    user_id = input("Enter user ID to view cart: ").strip()
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
            print("\n=== Cart ===")
            for row in rows:
                print(row)
        else:
            print("No items in cart for this user.")
    except sqlite3.Error as e:
        print(f"Error retrieving cart: {e}")

def add_product_to_cart(conn):
    """Add a product to the cart."""
    user_id = input("Enter user ID: ").strip()
    product_id = input("Enter product ID: ").strip()
    quantity = input("Enter quantity: ").strip()

    try:
        cursor = conn.cursor()
        # Insert values without explicitly setting 'id'
        cursor.execute("""
            INSERT INTO Cart (user_id, product_id, quantity)
            VALUES (?, ?, ?)
        """, (user_id, product_id, quantity))
        conn.commit()
        print("Product added to cart successfully!")
    except sqlite3.Error as e:
        print(f"Error adding product to cart: {e}")

def create_order(conn):
    """Create a new order."""
    user_id = input("Enter user ID: ").strip()

    # Step 1: Retrieve the cart items for the user and calculate the total amount
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Product.price, Cart.quantity
            FROM Cart
            JOIN Product ON Cart.product_id = Product.id
            WHERE Cart.user_id = ?
        """, (user_id,))
        cart_items = cursor.fetchall()
        
        if not cart_items:
            print("No items in the cart for this user.")
            return
        
        total_amount = sum(price * quantity for price, quantity in cart_items)

        # Step 2: Get order details from the user
        name = input("Enter name: ").strip()
        email = input("Enter email: ").strip()
        address = input("Enter address: ").strip()
        address2 = input("Enter address line 2 (optional): ").strip() or None
        city = input("Enter city: ").strip()
        state = input("Enter state: ").strip()
        zip_code = input("Enter zip code: ").strip()
        country = input("Enter country: ").strip()

        # Step 3: Insert the order into the Orders table
        cursor.execute("""
            INSERT INTO Orders (user_id, name, email, address, address2, city, state, zip_code, country, total_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, name, email, address, address2, city, state, zip_code, country, total_amount))
        conn.commit()

        # Step 4: Clear the cart for the user after successful order creation
        cursor.execute("""
            DELETE FROM Cart WHERE user_id = ?
        """, (user_id,))
        conn.commit()

        print(f"Order created successfully! Total amount: {total_amount:.2f}")
        print("Cart cleared after order creation.")
    
    except sqlite3.Error as e:
        print(f"Error creating order: {e}")

def view_orders(conn):
    """View all orders."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Orders")
        rows = cursor.fetchall()
        if rows:
            print("\n=== Orders ===")
            for row in rows:
                print(row)
        else:
            print("No orders found.")
    except sqlite3.Error as e:
        print(f"Error retrieving orders: {e}")

def add_review(conn):
    """Add a text review for a product."""
    order_id = input("Enter order ID to associate with the review: ").strip()
    product_id = input("Enter product ID to review: ").strip()
    text_review = input("Enter your text review for the product: ").strip()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Review (order_id, product_id, text_review)
            VALUES (?, ?, ?)
        """, (order_id, product_id, text_review))
        conn.commit()
        print("Review added successfully!")
    except sqlite3.Error as e:
        print(f"Error adding review: {e}")

def main():
    """Main function to run the application."""
    database = "Checkpoint2-dbase.sqlite3"  # Update with your database file name
    conn = connect_to_database(database)
    if conn is None:
        return
    
    while True:
        display_menu()
        choice = input("Enter your choice (1-8): ").strip()
        if choice == "1":
            view_all_users(conn)
        elif choice == "2":
            view_all_products(conn)
        elif choice == "3":
            view_cart(conn)
        elif choice == "4":
            add_product_to_cart(conn)
        elif choice == "5":
            create_order(conn)
        elif choice == "6":
            view_orders(conn)
        elif choice == "7":
            add_review(conn)
        elif choice == "8":
            print("Exiting the application. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
    
    conn.close()

if __name__ == "__main__":
    main()