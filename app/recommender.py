import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

class MovieRecommendationSystem:
    def __init__(self, data_path):
        # Load the dataset
        self.data = pd.read_csv(data_path)
        # Ensure necessary columns exist, fill with empty strings if not
        for col in ['genres', 'keywords', 'tagline', 'overview', 'poster_path', 'vote_average', 'release_date']:
            if col not in self.data.columns:
                if col == 'vote_average':
                    self.data[col] = 0.0
                else:
                    self.data[col] = ''
        # Create a new column with combined features
        self.data["combined_features"] = (
            self.data["overview"].fillna('') +
            self.data["genres"].fillna('') +
            self.data["keywords"].fillna('') +
            self.data["tagline"].fillna('')
        )
        # Preprocess the combined features text
        self.data['combined_features'] = self.data['combined_features'].apply(self._preprocess_text)
        # Create TF-IDF matrix
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform(self.data['combined_features'])
        # We'll calculate similarities dynamically
        self.cosine_sim = None
    
    def _preprocess_text(self, text):
        # Simple preprocessing: convert to lowercase and remove special characters
        return re.sub(r'[^a-z0-9\s]', '', text.lower())
    
    def recommend_movies(self, movie_title, top_n=12):
        # Check if the movie exists in the dataset
        if movie_title not in self.data['title'].values:
            return f"Movie '{movie_title}' not found in the dataset."
        
        # Get the movie's TF-IDF vector
        movie_idx = self.data[self.data['title'] == movie_title].index[0]
        movie_vector = self.tfidf_matrix[movie_idx]
        
        # Calculate cosine similarity against all movies
        similarity_scores = cosine_similarity(movie_vector, self.tfidf_matrix).flatten()
        
        # Get top N similar movies
        similar_indices = similarity_scores.argsort()[::-1][1:top_n+1]
        
        # Return top N movie titles as a list of dicts
        return self.data.iloc[similar_indices]
    
    def popular_movies(self, top_n=12):
        # Get the indices of the top N movies based on popularity
        return self.data.nlargest(top_n, 'popularity')
    
    def top_movies(self, top_n=12):
        return self.data.head(top_n)

    def search_movies_by_title(self, title_query):
        # Search for movies that contain the title query
        return self.data[self.data['title'].str.contains(title_query, case=False, na=False)]
    
    def search_movies_by_keyword(self, keyword_query):
        # Search for movies that contain the keyword query
        return self.data[self.data['keywords'].str.contains(keyword_query, case=False, na=False)]
    
    def search_movies_by_genre(self, genre_query):
        # Search for movies that contain the genre query
        return self.data[self.data['genres'].str.contains(genre_query, case=False, na=False)]

