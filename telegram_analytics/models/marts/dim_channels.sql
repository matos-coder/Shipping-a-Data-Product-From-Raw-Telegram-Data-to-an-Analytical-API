SELECT
    DISTINCT channel_id,
    -- In a real project, you would join this with a table
    -- containing channel names scraped separately.
    'Channel ' || channel_id::text AS channel_name -- Placeholder name
FROM
    {{ ref('stg_telegram_messages') }}
WHERE
    channel_id IS NOT NULL