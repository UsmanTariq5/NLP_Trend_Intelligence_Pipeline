# TrendScope Analytics - NLP Trend Intelligence Pipeline

## 📋 Project Overview

A reproducible NLP data engineering pipeline that collects, processes, and analyzes emerging technology products to identify linguistic trends and patterns. This project demonstrates end-to-end data pipeline development with version control, text processing, and automated orchestration.

**Business Goal**: Track emerging tech products, identify trending themes, analyze linguistic evolution, and maintain reproducible, versioned datasets.

## 🏗️ Architecture

```
Data Acquisition → Text Processing → Feature Engineering → Analysis → Versioning
     (Scraper)      (Preprocessing)    (BoW, N-grams)    (Statistics)    (DVC)
```

## 📊 Pipeline Stages

### Stage 1: Data Acquisition
- **Source**: GitHub Trending Repositories (as proxy for tech products)
- **Target**: 300+ product listings
- **Features**:
  - Rate limiting (1.2s between requests)
  - Retry logic (3 attempts with exponential backoff)
  - Missing value handling
- **Output**: `data/raw/products_raw.json`

### Stage 2: Data Versioning
- **Tool**: DVC (Data Version Control)
- **Remote**: DagsHub S3-compatible storage
- **Tracked Assets**:
  - Raw datasets
  - Processed datasets
  - Feature representations
- **Versioning**: Multiple dataset versions (v1: 300 entries)

### Stage 3: Text Processing
- **Preprocessing Pipeline**:
  1. Unicode normalization
  2. HTML removal
  3. URL removal
  4. Lowercasing
  5. Punctuation removal
  6. Tokenization
  7. Stopword removal
  8. Lemmatization
  9. Token filtering (length ≥ 2, non-numeric)
- **Output**: `data/processed/products_clean.csv`

### Stage 4: Data Representation
- **Manual Implementations**:
  - Vocabulary extraction (2,455 unique tokens)
  - One-Hot Encoding
  - Bag-of-Words matrix (300 × 2,455)
  - Unigram frequency distribution
  - Bigram frequency distribution
- **Outputs**:
  - `data/features/vocab.json`
  - `data/features/bow_matrix.npy`
  - `data/features/onehot_sample.npy`
  - `data/features/ngram_frequencies.json`

### Stage 5: Linguistic Intelligence
- **Statistical Analysis**:
  - Top 30 unigrams
  - Top 20 bigrams
  - Most common tags/categories
  - Vocabulary size: 2,455 tokens
  - Average description length: 33.94 tokens
  - Duplicate detection using Minimum Edit Distance
  - Unigram probability estimation
  - Perplexity calculation on 5 held-out descriptions
- **Output**: `reports/trend_summary.txt`

### Stage 6: Airflow Pipeline Orchestration
- **DAG Tasks**:
  1. `scrape_data` - Data acquisition
  2. `preprocess_data` - Text cleaning
  3. `generate_features` - Feature engineering
  4. `compute_statistics` - Analysis
  5. `dvc_push` - Version control
- **Features**:
  - Automatic retries (2 attempts)
  - Task dependencies
  - Logging
  - Manual triggering support
- **Schedule**: Weekly execution

## 📁 Project Structure

```
trend_intelligence_pipeline/
├── dags/
│   └── nlp_trend_dag.py          # Airflow DAG definition
│
├── src/
│   ├── scraper.py                # Data acquisition module
│   ├── preprocess.py             # Text preprocessing module
│   ├── representation.py         # Feature engineering module
│   └── statistics.py             # Statistical analysis module
│
├── data/
│   ├── raw/
│   │   └── products_raw.json     # Raw scraped data
│   ├── processed/
│   │   └── products_clean.csv    # Cleaned data
│   └── features/
│       ├── vocab.json            # Vocabulary
│       ├── bow_matrix.npy        # Bag-of-Words matrix
│       ├── onehot_sample.npy     # One-Hot encoding sample
│       └── ngram_frequencies.json # N-gram frequencies
│
├── reports/
│   └── trend_summary.txt         # Linguistic intelligence report
│
├── dvc.yaml                      # DVC pipeline configuration
├── .dvc/                         # DVC internal files
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Git
- DVC (Data Version Control)
- Apache Airflow (for orchestration)

### Installation

1. **Clone Repository**:
   ```bash
   git clone <repository-url>
   cd trend_intelligence_pipeline
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize DVC**:
   ```bash
   dvc init
   ```

4. **Configure DVC Remote** (Optional - DagsHub):
   ```bash
   dvc remote add -d dagshub dagshub://your-username/your-repo
   dvc remote modify dagshub --local auth basic
   dvc remote modify dagshub --local user your-username
   dvc remote modify dagshub --local password your-token
   ```

### Running the Pipeline

#### Option 1: Run Individual Stages
```bash
# Stage 1: Data Acquisition
python src/scraper.py

# Stage 2: Text Preprocessing
python src/preprocess.py

# Stage 3: Feature Engineering
python src/representation.py

# Stage 4: Statistical Analysis
python src/statistics.py
```

#### Option 2: Run with Airflow
```bash
# Initialize Airflow
airflow db init

# Copy DAG to Airflow directory
cp dags/nlp_trend_dag.py $AIRFLOW_HOME/dags/

# Start Airflow webserver
airflow webserver -p 8080

# Start Airflow scheduler (in separate terminal)
airflow scheduler

# Trigger DAG manually
airflow dags trigger nlp_trend_intelligence_pipeline
```

## 📈 Key Results

### Dataset Statistics
- **Total Products**: 300
- **Vocabulary Size**: 2,455 unique tokens
- **Total Tokens**: 10,182
- **Average Description Length**: 33.94 tokens
- **Matrix Sparsity**: 99.20%

### Top Trending Terms
1. **machine** - 453 occurrences
2. **learn** - 387 occurrences
3. **model** - 321 occurrences
4. **data** - 298 occurrences
5. **tool** - 276 occurrences

### Language Model Performance
- **Average Perplexity**: 1,237.55
- Lower perplexity indicates better model fit to the data

### Duplicate Detection
- **Potential Duplicates**: 166 pairs (using edit distance ≤ 3)

## 🔬 Technical Implementation Details

### Manual NLP Implementations

1. **Vocabulary Building**:
   - Token frequency counting
   - Sorted by frequency and alphabetically
   - Word-to-index mapping

2. **Bag-of-Words**:
   - Manual sparse matrix construction
   - Frequency-based representation
   - Shape: (300 documents, 2,455 features)

3. **N-gram Extraction**:
   - Unigram frequencies: 2,455 unique
   - Bigram frequencies: 5,567 unique
   - Manual sliding window implementation

4. **Minimum Edit Distance**:
   - Dynamic programming algorithm
   - O(n*m) time complexity
   - Used for duplicate detection

5. **Language Model**:
   - Unigram model with Laplace smoothing
   - Probability estimation: P(w) = (count(w) + 1) / (N + V)
   - Perplexity: 2^(-1/N * Σ log₂(P(w)))

## 🔄 Data Versioning with DVC

### Tracking Datasets
```bash
dvc add data/raw/products_raw.json
dvc add data/processed/products_clean.csv
dvc add data/features/vocab.json
dvc add data/features/bow_matrix.npy
```

### Committing Changes
```bash
git add data/raw/.gitignore data/raw/products_raw.json.dvc
git commit -m "Add raw dataset v1"
```

### Pushing to Remote
```bash
dvc push
```

### Retrieving Specific Version
```bash
git checkout <commit-hash>
dvc checkout
```

## 🛠️ Reproducibility

This pipeline ensures reproducibility through:
1. **Version Control**: Git for code, DVC for data
2. **Dependency Management**: `requirements.txt` with pinned versions
3. **Modular Design**: Independent, reusable components
4. **Documentation**: Comprehensive inline comments
5. **Automated Orchestration**: Airflow DAG for consistent execution

## 📝 NLP Concepts Demonstrated

- ✅ Text Preprocessing
- ✅ Tokenization
- ✅ Stopword Removal
- ✅ Lemmatization
- ✅ Vocabulary Extraction
- ✅ One-Hot Encoding
- ✅ Bag-of-Words
- ✅ N-gram Analysis (Unigrams, Bigrams)
- ✅ Minimum Edit Distance
- ✅ Language Model (Unigram)
- ✅ Perplexity Calculation

## 🤝 Contributing

This is an academic project for NLP coursework. For suggestions or improvements:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is created for educational purposes as part of NLP coursework.

## 👥 Authors

- **TrendScope Analytics Team**
- NLP Research & Innovation Department

## 🙏 Acknowledgments

- GitHub API for data access
- Open-source NLP community
- Course instructors and teaching assistants

---

**Note**: This pipeline focuses on data engineering and linguistic analysis. No machine learning model training is included as per project requirements.

## 📞 Support

For questions or issues:
- Open an issue in the repository
- Contact: analytics@trendscope.com
- Documentation: See inline code comments

---

*Last Updated: February 28, 2026*
