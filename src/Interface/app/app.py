import datetime
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from recommender import MovieRecommendationSystem

# Flask App Configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change this to a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# User Model
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

from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Load Movie Data
MRS = MovieRecommendationSystem(data_path="src\\Interface\\app\\TMDB_movie_dataset_v11.csv")
top_movies = MRS.popular_movies().to_dict(orient='records')
print(MRS.data.shape)
# Create database tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # Check if user is logged in
    if 'user_id' not in session:
        return render_template('index.html', top_movies=top_movies, username="", login=True, signup=False)
    
    
    return render_template('index.html', top_movies=top_movies, username=session.get('username'), login=False, signup=False)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    next_page = request.form.get('next', url_for('index'))
    
    # Find user
    user = User.query.filter_by(username=username).first()
    
    if user and bcrypt.check_password_hash(user.password, password):
        # Login successful
        session['user_id'] = user.id
        session['username'] = user.username
        flash('Login successful!', 'success')
        return redirect(next_page)
    else:
        flash('Invalid username or password', 'error')  # Error notification
        return redirect(url_for('index'))

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    next_page = request.form.get('next', url_for('index'))
    
    # Validation
    if password != confirm_password:
        flash('Passwords do not match', 'error')  # Error notification
        return redirect(url_for('index'))
    
    # Check if user already exists
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        flash('Username or email already exists', 'error')  # Error notification
        return redirect(url_for('index'))
    
    # Hash password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    # Create new user
    new_user = User(username=username, email=email, password=hashed_password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful! Please log in.', 'success')
        return redirect(next_page)
    except Exception as e:
        db.session.rollback()
        flash('An error occurred during signup', 'error')  # Error notification
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def search():
        
    search_query = request.json.get('search_query')
    search_type = request.json.get('search_type')
    page = request.json.get('page', 1)
    per_page = 10
    
    if search_type == 'title':
        results = MRS.search_movies_by_title(search_query)
    elif search_type == 'keyword':
        results = MRS.search_movies_by_keyword(search_query)
    elif search_type == 'genre':
        results = MRS.search_movies_by_genre(search_query)
    else:
        return jsonify({'error': 'Invalid search type.'})
    
    if not results.empty:
        total_results = results.shape[0]
        start = (page - 1) * per_page
        end = start + per_page
        paginated_results = results.iloc[start:end]
        paths = paginated_results[['id', 'title', 'poster_path', 'vote_average']].to_dict(orient='records')
        return jsonify({'paths': paths, 'total_results': total_results, 'page': page, 'per_page': per_page})
    else:
        return jsonify({'error': 'No movies found.'})

@app.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    movie = MRS.data[MRS.data['id'] == movie_id].iloc[0]
    
    # Calculate average rating from the database
    ratings = Rating.query.filter_by(movie_id=movie.id).all()
    if ratings:
        average_rating = sum(rating.rating for rating in ratings) / len(ratings)
    else:
        average_rating = movie.vote_average

    return render_template('movie.html', movie=movie, average_rating=average_rating, username=session.get('username'))
    
@app.route('/user/<username>')
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    user_ratings = Rating.query.filter_by(user_id=user.id).all()
    rated_movies = []
    for rating in user_ratings:
        movie = Movie.query.get(rating.movie_id)
        if movie:
            rated_movies.append({
                'title': movie.title,
                'rating': rating.rating,
                'poster_path': movie.poster_path
            })
    return render_template('user.html', user=user, rated_movies=rated_movies, username=session.get('username'))

if __name__ == '__main__':
    app.run(debug=True)