import requests
import json
import time
import os
import sys
from central_config import get_headers

class IMDbDataScraper:
    def __init__(self, user_id, user_count=16):
        self.user_id = user_id
        self.user_count = user_count
        self.headers = get_headers(user_id)
        self.base_dir = f'Moppie{user_id}/scrapping'
        self.cache_file = f'./imdb_ids_cache.json'
        self.data_file = f'{self.base_dir}/data.json'
        self.progress_file = f'{self.base_dir}/progress.json'
        self.error_file = f'{self.base_dir}/error_ids.json'
        
        # Create directory if it doesn't exist
        os.makedirs(self.base_dir, exist_ok=True)
    
    def load_imdb_ids_from_cache(self):
        """Load IMDb IDs from cache file"""
        try:
            with open(self.cache_file, 'r') as f:
                all_imdb_ids = json.load(f)
                print(f"Loaded {len(all_imdb_ids)} IMDb IDs from cache")
                return all_imdb_ids
        except (FileNotFoundError, json.JSONDecodeError):
            print("Cache not found")
            return []
    
    def get_user_task_ids(self, all_imdb_ids):
        """Get the portion of IDs assigned to this user"""
        n_ids = len(all_imdb_ids)
        start_index = self.user_id * (n_ids // self.user_count)
        end_index = start_index + (n_ids // self.user_count) - 1
        task_ids = all_imdb_ids[start_index:end_index]
        
        print(f"User {self.user_id} will process {len(task_ids)} IDs from {start_index} to {end_index}")
        return task_ids
    
    def load_progress(self):
        """Load progress from previous run"""
        try:
            with open(self.progress_file, 'r') as f:
                progress_data = json.load(f)
                start_index = progress_data.get('last_index', 0)
                success_count = progress_data.get('success_count', 0)
                error_count = progress_data.get('error_count', 0)
                print(f"Kaldığı yerden devam ediliyor: {start_index}")
                return start_index, success_count, error_count
        except (FileNotFoundError, json.JSONDecodeError):
            return 0, 0, 0
    
    def save_progress(self, index, success_count, error_count):
        """Save current progress"""
        progress_data = {
            'last_index': index,
            'success_count': success_count,
            'error_count': error_count,
            'timestamp': time.time()
        }
        with open(self.progress_file, 'w') as f:
            json.dump(progress_data, f)
    
    def log_error(self, imdb_id, error_type):
        """Log error to error file"""
        with open(self.error_file, 'a', encoding='utf-8') as error_file:
            error_data = {
                'imdb_id': imdb_id,
                'error_type': error_type,
                'timestamp': time.time()
            }
            json.dump(error_data, error_file)
            error_file.write('\n')
            error_file.flush()
    
    def save_data(self, data, imdb_id):
        """Save successful data to file"""
        with open(self.data_file, 'a', encoding='utf-8') as f:
            data_with_id = data.copy()
            data_with_id['imdb_id'] = imdb_id
            json.dump(data_with_id, f)
            f.write('\n')
            f.flush()
    
    def fetch_imdb_data(self, imdb_id):
        """Fetch data for a single IMDb ID"""
        url = f"https://api.themoviedb.org/3/find/{imdb_id}?external_source=imdb_id"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if not response.ok:
                error_message = f"{response.status_code} - {response.reason}"
                print(f"Error for {imdb_id}: {error_message}")
                self.log_error(imdb_id, error_message)
                
                # Add delay for rate limiting issues
                if response.status_code == 429:  # Too Many Requests
                    time.sleep(10)
                return False
                
            data = response.json()
            
            if any(data.values()):  # Only save if there are non-empty results
                self.save_data(data, imdb_id)
                return True
            
            return False
            
        except Exception as e:
            error_message = f"Exception: {str(e)}"
            print(f"Exception processing {imdb_id}: {error_message}")
            self.log_error(imdb_id, error_message)
            return False
    
    def process_failed_ids(self):
        """Process previously failed IDs"""
        print("\nProcessing failed IDs from previous runs...")
        failed_ids = set()
        
        try:
            with open(self.error_file, 'r') as f:
                for line in f:
                    try:
                        error_data = json.loads(line)
                        failed_ids.add(error_data['imdb_id'])
                    except json.JSONDecodeError:
                        continue

            if failed_ids:
                print(f"Found {len(failed_ids)} failed IDs to retry")
                failed_ids = list(failed_ids)
                success_retry = 0
                
                for imdb_id in failed_ids[::-1]:
                    if self.fetch_imdb_data(imdb_id):
                        success_retry += 1
                        print(f"Successfully processed previously failed ID: {imdb_id}")
                    
                    time.sleep(0.25)
                
                print(f"Retry completed: {success_retry} out of {len(failed_ids)} failed IDs were successful")
            else:
                print("No failed IDs found to retry")
                
        except FileNotFoundError:
            print("No error_ids.json file found")
    
    def run(self):
        """Main execution method"""
        try:
            # Load IMDb IDs from cache
            all_imdb_ids = self.load_imdb_ids_from_cache()
            if not all_imdb_ids:
                print("No IMDb IDs found in cache. Exiting.")
                return
            
            # Get user's assigned task IDs
            task_ids = self.get_user_task_ids(all_imdb_ids)
            if not task_ids:
                print("No task IDs assigned to this user. Exiting.")
                return
            
            # Load progress from previous run
            start_index, success_count, error_count = self.load_progress()
            
            # Process IDs
            for i, imdb_id in enumerate(task_ids[start_index:], start=start_index):
                # Show progress every 10 items
                if i % 10 == 0:
                    print(f"Processing {i}/{len(task_ids)} ({i/len(task_ids)*100:.1f}%)")
                
                # Save progress every 100 items
                if i % 100 == 0 and i > start_index:
                    self.save_progress(i, success_count, error_count)
                
                # Fetch data
                if self.fetch_imdb_data(imdb_id):
                    success_count += 1
                else:
                    error_count += 1
                
                # Small delay to avoid hitting rate limits
                time.sleep(0.25)
            
            # Final progress save
            self.save_progress(len(task_ids), success_count, error_count)
            
            # Process failed IDs
            self.process_failed_ids()
            
            print(f"Completed: {success_count} successes, {error_count} errors out of {len(task_ids)} total")
            
        except Exception as e:
            print(f"Error: {str(e)}")

def main():
    """Main function to run the scraper"""
    if len(sys.argv) != 2:
        print("Usage: python find_content_imdb_id.py <user_id>")
        print("user_id should be between 0 and 15")
        sys.exit(1)
    
    try:
        user_id = int(sys.argv[1])
        if user_id < 0 or user_id > 15:
            raise ValueError("user_id must be between 0 and 15")
    except ValueError as e:
        print(f"Invalid user_id: {e}")
        sys.exit(1)
    
    scraper = IMDbDataScraper(user_id)
    scraper.run()

if __name__ == "__main__":
    main()