
CREATE DATABASE IF NOT EXISTS trend_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE trend_db;

CREATE TABLE IF NOT EXISTS metrics_raw (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    tool_name VARCHAR(255) NOT NULL,
    platform VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DOUBLE,
    metric_text TEXT,
    retrieved_at DATETIME NOT NULL,
    source_url TEXT,
    extra_json JSON,
    UNIQUE KEY unique_snapshot (tool_name, platform, metric_name, retrieved_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS tools (
    tool_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    canonical_name VARCHAR(255) UNIQUE NOT NULL,
    aliases JSON,
    tags JSON,
    first_seen DATETIME,
    last_seen DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS metrics_daily (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    tool_id BIGINT NOT NULL,
    platform VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DOUBLE,
    metric_date DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tool_id) REFERENCES tools(tool_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS trend_scores (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    tool_id BIGINT NOT NULL,
    score_date DATE NOT NULL,
    trend_score DOUBLE,
    `rank` INT,
    components JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tool_id) REFERENCES tools(tool_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
