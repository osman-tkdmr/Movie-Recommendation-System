# Movie-Recommendation-System

## Recommendation System

This project is a movie recommendation system built using Flask, SQLAlchemy, and a custom recommendation algorithm. The system allows users to search for movies, view movie details, and manage their profiles. The recommendation algorithm uses content-based filtering to suggest movies based on user preferences and movie similarities.

### Features

- **User Authentication**: Users can sign up, log in, and log out.
- **Movie Search**: Users can search for movies by title, keyword, or genre.
- **Movie Details**: Users can view detailed information about a movie, including its overview, genres, and release date.
- **User Profile**: Users can view their profile, including their rated movies.
- **Movie Recommendations**: Users can get movie recommendations based on their preferences.

### Technologies Used

- **Flask**: A lightweight WSGI web application framework in Python.
- **SQLAlchemy**: An SQL toolkit and Object-Relational Mapping (ORM) library for Python.
- **bcrypt**: A library for hashing passwords.
- **HTML/CSS**: For structuring and styling the web pages.
- **JavaScript**: For handling client-side interactions.
- **Pandas**: For data manipulation and analysis.
- **scikit-learn**: For machine learning algorithms and tools.

### Recommendation Algorithm

The recommendation system uses a content-based filtering approach. The main steps involved are:

1. **Data Preprocessing**: The movie data is preprocessed to combine relevant features (e.g., overview, genres, keywords, tagline) into a single text field.
2. **TF-IDF Vectorization**: The combined text field is vectorized using the TF-IDF (Term Frequency-Inverse Document Frequency) technique to convert the text data into numerical vectors.
3. **Cosine Similarity**: The cosine similarity between the TF-IDF vectors is computed to measure the similarity between movies.
4. **Recommendation**: Based on the similarity scores, the top N most similar movies are recommended to the user.

### Setup Instructions

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/Movie-Recommendation-System.git
    cd Movie-Recommendation-System
    ```

2. **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the database**:
    ```bash
    flask db init
    flask db migrate -m "Initial migration."
    flask db upgrade
    ```

5. **Run the application**:
    ```bash
    flask run
    ```

6. **Access the application**:
    Open your web browser and go to `http://127.0.0.1:5000`.

### Project Structure

- `app/`: Contains the Flask application and its modules.
- `static/`: Contains static files like CSS and JavaScript.
- `templates/`: Contains HTML templates for rendering web pages.
- `README.md`: This file.

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
