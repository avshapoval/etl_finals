-- БД, юзер и гранты
CREATE DATABASE ${POSTGRESQL_APP_DB};
CREATE USER ${POSTGRESQL_APP_USER} WITH PASSWORD '${POSTGRESQL_APP_PASSWORD}';
GRANT ALL PRIVILEGES ON DATABASE ${POSTGRESQL_APP_DB} TO ${POSTGRESQL_APP_USER};

-- Подключение к БД
\c ${POSTGRESQL_APP_DB}

-- Создание схемы, изменение дефолтной схемы и гранты
-- Создание схем STG и CDM
CREATE SCHEMA IF NOT EXISTS ${POSTGRESQL_STG_SCHEMA} AUTHORIZATION ${POSTGRESQL_APP_USER};
CREATE SCHEMA IF NOT EXISTS ${POSTGRESQL_MARTS_SCHEMA} AUTHORIZATION ${POSTGRESQL_APP_USER};

ALTER DEFAULT PRIVILEGES IN SCHEMA ${POSTGRESQL_STG_SCHEMA} GRANT ALL PRIVILEGES ON TABLES TO ${POSTGRESQL_APP_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA ${POSTGRESQL_STG_SCHEMA} GRANT USAGE ON SEQUENCES TO ${POSTGRESQL_APP_USER};

ALTER DEFAULT PRIVILEGES IN SCHEMA ${POSTGRESQL_MARTS_SCHEMA} GRANT ALL PRIVILEGES ON TABLES TO ${POSTGRESQL_APP_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA ${POSTGRESQL_MARTS_SCHEMA} GRANT USAGE ON SEQUENCES TO ${POSTGRESQL_APP_USER};

ALTER ROLE ${POSTGRESQL_APP_USER} SET search_path TO stg, cdm, public;

-- STG
SET search_path TO stg;

CREATE TABLE IF NOT EXISTS user_sessions (
    session_id TEXT PRIMARY KEY,
    user_id INT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    pages_visited JSONB,
    device JSONB,
    actions JSONB
);

CREATE TABLE IF NOT EXISTS product_price_history (
    product_id INT PRIMARY KEY,
    price_changes JSONB,
    current_price NUMERIC(10,2),
    currency VARCHAR(3)
);

CREATE TABLE IF NOT EXISTS event_logs (
    event_id TEXT PRIMARY KEY,
    timestamp TIMESTAMP,
    event_type TEXT,
    details JSONB
);

CREATE TABLE IF NOT EXISTS support_tickets (
    ticket_id TEXT PRIMARY KEY,
    user_id INT,
    status TEXT,
    issue_type TEXT,
    messages JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_recommendations (
    user_id INT PRIMARY KEY,
    recommended_products JSONB,
    last_updated TIMESTAMP
);

CREATE TABLE IF NOT EXISTS moderation_queue (
    review_id TEXT PRIMARY KEY,
    user_id INT,
    product_id INT,
    review_text TEXT,
    rating INT,
    moderation_status TEXT,
    flags JSONB,
    submitted_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS search_queries (
    query_id TEXT PRIMARY KEY,
    user_id INT,
    query_text TEXT,
    timestamp TIMESTAMP,
    filters JSONB,
    results_count INT
);

-- CDM
SET search_path TO cdm;

-- Витрина с агрегатами сессий пользователей в разбивке по дням и типам устройств
CREATE MATERIALIZED VIEW user_session_analysis AS
SELECT 
    DATE_TRUNC('day', start_time) AS session_date,
    COUNT(DISTINCT session_id) AS total_sessions,
    AVG(EXTRACT(EPOCH FROM (end_time - start_time))::INT) AS avg_duration_sec,
    (SELECT COUNT(*) FROM jsonb_array_elements(pages_visited)) AS avg_pages_per_session,
    device->>'type' AS device_type
FROM stg.user_sessions
GROUP BY session_date, device_type;

-- Витрина с динамикой цен товаров
CREATE MATERIALIZED VIEW product_price_dynamics AS
SELECT
    product_id,
    current_price,
    (
        SELECT 
            MAX((value->>'changed_at')::TIMESTAMP) 
        FROM jsonb_array_elements(price_changes)
    ) AS last_change_date,
    (
        SELECT 
            AVG((value->>'price')::NUMERIC) 
        FROM jsonb_array_elements(price_changes)
    ) AS historical_avg_price
FROM stg.product_price_history;

-- Витрина со статистикой модерации
CREATE MATERIALIZED VIEW moderation_stats AS
SELECT
    DATE_TRUNC('week', submitted_at) AS week_start,
    product_id,
    COUNT(*) FILTER (WHERE moderation_status = 'pending') AS pending_reviews,
    COUNT(*) FILTER (WHERE moderation_status = 'approved') AS approved_reviews,
    COUNT(*) FILTER (WHERE jsonb_array_length(flags) > 0) AS flagged_reviews
FROM stg.moderation_queue
GROUP BY week_start, product_id;