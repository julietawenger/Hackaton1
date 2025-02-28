""" 2. Build the Recommendation Engine:

Generate personalized recommendations by:

    Filtering books from a dataset that match the user’s preferences.
    Ranking books based on user ratings or genre overlap.

Simulate recommendations like: “Since you liked Inception, you might enjoy Interstellar.”

    SciPy Application: Apply correlation metrics (e.g., Pearson correlation using scipy.stats.pearsonr) to compare the ratings given to movies by different users. This can help recommend movies based on similar user preferences or past ratings.

Additionally, use k-means clustering from scipy.cluster.vq to cluster users into groups based on their genre preferences or ratings, and then recommend the top-rated movies within each cluster.
"""

from simulate_users import book_df as df
from simulate_users import user_data
from scipy.stats import pearsonr
from scipy.cluster.vq import kmeans, vq
import numpy as np
import pandas as pd

synthetic_database = user_data(1000)

# First I need to access the user. Let's imagine this is user 20.
#user = synthetic_database.loc(20)

user_preferences = synthetic_database.iloc[20]["preferences"]

# I need to filter the dataframe based on the user's preferences 

filtered_movies = df[df['genre'].apply(lambda x: any(g in x for g in user_preferences))]
filtered_movies = filtered_movies.sort_values(by = 'rating', ascending=False)


### HASTA ACA LO QUE HACE ES FILTRAR DF POR LOS GENEROS QUE LE GUSTA AL USUARIO Y ORDENAR POR RATING

#### DESDE ACA ES BALAGAN PARA ENCONTRAR LA CORRELACION DE PEARSON


def book_hist_to_df(df, row):
# ESTA FUNCION AGARRA LA BASE DE DATOS DE USUARIO Y UNA FILA Y ME DEVUELVE UNA BASE DE DATOS DE BOOK HISTORY
    book_ratings = []
    for book in df.iloc[row]["book_history"]:
            book_ratings.append({"user_id": row["ID"], "book": book["book"], "rating": book["rating"]})
    return pd.DataFrame(book_ratings)


# AHORA QUIERO CONCATENAR PARA TODA LA BASE DE DATOS DE USUARIOS
ratings_df_list = df.apply(book_hist_to_df, axis=1).dropna().tolist()
ratings_df = pd.concat(ratings_df_list, ignore_index=True) # no funciona
print(ratings_df)
#ratings_df = ratings_df.groupby(["user_id", "book"], as_index=False).agg({"rating": "mean"})


def user_similarity(user1_ratings, user2_ratings):
    return pearsonr(user1_ratings, user2_ratings)[0]



#print(ratings_df)