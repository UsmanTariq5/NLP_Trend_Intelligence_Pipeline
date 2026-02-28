"""
Data Acquisition Module for TrendScope Analytics
Scrapes tech product listings from GitHub Trending repositories
"""

import requests
import json
import time
from datetime import datetime, timezone
from typing import List, Dict, Optional
import random


class TechProductScraper:
    """
    Scraper for collecting emerging tech product data.
    Uses GitHub API to collect trending repositories as proxy for tech products.
    """
    
    def __init__(self, rate_limit_delay: float = 1.0):
        """
        Initialize scraper with rate limiting.
        
        Args:
            rate_limit_delay: Seconds to wait between requests
        """
        self.base_url = "https://api.github.com"
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'TrendScope-Analytics-Research'
        })
        
    def _rate_limit(self):
        """Implement rate limiting between requests"""
        time.sleep(self.rate_limit_delay + random.uniform(0, 0.5))
        
    def _make_request(self, url: str, params: Optional[Dict] = None, retries: int = 3) -> Optional[Dict]:
        """
        Make HTTP request with retry logic.
        
        Args:
            url: API endpoint URL
            params: Query parameters
            retries: Number of retry attempts
            
        Returns:
            JSON response or None if failed
        """
        for attempt in range(retries):
            try:
                response = self.session.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 403:
                    # Rate limit exceeded
                    print(f"Rate limit exceeded. Waiting 60 seconds...")
                    time.sleep(60)
                    continue
                elif response.status_code == 404:
                    print(f"Resource not found: {url}")
                    return None
                else:
                    print(f"HTTP {response.status_code}: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                print(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
        return None
        
    def search_repositories(self, query: str, per_page: int = 100, max_pages: int = 10) -> List[Dict]:
        """
        Search GitHub repositories.
        
        Args:
            query: Search query string
            per_page: Results per page (max 100)
            max_pages: Maximum pages to fetch
            
        Returns:
            List of repository data
        """
        repositories = []
        
        for page in range(1, max_pages + 1):
            print(f"Fetching page {page}/{max_pages} for query: {query}")
            
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': min(per_page, 100),
                'page': page
            }
            
            url = f"{self.base_url}/search/repositories"
            data = self._make_request(url, params)
            
            if data and 'items' in data:
                repositories.extend(data['items'])
                
                # Check if we've reached the end
                if len(data['items']) < per_page:
                    break
                    
                self._rate_limit()
            else:
                break
                
        return repositories
        
    def get_repository_details(self, repo_full_name: str) -> Optional[Dict]:
        """
        Get detailed information about a repository.
        
        Args:
            repo_full_name: Repository full name (owner/repo)
            
        Returns:
            Repository details or None
        """
        url = f"{self.base_url}/repos/{repo_full_name}"
        return self._make_request(url)
        
    def transform_to_product_format(self, repo: Dict) -> Dict:
        """
        Transform GitHub repository data to product listing format.
        
        Args:
            repo: GitHub repository data
            
        Returns:
            Standardized product listing
        """
        return {
            'product_name': repo.get('name', 'N/A'),
            'tagline': repo.get('description', 'N/A'),
            'tags': repo.get('topics', []),
            'category': repo.get('language', 'N/A'),
            'popularity_signal': {
                'stars': repo.get('stargazers_count', 0),
                'forks': repo.get('forks_count', 0),
                'watchers': repo.get('watchers_count', 0),
                'open_issues': repo.get('open_issues_count', 0)
            },
            'product_url': repo.get('html_url', 'N/A'),
            'created_at': repo.get('created_at', 'N/A'),
            'updated_at': repo.get('updated_at', 'N/A'),
            'scrape_timestamp': datetime.now(timezone.utc).isoformat(),
            'owner': repo.get('owner', {}).get('login', 'N/A'),
            'license': repo.get('license', {}).get('name', 'N/A') if repo.get('license') else 'N/A',
            'homepage': repo.get('homepage', 'N/A')
        }
        
    def scrape_tech_products(self, target_count: int = 300) -> List[Dict]:
        """
        Scrape tech products to meet target count.
        
        Args:
            target_count: Minimum number of products to collect
            
        Returns:
            List of product listings
        """
        products = []
        
        # Define search queries for different tech categories
        queries = [
            'ai machine-learning stars:>500',
            'automation tool stars:>300',
            'developer-tools stars:>300',
            'api framework stars:>400',
            'saas platform stars:>200',
            'chatbot ai stars:>200',
            'productivity tool stars:>300',
            'analytics dashboard stars:>200',
            'nlp text-processing stars:>200',
            'web3 blockchain stars:>200',
        ]
        
        for query in queries:
            if len(products) >= target_count:
                break
                
            print(f"\nSearching: {query}")
            repos = self.search_repositories(query, per_page=100, max_pages=5)
            
            for repo in repos:
                if len(products) >= target_count:
                    break
                    
                # Transform and add product
                product = self.transform_to_product_format(repo)
                products.append(product)
                
            print(f"Collected {len(products)} products so far...")
            
        return products[:target_count]
        
    def save_products(self, products: List[Dict], output_path: str):
        """
        Save product listings to JSON file.
        
        Args:
            products: List of product data
            output_path: Output file path
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
            
        print(f"Saved {len(products)} products to {output_path}")


def main():
    """Main scraping workflow"""
    print("=" * 60)
    print("TrendScope Analytics - Data Acquisition")
    print("=" * 60)
    
    # Initialize scraper
    scraper = TechProductScraper(rate_limit_delay=1.2)
    
    # Scrape products
    print("\nStarting data collection...")
    products = scraper.scrape_tech_products(target_count=300)
    
    # Handle missing values
    for product in products:
        for key, value in product.items():
            if value is None or value == '':
                product[key] = 'N/A'
                
    print(f"\nSuccessfully collected {len(products)} products")
    print(f"Products with descriptions: {sum(1 for p in products if p['tagline'] != 'N/A')}")
    print(f"Products with tags: {sum(1 for p in products if p['tags'])}")
    
    # Save raw data
    output_path = 'data/raw/products_raw.json'
    scraper.save_products(products, output_path)
    
    print("\n✓ Data acquisition complete!")
    print(f"  Raw data saved to: {output_path}")
    

if __name__ == '__main__':
    main()
