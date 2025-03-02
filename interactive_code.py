import csv
import os
import random

# Import the function from recommendations_engine.py
from recommendations_engine import recommend_by_total_rating

###############################################################################
# HELPER FUNCTIONS: users.csv
###############################################################################

def get_next_zero(file_path="users.csv"):
    """
    Auto-increment the '0' column by scanning existing rows for the max value in '0'.
    """
    if not os.path.isfile(file_path):
        return 1
    max_val = 0
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                zero_int = int(row["0"])
                if zero_int > max_val:
                    max_val = zero_int
            except (ValueError, KeyError):
                continue
    return max_val + 1

def get_next_id(file_path="users.csv"):
    """
    Determine the next user's ID by scanning existing rows in users.csv.
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
    Return True if there's a row in 'users.csv' with ID == user_id and name == user_name (case-insensitive).
    """
    if not os.path.isfile(file_path):
        return False
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["ID"] == str(user_id) and row["name"].strip().lower() == user_name.strip().lower():
                return True
    return False

def get_user_row(user_id, file_path="users.csv"):
    """
    Return the entire row (dict) for the user with ID == user_id, or None if not found.
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

    # find & replace
    for i, row in enumerate(all_rows):
        if row["ID"] == updated_row["ID"]:
            all_rows[i] = updated_row
            break

    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

###############################################################################
# HELPER FUNCTIONS: Amazon_books_cleaned.csv
###############################################################################

def book_exists_in_db(title, author, books_file="Amazon_books_cleaned.csv"):
    """
    Check if a book with the same title & author (case-insensitive) exists in books_file.
    """
    if not os.path.isfile(books_file):
        return False
    import pandas as pd
    df = pd.read_csv(books_file)
    # If there's no 'title' or 'author' column, this will KeyError
    # We assume 'title' and 'author' exist
    df["title_lower"] = df["title"].str.lower().str.strip()
    df["author_lower"] = df["author"].str.lower().str.strip()

    match = df[
        (df["title_lower"] == title.strip().lower()) &
        (df["author_lower"] == author.strip().lower())
    ]
    return not match.empty

def get_next_book_id(books_file="Amazon_books_cleaned.csv"):
    """
    Return the next integer 'id' for a new book, scanning existing rows in 'Amazon_books_cleaned.csv'.
    """
    if not os.path.isfile(books_file):
        return 1
    import pandas as pd
    df = pd.read_csv(books_file)
    if "id" not in df.columns:
        return 1
    max_id = 0
    for val in df["id"]:
        try:
            val_int = int(val)
            if val_int > max_id:
                max_id = val_int
        except:
            continue
    return max_id + 1

def add_book_to_db(title, author, user_rating, user_genre, books_file="Amazon_books_cleaned.csv"):
    """
    Append a new book to 'Amazon_books_cleaned.csv' with an auto-incremented 'id'.
    Initialize 'reviews_count' to 1 and store 'rating' = user_rating, 'genre' as a list string.
    """
    import pandas as pd
    new_id = get_next_book_id(books_file)
    reviews_count_val = 1
    genre_list_str = str([user_genre])  # e.g. "['Fantasy','Adventure']"

    file_exists = os.path.isfile(books_file)
    fieldnames = ["id","title","author","rating","reviews_count","genre"]
    with open(books_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
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

###############################################################################
# MENU ACTIONS: (1) Recommend, (2) Rate, (3) Surprise, (4) Log out
###############################################################################

def recommend_books_for_user(user_id):
    """
    Call the 'recommend_by_total_rating' function from recommendations_engine.py.
    NOTE: This code uses 'target_user_ID' as a row index in user_df, so if user_id doesn't
    match the row index, you can get KeyError. This is a known limitation.
    """
    import pandas as pd
    import ast
    from recommendations_engine import recommend_by_total_rating
    from recommendations_engine import recommend_books_by_users

    # Read up-to-date user and book data
    if not os.path.isfile("users.csv"):
        print("No users.csv found, cannot recommend.")
        return
    user_df = pd.read_csv("users.csv")

    if not os.path.isfile("Cleaned Data/Amazon_books_cleaned.csv"):
        print("No Amazon_books_cleaned.csv found, cannot recommend.")
        return
    book_data = pd.read_csv("Cleaned Data/Amazon_books_cleaned.csv")

    # The existing function expects 'target_user_ID' to be the row index in user_df
    # So let's parse user_id as int, but that won't help if user_id=500 but the row is actually at index=0
    user_id_int = int(user_id)

    try:
        titles, authors = recommend_by_total_users(book_data, user_df, user_id_int)
    except KeyError as e:
        print(f"KeyError: {e}. Possibly your user ID is larger than user_df has rows.")
        print("In your engine code, you used .iloc[target_user_ID], so user_id must match row index!")
        return

    if not titles:
        print("No recommendations found (maybe user has read everything or no matching genres).")
        return

    print("\nRecommended Books for You:\n")
    for t, a in zip(titles, authors):
        print(f" - {t} by {a}")
    print()

def rate_a_book(user_id):
    """
    Let the logged-in user add (rate) a single book. 
    If the book doesn't exist in DB, add it. 
    Then update their 'book_history' in users.csv.
    """
    row = get_user_row(user_id)
    if not row:
        print("User not found in CSV. Can't rate a book.")
        return

    book_title = input("Enter the book title: ").strip()
    author = input("Enter the author: ").strip()

    rating_str = input("Enter rating (1-5): ").strip()
    try:
        rating_val = float(rating_str)
        if rating_val < 1 or rating_val > 5:
            print("Rating must be between 1 and 5. Setting to 5.")
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
        print("Book already exists in DB; we'll just record your rating in your read history.")

    import ast
    history_str = row["book_history"]
    try:
        history_list = ast.literal_eval(history_str) if history_str else []
    except:
        history_list = []

    # Append new rating
    new_rating_dict = {
        "book": book_title,
        "author": author,
        "genre": book_genre,
        "rating": rating_val
    }
    history_list.append(new_rating_dict)
    row["book_history"] = str(history_list)

    overwrite_user_row(row)
    print(f"'{book_title}' added to your read history with a rating of {rating_val}.")

def surprise_me():
    """
    Print 3 random books from 'Amazon_books_cleaned.csv'.
    """
    if not os.path.isfile("Cleaned Data/Amazon_books_cleaned.csv"):
        print("No Amazon_books_cleaned.csv found. Cannot surprise you.")
        return

    import pandas as pd
    df = pd.read_csv("Cleaned Data/Amazon_books_cleaned.csv")
    if df.empty:
        print("No books in the DB yet.")
        return

    picks = df.sample(min(3, len(df)))
    print("\nSurprise Books:\n")
    for _, row in picks.iterrows():
        print(f" - {row['title']} by {row['author']} (ID={row['id']})")
    print()

def logged_in_menu(user_id, user_name):
    """
    Once the user logs in, show the 4 options:
     1) Recommend a new book
     2) Rate a book
     3) Surprise me
     4) Log out
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
            print("We hope to see you soon!")
            break
        else:
            print("Invalid choice. Please select 1, 2, 3, or 4.")

###############################################################################
# CREATE USER OR LOG IN
###############################################################################

def create_user():
    """
    Create a new row in users.csv with columns:
      0,name,age,preferences,book_history,ID
    The user will log in with ID plus name.
    """
    name = input("Enter your name: ").strip()
    age = input("Enter your age: ").strip()
    prefs_inp = input("Enter your preferred genres (comma-separated): ")
    prefs_list = [p.strip() for p in prefs_inp.split(',') if p.strip()]
    prefs_str = str(prefs_list)

    book_history_list = []
    new_books_added = []

    add_books = input("Would you like to add any books you've read? (yes/no): ").strip().lower()
    if add_books in ["yes", "y"]:
        while True:
            btitle = input("Enter book title (or press Enter to finish): ").strip()
            if not btitle:
                break
            bauthor = input("Enter author: ").strip()
            brating = input("Enter rating (1-5): ").strip()
            try:
                r_val = float(brating)
                if r_val < 1 or r_val > 5:
                    r_val = 5.0
            except ValueError:
                r_val = 5.0
            bgenre = input("Enter genre: ").strip()

            if not book_exists_in_db(btitle, bauthor):
                new_bk_id = add_book_to_db(btitle, bauthor, r_val, bgenre)
                new_books_added.append((btitle, bauthor, new_bk_id))

            book_history_list.append({
                "book": btitle,
                "author": bauthor,
                "genre": bgenre,
                "rating": r_val
            })

    zero_val = get_next_zero()
    new_id = get_next_id()
    bh_str = str(book_history_list)

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
            "book_history": bh_str,
            "ID": new_id
        })

    print(f"User '{name}' created successfully!")
    print(f"Your user ID is {new_id}. You'll need it (and your name) to log in.")
    for t, a, bid in new_books_added:
        print(f"Added new book '{t}' by {a} (ID={bid}) to Amazon_books_cleaned.csv.")

def main():
    print("Welcome to The BibliOracle!")
    while True:
        choice = input("Would you like to (1) Log in or (2) Create a new account? ").strip()
        if choice == "1":
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