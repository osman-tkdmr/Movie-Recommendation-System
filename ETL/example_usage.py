#!/usr/bin/env python3
"""
Example usage of the modular IMDb data scraping system

This script demonstrates how to use the new modular system:
1. Single virtual environment
2. Centralized configuration
3. Modular scraper class
"""

import os
import sys
from find_content_imdb_id import IMDbDataScraper

def example_single_user():
    """Example: Run scraper for a single user"""
    print("=" * 60)
    print("Example 1: Running scraper for User ID 0")
    print("=" * 60)
    
    # Create scraper instance for user 0
    scraper = IMDbDataScraper(user_id=0)
    
    # Run the scraper
    scraper.run()
    
    print("\nScraping completed for User ID 0")
    print(f"Data saved to: Moppie0/scrapping/data.json")
    print(f"Progress saved to: Moppie0/scrapping/progress.json")
    print(f"Errors logged to: Moppie0/scrapping/error_ids.json")

def example_multiple_users():
    """Example: Run scraper for multiple users"""
    print("=" * 60)
    print("Example 2: Running scraper for Users 0, 1, 2")
    print("=" * 60)
    
    user_ids = [0, 1, 2]
    
    for user_id in user_ids:
        print(f"\nStarting scraper for User ID {user_id}...")
        scraper = IMDbDataScraper(user_id=user_id)
        scraper.run()
        print(f"Completed scraper for User ID {user_id}")

def show_system_info():
    """Show information about the current system setup"""
    print("=" * 60)
    print("System Information")
    print("=" * 60)
    
    # Check virtual environment
    venv_path = os.path.join(os.getcwd(), 'venv')
    if os.path.exists(venv_path):
        print("✓ Single virtual environment found at: ./venv")
    else:
        print("✗ Virtual environment not found")
    
    # Check central config
    config_path = os.path.join(os.getcwd(), 'central_config.py')
    if os.path.exists(config_path):
        print("✓ Central configuration found at: ./central_config.py")
    else:
        print("✗ Central configuration not found")
    
    # Check modular scraper
    scraper_path = os.path.join(os.getcwd(), 'find_content_imdb_id.py')
    if os.path.exists(scraper_path):
        print("✓ Modular scraper found at: ./find_content_imdb_id.py")
    else:
        print("✗ Modular scraper not found")
    
    # Check Moppie directories
    moppie_count = 0
    for i in range(16):
        moppie_dir = f'Moppie{i}'
        if os.path.exists(moppie_dir):
            moppie_count += 1
    
    print(f"✓ Found {moppie_count}/16 Moppie directories")
    
    print("\nSystem is ready for distributed scraping!")

def main():
    """Main function to demonstrate the system"""
    print("Modular IMDb Data Scraping System - Example Usage")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'info':
            show_system_info()
        elif command == 'single':
            example_single_user()
        elif command == 'multiple':
            example_multiple_users()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: info, single, multiple")
    else:
        print("Available commands:")
        print("  python example_usage.py info      - Show system information")
        print("  python example_usage.py single    - Run scraper for single user")
        print("  python example_usage.py multiple  - Run scraper for multiple users")
        print("\nFor production use:")
        print("  python run_scraper.py <user_id>   - Run scraper for specific user")
        print("  python run_scraper.py all         - Run scraper for all users")

if __name__ == "__main__":
    main()