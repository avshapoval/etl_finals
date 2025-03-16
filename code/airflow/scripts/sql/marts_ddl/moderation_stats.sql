CREATE MATERIALIZED VIEW {{params.marts_schema}}.{{params.mat_view_name}} AS
    SELECT
        DATE_TRUNC('week', submitted_at) AS week_start,
        product_id,
        COUNT(*) FILTER (WHERE moderation_status = 'pending') AS pending_reviews,
        COUNT(*) FILTER (WHERE moderation_status = 'approved') AS approved_reviews,
        COUNT(*) FILTER (WHERE jsonb_array_length(flags) > 0) AS flagged_reviews
    FROM {{params.stg_schema}}.moderation_queue
    GROUP BY week_start, product_id