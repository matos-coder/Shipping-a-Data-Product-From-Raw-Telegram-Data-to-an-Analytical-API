import textwrap

sql = textwrap.dedent("""
    SELECT
        (raw_message_data ->> 'id')::bigint AS message_id,
        (raw_message_data -> 'peer_id' ->> 'channel_id')::bigint AS channel_id,
        raw_message_data ->> 'message' AS message_text,
        (raw_message_data ->> 'date')::timestamptz AS post_date,
        (raw_message_data ->> 'views')::integer AS view_count,
        (raw_message_data -> 'photo') IS NOT NULL AS has_image
    FROM raw_telegram.messages
    LIMIT 10;
""")
