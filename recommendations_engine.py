
from simulate_users import book_df 
from simulate_users import exploded_df
from simulate_users import user_data
from scipy.stats import pearsonr
import numpy as np
import pandas as pd

user_df = user_data(5000)



#%%
def recommend_by_total_rating(user_df, book_df, target_user_ID):
    
    # First I need to access the user preferences
    user_preferences = user_df.iloc[target_user_ID]["preferences"]
    # I need to filter the dataframe based on the user's preferences 
    filtered_books = book_df[book_df['genre'].apply(lambda x: any(g in x for g in user_preferences))]
    # Sort by rating
    filtered_books = filtered_books.sort_values(by = 'rating', ascending=False)
    # Creates a list of the books read by the user
    reader_book_list = [i['book'] for i in user_df.iloc[target_user_ID]["book_history"]]
    # Remove books that the user has already read
    recommended_books = filtered_books[~filtered_books['title'].isin(reader_book_list)]
    # Return top 5 recommendations
    return list(recommended_books.head(5)["title"])     
    


def book_hist_to_df(df, row):
    """This function takes a row from the users database and returns the users reading history in a DataFrame."""    
    book_ratings = []
    for book in df.iloc[row]["book_history"]:
            book_ratings.append({"user_id": row, "book": book["book"], "rating": book["rating"]})
    return pd.DataFrame(book_ratings)

def user_book_rating_df(user_df):
    """This function concatenates the book_hist_to_df to all rows in the users database."""    
    ratings_df_list = []
    for i in user_df.index:
        ratings_df_list.append(book_hist_to_df(user_df,i))
    ratings_df = pd.concat(ratings_df_list, ignore_index= True) 
    return ratings_df

#If a user rated the same book multiple times, take the average rating.
ratings_df = user_book_rating_df(user_df).groupby(["user_id", "book"], as_index=False).agg({"rating": "mean"})


# Rating matrix has the size books x users and if they read the book, the value is the rating. Otherwise it's 0.
rating_matrix = ratings_df.pivot(index="user_id", columns="book", values="rating")
rating_matrix = rating_matrix.fillna(0)  # Fill missing values with 0



def find_similar_users(user_id, rating_matrix):
    """This function finds users who correlate to the target user."""
    similarities = {}
    target_user_ratings = rating_matrix.loc[user_id]
    
    for other_user in rating_matrix.index:
        if other_user != user_id:
            corr, _ = pearsonr(target_user_ratings, rating_matrix.loc[other_user])
            similarities[other_user] = corr

    return sorted(similarities.items(), key=lambda x: x[1], reverse=True) 

def recommend_books_by_users(user_id, rating_matrix, top_n=5):
    similar_users = find_similar_users(user_id, rating_matrix)[:5]
    similar_users_ids = [user[0] for user in similar_users]
    
    # Get books rated highly by similar users
    similar_users_ratings = rating_matrix.loc[similar_users_ids]
    avg_ratings = similar_users_ratings.mean().sort_values(ascending=False)

    # Exclude books already rated by the target user
    user_rated_books = set(rating_matrix.loc[user_id][rating_matrix.loc[user_id] > 0].index)
    recommendations = avg_ratings.drop(user_rated_books).head(top_n)

    # Keep only recommendations with correlations higher than zero.
    recommendations = recommendations[recommendations > 0] 

    return [i[0] for i in recommendations.items()],avg_ratings
#%%
user_id = 20
top_n = 5
similar_users = find_similar_users(user_id, rating_matrix)[:5]
similar_users_ids = [user[0] for user in similar_users]

# Get books rated highly by similar users
similar_users_ratings = rating_matrix.loc[similar_users_ids]
avg_ratings = similar_users_ratings.mean().sort_values(ascending=False)
print([corr for book, corr in avg_ratings])
    # Arreglar que si no tiene correlacion que no imprima
#%%
user_df.iloc[20]


recommended_books = recommend_books_by_users(20, rating_matrix)
recommended_books_2 = recommend_by_total_rating(user_df, book_df, 20)
print(user_df.iloc[20])
print(recommended_books, recommended_books_2)