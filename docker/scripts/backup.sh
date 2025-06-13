#!/bin/bash

# ===== 数据库备份脚本 =====
# 用于定期备份PostgreSQL数据库

set -e

# 配置变量
BACKUP_DIR="/backup"
DB_NAME="${POSTGRES_DB:-cardverification}"
DB_USER="${POSTGRES_USER:-cardverification}"
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/cardverification_${TIMESTAMP}.sql"
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 创建备份目录
mkdir -p "$BACKUP_DIR"

log_info "开始数据库备份..."
log_info "数据库: $DB_NAME"
log_info "主机: $DB_HOST:$DB_PORT"
log_info "备份文件: $BACKUP_FILE"

# 执行备份
if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    --no-password --verbose --clean --no-acl --no-owner \
    --format=plain > "$BACKUP_FILE"; then
    
    log_success "数据库备份完成！"
    
    # 压缩备份文件
    if gzip "$BACKUP_FILE"; then
        BACKUP_FILE="${BACKUP_FILE}.gz"
        log_success "备份文件已压缩: $BACKUP_FILE"
    else
        log_warning "备份文件压缩失败，保留原文件"
    fi
    
    # 显示备份文件信息
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log_info "备份文件大小: $BACKUP_SIZE"
    
else
    log_error "数据库备份失败！"
    exit 1
fi

# 清理旧备份文件
log_info "清理 $RETENTION_DAYS 天前的备份文件..."
find "$BACKUP_DIR" -name "cardverification_*.sql*" -type f -mtime +$RETENTION_DAYS -delete
REMAINING_BACKUPS=$(find "$BACKUP_DIR" -name "cardverification_*.sql*" -type f | wc -l)
log_info "剩余备份文件数量: $REMAINING_BACKUPS"

log_success "备份任务完成！"
