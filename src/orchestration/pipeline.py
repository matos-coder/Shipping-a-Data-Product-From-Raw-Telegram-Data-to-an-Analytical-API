# src/orchestration/pipeline.py
import subprocess
import sys
from pathlib import Path
from dagster import job, op

# Helper function to get the project root directory
def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent

@op
def scrape_telegram_data_op():
    """
    Dagster op to run the Telegram scraping script.
    """
    project_root = get_project_root()
    script_path = project_root / "src" / "telegram_scraper.py"
    
    print(f"Executing script: {script_path}")
    # We run the script as a separate process to ensure it uses the project's environment
    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Error output:", result.stderr)
        raise Exception(f"Telegram scraping script failed with return code {result.returncode}")
    
    print("Script output:", result.stdout)
    print("Telegram scraping completed successfully.")

@op
def load_raw_to_postgres_op(context):
    """
    Dagster op to run the script that loads raw data into PostgreSQL.
    This op will run only after scrape_telegram_data_op succeeds.
    """
    project_root = get_project_root()
    script_path = project_root / "src" / "load_raw_data.py"
    
    print(f"Executing script: {script_path}")
    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Error output:", result.stderr)
        raise Exception(f"Loading raw data script failed with return code {result.returncode}")
        
    print("Script output:", result.stdout)
    print("Loading raw data to PostgreSQL completed successfully.")

@op
def run_dbt_transformations_op(context):
    """
    Dagster op to run dbt transformations.
    This op will run only after load_raw_to_postgres_op succeeds.
    """
    project_root = get_project_root()
    dbt_project_dir = project_root / "telegram_analytics"
    
    print("Running dbt transformations...")
    # Run dbt run
    dbt_run_result = subprocess.run(["dbt", "run"], cwd=str(dbt_project_dir), capture_output=True, text=True)
    if dbt_run_result.returncode != 0:
        print("dbt run error:", dbt_run_result.stderr)
        raise Exception("dbt run failed.")
    print("dbt run output:", dbt_run_result.stdout)
    print("dbt run completed successfully.")
    
    # Run dbt test
    dbt_test_result = subprocess.run(["dbt", "test"], cwd=str(dbt_project_dir), capture_output=True, text=True)
    if dbt_test_result.returncode != 0:
        print("dbt test error:", dbt_test_result.stderr)
        raise Exception("dbt test failed.")
    print("dbt test output:", dbt_test_result.stdout)
    print("dbt test completed successfully.")
    
    print("dbt transformations completed successfully.")

@op
def run_yolo_enrichment_op(context):
    """
    Dagster op to run the YOLO enrichment script.
    This op will run only after scrape_telegram_data_op succeeds.
    """
    project_root = get_project_root()
    script_path = project_root / "src" / "run_yolo_enrichment.py"
    
    print(f"Executing script: {script_path}")
    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Error output:", result.stderr)
        raise Exception(f"YOLO enrichment script failed with return code {result.returncode}")
        
    print("Script output:", result.stdout)
    print("YOLO enrichment completed successfully.")

# Define the job by wiring the ops together
@job
def telegram_analytics_job():
    """
    The main job that orchestrates the entire ELT pipeline.
    """
    # Step 1: Scrape data
    scraped_data = scrape_telegram_data_op()
    
    # Step 2: Load and transform the main message data
    # The `start_after` parameter ensures this op waits for scraping to finish
    loaded_data = load_raw_to_postgres_op(start_after=scraped_data)
    run_dbt_transformations_op(start_after=loaded_data)
    
    # Step 3 (runs in parallel with Step 2): Enrich image data
    # This also depends on the initial scraping
    run_yolo_enrichment_op(start_after=scraped_data)
