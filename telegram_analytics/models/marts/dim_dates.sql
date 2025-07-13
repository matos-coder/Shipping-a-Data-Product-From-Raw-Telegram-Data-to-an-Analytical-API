SELECT
    date_dim_id,
    full_date,
    day_of_week_name,
    day_of_month,
    month_name,
    year
FROM
    -- This is a simplified example. In a real project, you'd use a more robust
    -- date dimension generator package or macro.
    (
        SELECT
            datum AS full_date,
            to_char(datum, 'YYYYMMDD')::integer AS date_dim_id,
            to_char(datum, 'Day') AS day_of_week_name,
            extract(DOY from datum) AS day_of_year,
            extract(DAY from datum) AS day_of_month,
            extract(MONTH from datum) AS month_number,
            to_char(datum, 'Month') AS month_name,
            extract(YEAR from datum) AS year
        FROM generate_series(
            '2020-01-01'::date,
            '2030-12-31'::date,
            '1 day'::interval
        ) datum
    ) AS date_data