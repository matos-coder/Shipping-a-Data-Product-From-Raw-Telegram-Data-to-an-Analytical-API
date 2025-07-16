# src/orchestration/pipeline.py
import subprocess
import sys
from pathlib import Path
from dagster import job, op

def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent

@op
def scrape_telegram_data_op():
    project_root = get_project_root()
    script_path = project_root / "src" / "telegram_scraper.py"
    
    print(f"Executing script: {script_path}")
    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Error output:", result.stderr)
        raise Exception(f"Telegram scraping script failed with return code {result.returncode}")
    
    print("Script output:", result.stdout)
    print("Telegram scraping completed successfully.")
    
    # Return a dummy value to pass to dependent ops
    return "scraped"

@op
def load_raw_to_postgres_op(_trigger):
    project_root = get_project_root()
    script_path = project_root / "src" / "load_raw_data.py"
    
    print(f"Executing script: {script_path}")
    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Error output:", result.stderr)
        raise Exception(f"Loading raw data script failed with return code {result.returncode}")
        
    print("Script output:", result.stdout)
    print("Loading raw data to PostgreSQL completed successfully.")
    return "loaded"

@op
def run_dbt_transformations_op(_trigger):
    project_root = get_project_root()
    dbt_project_dir = project_root / "telegram_analytics"
    
    print("Running dbt transformations...")
    dbt_run_result = subprocess.run(["dbt", "run"], cwd=str(dbt_project_dir), capture_output=True, text=True)
    if dbt_run_result.returncode != 0:
        print("dbt run error:", dbt_run_result.stderr)
        raise Exception("dbt run failed.")
    print("dbt run output:", dbt_run_result.stdout)
    
    dbt_test_result = subprocess.run(["dbt", "test"], cwd=str(dbt_project_dir), capture_output=True, text=True)
    if dbt_test_result.returncode != 0:
        print("dbt test error:", dbt_test_result.stderr)
        raise Exception("dbt test failed.")
    print("dbt test output:", dbt_test_result.stdout)

    print("dbt transformations completed successfully.")

@op
def run_yolo_enrichment_op(_trigger):
    project_root = get_project_root()
    script_path = project_root / "src" / "run_yolo_enrichment.py"
    
    print(f"Executing script: {script_path}")
    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Error output:", result.stderr)
        raise Exception(f"YOLO enrichment script failed with return code {result.returncode}")
        
    print("Script output:", result.stdout)
    print("YOLO enrichment completed successfully.")

@job
def telegram_analytics_job():
    scraped = scrape_telegram_data_op()
    
    loaded = load_raw_to_postgres_op(scraped)
    run_dbt_transformations_op(loaded)
    
    run_yolo_enrichment_op(scraped)
