import csv
import os
import random

# 1) Import your recommendation engine code or relevant functions
# For example:
from recommendations_engine import recommend_by_total_rating
# Or whatever function you use to recommend

########################################
# HELPER FUNCTIONS FOR BOOKS DB
########################################
def book_exists_in_db(title, author, books_file="Amazon_books_cleaned.csv"):
    """
    Return True if there's a row in Amazon_books_cleaned.csv with the same title and author.
    """
    if not os.path.isfile(books_file):
        return False
    with open(books_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["title"].strip().lower() == title.strip().lower() and \
               row["author"].strip().lower() == author.strip().lower():
                return True
    return False

def get_next_book_id(books_file="Amazon_books_cleaned.csv"):
    """
    Determine the next book id by scanning existing rows in Amazon_books_cleaned.csv.
    We'll assume 'id' is a numeric column.
    """
    if not os.path.isfile(books_file):
        return 1  # If no file yet, start at ID=1
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
    Add a brand-new book to Amazon_books_cleaned.csv using the rating & genre.
    We'll initialize reviews_count=1 for new books.
    """
    reviews_count_val = 1
    new_id = get_next_book_id(books_file)

    # We'll store the genre as a list in string form, e.g. "['Fantasy']"
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
# USER-RELATED FUNCTIONS
########################################

def get_next_user_id(file_path="users.csv"):
    """Determine the next user ID by reading the existing CSV file."""
    if not os.path.isfile(file_path):
        return 1
    max_id = 0
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                user_id = int(row["UserID"])
                if user_id > max_id:
                    max_id = user_id
            except (ValueError, KeyError):
                continue
    return max_id + 1

def user_exists(user_id, name, file_path="users.csv"):
    """Check if a user ID and name exist in the CSV file."""
    if not os.path.isfile(file_path):
        return False
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Compare user ID and name in a case-insensitive manner
            if row["UserID"] == user_id and row["Name"].strip().lower() == name.strip().lower():
                return True
    return False

def get_user_row(user_id, file_path="users.csv"):
    """
    Retrieve the entire row (as a dictionary) for the given user_id from users.csv.
    Return None if not found.
    """
    if not os.path.isfile(file_path):
        return None
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["UserID"] == user_id:
                return row
    return None

def overwrite_user_row(updated_row, file_path="users.csv"):
    """
    Given an updated row (dictionary) for a user, rewrite the entire CSV with this row replaced.
    """
    if not os.path.isfile(file_path):
        return

    # Read all existing rows into memory
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        all_rows = list(reader)

    # Modify the matching row
    for i, row in enumerate(all_rows):
        if row["UserID"] == updated_row["UserID"]:
            all_rows[i] = updated_row
            break

    # Rewrite the entire file
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

########################################
# MENU ACTIONS
########################################

def recommend_books_for_user(user_id):
    """
    Use your recommendations_engine.py to get recommended books for this user.
    We'll load user_df and exploded_df or whichever frames you need, then call the function.
    """
    import pandas as pd
    # For example, let's say your engine expects user_df and book_df, 
    # just as in your code. We'll do a quick load:
    user_df = pd.read_csv("users.csv")  
    # Maybe you need an 'exploded_df' or something from Amazon_books_cleaned.csv
    book_df = pd.read_csv("Amazon_books_cleaned.csv")
    # If you want to parse 'genre' as a list, do so. We'll assume your code can handle it or you do:
    # ...
    # Now call your recommendation function
    # Example:
    recommended_titles, recommended_authors = recommend_by_total_rating(user_df, book_df, int(user_id))
    print("\nRecommended Books for You:\n")
    for t, a in zip(recommended_titles, recommended_authors):
        print(f" - {t} by {a}")
    print()

def rate_a_book(user_id):
    """
    Let the logged-in user add (rate) a single book. 
    If it doesn't exist, create it. Then update the user's RatedBooks.
    """
    row = get_user_row(user_id)
    if not row:
        print("User not found. Cannot rate a book.")
        return

    # Prompt for book details
    book_title = input("Enter the book title you want to rate: ").strip()
    author = input("Enter the author for this book: ").strip()

    # rating
    rating_input = input("Enter rating for this book (1-5): ").strip()
    try:
        rating_val = float(rating_input)
        if rating_val < 1 or rating_val > 5:
            print("Rating must be between 1 and 5. Setting rating to 5 by default.")
            rating_val = 5.0
    except ValueError:
        print("Invalid rating. Setting rating to 5 by default.")
        rating_val = 5.0

    # genre
    book_genre = input("Enter genre for this book: ").strip()

    # If not in DB, add
    if not book_exists_in_db(book_title, author, "Amazon_books_cleaned.csv"):
        new_id = add_book_to_db(book_title, author, rating_val, book_genre, "Amazon_books_cleaned.csv")
        print(f"Added new book '{book_title}' by {author} (ID={new_id}) to Amazon_books_cleaned.csv.")
    else:
        print("Book already exists in DB. We'll just record your rating in your read history.")

    # Now add to user's read history
    import ast
    # parse the existing RatedBooks
    rated_books_str = row["RatedBooks"]
    try:
        rated_books_list = ast.literal_eval(rated_books_str) if rated_books_str else []
    except:
        rated_books_list = []

    new_book_entry = {
        "book": book_title,
        "author": author,
        "genre": book_genre,
        "rating": rating_val
    }
    rated_books_list.append(new_book_entry)

    # Update row
    row["RatedBooks"] = str(rated_books_list)
    overwrite_user_row(row)  # persist changes
    print(f"'{book_title}' has been added to your read history with a rating of {rating_val}.")

def surprise_me():
    """
    Pick 3 random books from Amazon_books_cleaned.csv and show them.
    """
    if not os.path.isfile("Amazon_books_cleaned.csv"):
        print("No books found in Amazon_books_cleaned.csv. Cannot surprise you yet!")
        return

    # read all books
    import pandas as pd
    df = pd.read_csv("Amazon_books_cleaned.csv")
    if df.empty:
        print("The books file is empty. No surprises available.")
        return

    # If we have fewer than 3 books, show all
    sample_size = min(3, len(df))
    picks = df.sample(sample_size)

    print("\nSurprise Books:\n")
    for _, row in picks.iterrows():
        print(f" - {row['title']} by {row['author']} (ID={row['id']})")
    print()

########################################
# CREATE/LOGIN USER
########################################

def create_user():
    name = input("Enter your name: ").strip()
    age = input("Enter your age: ").strip()
    genres_input = input("Enter your preferred genres (comma-separated): ")
    preferred_genres = [g.strip() for g in genres_input.split(',') if g.strip()]
    preferred_genres_str = str(preferred_genres)
    
    books_list = []
    newly_added_books = []
    
    add_books = input("Would you like to add books you have read and their details (title, author, rating, genre)? (yes/no): ").strip().lower()
    if add_books in ["yes", "y"]:
        while True:
            book_title = input("Enter book title (or press Enter to finish): ").strip()
            if not book_title:
                break

            author = input("Enter author for this book: ").strip()
            rating_input = input("Enter rating for this book (1-5): ").strip()
            try:
                rating_val = float(rating_input)
                if rating_val < 1 or rating_val > 5:
                    print("Rating must be between 1 and 5. Setting rating to 5 by default.")
                    rating_val = 5.0
            except ValueError:
                print("Invalid rating. Setting rating to 5 by default.")
                rating_val = 5.0

            book_genre = input("Enter genre for this book: ").strip()

            # If this book doesn't exist, add it
            if not book_exists_in_db(book_title, author):
                new_book_id = add_book_to_db(book_title, author, rating_val, book_genre)
                newly_added_books.append((book_title, author, new_book_id))

            # update local user read list
            book_entry = {
                "book": book_title,
                "author": author,
                "genre": book_genre,
                "rating": rating_val
            }
            books_list.append(book_entry)

    rated_books_str = str(books_list)
    flag = 1
    file_path = "users.csv"
    user_id = str(get_next_user_id(file_path))  # make sure it's string for easy matching
    file_exists = os.path.isfile(file_path)

    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        fieldnames = ["UserID", "Name", "Age", "PreferredGenres", "RatedBooks", "Flag"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "UserID": user_id,
            "Name": name,
            "Age": age,
            "PreferredGenres": preferred_genres_str,
            "RatedBooks": rated_books_str,
            "Flag": flag
        })
    
    print(f"User '{name}' created successfully!")
    print(f"Your user ID is {user_id}. You will need your user ID and name to log in.")
    for book_title, author, new_id in newly_added_books:
        print(f"Added new book '{book_title}' by {author} (ID={new_id}) to Amazon_books_cleaned.csv.")

def logged_in_menu(user_id, user_name):
    """
    Once the user is logged in, show them 4 menu options in a loop
    until they pick '4' (log out).
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
            print("Invalid choice. Please select 1, 2, 3, or 4.")

def main():
    print("Welcome to The BibliOracle!")
    while True:
        choice = input("Would you like to (1) Log in or (2) Create a new account? (Enter 1 or 2): ").strip()
        if choice == "1":
            user_id = input("Enter your User ID: ").strip()
            name = input("Enter your name: ").strip()
            if user_exists(user_id, name):
                print(f"Welcome back, {name}! (User ID: {user_id})")
                # Present the user with the logged-in menu
                logged_in_menu(user_id, name)
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
