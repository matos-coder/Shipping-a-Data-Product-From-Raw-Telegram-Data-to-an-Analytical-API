from sqlalchemy.orm import Session
from sqlalchemy import text


def search_messages_by_keyword(db: Session, keyword: str, limit: int = 100):
    """
    Searches for messages containing a specific keyword.
    NOTE: We join with the staging table to get the message_text.
    """
    query = text(f"""
        SELECT 
            fm.message_id, 
            stg.message_text,
            fm.view_count
        FROM dbt_schema.fct_messages AS fm
        JOIN dbt_schema.stg_telegram_messages AS stg ON fm.message_id = stg.message_id
        WHERE stg.message_text ILIKE :keyword
        LIMIT :limit
    """)
    result = db.execute(query, {"keyword": f"%{keyword}%", "limit": limit}).fetchall()
    return result

def get_channel_activity(db: Session, channel_name: str):
    """
    Gets the daily posting activity for a specific channel.
    """
    query = text(f"""
        SELECT 
            TO_CHAR(stg.post_date, 'YYYY-MM-DD') as post_date,
            COUNT(fm.message_id) as message_count
        FROM dbt_schema.fct_messages AS fm
        JOIN dbt_schema.dim_channels AS dc ON fm.channel_id = dc.channel_id
        JOIN dbt_schema.stg_telegram_messages AS stg ON fm.message_id = stg.message_id
        WHERE dc.channel_name = :channel_name
        GROUP BY 1
        ORDER BY 1 DESC;
    """)
    result = db.execute(query, {"channel_name": channel_name}).fetchall()
    return result

def get_top_detected_objects(db: Session, limit: int = 10):
    """
    Gets the top N most frequently detected objects from images.
    """
    query = text(f"""
        SELECT
            detected_object_name,
            COUNT(*) as mention_count
        FROM dbt_schema.fct_image_detections
        GROUP BY 1
        ORDER BY 2 DESC
        LIMIT :limit;
    """)
    result = db.execute(query, {"limit": limit}).fetchall()
    return result