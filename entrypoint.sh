#!/bin/bash

# 收集静态文件
echo "收集静态文件..."
python manage.py collectstatic --noinput

# 执行数据库迁移
echo "执行数据库迁移..."
python manage.py migrate

# 创建超级用户（如果不存在）
echo "检查超级用户..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('超级用户已创建: admin/admin123')
else:
    print('超级用户已存在')
EOF

# 启动应用
echo "启动应用..."
exec "$@"
