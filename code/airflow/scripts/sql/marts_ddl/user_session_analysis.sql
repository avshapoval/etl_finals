CREATE MATERIALIZED VIEW {{params.marts_schema}}.{{params.mat_view_name}} AS
    SELECT 
        DATE_TRUNC('day', start_time) AS session_date,
        COUNT(DISTINCT session_id) AS total_sessions,
        AVG(EXTRACT(EPOCH FROM (end_time - start_time))::INT) AS avg_duration_sec,
        AVG(jsonb_array_length(pages_visited)) AS avg_pages_per_session,
        (device->>'type')::VARCHAR AS device_type
    FROM {{params.stg_schema}}.user_sessions
    GROUP BY session_date, device_type