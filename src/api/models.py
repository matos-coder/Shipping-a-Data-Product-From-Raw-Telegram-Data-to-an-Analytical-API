from sqlalchemy import Column, Integer, String, BigInteger, Float, Boolean, DateTime
from .database import Base

# This file defines Python classes that map to your database tables.
# This is part of SQLAlchemy's Object-Relational Mapping (ORM).

class Message(Base):
    __tablename__ = "fct_messages"
    __table_args__ = {'schema': 'dbt_schema'} # Use the correct schema

    message_id = Column(BigInteger, primary_key=True, index=True)
    channel_id = Column(BigInteger)
    date_dim_id = Column(Integer)
    view_count = Column(Integer)
    message_length = Column(Integer)
    has_image = Column(Boolean)
    # Add message_text for querying even though it's not a direct column in the final fact table
    # We will select it from the staging table in the CRUD operation.
    message_text = Column(String) 

class ImageDetection(Base):
    __tablename__ = "fct_image_detections"
    __table_args__ = {'schema': 'dbt_schema'} # Use the correct schema

    image_detection_id = Column(String, primary_key=True, index=True)
    message_id = Column(BigInteger)
    detected_object_name = Column(String)
    confidence_score = Column(Float)
    bounding_box_xyxy = Column(String)