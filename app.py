from flask import Flask, request, jsonify, render_template
import pandas as pd

app = Flask(__name__)

movies_df = pd.read_csv('tmdb_5000_movies.csv')

def get_recommendations(title, movies_df):
    recommended_movies = movies_df[movies_df['original_title'].str.contains(title, case=False, na=False)]
    return recommended_movies[['original_title', 'genres', 'overview', 'original_language', 'production_companies', 'release_date', 'revenue']].to_dict(orient='records')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommendations', methods=['POST'])
def recommendations():
    title = request.json.get('title')
    if not title:
        return jsonify({'error': 'No title provided'}), 400

    recommendations = get_recommendations(title, movies_df)
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)
