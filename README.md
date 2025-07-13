# Shipping a Data Product From Raw Telegram Data to an Analytical API

## 🚀 Project Overview

This repository contains an end-to-end data pipeline built for **Kara Solutions**. The primary goal is to process raw data scraped from public Telegram channels related to Ethiopian medical businesses and transform it into a clean, structured, and queryable format.

The project addresses key business questions such as identifying top medical products, tracking price variations, and analyzing channel activity trends. This is achieved by implementing a modern **ELT (Extract, Load, Transform)** framework that converts unstructured Telegram data into a dimensional star schema, ready for analysis.

The pipeline leverages a modern data stack:

- **Docker** for running a reproducible PostgreSQL database instance.
- **Telethon** for scraping raw message and image data from Telegram.
- **PostgreSQL** as a robust data warehouse.
- **dbt (Data Build Tool)** for reliable, modular, and test-driven data transformation.

> ✅ This project strictly follows dbt best practices, including well-structured staging and mart models, documented sources, and custom data quality tests located at `telegram_analytics/tests/generic/assert_positive_value.sql`.

---

## 📁 Project Structure

ethiopian-medical-analytics/
├── data/
│ └── raw/
│ ├── images/ # Stores downloaded images by date and channel
│ └── telegram_messages/ # Stores raw JSONL messages by date and channel
├── src/
│ ├── load_raw_data.py # Script to load raw JSONL into PostgreSQL
│ └── telegram_scraper.py # Script to scrape data from Telegram channels
├── telegram_analytics/ # dbt project directory
│ ├── models/
│ │ ├── staging/
│ │ │ ├── stg_telegram_messages.sql
│ │ │ └── sources.yml
│ │ └── marts/
│ │ ├── dim_channels.sql
│ │ ├── dim_dates.sql
│ │ └── fct_messages.sql
│ ├── tests/
│ │ └── generic/
│ │ └── assert_positive_value.sql
│ └── dbt_project.yml
├── .env.example # Template for environment variables
├── .gitignore # Excludes secrets and local artifacts
├── docker-compose.yml # PostgreSQL service configuration
└── requirements.txt # Python dependencies

yaml
Copy
Edit

---

## 🛠 Technical Stack

| Component      | Technology                                    | Purpose                                                                                 |
|----------------|-----------------------------------------------|-----------------------------------------------------------------------------------------|
| **Database**   | **Docker + PostgreSQL**                       | Runs a consistent, containerized PostgreSQL instance                                   |
| **Scraping**   | **Python + Telethon**                         | Extracts messages and images from public Telegram channels                             |
| **Data Lake**  | **Local File System (JSONL)**                 | Stores raw, unaltered data in a partitioned directory structure                        |
| **Transform**  | **dbt (Data Build Tool)**                     | Cleans, models, and tests the data using SQL-based transformations and assertions      |

---

## ⚙️ Setup and Installation (Local)

### 1. Prerequisites

- Docker & Docker Compose
- Git
- Python 3.9+
- Telegram API credentials

### 2. Clone the Repository

```bash
git clone https://github.com/matos-coder/Shipping-a-Data-Product-From-Raw-Telegram-Data-to-an-Analytical-API
cd Shipping-a-Data-Product-From-Raw-Telegram-Data-to-an-Analytical-API
3. Configure Environment Variables
bash
Copy
Edit
cp .env.example .env
Edit .env and add your:

Telegram API credentials (telegram_app_id, telegram_api_hash)

PostgreSQL credentials (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB)

🔐 Your .env is already git-ignored for security.

4. Start PostgreSQL with Docker
bash
Copy
Edit
docker-compose up -d db
5. Set Up Local Python Environment
bash
Copy
Edit
python -m venv .venv
.venv\Scripts\activate  # On Windows
# OR
source .venv/bin/activate  # On macOS/Linux
6. Install Python Dependencies
bash
Copy
Edit
pip install -r requirements.txt
📡 Running the Pipeline (Local)
Step 1: Scrape Raw Data
bash
Copy
Edit
python src/telegram_scraper.py
Saves .jsonl messages and images under data/raw/YYYY-MM-DD/channel_name/.

Step 2: Load to PostgreSQL
bash
Copy
Edit
python src/load_raw_data.py
Loads all .jsonl into the raw_telegram.messages table as JSONB.

Step 3: Run dbt Transformations
bash
Copy
Edit
cd telegram_analytics
dbt run       # Transforms data (staging → marts)
dbt test      # Validates with built-in and custom tests
🧪 Custom test assert_positive_value.sql ensures numeric fields meet logical business rules.

🔄 Pipeline Stage Details
✅ Task 1: Data Scraping & Collection (Extract & Load)
Script: src/telegram_scraper.py

Output: data/raw/telegram_messages/YYYY-MM-DD/channel.jsonl

Logging: Robust logging with fallback for rate limits

Error Handling: Skips malformed entries, logs issues

Images: Saved under data/raw/images/

✅ Task 2: Data Modeling and Transformation (Transform)
Tool: dbt

Staging Models: Casts JSONB fields into typed SQL columns

Mart Models: Aggregates messages by date/channel

Tests: Includes dbt's built-in + assert_positive_value.sql

✅ Schema is organized into a star schema (facts & dimensions).

🧱 Data Warehouse Schema
Table	Description
fct_messages	Fact table for messages + metrics (views, text length)
dim_channels	Channel metadata
dim_dates	Calendar-based date dimension

📌 Final Notes
✅ dbt best practices followed: modular models, schema.yml, and tests

✅ Secrets handled via .env and excluded from git

✅ Reproducible setup with Docker

✅ Documented and clean project layout