import os
import pandas as pd
import torch
from LLM.model_utils import predict_sentiment, batch_predict

class MovieSentimentAnalyzer:
    """
    A class for analyzing sentiment in movie reviews using the trained model.
    This can be integrated into a movie recommendation system.
    """
    def __init__(self, model_path='./LLM/best_model'):
        self.model_path = model_path
        if not os.path.exists(model_path):
            print(f"Warning: Model not found at {model_path}. Please train models first.")
    
    def analyze_review(self, review_text):
        """
        Analyze a single movie review and return sentiment analysis.
        
        Args:
            review_text: The text of the movie review
            
        Returns:
            Dictionary with sentiment prediction and confidence scores
        """
        return predict_sentiment(review_text, self.model_path)
    
    def analyze_reviews(self, reviews):
        """
        Analyze multiple movie reviews and return sentiment analysis for each.
        
        Args:
            reviews: List of review texts
            
        Returns:
            List of dictionaries with sentiment predictions
        """
        return batch_predict(reviews, self.model_path)
    
    def analyze_reviews_df(self, reviews_df, text_column='review'):
        """
        Analyze movie reviews from a DataFrame and add sentiment columns.
        
        Args:
            reviews_df: DataFrame containing movie reviews
            text_column: Name of the column containing review text
            
        Returns:
            DataFrame with added sentiment columns
        """
        if text_column not in reviews_df.columns:
            raise ValueError(f"Column '{text_column}' not found in DataFrame")
        
        # Get list of reviews
        reviews = reviews_df[text_column].tolist()
        
        # Get sentiment predictions
        results = self.analyze_reviews(reviews)
        
        # Add sentiment and confidence to DataFrame
        reviews_df['sentiment'] = [r['sentiment'] for r in results]
        reviews_df['sentiment_confidence'] = [r['confidence'][r['sentiment']] for r in results]
        
        # Add sentiment score (0-4) for easier integration with recommendation systems
        sentiment_to_score = {
            "Very Negative": 0, 
            "Negative": 1, 
            "Neutral": 2, 
            "Positive": 3, 
            "Very Positive": 4
        }
        reviews_df['sentiment_score'] = reviews_df['sentiment'].map(sentiment_to_score)
        
        return reviews_df
    
    def get_sentiment_distribution(self, reviews_df, sentiment_column='sentiment'):
        """
        Get the distribution of sentiments in a DataFrame.
        
        Args:
            reviews_df: DataFrame containing sentiment analysis
            sentiment_column: Name of the column containing sentiment labels
            
        Returns:
            Dictionary with sentiment counts and percentages
        """
        if sentiment_column not in reviews_df.columns:
            raise ValueError(f"Column '{sentiment_column}' not found in DataFrame")
        
        # Count sentiments
        counts = reviews_df[sentiment_column].value_counts().to_dict()
        total = len(reviews_df)
        
        # Calculate percentages
        percentages = {k: (v / total) * 100 for k, v in counts.items()}
        
        return {
            'counts': counts,
            'percentages': percentages
        }

# Example usage
if __name__ == "__main__":
    # Create analyzer
    analyzer = MovieSentimentAnalyzer()
    
    # Example movie reviews
    example_reviews = [
        "This movie was absolutely fantastic! The plot was engaging and the acting was superb.",
        "I didn't really enjoy this film. The pacing was off and the characters were underdeveloped.",
        "An average movie with some good moments but nothing special.",
        "One of the worst movies I've ever seen. Complete waste of time and money.",
        "A masterpiece of modern cinema. Every scene was perfectly crafted."
    ]
    
    # Analyze individual review
    print("\n=== Individual Review Analysis ===\n")
    result = analyzer.analyze_review(example_reviews[0])
    print(f"Review: {result['text']}")
    print(f"Sentiment: {result['sentiment']}")
    print(f"Confidence: {result['confidence'][result['sentiment']]:.4f}")
    
    # Analyze multiple reviews
    print("\n=== Multiple Reviews Analysis ===\n")
    results = analyzer.analyze_reviews(example_reviews)
    for i, result in enumerate(results):
        print(f"Review {i+1}: {result['sentiment']} (Confidence: {result['confidence'][result['sentiment']]:.4f})")
    
    # Create a sample DataFrame
    print("\n=== DataFrame Analysis ===\n")
    df = pd.DataFrame({
        'movie_id': [1, 2, 3, 4, 5],
        'movie_title': ['Movie A', 'Movie B', 'Movie C', 'Movie D', 'Movie E'],
        'review': example_reviews
    })
    
    # Analyze DataFrame
    df_with_sentiment = analyzer.analyze_reviews_df(df)
    print(df_with_sentiment[['movie_title', 'sentiment', 'sentiment_score', 'sentiment_confidence']])
    
    # Get sentiment distribution
    distribution = analyzer.get_sentiment_distribution(df_with_sentiment)
    print("\nSentiment Distribution:")
    for sentiment, count in distribution['counts'].items():
        percentage = distribution['percentages'][sentiment]
        print(f"  {sentiment}: {count} reviews ({percentage:.1f}%)")