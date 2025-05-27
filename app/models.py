import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    overview = db.Column(db.Text, nullable=False)
    genres = db.Column(db.String(255), nullable=False)
    runtime = db.Column(db.Integer, nullable=False)
    keywords = db.Column(db.String(255), nullable=False)
    tagline = db.Column(db.String(255), nullable=False)
    poster_path = db.Column(db.String(255), nullable=False)
    vote_average = db.Column(db.Float, nullable=False)
    vote_count = db.Column(db.Integer, nullable=False)
    popularity = db.Column(db.Float, nullable=False)
    release_date = db.Column(db.Date, nullable=True)
    budget = db.Column(db.Integer, nullable=True)
    revenue = db.Column(db.Integer, nullable=True)
    original_language = db.Column(db.String(10), nullable=True)
    imdb_averageRating = db.Column(db.Float, nullable=True)
    imdb_numVotes = db.Column(db.Float, nullable=True)
    adult = db.Column(db.Boolean, nullable=False, default=False)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('favourites', lazy=True))
    movie = db.relationship('Movie', backref=db.backref('favourites', lazy=True))

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    user = db.relationship('User', backref=db.backref('ratings', lazy=True))
    movie = db.relationship('Movie', backref=db.backref('ratings', lazy=True))

    __table_args__ = (db.UniqueConstraint('user_id', 'movie_id', name='unique_user_movie_rating'), )

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    sentiment = db.Column(db.String(20), nullable=True)  # Very Negative, Negative, Neutral, Positive, Very Positive
    sentiment_score = db.Column(db.Integer, nullable=True)  # 0-4 score for easier color mapping
    sentiment_confidence = db.Column(db.Float, nullable=True)  # Confidence score for the sentiment prediction
    
    user = db.relationship('User', backref=db.backref('reviews', lazy=True))
    movie = db.relationship('Movie', backref=db.backref('reviews', lazy=True))
    

class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    added_date = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    user = db.relationship('User', backref=db.backref('watchlist', lazy=True))
    movie = db.relationship('Movie', backref=db.backref('watchlist', lazy=True))
