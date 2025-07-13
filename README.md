# Shipping a Data Product From Raw Telegram Data to an Analytical API

## Project Overview

This repository contains an end-to-end data pipeline built for **Kara Solutions**. The primary goal is to process raw data scraped from public Telegram channels related to Ethiopian medical businesses and transform it into a clean, structured, and queryable format.

The project addresses key business questions such as identifying top medical products, tracking price variations, and analyzing channel activity trends. This is achieved by implementing a modern **ELT (Extract, Load, Transform)** framework that converts unstructured Telegram data into a dimensional star schema, ready for analysis.

The pipeline leverages a modern data stack:
- **Docker** for running a reproducible PostgreSQL database instance.
- **Telethon** for scraping raw message and image data from Telegram.
- **PostgreSQL** as a robust data warehouse.
- **dbt (Data Build Tool)** for reliable, modular, and test-driven data transformation.

This README provides a comprehensive guide to setting up the environment, understanding the project structure, and running the data pipeline from your local machine.

## Table of Contents
1.  [Project Structure](#project-structure)
2.  [Technical Stack](#technical-stack)
3.  [Setup and Installation (Local)](#setup-and-installation-local)
4.  [Running the Pipeline (Local)](#running-the-pipeline-local)
5.  [Pipeline Stage Details](#pipeline-stage-details)
    - [Task 1: Data Scraping & Collection](#task-1-data-scraping--collection-extract--load)
    - [Task 2: Data Transformation & Modeling](#task-2-data-modeling-and-transformation-transform)
6.  [Data Warehouse Schema](#data-warehouse-schema)

---
## Project Structure

The project follows a modular structure to ensure clarity and maintainability.


ethiopian-medical-analytics/
├── data/
│   └── raw/
│       ├── images/                     # Stores downloaded images by date and channel
│       └── telegram_messages/          # Stores raw JSONL messages by date and channel
├── src/
│   ├── load_raw_data.py                # Script to load raw JSONL into PostgreSQL
│   └── telegram_scraper.py             # Script to scrape data from Telegram channels
├── telegram_analytics/                 # The dbt project for data transformation
│   ├── models/
│   │   ├── staging/                    # Staging models for cleaning and casting
│   │   │   ├── stg_telegram_messages.sql
│   │   │   └── sources.yml
│   │   └── marts/                      # Final dimensional and fact tables
│   │       ├── dim_channels.sql
│   │       ├── dim_dates.sql
│   │       └── fct_messages.sql
│   ├── tests/
│   │   └── generic/                    # Custom data tests
│   │       └── assert_positive_value.sql
│   └── dbt_project.yml
├── .env.example                        # Template for environment variables
├── .gitignore                          # Ensures secrets and local artifacts are not committed
├── docker-compose.yml                  # Defines and configures the PostgreSQL service
└── requirements.txt                    # Lists all Python dependencies

---
## Technical Stack

| Component      | Technology                                    | Purpose                                                                                |
| :------------- | :-------------------------------------------- | :------------------------------------------------------------------------------------- |
| **Database** | **Docker & PostgreSQL** | To run a consistent, containerized database instance.                                  |
| **Scraping** | **Python & Telethon** | To extract messages and images from public Telegram channels.                          |
| **Data Lake** | **Local File System (JSONL)** | To store raw, unaltered data in a partitioned directory structure.                     |
| **Transform** | **dbt (Data Build Tool)** | To clean, model, and test the data inside the warehouse, creating a reliable star schema.|

---
## Setup and Installation (Local)

Follow these steps to set up the project environment on your local machine.

### 1. Prerequisites
- Docker & Docker Compose installed and running on your machine.
- Git installed on your machine.
- Python 3.9+ installed on your machine.
- A Telegram account with API credentials.

### 2. Clone the Repository
```bash
git clone https://github.com/matos-coder/Shipping-a-Data-Product-From-Raw-Telegram-Data-to-an-Analytical-API
cd Shipping a Data Product From Raw Telegram Data to an Analytical API

3. Configure Environment Variables
Create a .env file to store your secrets. A template is provided.

Create the .env file:

cp .env.example .env

Edit the .env file with your credentials. This file is included in .gitignore and will never be committed to version control.

# Telegram API credentials from my.telegram.org
telegram_app_id="YOUR_TELEGRAM_APP_ID"
telegram_api_hash="YOUR_TELEGRAM_API_HASH"

# PostgreSQL credentials (you can define these yourself)
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=telegram_db

4. Start the PostgreSQL Database
This command uses Docker to start the PostgreSQL database container in the background. Your local Python scripts will connect to this database.

docker-compose up -d db

Note: We are only starting the db service defined in docker-compose.yml.

5. Set Up a Local Python Environment
Create and activate a virtual environment to manage project dependencies locally.

For Windows:

python -m venv .venv
.venv\Scripts\activate

For macOS/Linux:

python3 -m venv .venv
source .venv/bin/activate

6. Install Dependencies
Install all required Python libraries into your virtual environment.

pip install -r requirements.txt

Running the Pipeline (Local)
The pipeline is executed in three main steps from your local terminal.

Step 1: Scrape Raw Data
Ensure your virtual environment is activated. This script connects to Telegram, scrapes data, and populates the data/raw directory.

python src/telegram_scraper.py

Step 2: Load Raw Data into the Warehouse
This script loads the raw JSONL files from the data lake into the PostgreSQL database running in Docker.

python src/load_raw_data.py

Step 3: Transform Data with dbt
These commands navigate into the dbt project directory and execute the transformation and testing logic.

# Enter the dbt project directory
cd telegram_analytics

# Run all transformation models (staging -> marts)
dbt run

# Run all data quality tests
dbt test

After these steps, your PostgreSQL data warehouse will contain the clean, modeled data.

Pipeline Stage Details
Task 1: Data Scraping & Collection (Extract & Load)
Objective: To extract raw data from Telegram and store it in a structured data lake.

Implementation: The src/telegram_scraper.py script uses the Telethon library to connect to the Telegram API and download messages and images.

Data Lake Structure: Raw data is stored in a partitioned directory structure data/raw/telegram_messages/YYYY-MM-DD/channel_name.jsonl to facilitate incremental processing. This ensures the raw data remains the unaltered source of truth.

Logging & Error Handling: The script implements robust logging to track which channels and dates have been processed and to capture any API errors or rate-limiting issues, ensuring reliable execution.

Task 2: Data Modeling and Transformation (Transform)
Objective: To transform the raw JSON data into a clean, tested, and query-optimized star schema using dbt.

Staging Models: Models in models/staging perform the initial cleaning. They select fields from the raw JSONB data, cast data types correctly, and rename columns for clarity.

Data Mart Models: Models in models/marts build the final analytical tables by joining staging models. This creates a dimensional star schema optimized for analysis.

Data Testing: The project uses dbt's built-in tests (unique, not_null) to validate primary keys and a custom test (assert_positive_value) to enforce business rules, ensuring data integrity and trust.

Data Warehouse Schema
The final data warehouse is designed as a Star Schema to enable efficient analytical queries. This design separates quantitative data (facts) from descriptive attributes (dimensions).

fct_messages: The central fact table, with one row per message. It contains foreign keys to the dimension tables and key metrics like view_count and message_length.

dim_channels: A dimension table holding information about each Telegram channel.

dim_dates: A dimension table for powerful time-based analysis, allowing grouping by day, week, month, etc.