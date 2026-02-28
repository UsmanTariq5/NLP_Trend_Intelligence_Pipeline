"""
Statistical Analysis Module for TrendScope Analytics
Includes linguistic intelligence, duplicate detection, and language modeling
"""

import csv
import json
import math
from collections import Counter, defaultdict
from typing import List, Dict, Tuple


class MinimumEditDistance:
    """Implementation of Minimum Edit Distance (Levenshtein Distance)"""
    
    @staticmethod
    def calculate(str1: str, str2: str) -> int:
        """
        Calculate minimum edit distance between two strings.
        Uses dynamic programming.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Minimum number of edits required
        """
        m, n = len(str1), len(str2)
        
        # Create DP table
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Initialize base cases
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
            
        # Fill DP table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str1[i-1] == str2[j-1]:
                    dp[i][j] = dp[i-1][j-1]  # No edit needed
                else:
                    dp[i][j] = 1 + min(
                        dp[i-1][j],      # Deletion
                        dp[i][j-1],      # Insertion
                        dp[i-1][j-1]     # Substitution
                    )
                    
        return dp[m][n]


class UnigramLanguageModel:
    """Simple unigram language model for perplexity calculation"""
    
    def __init__(self):
        self.unigram_counts = Counter()
        self.total_tokens = 0
        self.vocab_size = 0
        self.probabilities = {}
        
    def train(self, token_lists: List[List[str]]):
        """
        Train unigram model on token lists.
        
        Args:
            token_lists: List of tokenized documents
        """
        print("Training unigram language model...")
        
        # Count unigrams
        for tokens in token_lists:
            self.unigram_counts.update(tokens)
            
        self.total_tokens = sum(self.unigram_counts.values())
        self.vocab_size = len(self.unigram_counts)
        
        # Calculate probabilities with Laplace smoothing
        for word, count in self.unigram_counts.items():
            self.probabilities[word] = (count + 1) / (self.total_tokens + self.vocab_size)
            
        # Unknown word probability
        self.unk_prob = 1 / (self.total_tokens + self.vocab_size)
        
        print(f"  Vocabulary size: {self.vocab_size}")
        print(f"  Total tokens: {self.total_tokens}")
        
    def get_probability(self, word: str) -> float:
        """Get probability of a word"""
        return self.probabilities.get(word, self.unk_prob)
        
    def calculate_perplexity(self, test_tokens: List[str]) -> float:
        """
        Calculate perplexity on test tokens.
        
        Args:
            test_tokens: List of tokens to evaluate
            
        Returns:
            Perplexity value
        """
        if not test_tokens:
            return float('inf')
            
        log_prob_sum = 0
        for token in test_tokens:
            prob = self.get_probability(token)
            log_prob_sum += math.log2(prob)
            
        # Perplexity = 2^(-1/N * sum(log2(P(w))))
        perplexity = 2 ** (-log_prob_sum / len(test_tokens))
        
        return perplexity


class LinguisticIntelligence:
    """Generate linguistic intelligence and trend summaries"""
    
    def __init__(self):
        self.records = []
        self.token_lists = []
        self.unigram_freq = Counter()
        self.bigram_freq = Counter()
        self.tag_freq = Counter()
        self.category_freq = Counter()
        
    def load_data(self, csv_path: str, freq_path: str):
        """Load processed data and frequencies"""
        print("Loading data...")
        
        # Load CSV
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.records = list(reader)
            
        # Parse tokens
        self.token_lists = []
        for record in self.records:
            tokens = record['tokens'].split('|') if record['tokens'] else []
            self.token_lists.append(tokens)
            
        # Load frequencies
        with open(freq_path, 'r', encoding='utf-8') as f:
            freq_data = json.load(f)
            
        # Convert back to Counter
        self.unigram_freq = Counter({word: count for word, count in freq_data['unigrams']['top_30']})
        
        # Parse bigrams
        for bigram_str, count in freq_data['bigrams']['top_20']:
            words = bigram_str.split()
            if len(words) == 2:
                self.bigram_freq[(words[0], words[1])] = count
                
        print(f"  Loaded {len(self.records)} products")
        
    def analyze_tags_categories(self):
        """Analyze tags and categories"""
        print("Analyzing tags and categories...")
        
        for record in self.records:
            # Parse tags
            tags = record['tags'].split('|') if record['tags'] else []
            self.tag_freq.update(tags)
            
            # Count category
            category = record.get('category', 'N/A')
            if category and category != 'N/A':
                self.category_freq[category] += 1
                
        print(f"  Unique tags: {len(self.tag_freq)}")
        print(f"  Unique categories: {len(self.category_freq)}")
        
    def detect_duplicates(self, threshold: int = 3) -> List[Tuple]:
        """
        Detect near-duplicate product names using Minimum Edit Distance.
        
        Args:
            threshold: Maximum edit distance to consider as duplicate
            
        Returns:
            List of duplicate pairs with edit distance
        """
        print(f"Detecting duplicates (threshold={threshold})...")
        
        duplicates = []
        product_names = [r['product_name'] for r in self.records]
        
        # Compare all pairs
        for i in range(len(product_names)):
            for j in range(i + 1, len(product_names)):
                name1 = product_names[i].lower()
                name2 = product_names[j].lower()
                
                # Skip if exactly the same
                if name1 == name2:
                    duplicates.append((product_names[i], product_names[j], 0))
                    continue
                    
                # Calculate edit distance
                distance = MinimumEditDistance.calculate(name1, name2)
                
                if distance <= threshold:
                    duplicates.append((product_names[i], product_names[j], distance))
                    
        print(f"  Found {len(duplicates)} potential duplicates")
        
        return duplicates
        
    def calculate_statistics(self) -> Dict:
        """Calculate various statistics"""
        print("Calculating statistics...")
        
        # Vocabulary size
        vocab_size = len(set(token for tokens in self.token_lists for token in tokens))
        
        # Average description length
        total_tokens = sum(len(tokens) for tokens in self.token_lists)
        avg_length = total_tokens / len(self.token_lists) if self.token_lists else 0
        
        # Description length distribution
        lengths = [len(tokens) for tokens in self.token_lists]
        min_length = min(lengths) if lengths else 0
        max_length = max(lengths) if lengths else 0
        
        stats = {
            'vocabulary_size': vocab_size,
            'total_products': len(self.records),
            'total_tokens': total_tokens,
            'avg_description_length': avg_length,
            'min_description_length': min_length,
            'max_description_length': max_length,
        }
        
        print(f"  Vocabulary size: {stats['vocabulary_size']}")
        print(f"  Average description length: {stats['avg_description_length']:.2f} tokens")
        
        return stats
        
    def estimate_probabilities(self) -> Dict[str, float]:
        """Estimate unigram probabilities"""
        print("Estimating unigram probabilities...")
        
        total = sum(self.unigram_freq.values())
        probabilities = {word: count / total for word, count in self.unigram_freq.items()}
        
        return probabilities
        
    def compute_perplexity_on_holdout(self, num_holdout: int = 5):
        """
        Compute perplexity on held-out descriptions.
        
        Args:
            num_holdout: Number of products to hold out
            
        Returns:
            Dictionary with perplexity results
        """
        print(f"Computing perplexity on {num_holdout} held-out descriptions...")
        
        # Split data: train on first N-5, test on last 5
        train_tokens = self.token_lists[:-num_holdout]
        test_tokens_list = self.token_lists[-num_holdout:]
        
        # Train language model
        lm = UnigramLanguageModel()
        lm.train(train_tokens)
        
        # Calculate perplexity for each test document
        perplexities = []
        for i, test_tokens in enumerate(test_tokens_list):
            if test_tokens:
                pp = lm.calculate_perplexity(test_tokens)
                perplexities.append(pp)
                print(f"    Document {i+1}: Perplexity = {pp:.2f}")
            else:
                print(f"    Document {i+1}: Empty (skipped)")
                
        avg_perplexity = sum(perplexities) / len(perplexities) if perplexities else 0
        
        return {
            'perplexities': perplexities,
            'average_perplexity': avg_perplexity,
            'num_evaluated': len(perplexities)
        }
        
    def generate_report(self, output_path: str):
        """Generate comprehensive trend summary report"""
        print("\nGenerating trend summary report...")
        
        # Load frequencies
        with open('data/features/ngram_frequencies.json', 'r', encoding='utf-8') as f:
            freq_data = json.load(f)
            
        # Get statistics
        stats = self.calculate_statistics()
        
        # Get probabilities
        probabilities = self.estimate_probabilities()
        top_prob_words = sorted(probabilities.items(), key=lambda x: -x[1])[:10]
        
        # Detect duplicates
        duplicates = self.detect_duplicates(threshold=3)
        
        # Compute perplexity
        perplexity_results = self.compute_perplexity_on_holdout(num_holdout=5)
        
        # Write report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("TRENDSCOPE ANALYTICS - LINGUISTIC INTELLIGENCE REPORT\n")
            f.write("=" * 70 + "\n\n")
            
            # Dataset Overview
            f.write("DATASET OVERVIEW\n")
            f.write("-" * 70 + "\n")
            f.write(f"Total Products Analyzed: {stats['total_products']}\n")
            f.write(f"Vocabulary Size: {stats['vocabulary_size']}\n")
            f.write(f"Total Tokens: {stats['total_tokens']}\n")
            f.write(f"Average Description Length: {stats['avg_description_length']:.2f} tokens\n")
            f.write(f"Min Description Length: {stats['min_description_length']} tokens\n")
            f.write(f"Max Description Length: {stats['max_description_length']} tokens\n\n")
            
            # Top Unigrams
            f.write("TOP 30 UNIGRAMS\n")
            f.write("-" * 70 + "\n")
            for i, (word, count) in enumerate(freq_data['unigrams']['top_30'], 1):
                f.write(f"{i:2d}. {word:20s} - {count:4d} occurrences\n")
            f.write("\n")
            
            # Top Bigrams
            f.write("TOP 20 BIGRAMS\n")
            f.write("-" * 70 + "\n")
            for i, (bigram, count) in enumerate(freq_data['bigrams']['top_20'], 1):
                f.write(f"{i:2d}. {bigram:30s} - {count:4d} occurrences\n")
            f.write("\n")
            
            # Top Categories
            f.write("MOST COMMON CATEGORIES/LANGUAGES\n")
            f.write("-" * 70 + "\n")
            for i, (category, count) in enumerate(self.category_freq.most_common(15), 1):
                f.write(f"{i:2d}. {category:20s} - {count:3d} products\n")
            f.write("\n")
            
            # Top Tags
            f.write("MOST COMMON TAGS\n")
            f.write("-" * 70 + "\n")
            top_tags = [(tag, count) for tag, count in self.tag_freq.most_common(20) if tag]
            for i, (tag, count) in enumerate(top_tags, 1):
                f.write(f"{i:2d}. {tag:30s} - {count:3d} occurrences\n")
            f.write("\n")
            
            # Unigram Probabilities
            f.write("TOP 10 UNIGRAM PROBABILITIES\n")
            f.write("-" * 70 + "\n")
            for i, (word, prob) in enumerate(top_prob_words, 1):
                f.write(f"{i:2d}. {word:20s} - P = {prob:.6f}\n")
            f.write("\n")
            
            # Duplicate Detection
            f.write("DUPLICATE DETECTION (Minimum Edit Distance ≤ 3)\n")
            f.write("-" * 70 + "\n")
            if duplicates:
                for i, (name1, name2, distance) in enumerate(duplicates[:20], 1):
                    f.write(f"{i:2d}. Distance={distance} | {name1} <-> {name2}\n")
                if len(duplicates) > 20:
                    f.write(f"... and {len(duplicates) - 20} more\n")
            else:
                f.write("No near-duplicates found.\n")
            f.write(f"\nTotal potential duplicates: {len(duplicates)}\n\n")
            
            # Perplexity
            f.write("LANGUAGE MODEL PERPLEXITY (5 Held-Out Descriptions)\n")
            f.write("-" * 70 + "\n")
            for i, pp in enumerate(perplexity_results['perplexities'], 1):
                f.write(f"Document {i}: Perplexity = {pp:.2f}\n")
            f.write(f"\nAverage Perplexity: {perplexity_results['average_perplexity']:.2f}\n\n")
            
            # Key Insights
            f.write("KEY INSIGHTS\n")
            f.write("-" * 70 + "\n")
            f.write("1. The dataset contains diverse tech products with rich descriptions.\n")
            f.write(f"2. Top terms like '{freq_data['unigrams']['top_30'][0][0]}' appear {freq_data['unigrams']['top_30'][0][1]} times.\n")
            f.write(f"3. Average description length is {stats['avg_description_length']:.1f} tokens per product.\n")
            f.write(f"4. Found {len(duplicates)} potential near-duplicates using edit distance.\n")
            f.write(f"5. Language model perplexity: {perplexity_results['average_perplexity']:.2f}\n")
            f.write("   (Lower perplexity indicates better language model fit)\n\n")
            
            f.write("=" * 70 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 70 + "\n")
            
        print(f"✓ Report saved to: {output_path}")


def main():
    """Main statistics workflow"""
    print("=" * 60)
    print("TrendScope Analytics - Linguistic Intelligence")
    print("=" * 60)
    
    intel = LinguisticIntelligence()
    
    # Load data
    intel.load_data(
        'data/processed/products_clean.csv',
        'data/features/ngram_frequencies.json'
    )
    
    # Analyze tags and categories
    intel.analyze_tags_categories()
    
    # Generate report
    intel.generate_report('reports/trend_summary.txt')
    
    print("\n✓ Linguistic intelligence analysis complete!")
    

if __name__ == '__main__':
    main()
