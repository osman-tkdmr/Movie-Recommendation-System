import pandas as pd
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app import app
from app.models import db, Movie

def convert_date(date_str):
    """Convert date string to datetime object."""
    if pd.isna(date_str):
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

def import_movies_from_csv(csv_path):
    """Import movies from CSV file to database."""
    # Read CSV file
    print("Reading CSV file...")
    df = pd.read_csv(csv_path)
    
    total_records = len(df)
    successful_imports = 0
    failed_imports = 0
    
    print(f"Found {total_records} records to import")
    
    # Process each movie
    with app.app_context():
        for index, row in df.iterrows():
            try:
                # Check if movie already exists
                existing_movie = Movie.query.filter_by(id=row['id']).first()
                if existing_movie:
                    print(f"Movie {row['id']} already exists, skipping...")
                    continue
                
                # Create new movie object
                movie = Movie(
                    id=row['id'],
                    title=row['title'],
                    overview=row['overview'] if pd.notna(row['overview']) else '',
                    genres=row['genres'] if pd.notna(row['genres']) else '',
                    runtime=int(row['runtime']) if pd.notna(row['runtime']) else 0,
                    keywords=row['keywords'] if pd.notna(row['keywords']) else '',
                    tagline=row['tagline'] if pd.notna(row['tagline']) else '',
                    poster_path=row['poster_path'] if pd.notna(row['poster_path']) else '',
                    vote_average=float(row['vote_average']) if pd.notna(row['vote_average']) else 0.0,
                    vote_count=int(row['vote_count']) if pd.notna(row['vote_count']) else 0,
                    popularity=float(row['popularity']) if pd.notna(row['popularity']) else 0.0,
                    release_date=convert_date(row['release_date']),
                    budget=int(row['budget']) if pd.notna(row['budget']) else None,
                    revenue=int(row['revenue']) if pd.notna(row['revenue']) else None,
                    original_language=row['original_language'] if pd.notna(row['original_language']) else None,
                    imdb_averageRating=float(row['imdb_averageRating']) if pd.notna(row['imdb_averageRating']) else None,
                    imdb_numVotes=float(row['imdb_numVotes']) if pd.notna(row['imdb_numVotes']) else None,
                    adult=bool(row['adult']) if pd.notna(row['adult']) else False
                )
                
                db.session.add(movie)
                db.session.commit()
                successful_imports += 1
                
                if successful_imports % 100 == 0:
                    print(f"Processed {successful_imports} movies...")
                
            except IntegrityError:
                db.session.rollback()
                failed_imports += 1
                print(f"Error importing movie {row['id']}: Integrity Error")
            except Exception as e:
                db.session.rollback()
                failed_imports += 1
                print(f"Error importing movie {row['id']}: {str(e)}")
    
    print("\nImport Summary:")
    print(f"Total records processed: {total_records}")
    print(f"Successfully imported: {successful_imports}")
    print(f"Failed imports: {failed_imports}")

if __name__ == "__main__":
    csv_path = "data/processed/myData.csv"
    import_movies_from_csv(csv_path)