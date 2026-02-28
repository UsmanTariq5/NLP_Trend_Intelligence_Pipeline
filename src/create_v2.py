"""
Script to create Version 2 of the dataset with 500 products
This demonstrates dataset versioning as required by the assignment
"""

from scraper import TechProductScraper

def create_version_2():
    """Create version 2 with 500 products"""
    print("=" * 60)
    print("Creating Dataset Version 2 (500 products)")
    print("=" * 60)
    
    scraper = TechProductScraper(rate_limit_delay=1.2)
    
    # Scrape 500 products for v2
    products = scraper.scrape_tech_products(target_count=500)
    
    # Handle missing values
    for product in products:
        for key, value in product.items():
            if value is None or value == '':
                product[key] = 'N/A'
    
    # Save as version 2
    output_path = 'data/raw/products_raw_v2.json'
    scraper.save_products(products, output_path)
    
    print(f"\n✓ Version 2 created with {len(products)} products")
    print(f"  Saved to: {output_path}")
    print("\nDataset Versions:")
    print("  v1: data/raw/products_raw.json (300 products)")
    print("  v2: data/raw/products_raw_v2.json (500 products)")

if __name__ == '__main__':
    create_version_2()
