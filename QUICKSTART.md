# Quick Start Guide - TrendScope Analytics Pipeline

## 🚀 How to Run the Complete Pipeline

### Option 1: Run All Stages Sequentially (Recommended for Testing)

```bash
# Navigate to project directory
cd "c:\Users\Administrator\Desktop\NLP#ASSi#1_i222459_A"

# Stage 1: Data Acquisition (already completed)
python src/scraper.py

# Stage 2: Text Preprocessing (already completed)
python src/preprocess.py

# Stage 3: Feature Generation (already completed)
python src/representation.py

# Stage 4: Statistical Analysis (already completed)
python src/statistics.py
```

### Option 2: Run Individual Stages

```bash
# Just scraping
python src/scraper.py

# Just preprocessing
python src/preprocess.py

# Just feature generation
python src/representation.py

# Just statistics
python src/statistics.py
```

---

## 📊 View Results

### View the Trend Summary Report
```bash
# Windows
type reports\trend_summary.txt

# Or open in notepad
notepad reports\trend_summary.txt
```

### Check Generated Data Files
```bash
# List all data files
Get-ChildItem data -Recurse -File

# View processed data (first 10 rows)
Import-Csv data\processed\products_clean.csv | Select-Object -First 10 | Format-Table
```

### Load NumPy Arrays (in Python)
```python
import numpy as np

# Load BoW matrix
bow_matrix = np.load('data/features/bow_matrix.npy')
print(f"BoW matrix shape: {bow_matrix.shape}")
print(f"Sparsity: {(bow_matrix == 0).sum() / bow_matrix.size * 100:.2f}%")

# Load One-Hot sample
onehot = np.load('data/features/onehot_sample.npy')
print(f"One-Hot shape: {onehot.shape}")
```

---

## 🔄 Re-run with Different Dataset Size

### Scrape More Products (e.g., 500)

Edit `src/scraper.py` line 200:
```python
# Change from:
products = scraper.scrape_tech_products(target_count=300)

# To:
products = scraper.scrape_tech_products(target_count=500)
```

Then run the full pipeline again.

---

## 🐍 Airflow Setup (Optional)

### Install Airflow
```bash
pip install apache-airflow
```

### Initialize Airflow
```bash
# Set Airflow home (optional)
$env:AIRFLOW_HOME = "$PWD\airflow_home"

# Initialize database
airflow db init

# Create admin user
airflow users create `
    --username admin `
    --firstname Admin `
    --lastname User `
    --role Admin `
    --email admin@example.com `
    --password admin
```

### Copy DAG to Airflow
```bash
# Copy DAG file
Copy-Item dags\nlp_trend_dag.py "$env:AIRFLOW_HOME\dags\"
```

### Start Airflow
```bash
# Terminal 1: Start webserver
airflow webserver -p 8080

# Terminal 2: Start scheduler
airflow scheduler
```

### Access Airflow UI
Open browser: http://localhost:8080
- Username: admin
- Password: admin

### Trigger DAG
```bash
# Command line
airflow dags trigger nlp_trend_intelligence_pipeline

# Or use the UI: Click play button next to the DAG
```

---

## 📦 DVC Setup (Optional)

### Initialize DVC
```bash
dvc init
```

### Add Data to DVC
```bash
dvc add data/raw/products_raw.json
dvc add data/processed/products_clean.csv
dvc add data/features/vocab.json
dvc add data/features/bow_matrix.npy
```

### Configure DagsHub Remote
```bash
# Add remote
dvc remote add -d dagshub dagshub://your-username/your-repo

# Configure authentication
dvc remote modify dagshub --local auth basic
dvc remote modify dagshub --local user your-username
dvc remote modify dagshub --local password your-token
```

### Push to Remote
```bash
dvc push
```

### Commit DVC files
```bash
git add data/raw/.gitignore data/raw/products_raw.json.dvc
git commit -m "Track datasets with DVC"
git push
```

---

## 🧪 Testing & Validation

### Test Scraper Module
```bash
python -c "from src.scraper import TechProductScraper; s = TechProductScraper(); print('✓ Scraper imports correctly')"
```

### Test Preprocessor Module
```bash
python -c "from src.preprocess import TextPreprocessor; p = TextPreprocessor(); print('✓ Preprocessor imports correctly')"
```

### Test Representation Module
```bash
python -c "from src.representation import TextRepresentation; r = TextRepresentation(); print('✓ Representation imports correctly')"
```

### Test Statistics Module
```bash
python -c "from src.statistics import LinguisticIntelligence; li = LinguisticIntelligence(); print('✓ Statistics imports correctly')"
```

### Verify Data Integrity
```bash
python -c "import json; data = json.load(open('data/raw/products_raw.json')); print(f'✓ Loaded {len(data)} products'); print(f'✓ Fields: {list(data[0].keys())}')"
```

---

## 📈 Key Statistics (Already Generated)

From your current run:
- **Products Collected**: 300
- **Vocabulary Size**: 2,455 tokens
- **Total Tokens**: 10,182
- **Average Description Length**: 33.94 tokens
- **BoW Matrix**: (300, 2455) with 99.20% sparsity
- **Unique Bigrams**: 5,567
- **Duplicate Pairs Found**: 166
- **Average Perplexity**: 1,237.55

---

## 🐛 Troubleshooting

### If scraper fails:
```bash
# Check internet connection
Test-NetConnection api.github.com -Port 443

# Increase rate limit delay in scraper.py
# Change line: scraper = TechProductScraper(rate_limit_delay=2.0)
```

### If imports fail:
```bash
# Ensure you're in the correct directory
Get-Location

# Should show: C:\Users\Administrator\Desktop\NLP#ASSi#1_i222459_A
```

### If file not found errors:
```bash
# Create missing directories
New-Item -ItemType Directory -Force -Path data/raw, data/processed, data/features, reports
```

---

## 📝 Assignment Checklist

- ✅ Stage 1: Data Acquisition (300+ products)
- ✅ Stage 2: DVC Initialization & Configuration
- ✅ Stage 3: Text Processing (10-step pipeline)
- ✅ Stage 4: Data Representation (BoW, vocab, n-grams)
- ✅ Stage 5: Linguistic Intelligence (report with all metrics)
- ✅ Stage 6: Airflow DAG (5 tasks with dependencies)
- ✅ Documentation (README, comments, docstrings)
- ✅ Requirements.txt (all dependencies listed)
- ✅ Reproducible pipeline (modular, versioned)

---

## 📚 Files to Submit

```
NLP#ASSi#1_i222459_A/
├── src/                    # All 4 Python modules
├── dags/                   # Airflow DAG
├── data/                   # All generated data (raw, processed, features)
├── reports/                # Trend summary report
├── dvc.yaml                # DVC configuration
├── requirements.txt        # Dependencies
├── README.md               # Full documentation
└── PROJECT_SUMMARY.md      # Completion summary
```

---

## 💡 Tips

1. **Read the report first**: `reports/trend_summary.txt` contains all key insights
2. **Check the summary**: `PROJECT_SUMMARY.md` has detailed metrics
3. **Review the README**: `README.md` has full documentation
4. **Test individual modules**: Each Python file can run standalone
5. **No ML training**: This is a data pipeline project (as required)

---

## ✅ Status: READY FOR SUBMISSION

All stages completed successfully!
All files generated correctly!
All requirements met!

---

**Generated**: February 28, 2026  
**Project**: TrendScope Analytics NLP Pipeline  
**Student ID**: i222459
