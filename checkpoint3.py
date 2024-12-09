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
    """Display the main menu with options based on user role."""
    print("\n=== Main Menu ===")
    if is_admin:
        print("1. View all users")
    print("2. View your cart")
    print("3. Add a product to the cart")
    print("4. Create an order")
    print("5. View your orders")
    print("6. Add a review for a product")
    print("7. Remove an item from your cart")  # New option for removing items
    print("8. Exit")

def view_all_users(conn):
    """Retrieve and display all users (Admin only)."""
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
            for row in rows:
                print(row)
        else:
            print("No items in cart.")
    except sqlite3.Error as e:
        print(f"Error retrieving cart: {e}")

def add_product_to_cart(conn, user_id):
    """Add a product to the cart for the logged-in user."""
    try:
        cursor = conn.cursor()

        # Display available products
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

            # Add the product to the cart
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

def create_order(conn, user_id):
    """Create a new order based on the items in the cart."""
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

        cursor.execute("""
            DELETE FROM Cart WHERE user_id = ?
        """, (user_id,))
        conn.commit()

        print(f"Order created successfully! Total amount: {total_amount:.2f}")
        print("Cart cleared after order creation.")
    
    except sqlite3.Error as e:
        print(f"Error creating order: {e}")

def view_orders(conn, user_id):
    """View all orders for the logged-in user."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM Orders WHERE user_id = ?
        """, (user_id,))
        rows = cursor.fetchall()
        if rows:
            print("\n=== Your Orders ===")
            for row in rows:
                print(row)
        else:
            print("No orders found.")
    except sqlite3.Error as e:
        print(f"Error retrieving orders: {e}")

def add_review(conn):
    """Add an anonymous text review for a product."""
    print("\n=== Select a Product to Review ===")
    
    # Display available products
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM Product")
    products = cursor.fetchall()
    
    if products:
        for idx, (product_id, product_name) in enumerate(products, start=1):
            print(f"{idx}. {product_name}")
        
        # Prompt user to select a product
        choice = int(input("Enter the number of the product you want to review: ").strip())
        if 1 <= choice <= len(products):
            selected_product = products[choice - 1]
            product_id = selected_product[0]
            product_name = selected_product[1]
            
            # Ask for review text
            text_review = input(f"Enter your text review for the product '{product_name}': ").strip()

            # Insert the review into the Review table (no user_id)
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

        # Retrieve all items in the cart for the user
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

        # Display the cart items to the user
        print("\n=== Your Cart ===")
        for idx, (cart_id, product_name, quantity) in enumerate(cart_items, start=1):
            print(f"{idx}. {product_name} (Quantity: {quantity})")

        # Prompt the user to select an item to remove
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
    # Verify the password (you could use a hash comparison here)
    if password != password_hash:
        print("Incorrect password.")
        return None, None

    print(f"Welcome {username}!")
    return user_id, is_admin

def display_menu(is_admin):
    """Display the main menu with options based on user role."""
    print("\n=== Main Menu ===")
    if is_admin:
        print("1. View all users")
    print("2. View your cart")
    print("3. Add a product to the cart")
    print("4. Create an order")
    print("5. View your orders")
    print("6. Add a review for a product")
    print("7. Remove an item from your cart")  # New option for removing items
    print("8. Exit")

def main():
    """Main function to run the application."""
    database = "Checkpoint2-dbase.sqlite3"
    conn = connect_to_database(database)
    if conn is None:
        return
    
    # Login and greet the user
    user_id, is_admin = login(conn)
    if user_id is None:
        return

    while True:
        display_menu(is_admin)
        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1" and is_admin:
            view_all_users(conn)
        elif choice == "2":
            view_cart(conn, user_id)
        elif choice == "3":
            add_product_to_cart(conn, user_id)
        elif choice == "4":
            create_order(conn, user_id)
        elif choice == "5":
            view_orders(conn, user_id)
        elif choice == "6":
            add_review(conn)
        elif choice == "7":
            remove_item_from_cart(conn, user_id)
        elif choice == "8":
            print("Exiting the application. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
    
    conn.close()

if __name__ == "__main__":
    main()