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

class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    added_date = db.Column(db.DateTime, default=lambda: datetime.now(datetime.timezone.utc))

    user = db.relationship('User', backref=db.backref('watchlist', lazy=True))
    movie = db.relationship('Movie', backref=db.backref('watchlist', lazy=True))