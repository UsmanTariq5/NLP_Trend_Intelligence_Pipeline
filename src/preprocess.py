"""
Text Preprocessing Module for TrendScope Analytics
Cleans and normalizes product descriptions for NLP analysis
"""

import json
import re
import unicodedata
import csv
from typing import List, Dict
import html


class TextPreprocessor:
    """
    Text preprocessing pipeline for product descriptions.
    Implements comprehensive text cleaning and normalization.
    """
    
    def __init__(self):
        """Initialize preprocessor with stopwords and utilities"""
        # Common English stopwords
        self.stopwords = {
            'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and',
            'any', 'are', 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below',
            'between', 'both', 'but', 'by', 'can', 'cannot', 'could', 'did', 'do', 'does',
            'doing', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had',
            'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'herself', 'him',
            'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'itself',
            'just', 'me', 'might', 'more', 'most', 'must', 'my', 'myself', 'no', 'nor',
            'not', 'now', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'our', 'ours',
            'ourselves', 'out', 'over', 'own', 's', 'same', 'she', 'should', 'so', 'some',
            'such', 't', 'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves',
            'then', 'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too',
            'under', 'until', 'up', 'very', 'was', 'we', 'were', 'what', 'when', 'where',
            'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'would', 'you', 'your',
            'yours', 'yourself', 'yourselves'
        }
        
        # Simple suffix rules for lemmatization
        self.suffix_rules = [
            ('sses', 'ss'),
            ('ies', 'i'),
            ('ss', 'ss'),
            ('s', ''),
            ('ing', ''),
            ('ed', ''),
            ('ly', ''),
        ]
        
    def normalize_unicode(self, text: str) -> str:
        """Normalize Unicode characters to ASCII"""
        if not text or text == 'N/A':
            return ''
        return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
        
    def remove_html(self, text: str) -> str:
        """Remove HTML tags and decode HTML entities"""
        if not text:
            return ''
        # Decode HTML entities
        text = html.unescape(text)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        return text
        
    def remove_urls(self, text: str) -> str:
        """Remove URLs from text"""
        if not text:
            return ''
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        return text
        
    def remove_punctuation(self, text: str) -> str:
        """Remove punctuation characters"""
        if not text:
            return ''
        # Keep only alphanumeric and spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        return text
        
    def tokenize(self, text: str) -> List[str]:
        """Simple whitespace tokenization"""
        if not text:
            return []
        return text.split()
        
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove stopwords from token list"""
        return [token for token in tokens if token not in self.stopwords]
        
    def simple_lemmatize(self, token: str) -> str:
        """
        Simple rule-based lemmatization.
        For production, use NLTK's WordNetLemmatizer.
        """
        token = token.lower()
        for suffix, replacement in self.suffix_rules:
            if token.endswith(suffix) and len(token) > len(suffix) + 2:
                return token[:-len(suffix)] + replacement
        return token
        
    def lemmatize_tokens(self, tokens: List[str]) -> List[str]:
        """Apply lemmatization to all tokens"""
        return [self.simple_lemmatize(token) for token in tokens]
        
    def filter_tokens(self, tokens: List[str]) -> List[str]:
        """
        Filter tokens by:
        - Remove numeric-only tokens
        - Remove tokens with length < 2
        """
        filtered = []
        for token in tokens:
            # Skip numeric-only tokens
            if token.isdigit():
                continue
            # Skip short tokens
            if len(token) < 2:
                continue
            filtered.append(token)
        return filtered
        
    def preprocess(self, text: str) -> Dict:
        """
        Full preprocessing pipeline.
        
        Args:
            text: Raw text string
            
        Returns:
            Dictionary with raw text, clean text, tokens, and token count
        """
        if not text or text == 'N/A':
            return {
                'text_raw': '',
                'text_clean': '',
                'tokens': [],
                'token_count': 0
            }
            
        # Store original
        text_raw = text
        
        # Apply preprocessing steps
        text = self.normalize_unicode(text)
        text = self.remove_html(text)
        text = self.remove_urls(text)
        text = text.lower()
        text = self.remove_punctuation(text)
        
        # Tokenization
        tokens = self.tokenize(text)
        
        # Remove stopwords
        tokens = self.remove_stopwords(tokens)
        
        # Lemmatization
        tokens = self.lemmatize_tokens(tokens)
        
        # Filter
        tokens = self.filter_tokens(tokens)
        
        # Join for clean text
        text_clean = ' '.join(tokens)
        
        return {
            'text_raw': text_raw,
            'text_clean': text_clean,
            'tokens': tokens,
            'token_count': len(tokens)
        }
        
    def process_products(self, input_path: str, output_path: str):
        """
        Process all products from raw JSON to clean CSV.
        
        Args:
            input_path: Path to raw products JSON
            output_path: Path to output clean CSV
        """
        print(f"Loading products from {input_path}...")
        with open(input_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
            
        print(f"Processing {len(products)} products...")
        
        processed_data = []
        for i, product in enumerate(products):
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(products)} products...")
                
            # Combine product name and tagline for processing
            product_name = product.get('product_name', '')
            tagline = product.get('tagline', '')
            
            # Process name
            name_result = self.preprocess(product_name)
            
            # Process tagline
            tagline_result = self.preprocess(tagline)
            
            # Combine tokens
            combined_tokens = name_result['tokens'] + tagline_result['tokens']
            
            # Create record
            record = {
                'product_name': product_name,
                'tagline': tagline,
                'text_raw': f"{product_name} {tagline}",
                'text_clean': ' '.join(combined_tokens),
                'tokens': '|'.join(combined_tokens),  # Use pipe separator for CSV
                'token_count': len(combined_tokens),
                'tags': '|'.join(product.get('tags', [])),
                'category': product.get('category', 'N/A'),
                'stars': product.get('popularity_signal', {}).get('stars', 0),
                'product_url': product.get('product_url', '')
            }
            
            processed_data.append(record)
            
        # Write to CSV
        print(f"\nWriting processed data to {output_path}...")
        fieldnames = ['product_name', 'tagline', 'text_raw', 'text_clean', 'tokens', 
                     'token_count', 'tags', 'category', 'stars', 'product_url']
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(processed_data)
            
        print(f"✓ Processed {len(processed_data)} products")
        
        # Statistics
        total_tokens = sum(r['token_count'] for r in processed_data)
        avg_tokens = total_tokens / len(processed_data) if processed_data else 0
        print(f"  Total tokens: {total_tokens}")
        print(f"  Average tokens per product: {avg_tokens:.2f}")
        

def main():
    """Main preprocessing workflow"""
    print("=" * 60)
    print("TrendScope Analytics - Text Preprocessing")
    print("=" * 60)
    
    preprocessor = TextPreprocessor()
    
    input_path = 'data/raw/products_raw.json'
    output_path = 'data/processed/products_clean.csv'
    
    preprocessor.process_products(input_path, output_path)
    
    print("\n✓ Text preprocessing complete!")
    print(f"  Clean data saved to: {output_path}")
    

if __name__ == '__main__':
    main()
