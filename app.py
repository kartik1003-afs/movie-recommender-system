
import streamlit as st
import pickle
import pandas as pd
import numpy as np
import requests
import time


API_KEY = "97dbc36ee8ab2b716dad3e60c49470a0"
PLACEHOLDER_POSTER = "https://via.placeholder.com/500x750.png?text=No+Poster"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    for attempt in range(3):  # retry 3 times
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500/{poster_path}"
            else:
                return PLACEHOLDER_POSTER
        except (requests.exceptions.RequestException, ConnectionResetError):
            time.sleep(2)
    return PLACEHOLDER_POSTER



def fetch_movie_details(movie_id):
    """Fetch movie overview, rating, and genres."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        data = res.json()
        overview = data.get("overview", "No description available.")
        rating = data.get("vote_average", "N/A")
        genres = ", ".join([g["name"] for g in data.get("genres", [])]) or "Unknown"
        return overview, rating, genres
    except (requests.exceptions.RequestException, ConnectionResetError):
        return "No details available.", "N/A", "Unknown"



def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(enumerate(distances), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    recommended_movies_details = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        poster = fetch_poster(movie_id)
        overview, rating, genres = fetch_movie_details(movie_id)

        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(poster)
        recommended_movies_details.append((overview, rating, genres))

    return recommended_movies, recommended_movies_posters, recommended_movies_details



# movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
# movies = pd.DataFrame(movies_dict)
# similarity = pickle.load(open("similarity2.pkl", "rb"))




import os
import pickle
import pandas as pd
import requests

# Function to download file from Google Drive
def download_file(url, filename):
    if not os.path.exists(filename):
        print(f"Downloading {filename} ...")
        r = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(r.content)
        print(f"{filename} downloaded successfully!")

# Your Google Drive direct download links
movie_dict_url = "https://drive.google.com/uc?export=download&id=1Fd4dd53_wDA72e_AJcVS52jqcni2L1HR"
similarity_url = "https://drive.google.com/uc?export=download&id=1SpDWnZI1pykKPzGpiOeLq3-xmsb65B1O"

# Download the files if not present
download_file(movie_dict_url, "movie_dict.pkl")
download_file(similarity_url, "similarity2.pkl")

# Load the data
movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open("similarity2.pkl", "rb"))












st.set_page_config(page_title="Movie Recommender", layout="wide")

st.title("🎬 Smart Movie Recommender System")
st.markdown("##### Find your next favorite movie instantly — powered by content-based filtering & TMDB API.")



st.sidebar.header(" Options")
show_top_rated = st.sidebar.checkbox("Show Top Rated Movies", value=False)
st.sidebar.markdown("---")
# st.sidebar.markdown("💡 **Tip:** Try searching for classics like *Inception*, *Avatar*, or *Interstellar*")


movie_list = movies["title"].values
selected_movie_name = st.selectbox("Choose a movie you like", movie_list)



if st.button("🔍 Show Recommendations"):
    with st.spinner("Fetching recommendations..."):
        names, posters, details = recommend(selected_movie_name)

    st.subheader("🎯 Top Recommendations for You")

    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.image(posters[idx], use_container_width=True)
            st.markdown(f"**{names[idx]}**")
            overview, rating, genres = details[idx]
            st.caption(f"⭐ {rating} | 🎭 {genres}")
            with st.expander("> Overview"):
                st.write(overview)



if show_top_rated:
    st.markdown("---")
    st.subheader("🏆 Top Rated Movies (Live from TMDB)")
    try:
        url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={API_KEY}&language=en-US&page=1"
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        data = res.json().get("results", [])
        top_cols = st.columns(5)
        for i, col in enumerate(top_cols[:5]):
            poster = (
                f"https://image.tmdb.org/t/p/w500/{data[i]['poster_path']}"
                if data[i].get("poster_path")
                else PLACEHOLDER_POSTER
            )
            with col:
                st.image(poster, use_container_width=True)
                st.markdown(f"**{data[i]['title']}**")
                st.caption(f"⭐ {data[i]['vote_average']}")
    except (requests.exceptions.RequestException, ConnectionResetError):
        st.error("⚠️ Could not fetch top rated movies (connection issue). Try again later.")



