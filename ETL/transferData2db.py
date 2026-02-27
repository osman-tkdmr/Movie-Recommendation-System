import json
import psycopg2
from psycopg2.extras import Json
from datetime import datetime

class MovieDataImporter:
    def __init__(self, db_config):
        db_config = {
            'host': 'localhost',
            'database': 'moppie2',
            'user': 'postgres',
            'password': 'Oppie42!',
            'port': 5432
        }
        self.db_config = db_config
        self.connection = None
        self.cursor = None
        
    def parse_date(self, date_string):
        """Tarih string'ini DATE formatına çevir"""
        if not date_string:
            return None
        try:
            return datetime.strptime(date_string, '%Y-%m-%d').date()
        except ValueError:
            try:
                return datetime.strptime(date_string, '%Y-%m').date().replace(day=1)
            except ValueError:
                return None
    def connect_database(self):
        """Veritabanına bağlan"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.connection.autocommit = False  # Manuel transaction kontrolü
            self.cursor = self.connection.cursor()
            print("Veritabanı bağlantısı başarılı!")
        except Exception as e:
            print(f"Veritabanı bağlantı hatası: {e}")
            raise
    
    def create_movies_table(self):
        """Movies tablosunu oluştur"""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS movies (
            imdb_id VARCHAR(20) PRIMARY KEY,
            tmdb_id INTEGER,
            title VARCHAR(500),
            original_title VARCHAR(500),
            overview TEXT,
            poster_path VARCHAR(200),
            backdrop_path VARCHAR(200),
            media_type VARCHAR(50),
            adult BOOLEAN,
            original_language VARCHAR(10),
            genre_ids INTEGER[],
            popularity DECIMAL(10,3),
            release_date DATE,
            video BOOLEAN,
            vote_average DECIMAL(3,1),
            vote_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        try:
            self.cursor.execute(create_table_query)
            self.connection.commit()
            print("Movies tablosu oluşturuldu!")
        except Exception as e:
            print(f"Tablo oluşturma hatası: {e}")
            self.connection.rollback()
            raise
    
    def validate_and_clean_data(self, movie_data):
        """Veriyi doğrula ve temizle"""
        cleaned_data = {}
        
        # String alanlar için güvenli temizleme
        string_fields = ['title', 'original_title', 'overview', 'poster_path', 
                        'backdrop_path', 'media_type', 'original_language']
        
        for field in string_fields:
            value = movie_data.get(field)
            if value is not None:
                # Çok uzun string'leri kırp
                if field in ['title', 'original_title'] and len(str(value)) > 500:
                    cleaned_data[field] = str(value)[:500]
                elif field == 'overview' and len(str(value)) > 5000:
                    cleaned_data[field] = str(value)[:5000]
                else:
                    cleaned_data[field] = str(value) if value else None
            else:
                cleaned_data[field] = None
        
        # Sayısal alanlar için güvenli dönüşüm
        cleaned_data['id'] = movie_data.get('id', 0)
        cleaned_data['adult'] = bool(movie_data.get('adult', False))
        cleaned_data['video'] = bool(movie_data.get('video', False))
        
        # Popularity, vote_average, vote_count için güvenli dönüşüm
        try:
            cleaned_data['popularity'] = float(movie_data.get('popularity', 0))
        except (ValueError, TypeError):
            cleaned_data['popularity'] = 0.0
            
        try:
            cleaned_data['vote_average'] = float(movie_data.get('vote_average', 0))
        except (ValueError, TypeError):
            cleaned_data['vote_average'] = 0.0
            
        try:
            cleaned_data['vote_count'] = int(movie_data.get('vote_count', 0))
        except (ValueError, TypeError):
            cleaned_data['vote_count'] = 0
        
        # Genre IDs ve release_date için özel işleme
        cleaned_data['genre_ids'] = self.normalize_genre_ids(movie_data.get('genre_ids'))
        cleaned_data['release_date'] = movie_data.get('release_date')
        
        return cleaned_data

    def normalize_genre_ids(self, genre_ids):
        """Genre ID'leri her zaman liste formatına çevir"""
        if genre_ids is None:
            return []
        elif isinstance(genre_ids, list):
            return genre_ids
        elif isinstance(genre_ids, (int, str)):
            try:
                # String ise integer'a çevir, sonra listeye al
                return [int(genre_ids)]
            except (ValueError, TypeError):
                return []
        else:
            return []
        """Tarih string'ini DATE formatına çevir"""
        if not date_string:
            return None
        try:
            return datetime.strptime(date_string, '%Y-%m-%d').date()
        except ValueError:
            try:
                return datetime.strptime(date_string, '%Y-%m').date().replace(day=1)
            except ValueError:
                return None
    
    def insert_movie_data_batch(self, json_data):
        """JSON verilerini toplu olarak (batch) veritabanına ekle - Daha hızlı"""
        insert_query = """
        INSERT INTO movies (
            imdb_id, tmdb_id, title, original_title, overview, poster_path,
            backdrop_path, media_type, adult, original_language, genre_ids,
            popularity, release_date, video, vote_average, vote_count
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) ON CONFLICT (imdb_id) DO UPDATE SET
            tmdb_id = EXCLUDED.tmdb_id,
            title = EXCLUDED.title,
            original_title = EXCLUDED.original_title,
            overview = EXCLUDED.overview,
            poster_path = EXCLUDED.poster_path,
            backdrop_path = EXCLUDED.backdrop_path,
            media_type = EXCLUDED.media_type,
            adult = EXCLUDED.adult,
            original_language = EXCLUDED.original_language,
            genre_ids = EXCLUDED.genre_ids,
            popularity = EXCLUDED.popularity,
            release_date = EXCLUDED.release_date,
            video = EXCLUDED.video,
            vote_average = EXCLUDED.vote_average,
            vote_count = EXCLUDED.vote_count;
        """
        
        batch_data = []
        error_records = []
        
        # Tüm veriyi hazırla
        for imdb_id, movie_data in json_data.items():
            try:
                # Veriyi temizle ve doğrula
                cleaned_data = self.validate_and_clean_data(movie_data)
                
                values = (
                    imdb_id,
                    cleaned_data['id'],
                    cleaned_data['title'],
                    cleaned_data['original_title'],
                    cleaned_data['overview'],
                    cleaned_data['poster_path'],
                    cleaned_data['backdrop_path'],
                    cleaned_data['media_type'],
                    cleaned_data['adult'],
                    cleaned_data['original_language'],
                    cleaned_data['genre_ids'],
                    cleaned_data['popularity'],
                    self.parse_date(cleaned_data['release_date']),
                    cleaned_data['video'],
                    cleaned_data['vote_average'],
                    cleaned_data['vote_count']
                )
                batch_data.append(values)
            except Exception as e:
                error_records.append((imdb_id, str(e)))
        
        # Toplu ekleme yap
        try:
            self.connection.rollback()  # Temiz başlangıç
            self.cursor.executemany(insert_query, batch_data)
            self.connection.commit()
            print(f"Toplu işlem tamamlandı! Başarılı: {len(batch_data)}, Hatalı: {len(error_records)}")
            
            if error_records:
                print("Hatalı kayıtlar:")
                for imdb_id, error in error_records:
                    print(f"  {imdb_id}: {error}")
                    
        except Exception as e:
            print(f"Toplu ekleme hatası: {e}")
            self.connection.rollback()
            # Hata durumunda tek tek eklemeyi dene
            print("Tek tek ekleme moduna geçiliyor...")
            self.insert_movie_data(json_data)

    def insert_movie_data(self, json_data):
        """JSON verilerini veritabanına ekle"""
        insert_query = """
        INSERT INTO movies (
            imdb_id, tmdb_id, title, original_title, overview, poster_path,
            backdrop_path, media_type, adult, original_language, genre_ids,
            popularity, release_date, video, vote_average, vote_count
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) ON CONFLICT (imdb_id) DO UPDATE SET
            tmdb_id = EXCLUDED.tmdb_id,
            title = EXCLUDED.title,
            original_title = EXCLUDED.original_title,
            overview = EXCLUDED.overview,
            poster_path = EXCLUDED.poster_path,
            backdrop_path = EXCLUDED.backdrop_path,
            media_type = EXCLUDED.media_type,
            adult = EXCLUDED.adult,
            original_language = EXCLUDED.original_language,
            genre_ids = EXCLUDED.genre_ids,
            popularity = EXCLUDED.popularity,
            release_date = EXCLUDED.release_date,
            video = EXCLUDED.video,
            vote_average = EXCLUDED.vote_average,
            vote_count = EXCLUDED.vote_count;
        """
        
        success_count = 0
        error_count = 0
        
        for imdb_id, movie_data in json_data.items():
            try:
                # Her kayıt için ayrı transaction başlat
                self.connection.rollback()  # Önceki hataları temizle
                
                # Veriyi temizle ve doğrula
                cleaned_data = self.validate_and_clean_data(movie_data)
                
                values = (
                    imdb_id,
                    cleaned_data['id'],
                    cleaned_data['title'],
                    cleaned_data['original_title'],
                    cleaned_data['overview'],
                    cleaned_data['poster_path'],
                    cleaned_data['backdrop_path'],
                    cleaned_data['media_type'],
                    cleaned_data['adult'],
                    cleaned_data['original_language'],
                    cleaned_data['genre_ids'],
                    cleaned_data['popularity'],
                    self.parse_date(cleaned_data['release_date']),
                    cleaned_data['video'],
                    cleaned_data['vote_average'],
                    cleaned_data['vote_count']
                )
                
                self.cursor.execute(insert_query, values)
                self.connection.commit()  # Her kayıt için ayrı commit
                success_count += 1
                
            except Exception as e:
                print(f"Film ekleme hatası ({imdb_id}): {e}")
                self.connection.rollback()  # Hata durumunda rollback
                error_count += 1
                continue
        
        print(f"İşlem tamamlandı! Başarılı: {success_count}, Hatalı: {error_count}")
    
    def load_and_import_json(self, json_file_path):
        """JSON dosyasını yükleyip veritabanına aktar"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
            
            print(f"{len(json_data)} film verisi yüklendi.")
            self.insert_movie_data(json_data)
            
        except FileNotFoundError:
            print(f"JSON dosyası bulunamadı: {json_file_path}")
        except json.JSONDecodeError:
            print("JSON dosyası formatı hatalı!")
        except Exception as e:
            print(f"JSON yükleme hatası: {e}")
    
    def import_from_dict(self, json_data):
        """Dictionary formatındaki veriyi doğrudan aktar"""
        print(f"{len(json_data)} film verisi işleniyor...")
        self.insert_movie_data(json_data)
    
    def close_connection(self):
        """Veritabanı bağlantısını kapat"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Veritabanı bağlantısı kapatıldı.")

# Kullanım örneği
def main():
    # Veritabanı yapılandırması
    db_config = {
        'host': 'localhost',
        'database': 'movie_db',
        'user': 'postgres',
        'password': 'your_password',
        'port': 5432
    }
    
    # Örnek JSON verisi (farklı genre_ids formatları ile)
    sample_data = {
        "tt0001115": {
            "backdrop_path": None,
            "id": 1439199,
            "title": "Ansigtstyven",
            "original_title": "Ansigtstyven",
            "overview": "",
            "poster_path": None,
            "media_type": "movie",
            "adult": False,
            "original_language": "da",
            "genre_ids": [],  # Boş liste
            "popularity": 0.001,
            "release_date": "1910-10-27",
            "video": False,
            "vote_average": 0,
            "vote_count": 0
        },
        "tt0001476": {
            "backdrop_path": None,
            "id": 1063186,
            "title": "Love that Kills",
            "original_title": "Amor que mata",
            "overview": "In this version, opposite to Gelabert's film of 1908, the story tells about a woman who dies of a broken heart.",
            "poster_path": "/kgoSmSbKK81gBoojkZ1ebZG0UiX.jpg",
            "media_type": "movie",
            "adult": False,
            "original_language": "es",
            "genre_ids": [18, 10749],  # Liste formatı
            "popularity": 0.001,
            "release_date": "1911-01-01",
            "video": False,
            "vote_average": 0,
            "vote_count": 0
        },
        "tt0001489": {
            "backdrop_path": None,
            "id": 1439684,
            "title": "The Awakening of John Bond",
            "original_title": "The Awakening of John Bond",
            "overview": "A slumlord learns just how important it is to maintain clean living quarters when his wife contracts tuberculosis.",
            "poster_path": "/z1fwY7c7McxelFSu1gA0dnTIXdu.jpg",
            "media_type": "movie",
            "adult": False,
            "original_language": "en",
            "genre_ids": 18,  # Tek integer (problematik format)
            "popularity": 0.001,
            "release_date": "1911-12-04",
            "video": False,
            "vote_average": 0,
            "vote_count": 0
        },
        "tt30056863": {
            "backdrop_path": None,
            "id": 1234567,
            "title": "Test Movie",
            "original_title": "Test Movie",
            "overview": "Test description",
            "poster_path": "/test.jpg",
            "media_type": "movie",
            "adult": False,
            "original_language": "tl",
            "genre_ids": "18",  # String formatı (problematik)
            "popularity": 0.02,
            "release_date": "2023-01-01",
            "video": False,
            "vote_average": 5.5,
            "vote_count": 10
        }
    }
    
    # Importer'ı başlat
    importer = MovieDataImporter(db_config)
    
    try:
        # Veritabanına bağlan
        importer.connect_database()
        
        # Tabloyu oluştur
        importer.create_movies_table()
        
        # Veriyi aktar (3 farklı yöntem)
        
        # Yöntem 1: Hızlı toplu ekleme (önerilen)
        # importer.insert_movie_data_batch(sample_data)
        
        # Yöntem 2: Tek tek ekleme (güvenli ama yavaş)
        # importer.insert_movie_data(sample_data)
        
        # Yöntem 3: JSON dosyasından
        importer.load_and_import_json('movies.json')
        
    except Exception as e:
        print(f"İşlem hatası: {e}")
    finally:
        # Bağlantıyı kapat
        importer.close_connection()

if __name__ == "__main__":
    main()