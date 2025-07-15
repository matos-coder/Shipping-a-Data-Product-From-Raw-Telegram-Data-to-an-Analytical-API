    -- models/marts/fct_image_detections.sql
    
    -- This model reads the data loaded by the 'dbt seed' command
    -- and creates a final, clean fact table for image detections.
    
    WITH source AS (
        -- The {{ ref() }} function points to the CSV seed file.
        -- dbt will treat 'image_detections' as a table in the database.
        SELECT * FROM {{ ref('image_detections') }}
    )
    
    SELECT
        -- Primary key for this table
        image_path || '-' || detected_object_class_id || '-' || bounding_box_xyxy AS image_detection_id,
    
        -- Foreign key to link back to the fct_messages table
        message_id::bigint,
    
        -- Details about the detection
        detected_object_name,
        confidence_score::float,
        bounding_box_xyxy
    
    FROM
        source
    