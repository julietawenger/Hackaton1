import pandas as pd

# Simulate a small book database
book_data = [
    {"title": "To Kill a Mockingbird", "author": "Harper Lee", "genre": ["Fiction", "Classic"], "ISBN": "9780061120084", "rating": 4.8},
    {"title": "1984", "author": "George Orwell", "genre": ["Dystopian", "Science Fiction"], "ISBN": "9780451524935", "rating": 4.7},
    {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "genre": ["Fiction", "Classic"], "ISBN": "9780743273565", "rating": 4.6},
    {"title": "Harry Potter and the Sorcerer's Stone", "author": "J.K. Rowling", "genre": ["Fantasy", "Adventure"], "ISBN": "9780590353427", "rating": 4.9},
    {"title": "Pride and Prejudice", "author": "Jane Austen", "genre": ["Romance", "Classic"], "ISBN": "9780141439518", "rating": 4.8},
    {"title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "genre": ["Fantasy", "Adventure"], "ISBN": "9780618640157", "rating": 4.9},
    {"title": "The Catcher in the Rye", "author": "J.D. Salinger", "genre": ["Fiction", "Classic"], "ISBN": "9780316769488", "rating": 4.3},
    {"title": "The Hobbit", "author": "J.R.R. Tolkien", "genre": ["Fantasy", "Adventure"], "ISBN": "9780345339683", "rating": 4.8},
    {"title": "Moby-Dick", "author": "Herman Melville", "genre": ["Fiction", "Adventure"], "ISBN": "9781503280786", "rating": 4.1},
    {"title": "War and Peace", "author": "Leo Tolstoy", "genre": ["Historical", "Classic"], "ISBN": "9781400079988", "rating": 4.7}
]

# Convert to DataFrame
book_df = pd.DataFrame(book_data)


# Display the book DataFrame
#print(book_df)

exploded_df = book_df.explode('genre')

# Now, group by genre
df_genre = exploded_df.reset_index(drop=True)

# Display the grouped data
#print(df_genre)

{
    "name": "John",
    "age": 25,
    "preferences": ["action", "thriller"],
    "watch_history": [{"movie": "Inception", "genre": "sci-fi", "rating": 5}]
}


"""
First, we need to create a list of all unique genres:
"""
unique_genres = set()
for genres in book_df['genre']:
    unique_genres.update(genres)


import numpy as np
import faker
fake = faker.Faker()
import random

 

def random_book(df, genre):
    """Given a dataframe and a genre, 
    Returns:
    title, ISBN
    """
    genre_books = df[df["genre"] == genre]
    if genre_books.empty:
        return None, None  # In case no books are found for the genre
    
    selected_book = genre_books.sample(1).iloc[0]  # Get a random book
    return selected_book["title"], selected_book["ISBN"]


def random_person(df):
    
    # Creates a random list of a person's favorites genres
    preferences = random.sample(list(unique_genres), random.randint(1,4))
    
    # "book_history": [{"book": "Harry Potter", "genre": "Adventure", "rating": 5}]
    book_history = []

    for i in range(random.randint(1,5)):
        genre = random.choice(preferences)
        book_title, book_isbn = random_book(df, genre)
        rating = df.loc[df['ISBN'] == book_isbn, 'rating'].values[0]
        book_history.append({"book": book_title, "genre": genre, "rating": int(rating) })

    dict ={"name": fake.name(), "age": np.random.randint(12,85), "preferences": preferences, "book_history": book_history}
    return dict
print(random_person(df_genre))


