import sys
import os
import subprocess

def main():
    """Run the IMDb data scraper for a specific user ID or all users"""
    if len(sys.argv) != 2:
        print("Usage: python run_scraper.py <user_id>")
        print("user_id should be between 0 and 15, or 'all' to run for all users")
        sys.exit(1)
    
    user_input = sys.argv[1]
    
    if user_input.lower() == 'all':
        # Run for all users in sequence
        for user_id in range(16):
            print(f"\n{'='*50}")
            print(f"Starting scraper for user_id {user_id}")
            print(f"{'='*50}\n")
            subprocess.run([sys.executable, 'find_content_imdb_id.py', str(user_id)])
    else:
        # Run for a specific user
        try:
            user_id = int(user_input)
            if user_id < 0 or user_id > 15:
                raise ValueError("user_id must be between 0 and 15")
                
            print(f"\n{'='*50}")
            print(f"Starting scraper for user_id {user_id}")
            print(f"{'='*50}\n")
            subprocess.run([sys.executable, 'find_content_imdb_id.py', str(user_id)])
            
        except ValueError:
            print(f"Invalid user_id: {user_input}")
            print("user_id should be between 0 and 15, or 'all' to run for all users")
            sys.exit(1)

if __name__ == "__main__":
    main()