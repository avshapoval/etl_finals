CREATE MATERIALIZED VIEW {{params.marts_schema}}.{{params.mat_view_name}} AS
    SELECT
        product_id,
        current_price,
        MAX((value->>'changed_at')::TIMESTAMP) AS last_change_date,
        AVG((value->>'price')::NUMERIC) AS historical_avg_price
    FROM {{params.stg_schema}}.product_price_history,
    LATERAL jsonb_array_elements(price_changes) AS value
    GROUP BY product_id, current_price