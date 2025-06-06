from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_migrate import Migrate
# Change relative imports to absolute imports
from app.models import db, bcrypt, User, Movie, Favorite, Rating, Watchlist, Review
from app.recommender import MovieRecommendationSystem
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Load Movie Data
MRS = MovieRecommendationSystem(data_path="./Data/myData.csv")
top_movies = MRS.top_movies().to_dict(orient='records')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    username = session.get('username', "")
    login = 'user_id' not in session
    return render_template('index.html', top_movies=top_movies, username=username, login=login, signup=False)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    next_page = request.form.get('next', url_for('index'))
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['username'] = user.username
        flash('Login successful!', 'success')
        return redirect(next_page)
    flash('Invalid username or password', 'error')
    return redirect(url_for('index'))

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    next_page = request.form.get('next', url_for('index'))
    if password != confirm_password:
        flash('Passwords do not match', 'error')
        return redirect(url_for('index'))
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        flash('Username or email already exists', 'error')
        return redirect(url_for('index'))
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password=hashed_password)
    try:
        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful! Please log in.', 'success')
        return redirect(next_page)
    except Exception:
        db.session.rollback()
        flash('An error occurred during signup', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def search():
    search_query = request.json.get('search_query', '')
    search_type = request.json.get('search_type', 'title')
    page = request.json.get('page', 1)
    genre_filter = request.json.get('genre', '')
    year_filter = request.json.get('year', '')
    rating_filter = request.json.get('rating', '')
    per_page = 10
    
    search_methods = {
        'title': MRS.search_movies_by_title,
        'keyword': MRS.search_movies_by_keyword,
        'genre': MRS.search_movies_by_genre
    }
    
    if search_type not in search_methods:
        return jsonify({'error': 'Invalid search type.'})
    
    # İlk arama işlemini gerçekleştir
    if search_query:
        results = search_methods[search_type](search_query)
    else:
        # Arama sorgusu yoksa tüm filmleri al
        results = MRS.data
    
    # Filtreleri uygula
    if genre_filter and search_type != 'genre':
        results = results[results['genres'].str.contains(genre_filter, case=False, na=False)]
    
    if year_filter:
        results = results[results['release_date'].str.contains(year_filter, case=False, na=False)]
    
    if rating_filter:
        # Rating filtresi "7+" gibi bir format olduğundan, + işaretini kaldırıp sayıya dönüştürüyoruz
        min_rating = float(rating_filter.replace('+', ''))
        results = results[results['vote_average'] >= min_rating]
    
    if results.empty:
        return jsonify({'paths': [], 'total_results': 0, 'page': page, 'per_page': per_page})
    
    total_results = results.shape[0]
    start = (page - 1) * per_page
    end = start + per_page
    paginated_results = results.iloc[start:end]
    paths = paginated_results[['id', 'title', 'poster_path', 'vote_average', 'release_date']].to_dict(orient='records')
    
    return jsonify({'paths': paths, 'total_results': total_results, 'page': page, 'per_page': per_page})

@app.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    movie = MRS.data[MRS.data['id'] == movie_id].iloc[0]
    ratings = Rating.query.filter_by(movie_id=movie.id).all()
    user_rating = None
    
    if 'user_id' in session:
        user_rating = Rating.query.filter_by(
            user_id=session['user_id'], 
            movie_id=movie.id
        ).first()

    average_rating = sum(rating.rating for rating in ratings) / len(ratings) if ratings else movie.vote_average
    recommended_movies = MRS.recommend_movies(movie.title).to_dict(orient='records')
    movie_reviews = Review.query.filter_by(movie_id=int(movie.id)).all()

    return render_template('movie.html', movie=movie, average_rating=average_rating, 
                         username=session.get('username'), recommended_movies=recommended_movies,
                         user_rating=user_rating, movie_reviews=movie_reviews)

@app.route('/rate_movie', methods=['POST'])
@login_required
def rate_movie():
    user_id = session['user_id']
    movie_id = request.form.get('movie_id')
    rating_value = request.form.get('rating')
    
    if not movie_id or not rating_value:
        flash('Invalid rating submission', 'error')
        return redirect(url_for('movie_details', movie_id=movie_id))

    # Check for existing rating
    existing_rating = Rating.query.filter_by(
        user_id=user_id, 
        movie_id=movie_id
    ).first()

    if existing_rating:
        existing_rating.rating = float(rating_value)
    else:
        new_rating = Rating(
            user_id=user_id,
            movie_id=movie_id,
            rating=float(rating_value)
        )
        db.session.add(new_rating)
    
    try:
        db.session.commit()
        flash('Rating submitted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error submitting rating', 'error')
    
    return redirect(url_for('movie_details', movie_id=movie_id))

@app.route('/submit_review', methods=['POST'])
@login_required
def submit_review():
    user_id = session['user_id']
    movie_id = request.form.get('movie_id')
    review_content = request.form.get('review_content')
    
    if not movie_id or not review_content:
        flash('Invalid review submission', 'error')
        return redirect(url_for('movie_details', movie_id=movie_id))
    
    # Analyze sentiment using MovieSentimentAnalyzer
    try:
        from LLM.movie_sentiment_analyzer import MovieSentimentAnalyzer
        analyzer = MovieSentimentAnalyzer()
        sentiment_result = analyzer.analyze_review(review_content)
        
        # Map sentiment to score for color coding
        sentiment_to_score = {
            "Very Negative": 0, 
            "Negative": 1, 
            "Neutral": 2, 
            "Positive": 3, 
            "Very Positive": 4
        }
        
        new_review = Review(
            user_id=user_id,
            movie_id=movie_id,
            content=review_content,
            sentiment=sentiment_result['sentiment'],
            sentiment_score=sentiment_to_score[sentiment_result['sentiment']],
            sentiment_confidence=sentiment_result['confidence'][sentiment_result['sentiment']]
        )
    except Exception as e:
        # If sentiment analysis fails, still save the review without sentiment data
        print(f"Sentiment analysis error: {e}")
        new_review = Review(
            user_id=user_id,
            movie_id=movie_id,
            content=review_content
        )
    
    db.session.add(new_review)
    
    try:
        db.session.commit()
        flash('Review submitted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error submitting review', 'error')
    
    return redirect(url_for('movie_details', movie_id=movie_id))


@app.route('/user/<username>')
@login_required
def user_profile(username):
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Items per page
    
    user = User.query.filter_by(username=username).first_or_404()
    pagination = Rating.query.filter_by(user_id=user.id).paginate(page=page, per_page=per_page)
    
    rated_movies = [{
        'title': MRS.data[MRS.data['id'] == rating.movie_id].iloc[0]['title'],
        'rating': rating.rating,
        'poster_path': MRS.data[MRS.data['id'] == rating.movie_id].iloc[0]['poster_path']
    } for rating in pagination.items if not MRS.data[MRS.data['id'] == rating.movie_id].empty]
    
    return render_template('user.html', 
                         user=user,
                         rated_movies=rated_movies,
                         pagination=pagination,
                         username=session.get('username'))  # Fixed missing quote