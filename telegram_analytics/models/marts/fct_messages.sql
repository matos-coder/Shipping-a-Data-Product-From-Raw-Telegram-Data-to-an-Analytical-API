SELECT
    msg.message_id,
    msg.channel_id,
    to_char(msg.post_date, 'YYYYMMDD')::integer AS date_dim_id,
    msg.view_count,
    LENGTH(msg.message_text) AS message_length,
    msg.has_image
FROM
    {{ ref('stg_telegram_messages') }} msg
JOIN
    {{ ref('dim_channels') }} chans ON msg.channel_id = chans.channel_id