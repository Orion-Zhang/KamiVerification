-- PostgreSQL 初始化脚本
-- 为 CardVerification 项目创建数据库和用户

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- 设置时区
SET timezone = 'Asia/Shanghai';

-- 创建索引优化
-- 这些索引将在 Django 迁移后手动创建，这里只是示例

-- 性能优化设置
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_duration = on;
ALTER SYSTEM SET log_min_duration_statement = 1000; -- 记录超过1秒的查询

-- 连接池优化
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- 重新加载配置
SELECT pg_reload_conf();
