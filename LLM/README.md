# Sentiment Analysis Project

This project implements sentiment analysis using various transformer-based models (BERT, RoBERTa, DistilBERT, ALBERT) to classify text sentiment into 5 categories (Very Negative, Negative, Neutral, Positive, Very Positive).

## Project Structure

- `Sentiment_analysis.py`: Main script for training and evaluating multiple transformer models
- `model_utils.py`: Utility functions for model visualization and inference
- `sentiment_demo.py`: Demonstration script showing how to use the trained models

## Features

- Training and evaluation of multiple transformer models
- Comparison of model performance (accuracy, F1 score, training time)
- Visualization of model performance metrics
- Confusion matrix generation for error analysis
- Inference functions for sentiment prediction on new text

## Usage

### Training Models

To train the models, run the main script:

```bash
python Sentiment_analysis.py
```

This will:
1. Load and preprocess the dataset
2. Train multiple transformer models (BERT, RoBERTa, DistilBERT, ALBERT)
3. Evaluate each model and save the results
4. Save the best performing model to the `best_model` directory

### Using Trained Models for Prediction

After training, you can use the models for sentiment prediction:

```bash
python sentiment_demo.py
```

This demonstrates how to:
- Make predictions on individual texts
- Process batches of texts
- Visualize model performance comparisons
- Generate confusion matrices for error analysis

### Utility Functions

The `model_utils.py` file provides several useful functions:

- `visualize_model_comparison(results)`: Visualize performance metrics across models
- `plot_confusion_matrix(model, tokenizer, texts, true_labels)`: Generate confusion matrix
- `predict_sentiment(text, model_path)`: Predict sentiment for a single text
- `batch_predict(texts, model_path)`: Predict sentiment for multiple texts

## Model Performance

After training, the models are compared based on:
- Accuracy
- F1 Score
- Training time

The best performing model is automatically saved to the `best_model` directory for easy access.

## Requirements

- Python 3.6+
- PyTorch
- Transformers
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Scikit-learn

## Dataset

The project uses the Sentiment Analysis dataset with movie reviews, containing text phrases labeled with sentiment scores from 0-4:

- 0: Very Negative
- 1: Negative
- 2: Neutral
- 3: Positive
- 4: Very Positive

## Extending the Project

You can extend this project by:

1. Adding more transformer models
2. Implementing hyperparameter tuning
3. Creating a web interface for real-time sentiment analysis
4. Applying the models to different domains (e.g., product reviews, social media)

## Use Case: Enhancing Movie Recommendation Systems

This sentiment analysis model can be integrated into movie recommendation systems to improve personalization and user experience:

### Integration Example

The `movie_sentiment_analyzer.py` module demonstrates how to use the trained model for analyzing movie reviews:

```python
from movie_sentiment_analyzer import MovieSentimentAnalyzer

# Initialize the analyzer with the trained model
analyzer = MovieSentimentAnalyzer(model_path='./LLM/best_model')

# Analyze a single review
result = analyzer.analyze_review("This movie was absolutely fantastic!")
print(f"Sentiment: {result['sentiment']} (Confidence: {result['confidence'][result['sentiment']]:.4f})")

# Analyze a batch of reviews
reviews_df = load_movie_reviews()  # Your function to load reviews
reviews_with_sentiment = analyzer.analyze_reviews_df(reviews_df, text_column='review_text')

# Get sentiment distribution
distribution = analyzer.get_sentiment_distribution(reviews_with_sentiment)
print(f"Positive reviews: {distribution['percentages'].get('Positive', 0) + distribution['percentages'].get('Very Positive', 0):.1f}%")
```

### Benefits for Recommendation Systems

1. **Sentiment-Enhanced Recommendations**: Filter or boost recommendations based on sentiment scores
2. **User Preference Modeling**: Understand user preferences by analyzing the sentiment of their reviews
3. **Content Categorization**: Group movies by the emotional responses they generate
4. **Trend Analysis**: Track sentiment changes over time for different movie genres or directors
5. **Personalized User Experience**: Tailor the user interface based on sentiment patterns (e.g., highlighting positive aspects for users who prefer positive content)

### Real-World Application

In our movie recommendation system, we use sentiment analysis to:

- Adjust recommendation scores based on sentiment analysis of user reviews
- Identify controversial movies (mixed sentiment) vs. universally liked/disliked films
- Provide more nuanced recommendations by considering both rating scores and sentiment analysis
- Improve cold-start recommendations by analyzing sentiment in movie descriptions and critic reviews