from dagster import Definitions
from src.orchestration.pipeline import telegram_analytics_job

defs = Definitions(
    jobs=[telegram_analytics_job]
)
