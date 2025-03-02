import csv
import os
import random

# If you have a separate recommendation engine, import it here.
# Example:
from recommendations_engine import recommend_by_total_rating

########################################
# HELPER FUNCTIONS: Managing the users.csv
########################################

def get_next_zero(file_path="users.csv"):
    """
    Auto-increment the '0' column by scanning existing rows for the max value in '0'.
    If file doesn't exist yet, return 1.
    """
    if not os.path.isfile(file_path):
        return 1
    max_val = 0
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                zero_int = int(row["0"])  # Convert the '0' column to int
                if zero_int > max_val:
                    max_val = zero_int
            except (ValueError, KeyError):
                continue
    return max_val + 1

def get_next_id(file_path="users.csv"):
    """
    Determine the next unique user 'ID' by scanning existing rows in users.csv.
    If file doesn't exist yet, return 1.
    """
    if not os.path.isfile(file_path):
        return 1
    max_id = 0
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                current_id = int(row["ID"])
                if current_id > max_id:
                    max_id = current_id
            except (ValueError, KeyError):
                continue
    return max_id + 1

def user_exists(user_id, user_name, file_path="users.csv"):
    """
    Returns True if a row in users.csv has ID == user_id and name == user_name.
    """
    if not os.path.isfile(file_path):
        return False
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Compare ID column and case-insensitive name
            if row["ID"] == str(user_id) and row["name"].strip().lower() == user_name.strip().lower():
                return True
    return False

def get_user_row(user_id, file_path="users.csv"):
    """
    Return the entire row (as a dict) for the user with ID == user_id, else None.
    """
    if not os.path.isfile(file_path):
        return None
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["ID"] == str(user_id):
                return row
    return None

def overwrite_user_row(updated_row, file_path="users.csv"):
    """
    Rewrite the CSV, replacing the row that has the same 'ID' as updated_row['ID'].
    """
    if not os.path.isfile(file_path):
        return

    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        all_rows = list(reader)

    # Find the matching row and replace it
    for i, row in enumerate(all_rows):
        if row["ID"] == updated_row["ID"]:
            all_rows[i] = updated_row
            break

    # Write all rows back
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

########################################
# HELPER FUNCTIONS: Managing Amazon_books_cleaned.csv
########################################

def book_exists_in_db(title, author, books_file="Amazon_books_cleaned.csv"):
    """
    Return True if there's a row in books_file with the same title+author (case-insensitive).
    """
    if not os.path.isfile(books_file):
        return False
    with open(books_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["title"].strip().lower() == title.strip().lower() \
               and row["author"].strip().lower() == author.strip().lower():
                return True
    return False

def get_next_book_id(books_file="Amazon_books_cleaned.csv"):
    """
    Return the next numeric id for a new book by scanning the existing 'id' column.
    """
    if not os.path.isfile(books_file):
        return 1
    max_id = 0
    with open(books_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                current_id = int(row["id"])
                if current_id > max_id:
                    max_id = current_id
            except (ValueError, KeyError):
                continue
    return max_id + 1

def add_book_to_db(title, author, user_rating, user_genre, books_file="Amazon_books_cleaned.csv"):
    """
    Add a brand-new book with user_rating, user_genre. Initialize reviews_count=1.
    """
    reviews_count_val = 1
    new_id = get_next_book_id(books_file)
    genre_list_str = str([user_genre])

    file_exists = os.path.isfile(books_file)
    with open(books_file, mode='a', newline='', encoding='utf-8') as file:
        fieldnames = ["id", "title", "author", "rating", "reviews_count", "genre"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "id": new_id,
            "title": title,
            "author": author,
            "rating": user_rating,
            "reviews_count": reviews_count_val,
            "genre": genre_list_str
        })
    return new_id

########################################
# MENU ACTIONS
########################################

def recommend_books_for_user(user_id):
    """
    Example: call your recommendation function from recommendations_engine.
    """
    import pandas as pd
    user_df = pd.read_csv("users.csv")
    book_df = pd.read_csv("Amazon_books_cleaned.csv")

    # Convert user_id to int if your engine uses integer IDs
    user_id_int = int(user_id)

    # Example call:
    recommended_titles, recommended_authors = recommend_by_total_rating(user_df, book_df, user_id_int)

    print("\nRecommended Books:\n")
    for t, a in zip(recommended_titles, recommended_authors):
        print(f" - {t} by {a}")
    print()

def rate_a_book(user_id):
    """
    Let the logged-in user add (rate) a single book. If it's missing, add it to DB.
    Then update their book_history in users.csv.
    """
    row = get_user_row(user_id)
    if not row:
        print("User not found in CSV. Can't rate.")
        return

    book_title = input("Enter the book title you want to rate: ").strip()
    author = input("Enter the author for this book: ").strip()

    rating_input = input("Enter rating for this book (1-5): ").strip()
    try:
        rating_val = float(rating_input)
        if rating_val < 1 or rating_val > 5:
            print("Rating must be 1-5. Setting to 5.")
            rating_val = 5.0
    except ValueError:
        print("Invalid rating. Setting to 5.")
        rating_val = 5.0

    book_genre = input("Enter genre for this book: ").strip()

    # If not in DB, add it
    if not book_exists_in_db(book_title, author):
        new_book_id = add_book_to_db(book_title, author, rating_val, book_genre)
        print(f"Added new book '{book_title}' by {author} (ID={new_book_id}).")
    else:
        print("Book already in DB. We'll just record your rating in your read history.")

    import ast
    history_str = row["book_history"]
    try:
        history_list = ast.literal_eval(history_str) if history_str else []
    except:
        history_list = []

    new_entry = {
        "book": book_title,
        "author": author,
        "genre": book_genre,
        "rating": rating_val
    }
    history_list.append(new_entry)

    row["book_history"] = str(history_list)
    overwrite_user_row(row)
    print(f"'{book_title}' added to your read history.")

def surprise_me():
    """
    Show 3 random books from Amazon_books_cleaned.csv.
    """
    if not os.path.isfile("Amazon_books_cleaned.csv"):
        print("No books in DB.")
        return

    import pandas as pd
    df = pd.read_csv("Amazon_books_cleaned.csv")
    if df.empty:
        print("No books found.")
        return

    picks = df.sample(min(3, len(df)))
    print("\nSurprise Books:\n")
    for _, row in picks.iterrows():
        print(f" - {row['title']} by {row['author']} (ID={row['id']})")
    print()

def logged_in_menu(user_id, user_name):
    """
    Once the user is logged in, present the 4 main options:
    1) recommend, 2) rate, 3) surprise, 4) logout.
    """
    while True:
        print("\n--- Logged In Menu ---")
        print("1) Recommend a new book")
        print("2) Rate a book")
        print("3) Surprise me")
        print("4) Log out")

        choice = input("Enter choice (1-4): ").strip()
        if choice == "1":
            recommend_books_for_user(user_id)
        elif choice == "2":
            rate_a_book(user_id)
        elif choice == "3":
            surprise_me()
        elif choice == "4":
            print("Logging out. Hope to see you soon!")
            break
        else:
            print("Invalid choice. Select 1, 2, 3, or 4.")

########################################
# CREATE OR LOG IN USER
########################################

def create_user():
    """
    Create a new user row in users.csv with columns:
    0,name,age,preferences,book_history,ID
    The user logs in with the ID column.
    """
    name = input("Enter your name: ").strip()
    age = input("Enter your age: ").strip()
    prefs_inp = input("Enter your preferred genres (comma-separated): ")
    prefs_list = [p.strip() for p in prefs_inp.split(',') if p.strip()]
    prefs_str = str(prefs_list)

    book_history_list = []
    new_books_added = []

    add_books = input("Would you like to add books you have read? (yes/no): ").strip().lower()
    if add_books in ["yes", "y"]:
        while True:
            title = input("Enter book title (or press Enter to finish): ").strip()
            if not title:
                break
            author = input("Enter author for this book: ").strip()
            r_inp = input("Enter rating (1-5): ").strip()
            try:
                r_val = float(r_inp)
                if r_val < 1 or r_val > 5:
                    r_val = 5.0
            except ValueError:
                r_val = 5.0
            g_inp = input("Enter genre for this book: ").strip()

            if not book_exists_in_db(title, author):
                new_bk_id = add_book_to_db(title, author, r_val, g_inp)
                new_books_added.append((title, author, new_bk_id))

            book_history_list.append({
                "book": title,
                "author": author,
                "genre": g_inp,
                "rating": r_val
            })

    zero_val = get_next_zero("users.csv")  # auto-increment for '0'
    new_id = get_next_id("users.csv")      # unique user ID
    b_history_str = str(book_history_list)

    file_exists = os.path.isfile("users.csv")
    with open("users.csv", mode='a', newline='', encoding='utf-8') as f:
        fieldnames = ["0", "name", "age", "preferences", "book_history", "ID"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "0": zero_val,
            "name": name,
            "age": age,
            "preferences": prefs_str,
            "book_history": b_history_str,
            "ID": new_id
        })

    print(f"User '{name}' created successfully!")
    print(f"Your user ID is {new_id}. Please use it (and your name) to log in.")
    for t, a, bid in new_books_added:
        print(f"Added new book '{t}' by {a} (ID={bid}) to Amazon_books_cleaned.csv.")

def main():
    print("Welcome to The BibliOracle!")
    while True:
        choice = input("Would you like to (1) Log in or (2) Create a new account? ").strip()
        if choice == "1":
            # The user logs in with ID column
            user_id = input("Enter your ID: ").strip()
            user_name = input("Enter your name: ").strip()
            if user_exists(user_id, user_name):
                print(f"Welcome back, {user_name}! (ID: {user_id})")
                logged_in_menu(user_id, user_name)
                break
            else:
                print("ID either does not exist or is invalid. Please try again.")
        elif choice == "2":
            create_user()
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()
