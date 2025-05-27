import os
import pandas as pd
import numpy as np
from movie_sentiment_analyzer import MovieSentimentAnalyzer

class SentimentEnhancedRecommender:
    """
    A demonstration class that shows how sentiment analysis can enhance movie recommendations.
    This is a simplified example that could be integrated into a more complex recommendation system.
    """
    def __init__(self, sentiment_analyzer=None):
        # Initialize sentiment analyzer
        self.sentiment_analyzer = sentiment_analyzer or MovieSentimentAnalyzer()
        
        # This would typically be loaded from a database
        # For demonstration, we'll create a sample dataset
        self.create_sample_data()
    
    def create_sample_data(self):
        """
        Create sample movie and review data for demonstration purposes.
        In a real system, this would be loaded from a database.
        """
        # Sample movies
        self.movies = pd.DataFrame({
            'movie_id': range(1, 11),
            'title': [
                'The Shawshank Redemption', 'The Godfather', 'Pulp Fiction',
                'The Dark Knight', 'Fight Club', 'Inception', 'Goodfellas',
                'The Matrix', 'Interstellar', 'The Silence of the Lambs'
            ],
            'genre': [
                'Drama', 'Crime', 'Crime', 'Action', 'Drama', 
                'Sci-Fi', 'Crime', 'Sci-Fi', 'Sci-Fi', 'Thriller'
            ],
            'year': [1994, 1972, 1994, 2008, 1999, 2010, 1990, 1999, 2014, 1991]
        })
        
        # Sample user ratings
        np.random.seed(42)  # For reproducibility
        user_ids = range(1, 21)  # 20 users
        ratings_data = []
        
        for user_id in user_ids:
            # Each user rates some random subset of movies
            for movie_id in np.random.choice(self.movies['movie_id'], size=np.random.randint(3, 8), replace=False):
                ratings_data.append({
                    'user_id': user_id,
                    'movie_id': movie_id,
                    'rating': np.random.randint(1, 6)  # Ratings from 1-5
                })
        
        self.ratings = pd.DataFrame(ratings_data)
        
        # Sample reviews (for sentiment analysis)
        reviews_data = []
        positive_templates = [
            "I loved {title}! It was an amazing film.",
            "{title} is one of the best movies I've ever seen.",
            "Absolutely fantastic movie. {title} is a masterpiece.",
            "{title} was brilliant, with great performances throughout."
        ]
        
        neutral_templates = [
            "{title} was okay, nothing special.",
            "I thought {title} was decent but not great.",
            "{title} had some good moments but overall was average.",
            "Not bad, not great. {title} was just fine."
        ]
        
        negative_templates = [
            "I didn't enjoy {title} at all.",
            "{title} was disappointing and boring.",
            "I wouldn't recommend {title} to anyone.",
            "A waste of time. {title} was terrible."
        ]
        
        for _, rating in self.ratings.iterrows():
            # Generate a review based on the rating
            if rating['rating'] >= 4:  # Positive
                template = np.random.choice(positive_templates)
            elif rating['rating'] <= 2:  # Negative
                template = np.random.choice(negative_templates)
            else:  # Neutral
                template = np.random.choice(neutral_templates)
            
            movie_title = self.movies.loc[self.movies['movie_id'] == rating['movie_id'], 'title'].iloc[0]
            review_text = template.format(title=movie_title)
            
            reviews_data.append({
                'user_id': rating['user_id'],
                'movie_id': rating['movie_id'],
                'review': review_text
            })
        
        self.reviews = pd.DataFrame(reviews_data)
    
    def analyze_reviews(self):
        """
        Analyze the sentiment of all reviews using the sentiment analyzer.
        """
        if not hasattr(self, 'reviews') or len(self.reviews) == 0:
            print("No reviews available for analysis.")
            return
        
        # Analyze reviews and add sentiment information
        self.reviews = self.sentiment_analyzer.analyze_reviews_df(self.reviews)
        print(f"Analyzed {len(self.reviews)} reviews for sentiment.")
        
        # Summarize sentiment by movie
        movie_sentiment = self.reviews.groupby('movie_id').agg({
            'sentiment_score': ['mean', 'count'],
            'sentiment': lambda x: x.value_counts().index[0]  # Most common sentiment
        })
        
        movie_sentiment.columns = ['avg_sentiment_score', 'review_count', 'most_common_sentiment']
        movie_sentiment = movie_sentiment.reset_index()
        
        # Merge with movies dataframe
        self.movies = self.movies.merge(movie_sentiment, on='movie_id', how='left')
        
        # Fill NaN values for movies without reviews
        self.movies['avg_sentiment_score'] = self.movies['avg_sentiment_score'].fillna(2)  # Neutral
        self.movies['review_count'] = self.movies['review_count'].fillna(0)
        self.movies['most_common_sentiment'] = self.movies['most_common_sentiment'].fillna('No reviews')
    
    def get_user_recommendations(self, user_id, n=3, use_sentiment=True):
        """
        Get movie recommendations for a user.
        
        Args:
            user_id: ID of the user
            n: Number of recommendations to return
            use_sentiment: Whether to use sentiment analysis in recommendations
            
        Returns:
            DataFrame with recommended movies
        """
        if user_id not in self.ratings['user_id'].unique():
            print(f"User {user_id} not found in ratings data.")
            return pd.DataFrame()
        
        # Get movies the user has already rated
        user_rated_movies = self.ratings[self.ratings['user_id'] == user_id]['movie_id'].tolist()
        
        # Get candidate movies (those the user hasn't rated)
        candidate_movies = self.movies[~self.movies['movie_id'].isin(user_rated_movies)]
        
        if len(candidate_movies) == 0:
            print(f"User {user_id} has already rated all available movies.")
            return pd.DataFrame()
        
        # Get user's genre preferences based on their highest-rated movies
        user_ratings = self.ratings[self.ratings['user_id'] == user_id]
        top_rated = user_ratings[user_ratings['rating'] >= 4]
        
        if len(top_rated) > 0:
            # Get genres of user's top-rated movies
            top_genres = self.movies[self.movies['movie_id'].isin(top_rated['movie_id'])]['genre'].tolist()
            # Count genre occurrences
            genre_counts = pd.Series(top_genres).value_counts()
            preferred_genres = genre_counts.index.tolist()
        else:
            # If no high ratings, use all genres the user has rated
            rated_genres = self.movies[self.movies['movie_id'].isin(user_rated_movies)]['genre'].tolist()
            preferred_genres = pd.Series(rated_genres).value_counts().index.tolist()
        
        # Score candidate movies based on genre match
        candidate_movies['genre_score'] = candidate_movies['genre'].apply(
            lambda g: preferred_genres.index(g) + 1 if g in preferred_genres else len(preferred_genres) + 1
        )
        candidate_movies['genre_score'] = 1 / candidate_movies['genre_score']  # Inverse rank for scoring
        
        # If using sentiment, incorporate it into the recommendation score
        if use_sentiment and 'avg_sentiment_score' in candidate_movies.columns:
            # Normalize sentiment score to 0-1 range (original is 0-4)
            candidate_movies['norm_sentiment'] = candidate_movies['avg_sentiment_score'] / 4
            
            # Weight genre more heavily than sentiment (70% genre, 30% sentiment)
            candidate_movies['score'] = (0.7 * candidate_movies['genre_score'] + 
                                        0.3 * candidate_movies['norm_sentiment'])
        else:
            # Use only genre score
            candidate_movies['score'] = candidate_movies['genre_score']
        
        # Sort by score and return top n recommendations
        recommendations = candidate_movies.sort_values('score', ascending=False).head(n)
        
        # Select relevant columns for output
        result_columns = ['movie_id', 'title', 'genre', 'year', 'score']
        if use_sentiment and 'avg_sentiment_score' in candidate_movies.columns:
            result_columns.extend(['avg_sentiment_score', 'most_common_sentiment', 'review_count'])
        
        return recommendations[result_columns]
    
    def compare_recommendation_methods(self, user_id, n=3):
        """
        Compare recommendations with and without sentiment analysis.
        
        Args:
            user_id: ID of the user
            n: Number of recommendations to return
            
        Returns:
            Tuple of DataFrames (with_sentiment, without_sentiment)
        """
        # Get recommendations with sentiment
        with_sentiment = self.get_user_recommendations(user_id, n, use_sentiment=True)
        if len(with_sentiment) == 0:
            return None, None
        
        # Get recommendations without sentiment
        without_sentiment = self.get_user_recommendations(user_id, n, use_sentiment=False)
        
        return with_sentiment, without_sentiment

# Example usage
if __name__ == "__main__":
    # Create recommender
    sentiment_analyzer = MovieSentimentAnalyzer()
    recommender = SentimentEnhancedRecommender(sentiment_analyzer)
    
    # Analyze reviews
    recommender.analyze_reviews()
    
    # Print movie data with sentiment
    print("\n=== Movies with Sentiment Analysis ===\n")
    print(recommender.movies[['movie_id', 'title', 'genre', 'avg_sentiment_score', 'most_common_sentiment', 'review_count']])
    
    # Get recommendations for a user
    user_id = 1
    print(f"\n=== Recommendations for User {user_id} ===\n")
    recommendations = recommender.get_user_recommendations(user_id, n=3)
    print(recommendations)
    
    # Compare recommendation methods
    print(f"\n=== Recommendation Comparison for User {user_id} ===\n")
    with_sentiment, without_sentiment = recommender.compare_recommendation_methods(user_id, n=3)
    
    print("With Sentiment Analysis:")
    print(with_sentiment[['title', 'genre', 'score', 'avg_sentiment_score', 'most_common_sentiment']])
    
    print("\nWithout Sentiment Analysis:")
    print(without_sentiment[['title', 'genre', 'score']])
    
    # Show how recommendations differ
    with_titles = set(with_sentiment['title'])
    without_titles = set(without_sentiment['title'])
    
    different_recs = with_titles.symmetric_difference(without_titles)
    if different_recs:
        print(f"\nDifferent recommendations: {different_recs}")
    else:
        print("\nBoth methods recommended the same movies.")