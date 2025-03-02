

from scipy.stats import pearsonr
import numpy as np
import pandas as pd
import ast

user_df = pd.read_csv(r"users.csv")

book_data = pd.read_csv(r"Amazon_books_cleaned.csv")
def clean_book_df(book_data):

    # Convert to DataFrame and clean
    book_df = pd.DataFrame(book_data)
    book_df = book_df.dropna(axis=1, thresh=len(book_df)*2/3)
    book_df = book_df.dropna(subset=['genre'])

    # I need this line to read the genre column as a list
    book_df['genre'] = book_df['genre'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else x)
    return book_df

book_df = clean_book_df(book_data)

def explode_df(book_df):

    exploded_df = book_df.explode('genre')
    exploded_df = exploded_df.reset_index(drop=True)
    return exploded_df

def recommend_by_total_rating(book_df, user_df, target_user_ID):
    book_df_2 = explode_df(book_df)
    # First I need to access the user preferences
    user_preferences = ast.literal_eval(user_df.iloc[target_user_ID]["preferences"])
    # I need to filter the dataframe based on the user's preferences 
    filtered_books = book_df_2[book_df_2['genre'].apply(lambda x: any(g in x for g in user_preferences))]
    # Sort by rating
    filtered_books = filtered_books.sort_values(by = 'rating', ascending=False)
    # Creates a list of the books read by the user
    reader_book_list = [i['book'] for i in ast.literal_eval(user_df.iloc[target_user_ID]["book_history"])]
    # Remove books that the user has already read
    recommended_books = filtered_books[~filtered_books['title'].isin(reader_book_list)]
    recommended_books = recommended_books.drop_duplicates(subset = 'title')
    # Return top 5 recommendations
    authors = []
    titles = list(recommended_books.head(5)["title"])
    for i in titles:
        authors.append(list(book_df_2[book_df_2["title"]== i]['author'])[0])
    return titles, authors      
    

def book_hist_to_df(user_df, target_user_ID):
    """This function takes a row from the users database and returns the users reading history in a DataFrame."""    
    book_ratings = []
    for book in ast.literal_eval(user_df.iloc[target_user_ID]["book_history"]):
            book_ratings.append({"user_id": target_user_ID, "book": book["book"], "rating": book["rating"]})
    return pd.DataFrame(book_ratings)

def user_book_rating_df(user_df):
    """This function concatenates the book_hist_to_df to all rows in the users database."""    
    ratings_df_list = []
    for i in user_df.index:
        ratings_df_list.append(book_hist_to_df(user_df,i))
    ratings_df = pd.concat(ratings_df_list, ignore_index= True) 
    return ratings_df

def ratings_matrix(user_df):
    #If a user rated the same book multiple times, take the average rating.
    ratings_df = user_book_rating_df(user_df).groupby(["user_id", "book"], as_index=False).agg({"rating": "mean"})

    # Rating matrix has the size books x users and if they read the book, the value is the rating. Otherwise it's 0.
    rating_matrix = ratings_df.pivot(index="user_id", columns="book", values="rating")
    rating_matrix = rating_matrix.fillna(0)  # Fill missing values with 0
    return rating_matrix
#
def find_similar_users(user_id, user_df):
    """This function finds users who correlate to the target user."""
    
    rating_matrix = ratings_matrix(user_df)
    similarities = {}
    target_user_ratings = rating_matrix.loc[user_id]
    
    for other_user in rating_matrix.index:
        if other_user != user_id:
            corr, _ = pearsonr(target_user_ratings, rating_matrix.loc[other_user])
            similarities[other_user] = corr

    return sorted(similarities.items(), key=lambda x: x[1], reverse=True) 

def recommend_books_by_users(book_df, user_df, user_id):
    book_df_2 = explode_df(book_df)
    rating_matrix = ratings_matrix(user_df)

    similar_users = find_similar_users(user_id, user_df)[:5]
    similar_users_ids = [user[0] for user in similar_users]
    
    # Get books rated highly by similar users
    similar_users_ratings = rating_matrix.loc[similar_users_ids]
    avg_ratings = similar_users_ratings.mean().sort_values(ascending=False)

    # Exclude books already rated by the target user
    user_rated_books = set(rating_matrix.loc[user_id][rating_matrix.loc[user_id] > 0].index)
    recommendations = avg_ratings.drop(user_rated_books).head()

    # Keep only recommendations with correlations higher than zero.
    recommendations = recommendations[recommendations > 0] 
    if len(recommendations) >0:
        books=[]
        authors=[]
        for i in recommendations.items():
            book = i[0]
            author = book_df_2.loc[book_df_2['title'] == book, 'author'].iloc[0]
            books.append(book)
            authors.append(author)

        return books, authors

print(recommend_books_by_users(book_df, user_df, 20))
print(recommend_by_total_rating(book_df, user_df, 20))