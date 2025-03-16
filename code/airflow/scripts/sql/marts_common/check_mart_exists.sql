SELECT EXISTS (
    SELECT 1 FROM pg_matviews 
    WHERE matviewname = '{{params.mat_view_name}}' AND schemaname = '{{params.marts_schema}}'
) 