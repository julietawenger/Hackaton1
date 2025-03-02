from scipy.stats import pearsonr
import numpy as np
import pandas as pd
import ast

# Load datasets
user_df = pd.read_csv(r"users.csv")
book_data = pd.read_csv(r"Amazon_books_cleaned.csv")

<<<<<<< HEAD
book_data = pd.read_csv(r"Amazon_books_cleaned.csv")
=======
>>>>>>> 1b4d8168df590c1809b116e0f06f30ae8e333293
def clean_book_df(book_data):
    """Cleans the book dataset and ensures the genre column is properly formatted."""
    book_df = book_data.dropna(axis=1, thresh=len(book_data) * 2 / 3)
    book_df = book_df.dropna(subset=['genre'])

    # Convert genre column from string representation to list
    book_df['genre'] = book_df['genre'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else x)
    
    return book_df

book_df = clean_book_df(book_data)

def explode_df(book_df):
    """Explodes the genre column to facilitate filtering."""
    return book_df.explode('genre').reset_index(drop=True)

def book_hist_to_df(user_df, target_user_ID):
    """Converts a user's book history into a DataFrame."""
    book_ratings = []
    
    book_history = user_df.iloc[target_user_ID]["book_history"]

    if pd.isna(book_history):
        return pd.DataFrame(book_ratings)  # Return empty DataFrame if missing

    if isinstance(book_history, str):
        try:
            book_history = ast.literal_eval(book_history)
        except (ValueError, SyntaxError):
            return pd.DataFrame(book_ratings)  # Return empty DataFrame if parsing fails

    if isinstance(book_history, list):
        for book in book_history:
            if isinstance(book, dict) and "book" in book and "rating" in book:
                book_ratings.append({"user_id": target_user_ID, "book": book["book"], "rating": book["rating"]})

    return pd.DataFrame(book_ratings)

def user_book_rating_df(user_df):
    """Creates a DataFrame of all users' book ratings."""
    ratings_df_list = [book_hist_to_df(user_df, i) for i in user_df.index]
    return pd.concat(ratings_df_list, ignore_index=True)

def ratings_matrix(user_df):
    """Generates a user-item ratings matrix with books as columns and users as rows."""
    ratings_df = user_book_rating_df(user_df).groupby(["user_id", "book"], as_index=False).agg({"rating": "mean"})
    return ratings_df.pivot(index="user_id", columns="book", values="rating").fillna(0)

def find_similar_users(user_id, user_df):
    """Finds the most similar users to a given user using Pearson correlation."""
    rating_matrix = ratings_matrix(user_df)
    similarities = {}
    target_user_ratings = rating_matrix.loc[user_id]

    for other_user in rating_matrix.index:
        if other_user != user_id:
            corr, _ = pearsonr(target_user_ratings, rating_matrix.loc[other_user])
            similarities[other_user] = corr

    return sorted(similarities.items(), key=lambda x: x[1], reverse=True)

def recommend_books_by_users(book_df, user_df, user_id):
    """Recommends books based on similar users' preferences."""
    book_df_2 = explode_df(book_df)
    rating_matrix = ratings_matrix(user_df)

    similar_users = find_similar_users(user_id, user_df)[:5]
    similar_users_ids = [user[0] for user in similar_users]

    similar_users_ratings = rating_matrix.loc[similar_users_ids]
    avg_ratings = similar_users_ratings.mean().sort_values(ascending=False)

    user_rated_books = set(rating_matrix.loc[user_id][rating_matrix.loc[user_id] > 0].index)
    recommendations = avg_ratings.drop(user_rated_books).head()
    recommendations = recommendations[recommendations > 0] 

    if recommendations.empty:
        return [], []

<<<<<<< HEAD
print(recommend_books_by_users(book_df, user_df, 20))
print(recommend_by_total_rating(book_df, user_df, 20))
=======
    books, authors = [], []
    for book_title in recommendations.index:
        matching_books = book_df_2[book_df_2['title'] == book_title]
        if not matching_books.empty:
            books.append(book_title)
            authors.append(matching_books['author'].iloc[0])

    return books, authors

def recommend_by_total_rating(book_df, user_df, target_user_ID):
    """Recommends books based on the highest overall rating in the user's preferred genres."""
    book_df_2 = explode_df(book_df)
    
    try:
        user_preferences = ast.literal_eval(user_df.iloc[target_user_ID]["preferences"])
    except (ValueError, SyntaxError):
        return [], []  # Return empty lists if preferences cannot be parsed

    filtered_books = book_df_2[book_df_2['genre'].apply(lambda x: any(g in x for g in user_preferences))]
    filtered_books = filtered_books.sort_values(by='rating', ascending=False)

    try:
        reader_book_list = [i['book'] for i in ast.literal_eval(user_df.iloc[target_user_ID]["book_history"])]
    except (ValueError, SyntaxError):
        reader_book_list = []  # Default to empty list if parsing fails

    recommended_books = filtered_books[~filtered_books['title'].isin(reader_book_list)].drop_duplicates(subset='title')

    books, authors = [], []
    for _, row in recommended_books.head(5).iterrows():
        books.append(row["title"])
        authors.append(row["author"])

    return books, authors

""" # Example usage
user_id = 500

books_by_users, authors_by_users = recommend_books_by_users(book_df, user_df, user_id)
books_by_rating, authors_by_rating = recommend_by_total_rating(book_df, user_df, user_id)

print("Recommended Books Based on Similar Users:")
for title, author in zip(books_by_users, authors_by_users):
    print(f" - {title} by {author}")

print("\nRecommended Books Based on High Ratings in Preferred Genres:")
for title, author in zip(books_by_rating, authors_by_rating):
    print(f" - {title} by {author}")
 """
>>>>>>> 1b4d8168df590c1809b116e0f06f30ae8e333293
