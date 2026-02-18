#!/usr/bin/env python3
"""
Manga Metadata Fetcher for Mihon Local Source
==============================================
This script traverses manga directories and creates:
- details.json: Metadata file with manga information
- cover.jpg: Cover image for the manga

Based on Mihon documentation: https://mihon.app/docs/guides/local-source/advanced
"""

import os
import json
import time
import requests
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Configuration
JIKAN_API_BASE = "https://api.jikan.moe/v4"
REQUEST_DELAY = 1.0  # Delay between API requests (Jikan rate limit: 3 req/sec, 60 req/min)

class MangaMetadataFetcher:
    """Fetches manga metadata from Jikan API (MyAnimeList)"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MangaMetadataFetcher/1.0'
        })
    
    def search_manga(self, title: str) -> Optional[Dict[str, Any]]:
        """Search for manga by title using Jikan API"""
        try:
            logger.info(f"Searching for: {title}")
            url = f"{JIKAN_API_BASE}/manga"
            params = {
                'q': title,
                'limit': 5,  # Get top 5 results to find best match
                'order_by': 'popularity'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('data') and len(data['data']) > 0:
                # Try to find the best match by comparing titles
                search_title_lower = title.lower().strip()
                best_match = None
                best_score = 0
                
                for manga in data['data']:
                    manga_title = manga.get('title', '').lower().strip()
                    manga_title_english = manga.get('title_english', '').lower().strip() if manga.get('title_english') else ''
                    
                    # Check for exact match first
                    if manga_title == search_title_lower or manga_title_english == search_title_lower:
                        best_match = manga
                        break
                    
                    # Check if search title is in manga title or vice versa
                    if search_title_lower in manga_title or manga_title in search_title_lower:
                        score = len(search_title_lower) / max(len(manga_title), 1)
                        if score > best_score:
                            best_score = score
                            best_match = manga
                    elif manga_title_english and (search_title_lower in manga_title_english or manga_title_english in search_title_lower):
                        score = len(search_title_lower) / max(len(manga_title_english), 1)
                        if score > best_score:
                            best_score = score
                            best_match = manga
                
                # If no good match found, use the first result (most popular)
                if not best_match:
                    best_match = data['data'][0]
                    logger.warning(f"No exact match found, using most popular result")
                
                logger.info(f"Found: {best_match.get('title', 'Unknown')}")
                return best_match
            else:
                logger.warning(f"No results found for: {title}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching for {title}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error searching for {title}: {e}")
            return None
    
    def download_cover(self, image_url: str, output_path: Path) -> bool:
        """Download cover image from URL"""
        try:
            logger.info(f"Downloading cover image...")
            response = self.session.get(image_url, timeout=15)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Cover saved to: {output_path}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading cover: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error downloading cover: {e}")
            return False
    
    def create_details_json(self, manga_data: Dict[str, Any], output_path: Path) -> bool:
        """Create details.json file from manga data"""
        try:
            # Extract relevant information according to Mihon format
            details = {
                "title": manga_data.get('title', ''),
                "author": ', '.join([author['name'] for author in manga_data.get('authors', [])]),
                "artist": ', '.join([author['name'] for author in manga_data.get('authors', [])]),
                "description": manga_data.get('synopsis', ''),
                "genre": [genre['name'] for genre in manga_data.get('genres', [])],
                "status": self._map_status(manga_data.get('status', '')),
                "_status values": ["0 = Unknown", "1 = Ongoing", "2 = Completed", "3 = Licensed", "4 = Publishing paused", "5 = Cancelled", "6 = On hiatus"]
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(details, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Details saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating details.json: {e}")
            return False
    
    def _map_status(self, mal_status: str) -> int:
        """Map MyAnimeList status to Mihon status codes"""
        status_map = {
            'Finished': 2,
            'Publishing': 1,
            'On Hiatus': 6,
            'Discontinued': 5,
            'Not yet published': 0
        }
        return status_map.get(mal_status, 0)
    
    def process_manga_directory(self, manga_dir: Path) -> bool:
        """Process a single manga directory"""
        manga_name = manga_dir.name
        
        # Skip non-manga directories
        if manga_name in ['free maga downloader 2', 'Kindle Comic Converter']:
            logger.info(f"Skipping non-manga directory: {manga_name}")
            return False
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {manga_name}")
        logger.info(f"{'='*60}")
        
        details_path = manga_dir / 'details.json'
        cover_path = manga_dir / 'cover.jpg'
        
        # Check if files already exist
        if details_path.exists() and cover_path.exists():
            logger.info(f"Metadata already exists for {manga_name}, skipping...")
            return True
        
        # Search for manga
        manga_data = self.search_manga(manga_name)
        
        if not manga_data:
            logger.warning(f"Could not find metadata for: {manga_name}")
            return False
        
        # Rate limiting
        time.sleep(REQUEST_DELAY)
        
        # Create details.json
        if not details_path.exists():
            self.create_details_json(manga_data, details_path)
        
        # Download cover image
        if not cover_path.exists():
            image_url = manga_data.get('images', {}).get('jpg', {}).get('large_image_url')
            if not image_url:
                image_url = manga_data.get('images', {}).get('jpg', {}).get('image_url')
            
            if image_url:
                self.download_cover(image_url, cover_path)
                time.sleep(REQUEST_DELAY)  # Rate limiting
            else:
                logger.warning(f"No cover image URL found for: {manga_name}")
        
        return True
    
    def process_all_manga(self):
        """Process all manga directories in the base directory"""
        logger.info(f"Starting metadata fetch for manga in: {self.base_dir}")
        logger.info(f"Using Jikan API (MyAnimeList)")
        
        # Get all subdirectories
        manga_dirs = [d for d in self.base_dir.iterdir() if d.is_dir()]
        
        logger.info(f"\nFound {len(manga_dirs)} directories to process\n")
        
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        for manga_dir in sorted(manga_dirs):
            try:
                result = self.process_manga_directory(manga_dir)
                if result:
                    success_count += 1
                else:
                    if manga_dir.name in ['free maga downloader 2', 'Kindle Comic Converter']:
                        skipped_count += 1
                    else:
                        failed_count += 1
            except Exception as e:
                logger.error(f"Error processing {manga_dir.name}: {e}")
                failed_count += 1
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total directories: {len(manga_dirs)}")
        logger.info(f"Successfully processed: {success_count}")
        logger.info(f"Failed: {failed_count}")
        logger.info(f"Skipped: {skipped_count}")
        logger.info(f"{'='*60}\n")


def main():
    """Main entry point"""
    # Get the directory where the script is located
    script_dir = Path(__file__).parent
    
    print("="*60)
    print("Manga Metadata Fetcher for Mihon")
    print("="*60)
    print(f"Working directory: {script_dir}")
    print(f"Data source: Jikan API (MyAnimeList)")
    print("="*60)
    print()
    
    # Confirm before proceeding
    response = input("Do you want to proceed? (y/n): ").strip().lower()
    if response != 'y':
        print("Operation cancelled.")
        return
    
    # Create fetcher and process all manga
    fetcher = MangaMetadataFetcher(script_dir)
    fetcher.process_all_manga()
    
    print("\nDone! Check the logs above for any errors.")


if __name__ == "__main__":
    main()
