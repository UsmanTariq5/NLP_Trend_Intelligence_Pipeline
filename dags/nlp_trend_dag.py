"""
Airflow DAG for TrendScope Analytics NLP Pipeline
Orchestrates data acquisition, processing, representation, and analysis
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
import os

# Add project src directory to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

# Import pipeline modules
from scraper import TechProductScraper
from preprocess import TextPreprocessor
from representation import TextRepresentation, load_processed_data
from statistics import LinguisticIntelligence


# Default arguments for the DAG
default_args = {
    'owner': 'trendscope',
    'depends_on_past': False,
    'email': ['analytics@trendscope.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}


def scrape_data_task(**context):
    """Task 1: Scrape tech product data"""
    print("Starting data scraping...")
    
    scraper = TechProductScraper(rate_limit_delay=1.2)
    products = scraper.scrape_tech_products(target_count=300)
    
    # Handle missing values
    for product in products:
        for key, value in product.items():
            if value is None or value == '':
                product[key] = 'N/A'
                
    # Save raw data
    output_path = os.path.join(PROJECT_ROOT, 'data/raw/products_raw.json')
    scraper.save_products(products, output_path)
    
    print(f"Scraped {len(products)} products")
    
    # Push metadata to XCom
    context['task_instance'].xcom_push(key='num_products', value=len(products))
    
    return f"Scraped {len(products)} products"


def preprocess_data_task(**context):
    """Task 2: Preprocess and clean text data"""
    print("Starting text preprocessing...")
    
    preprocessor = TextPreprocessor()
    
    input_path = os.path.join(PROJECT_ROOT, 'data/raw/products_raw.json')
    output_path = os.path.join(PROJECT_ROOT, 'data/processed/products_clean.csv')
    
    preprocessor.process_products(input_path, output_path)
    
    print("Text preprocessing complete")
    
    return "Text preprocessing complete"


def generate_features_task(**context):
    """Task 3: Generate NLP features (BoW, vocab, n-grams)"""
    print("Starting feature generation...")
    
    # Load data
    input_path = os.path.join(PROJECT_ROOT, 'data/processed/products_clean.csv')
    token_lists, records = load_processed_data(input_path)
    
    # Initialize representation engine
    repr_engine = TextRepresentation()
    
    # Build vocabulary
    vocab_stats = repr_engine.build_vocabulary(token_lists)
    vocab_path = os.path.join(PROJECT_ROOT, 'data/features/vocab.json')
    repr_engine.save_vocabulary(vocab_path)
    
    # Create BoW matrix
    bow_matrix = repr_engine.create_bow_matrix(token_lists)
    bow_path = os.path.join(PROJECT_ROOT, 'data/features/bow_matrix.npy')
    
    import numpy as np
    np.save(bow_path, bow_matrix)
    
    # One-hot encoding sample
    onehot_matrix = np.array([repr_engine.one_hot_encode(tokens) for tokens in token_lists[:10]])
    onehot_path = os.path.join(PROJECT_ROOT, 'data/features/onehot_sample.npy')
    np.save(onehot_path, onehot_matrix)
    
    # Extract n-grams
    repr_engine.extract_unigrams(token_lists)
    repr_engine.extract_bigrams(token_lists)
    freq_path = os.path.join(PROJECT_ROOT, 'data/features/ngram_frequencies.json')
    repr_engine.save_frequencies(freq_path)
    
    print("Feature generation complete")
    
    # Push metadata to XCom
    context['task_instance'].xcom_push(key='vocab_size', value=vocab_stats['vocabulary_size'])
    
    return "Feature generation complete"


def compute_statistics_task(**context):
    """Task 4: Compute linguistic statistics and generate report"""
    print("Starting statistical analysis...")
    
    intel = LinguisticIntelligence()
    
    # Load data
    csv_path = os.path.join(PROJECT_ROOT, 'data/processed/products_clean.csv')
    freq_path = os.path.join(PROJECT_ROOT, 'data/features/ngram_frequencies.json')
    intel.load_data(csv_path, freq_path)
    
    # Analyze tags and categories
    intel.analyze_tags_categories()
    
    # Generate report
    report_path = os.path.join(PROJECT_ROOT, 'reports/trend_summary.txt')
    intel.generate_report(report_path)
    
    print("Statistical analysis complete")
    
    return "Statistical analysis complete"


def dvc_push_task(**context):
    """Task 5: Version data with DVC and push to remote"""
    print("Starting DVC versioning...")
    
    # Note: This task demonstrates DVC commands
    # In production, ensure DVC is properly configured with remote storage
    
    print("DVC versioning would be executed here")
    print("Commands:")
    print("  dvc add data/raw/products_raw.json")
    print("  dvc add data/processed/products_clean.csv")
    print("  dvc add data/features/vocab.json")
    print("  dvc add data/features/bow_matrix.npy")
    print("  dvc push")
    
    return "DVC versioning complete (simulated)"


# Define the DAG
dag = DAG(
    'nlp_trend_intelligence_pipeline',
    default_args=default_args,
    description='TrendScope Analytics NLP Trend Intelligence Pipeline',
    schedule_interval=timedelta(days=7),  # Run weekly
    start_date=datetime(2026, 2, 1),
    catchup=False,
    tags=['nlp', 'trend-analysis', 'data-pipeline'],
)


# Define tasks
scrape_data = PythonOperator(
    task_id='scrape_data',
    python_callable=scrape_data_task,
    provide_context=True,
    dag=dag,
)

preprocess_data = PythonOperator(
    task_id='preprocess_data',
    python_callable=preprocess_data_task,
    provide_context=True,
    dag=dag,
)

generate_features = PythonOperator(
    task_id='generate_features',
    python_callable=generate_features_task,
    provide_context=True,
    dag=dag,
)

compute_statistics = PythonOperator(
    task_id='compute_statistics',
    python_callable=compute_statistics_task,
    provide_context=True,
    dag=dag,
)

dvc_push = PythonOperator(
    task_id='dvc_push',
    python_callable=dvc_push_task,
    provide_context=True,
    dag=dag,
)


# Define task dependencies
scrape_data >> preprocess_data >> generate_features >> compute_statistics >> dvc_push


# Task documentation
scrape_data.doc_md = """
## Scrape Data Task
Collects tech product listings from GitHub API.
- Target: 300+ products
- Rate limiting: 1.2s between requests
- Retry logic: 3 attempts with exponential backoff
"""

preprocess_data.doc_md = """
## Preprocess Data Task
Cleans and normalizes text data.
Steps:
- Unicode normalization
- HTML removal
- URL removal
- Lowercasing
- Tokenization
- Stopword removal
- Lemmatization
- Token filtering
"""

generate_features.doc_md = """
## Generate Features Task
Creates NLP representations.
Outputs:
- Vocabulary (JSON)
- Bag-of-Words matrix (NumPy)
- One-Hot encoding sample
- N-gram frequency distributions
"""

compute_statistics.doc_md = """
## Compute Statistics Task
Generates linguistic intelligence report.
Includes:
- Top unigrams and bigrams
- Category/tag analysis
- Duplicate detection (edit distance)
- Language model perplexity
"""

dvc_push.doc_md = """
## DVC Push Task
Versions datasets and pushes to remote storage.
Tracks:
- Raw data
- Processed data
- Feature representations
"""
