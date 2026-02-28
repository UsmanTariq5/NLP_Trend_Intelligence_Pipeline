"""
Data Representation Module for TrendScope Analytics
Implements vocabulary extraction, BoW, One-Hot, and N-gram frequency distributions
"""

import csv
import json
import numpy as np
from collections import Counter, defaultdict
from typing import List, Dict, Tuple


class TextRepresentation:
    """
    Manual implementation of NLP representations:
    - Vocabulary extraction
    - One-Hot Encoding
    - Bag-of-Words
    - N-gram frequency distributions
    """
    
    def __init__(self):
        self.vocabulary = []
        self.word_to_idx = {}
        self.idx_to_word = {}
        self.unigram_freq = Counter()
        self.bigram_freq = Counter()
        
    def build_vocabulary(self, token_lists: List[List[str]]) -> Dict:
        """
        Build vocabulary from token lists.
        
        Args:
            token_lists: List of tokenized documents
            
        Returns:
            Vocabulary statistics
        """
        print("Building vocabulary...")
        
        # Collect all unique tokens
        all_tokens = []
        for tokens in token_lists:
            all_tokens.extend(tokens)
            
        # Count frequencies
        token_counts = Counter(all_tokens)
        
        # Sort by frequency (descending) then alphabetically
        sorted_tokens = sorted(token_counts.items(), key=lambda x: (-x[1], x[0]))
        
        # Build vocabulary
        self.vocabulary = [token for token, count in sorted_tokens]
        self.word_to_idx = {word: idx for idx, word in enumerate(self.vocabulary)}
        self.idx_to_word = {idx: word for word, idx in self.word_to_idx.items()}
        
        vocab_stats = {
            'vocabulary_size': len(self.vocabulary),
            'total_tokens': len(all_tokens),
            'unique_tokens': len(set(all_tokens)),
            'most_common': sorted_tokens[:50]
        }
        
        print(f"  Vocabulary size: {vocab_stats['vocabulary_size']}")
        print(f"  Total tokens: {vocab_stats['total_tokens']}")
        
        return vocab_stats
        
    def save_vocabulary(self, output_path: str):
        """Save vocabulary to JSON file"""
        vocab_data = {
            'vocabulary': self.vocabulary,
            'size': len(self.vocabulary),
            'word_to_idx': self.word_to_idx
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(vocab_data, f, indent=2, ensure_ascii=False)
            
        print(f"  Vocabulary saved to: {output_path}")
        
    def one_hot_encode(self, tokens: List[str]) -> np.ndarray:
        """
        Create one-hot encoding for a document.
        
        Args:
            tokens: List of tokens in document
            
        Returns:
            One-hot encoded vector (vocab_size,)
        """
        vector = np.zeros(len(self.vocabulary), dtype=np.int8)
        
        for token in tokens:
            if token in self.word_to_idx:
                idx = self.word_to_idx[token]
                vector[idx] = 1
                
        return vector
        
    def bag_of_words(self, tokens: List[str]) -> np.ndarray:
        """
        Create Bag-of-Words representation for a document.
        
        Args:
            tokens: List of tokens in document
            
        Returns:
            BoW vector (vocab_size,)
        """
        vector = np.zeros(len(self.vocabulary), dtype=np.int32)
        
        for token in tokens:
            if token in self.word_to_idx:
                idx = self.word_to_idx[token]
                vector[idx] += 1
                
        return vector
        
    def create_bow_matrix(self, token_lists: List[List[str]]) -> np.ndarray:
        """
        Create BoW matrix for all documents.
        
        Args:
            token_lists: List of tokenized documents
            
        Returns:
            BoW matrix (num_docs, vocab_size)
        """
        print("Creating Bag-of-Words matrix...")
        
        num_docs = len(token_lists)
        vocab_size = len(self.vocabulary)
        
        bow_matrix = np.zeros((num_docs, vocab_size), dtype=np.int32)
        
        for doc_idx, tokens in enumerate(token_lists):
            bow_matrix[doc_idx] = self.bag_of_words(tokens)
            
        print(f"  BoW matrix shape: {bow_matrix.shape}")
        print(f"  Sparsity: {(bow_matrix == 0).sum() / bow_matrix.size * 100:.2f}%")
        
        return bow_matrix
        
    def extract_unigrams(self, token_lists: List[List[str]]) -> Counter:
        """
        Extract unigram frequency distribution.
        
        Args:
            token_lists: List of tokenized documents
            
        Returns:
            Counter of unigram frequencies
        """
        print("Extracting unigram frequencies...")
        
        self.unigram_freq = Counter()
        
        for tokens in token_lists:
            self.unigram_freq.update(tokens)
            
        print(f"  Unique unigrams: {len(self.unigram_freq)}")
        print(f"  Total unigrams: {sum(self.unigram_freq.values())}")
        
        return self.unigram_freq
        
    def extract_bigrams(self, token_lists: List[List[str]]) -> Counter:
        """
        Extract bigram frequency distribution.
        
        Args:
            token_lists: List of tokenized documents
            
        Returns:
            Counter of bigram frequencies
        """
        print("Extracting bigram frequencies...")
        
        self.bigram_freq = Counter()
        
        for tokens in token_lists:
            # Create bigrams
            bigrams = [(tokens[i], tokens[i+1]) for i in range(len(tokens)-1)]
            self.bigram_freq.update(bigrams)
            
        print(f"  Unique bigrams: {len(self.bigram_freq)}")
        print(f"  Total bigrams: {sum(self.bigram_freq.values())}")
        
        return self.bigram_freq
        
    def save_frequencies(self, output_path: str):
        """Save frequency distributions to JSON"""
        freq_data = {
            'unigrams': {
                'top_30': self.unigram_freq.most_common(30),
                'total': sum(self.unigram_freq.values()),
                'unique': len(self.unigram_freq)
            },
            'bigrams': {
                'top_20': [(f"{w1} {w2}", count) for (w1, w2), count in self.bigram_freq.most_common(20)],
                'total': sum(self.bigram_freq.values()),
                'unique': len(self.bigram_freq)
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(freq_data, f, indent=2, ensure_ascii=False)
            
        print(f"  Frequencies saved to: {output_path}")


def load_processed_data(file_path: str) -> Tuple[List[List[str]], List[Dict]]:
    """
    Load processed CSV data.
    
    Args:
        file_path: Path to processed CSV
        
    Returns:
        Tuple of (token_lists, records)
    """
    print(f"Loading processed data from {file_path}...")
    
    records = []
    token_lists = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
            # Parse tokens (stored as pipe-separated)
            tokens = row['tokens'].split('|') if row['tokens'] else []
            token_lists.append(tokens)
            
    print(f"  Loaded {len(records)} products")
    
    return token_lists, records


def main():
    """Main representation workflow"""
    print("=" * 60)
    print("TrendScope Analytics - Data Representation")
    print("=" * 60)
    
    # Load data
    input_path = 'data/processed/products_clean.csv'
    token_lists, records = load_processed_data(input_path)
    
    # Initialize representation
    repr_engine = TextRepresentation()
    
    # Build vocabulary
    print("\n" + "=" * 60)
    vocab_stats = repr_engine.build_vocabulary(token_lists)
    repr_engine.save_vocabulary('data/features/vocab.json')
    
    # Create BoW matrix
    print("\n" + "=" * 60)
    bow_matrix = repr_engine.create_bow_matrix(token_lists)
    np.save('data/features/bow_matrix.npy', bow_matrix)
    print(f"  BoW matrix saved to: data/features/bow_matrix.npy")
    
    # One-hot encoding (for first 10 documents as example)
    print("\n" + "=" * 60)
    print("Creating One-Hot encodings (first 10 documents)...")
    onehot_matrix = np.array([repr_engine.one_hot_encode(tokens) for tokens in token_lists[:10]])
    np.save('data/features/onehot_sample.npy', onehot_matrix)
    print(f"  One-Hot sample shape: {onehot_matrix.shape}")
    print(f"  One-Hot sample saved to: data/features/onehot_sample.npy")
    
    # Extract n-grams
    print("\n" + "=" * 60)
    repr_engine.extract_unigrams(token_lists)
    repr_engine.extract_bigrams(token_lists)
    repr_engine.save_frequencies('data/features/ngram_frequencies.json')
    
    print("\n✓ Data representation complete!")
    

if __name__ == '__main__':
    main()
