import pandas as pd
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import ast  # Importing ast to safely evaluate string representations of lists

def fetch_movie_summaries(title):
    try:
        imdb_url = f"https://www.imdb.com/find?q={title}"
        response = requests.get(imdb_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        imdb_link = soup.find('a', href=True, string=lambda text: title.lower() in text.lower())

        if imdb_link:
            imdb_page = requests.get("https://www.imdb.com" + imdb_link['href'])
            imdb_soup = BeautifulSoup(imdb_page.text, 'html.parser')
            imdb_summary = imdb_soup.find('div', class_='summary_text')
            imdb_summary = imdb_summary.get_text(strip=True) if imdb_summary else None
        else:
            imdb_summary = None

        wiki_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        response = requests.get(wiki_url)
        wiki_soup = BeautifulSoup(response.text, 'html.parser')
        wiki_summary = wiki_soup.find('div', class_='mw-parser-output').find('p')
        wiki_summary = wiki_summary.get_text(strip=True) if wiki_summary else None

        return imdb_summary, wiki_summary
    except Exception as e:
        print(f"Error fetching summaries: {e}")
        return None, None

def get_recommendations(title, movies_df):
    imdb_summary, wiki_summary = fetch_movie_summaries(title)

    full_summary = ""
    if imdb_summary:
        full_summary += imdb_summary + " "
    if wiki_summary:
        full_summary += wiki_summary + " "

    if not full_summary.strip():
        overview = movies_df.loc[movies_df['original_title'].str.lower() == title.lower(), 'overview']
        if not overview.empty:
            full_summary = overview.values[0]
        else:
            print(f"No valid summary for {title}.")
            return pd.DataFrame()

    if not full_summary.strip():
        print(f"No valid summary for {title}.")
        return pd.DataFrame()

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform([full_summary] + movies_df['overview'].dropna().tolist())
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    indices = pd.Series(movies_df.index, index=movies_df['original_title'].str.lower()).drop_duplicates()
    sim_indices = cosine_sim.argsort()[-6:-1][::-1]
    recommended_movies = movies_df.iloc[sim_indices]

    return recommended_movies[['original_title', 'genres', 'original_language', 'production_companies', 'release_date', 'revenue', 'overview']]

def main():
    movies_df = pd.read_csv(r"C:\Users\LENOVO\Desktop\archive\tmdb_5000_movies.csv")
    input_title = input("Enter the movie title: ")

    recommendations = get_recommendations(input_title, movies_df)

    if not recommendations.empty:
        print("\nRecommended Movies:\n")
        for idx, row in recommendations.iterrows():
            genres = [genre['name'] for genre in ast.literal_eval(row['genres'])] if isinstance(row['genres'], str) else []
            production_companies = [company['name'] for company in ast.literal_eval(row['production_companies'])] if isinstance(row['production_companies'], str) else []

            print(f"🎬 Title: {row['original_title']}")
            print(f"🎭 Genres: {', '.join(set(genres))}")
            print(f"🌐 Original Language: {row['original_language']}")
            print(f"🏢 Production Companies: {', '.join(set(production_companies))}")
            print(f"📅 Release Date: {row['release_date']}")
            print(f"💰 Revenue: ${row['revenue']}")
            print(f"\n📖 Overview: {row['overview']}\n")
            print("-" * 60)
    else:
        print("No recommendations found.")

if __name__ == "__main__":
    main()
