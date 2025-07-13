SELECT
    CAST((raw_message_data ->> 'id') AS BIGINT) AS message_id,
    CAST((raw_message_data -> 'peer_id' ->> 'channel_id') AS BIGINT) AS channel_id,
    raw_message_data ->> 'message' AS message_text,
    CAST((raw_message_data ->> 'date') AS TIMESTAMPTZ) AS post_date,
    CAST((raw_message_data ->> 'views') AS INTEGER) AS view_count,
    (raw_message_data -> 'photo') IS NOT NULL AS has_image

FROM
    {{ source('raw_telegram', 'messages') }}
