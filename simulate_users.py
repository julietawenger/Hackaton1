
import pandas as pd
import numpy as np
import faker
fake = faker.Faker()
import random
import ast

# Fist I load the Database
book_data = pd.read_csv(r"Cleaned Data/Amazon_books_cleaned.csv")

# Convert to DataFrame and clean
book_df = pd.DataFrame(book_data)
book_df = book_df.dropna(axis=1, thresh=len(book_df)*2/3)
book_df = book_df.dropna(subset=['genre'])

# I need this line to read the genre column as a list
book_df['genre'] = book_df['genre'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else x)

# Now I can explode by genre. This way I get a new row for every genre listed per book.
exploded_df = book_df.explode('genre')
exploded_df = exploded_df.reset_index(drop=True)

#

##### NOW WE CAN CREATE SOME FAKE PEOPLE ###


def random_book(df, genre):
    """Given a dataframe and a genre, returns: title, ID. """
    genre_books = df[df["genre"] == genre]
    if genre_books.empty:
        return None, None  # In case no books are found for the genre
    
    selected_book = genre_books.sample(1).iloc[0]  # Get a random book
    return selected_book["title"], selected_book["id"]


def random_person(df, max_book_amount = 5):
    """"Given a database that has to have these columns: 'genre', 'id', 'rating', 'book', returns a fake user history data."""
    #We need to create a list of all unique genres:

    # Creates a set of unique genres
    unique_genres = set()
    for genres in book_df['genre']:
        unique_genres.update(genres)

    
    # Creates a random list of a person's favorites genres
    preferences = random.sample(list(unique_genres), random.randint(1,4))
    
    # "book_history": [{"book": "Harry Potter", "author": 'J.K. Rowling' ,"genre": "Adventure", "rating": 5}]
    book_history = []
    seen_books = set()
    for i in range(random.randint(1,max_book_amount)):
        genre = random.choice(preferences) # Chooses one of the favorite genres
        book_title, book_id= random_book(df, genre) # Returns book title and ID of a book that genre
        if book_id in seen_books:  # Skip if book is already in history
            continue      
        seen_books.add(book_id)
    
        extract_rating = float(df.loc[df['id'] == book_id, 'rating'].values[0])
        rating =max(0, min(np.random.normal(extract_rating, 0.2), 5)) # Returns a rating of the book from a normal dist. centered on the book's rating.
        author = df.loc[df['id'] == book_id, 'author'].values[0]

        book_history.append({"book": book_title, "author": author,"genre": genre, "rating": round(rating,1), "genre": genre})
        
    # One fake user data
    dictionary ={"name": fake.name(), "age": np.random.randint(12,85), "preferences": preferences, "book_history": book_history}
    return dictionary

def user_data(n, max_book_amount = 5):
    """Creates a dataframe of length n."""
    df =  pd.DataFrame({i: random_person(exploded_df, max_book_amount) for i in range(n)}).T
    df["ID"] = df.index
    return df


# This creates users and saves them in a file
users = user_data(500, 100)
users.to_csv('users.csv')