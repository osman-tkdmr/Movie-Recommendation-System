import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

class MovieRecommendationSystem:
    def __init__(self, data_path):
        # Load the dataset
        self.data = pd.read_csv(data_path).head(10000)
        # Ensure 'title' and 'overview' columns exist
        if 'title' not in self.data.columns or 'overview' not in self.data.columns:
            raise ValueError("Dataset must contain 'title' and 'overview' columns.")
        # Preprocess the overview texts
        self.data["overview"] = self.data["overview"].fillna('') + self.data["genres"].fillna('') + self.data["keywords"].fillna('') + self.data["tagline"].fillna('')
        self.data['overview'] = self.data['overview'].apply(self._preprocess_text)
        # Create TF-IDF matrix
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform(self.data['overview'])
        # Compute cosine similarity matrix
        self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
    
    def _preprocess_text(self, text):
        # Simple preprocessing: convert to lowercase and remove special characters
        return re.sub(r'[^a-z0-9\s]', '', text.lower())
    
    def recommend_movies(self, movie_title, top_n=12):
        # Check if the movie exists in the dataset
        if movie_title not in self.data['title'].values:
            return f"Movie '{movie_title}' not found in the dataset."
        
        # Get the index of the movie
        idx = self.data[self.data['title'] == movie_title].index[0]
        
        # Get similarity scores
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        
        # Sort movies based on similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get top N similar movies
        sim_scores = sim_scores[1:top_n+1]
        
        # Get movie indices
        movie_indices = [i[0] for i in sim_scores]
        
        # Return top N movie titles as a list of dicts
        return self.data.iloc[movie_indices]
    
    def popular_movies(self, top_n=12):
        # Get the indices of the top N movies based on vote average
        return self.data.nlargest(top_n, 'popularity')

    def search_movies_by_title(self, title_query):
        # Search for movies that contain the title query
        return self.data[self.data['title'].str.contains(title_query, case=False, na=False)]
    
    def search_movies_by_keyword(self, keyword_query):
        # Search for movies that contain the keyword query
        return self.data[self.data['keywords'].str.contains(keyword_query, case=False, na=False)]
    
    def search_movies_by_genre(self, genre_query):
        # Search for movies that contain the genre query
        return self.data[self.data['genres'].str.contains(genre_query, case=False, na=False)]

