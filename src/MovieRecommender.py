import requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MovieRecommender:
    def __init__(self, api_key):
        """
        Initialize the MovieRecommender with TMDB API key
        """
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.movies_df = None
        
    def fetch_popular_movies(self, num_pages=5):
        """
        Fetch popular movies from TMDB API
        """
        movies_data = []
        
        for page in range(1, num_pages + 1):
            url = f"{self.base_url}/movie/popular"
            params = {
                "api_key": self.api_key,
                "language": "en-US",
                "page": page
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                results = response.json()["results"]
                for movie in results:
                    # Fetch additional movie details
                    movie_id = movie["id"]
                    details = self.fetch_movie_details(movie_id)
                    
                    if details:
                        movies_data.append({
                            "id": movie["id"],
                            "title": movie["title"],
                            "overview": movie["overview"],
                            "genres": ", ".join([genre["name"] for genre in details.get("genres", [])]),
                            "vote_average": movie["vote_average"],
                            "release_date": movie["release_date"],
                            "popularity": movie["popularity"]
                        })
        
        self.movies_df = pd.DataFrame(movies_data)
        return self.movies_df
    
    def fetch_movie_details(self, movie_id):
        """
        Fetch detailed information for a specific movie
        """
        url = f"{self.base_url}/movie/{movie_id}"
        params = {
            "api_key": self.api_key,
            "language": "en-US"
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    
    def create_content_matrix(self):
        """
        Create content-based features matrix using TF-IDF
        """
        if self.movies_df is None:
            raise ValueError("No movies data available. Please fetch movies first.")
            
        # Combine overview and genres for content-based filtering
        self.movies_df['content'] = self.movies_df['overview'] + ' ' + self.movies_df['genres']
        
        # Create TF-IDF matrix
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(self.movies_df['content'])
        
        # Calculate similarity matrix
        self.similarity_matrix = cosine_similarity(tfidf_matrix)
        print(self.similarity_matrix)
        
    def get_recommendations(self, movie_title, n_recommendations=5):
        """
        Get movie recommendations based on a movie title
        """
        if self.movies_df is None or not hasattr(self, 'similarity_matrix'):
            raise ValueError("Please fetch movies and create content matrix first.")
            
        # Find the movie index
        try:
            idx = self.movies_df[self.movies_df['title'] == movie_title].index[0]
        except IndexError:
            return f"Movie '{movie_title}' not found in the database."
        
        # Get similarity scores
        similarity_scores = list(enumerate(self.similarity_matrix[idx]))
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        
        # Get top N similar movies
        similar_movies = similarity_scores[1:n_recommendations+1]
        recommendations = []
        
        for i, score in similar_movies:
            movie = self.movies_df.iloc[i]
            recommendations.append({
                'title': movie['title'],
                'genres': movie['genres'],
                'similarity_score': score,
                'vote_average': movie['vote_average'],
                'release_date': movie['release_date']
            })
            
        return recommendations

    def get_recommendations_by_genre(self, genre, n_recommendations=5):
        """
        Get movie recommendations based on genre
        """
        if self.movies_df is None:
            raise ValueError("No movies data available. Please fetch movies first.")
            
        # Filter movies by genre
        genre_movies = self.movies_df[self.movies_df['genres'].str.contains(genre, case=False)]
        
        if len(genre_movies) == 0:
            return f"No movies found for genre '{genre}'."
            
        # Sort by vote average and popularity
        recommendations = genre_movies.sort_values(
            by=['vote_average', 'popularity'],
            ascending=[False, False]
        ).head(n_recommendations)
        
        return recommendations[['title', 'genres', 'vote_average', 'release_date']].to_dict('records')
