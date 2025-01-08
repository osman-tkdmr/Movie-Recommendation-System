from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from app.models import db, bcrypt, User, Movie, Favorite, Rating, Watchlist
from app.recommender import MovieRecommendationSystem
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
# Load Movie Data
MRS = MovieRecommendationSystem(data_path="data\\processed\\myData.csv")
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
    search_query = request.json.get('search_query')
    search_type = request.json.get('search_type')
    page = request.json.get('page', 1)
    per_page = 10
    search_methods = {
        'title': MRS.search_movies_by_title,
        'keyword': MRS.search_movies_by_keyword,
        'genre': MRS.search_movies_by_genre
    }
    if search_type not in search_methods:
        return jsonify({'error': 'Invalid search type.'})
    results = search_methods[search_type](search_query)
    if results.empty:
        return jsonify({'error': 'No movies found.'})
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
    average_rating = sum(rating.rating for rating in ratings) / len(ratings) if ratings else movie.vote_average
    # Get recommended movies
    recommended_movies = MRS.recommend_movies(movie.title).to_dict(orient='records')
    return render_template('movie.html', movie=movie, average_rating=average_rating, 
                         username=session.get('username'), recommended_movies=recommended_movies)


@app.route('/user/<username>')
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    user_ratings = Rating.query.filter_by(user_id=user.id).all()
    rated_movies = [{
        'title': Movie.query.get(rating.movie_id).title,
        'rating': rating.rating,
        'poster_path': Movie.query.get(rating.movie_id).poster_path
    } for rating in user_ratings if Movie.query.get(rating.movie_id)]
    return render_template('user.html', user=user, rated_movies=rated_movies, username=session.get('username'))