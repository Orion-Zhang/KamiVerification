-- ===== PostgreSQL 初始化脚本 =====
-- 卡片验证系统数据库初始化

-- 设置数据库编码和排序规则
ALTER DATABASE cardverification SET timezone TO 'Asia/Shanghai';

-- 创建扩展（如果需要）
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 创建索引优化查询性能
-- 这些索引将在Django迁移后创建，此处仅作为参考

-- 用户相关索引
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_accounts_customuser_username ON accounts_customuser(username);
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_accounts_customuser_email ON accounts_customuser(email);
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_accounts_customuser_is_active ON accounts_customuser(is_active);

-- 卡片相关索引
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cards_card_key ON cards_card(key);
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cards_card_status ON cards_card(status);
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cards_card_created_at ON cards_card(created_at);

-- API相关索引
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_apikey_key ON api_apikey(key);
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_apikey_is_active ON api_apikey(is_active);

-- 设置数据库参数优化
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_min_duration_statement = 1000;

-- 重新加载配置
SELECT pg_reload_conf();
