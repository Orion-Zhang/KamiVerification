# CardVerification 项目部署脚本 (PowerShell)
# 使用方法: .\deploy.ps1 [dev|prod]

param(
    [Parameter(Position=0)]
    [ValidateSet("dev", "prod")]
    [string]$Environment = "dev"
)

# 颜色函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Log-Info {
    param([string]$Message)
    Write-ColorOutput "[INFO] $Message" "Blue"
}

function Log-Success {
    param([string]$Message)
    Write-ColorOutput "[SUCCESS] $Message" "Green"
}

function Log-Warning {
    param([string]$Message)
    Write-ColorOutput "[WARNING] $Message" "Yellow"
}

function Log-Error {
    param([string]$Message)
    Write-ColorOutput "[ERROR] $Message" "Red"
}

# 检查部署要求
function Test-Requirements {
    Log-Info "检查部署要求..."
    
    # 检查 Docker
    try {
        docker --version | Out-Null
    }
    catch {
        Log-Error "Docker 未安装或未启动"
        exit 1
    }
    
    # 检查 Docker Compose
    try {
        docker-compose --version | Out-Null
    }
    catch {
        Log-Error "Docker Compose 未安装"
        exit 1
    }
    
    # 检查环境文件
    if ($Environment -eq "prod") {
        if (-not (Test-Path ".env.production")) {
            Log-Error "生产环境配置文件 .env.production 不存在"
            Log-Info "请复制 .env.production.example 为 .env.production 并配置相应参数"
            exit 1
        }
    }
    
    Log-Success "部署要求检查通过"
}

# 创建必要的目录
function New-Directories {
    Log-Info "创建必要的目录..."
    
    $directories = @("logs", "media", "backups")
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    Log-Success "目录创建完成"
}

# 部署服务
function Start-Services {
    Log-Info "构建和启动服务..."
    
    try {
        if ($Environment -eq "prod") {
            Log-Info "使用生产环境配置部署..."
            docker-compose -f docker-compose.prod.yml down
            docker-compose -f docker-compose.prod.yml build --no-cache
            docker-compose -f docker-compose.prod.yml up -d
        }
        else {
            Log-Info "使用开发环境配置部署..."
            docker-compose down
            docker-compose build --no-cache
            docker-compose up -d
        }
        
        Log-Success "服务启动完成"
    }
    catch {
        Log-Error "服务启动失败: $_"
        exit 1
    }
}

# 等待服务就绪
function Wait-ForServices {
    Log-Info "等待服务就绪..."
    
    Log-Info "等待数据库服务..."
    Start-Sleep -Seconds 10
    
    Log-Info "等待应用服务..."
    Start-Sleep -Seconds 5
    
    Log-Success "服务就绪"
}

# 运行数据库迁移
function Invoke-Migrations {
    Log-Info "运行数据库迁移..."
    
    try {
        if ($Environment -eq "prod") {
            docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
        }
        else {
            docker-compose exec web python manage.py migrate
        }
        
        Log-Success "数据库迁移完成"
    }
    catch {
        Log-Error "数据库迁移失败: $_"
    }
}

# 收集静态文件
function Invoke-CollectStatic {
    Log-Info "收集静态文件..."
    
    try {
        if ($Environment -eq "prod") {
            docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
        }
        else {
            docker-compose exec web python manage.py collectstatic --noinput
        }
        
        Log-Success "静态文件收集完成"
    }
    catch {
        Log-Error "静态文件收集失败: $_"
    }
}

# 创建超级用户
function New-SuperUser {
    if ($Environment -eq "dev") {
        Log-Info "创建超级用户 (开发环境)..."
        Log-Warning "请按提示输入超级用户信息"
        docker-compose exec web python manage.py createsuperuser
    }
}

# 显示部署信息
function Show-DeploymentInfo {
    Log-Success "部署完成！"
    Write-Host ""
    Log-Info "服务访问地址:"
    
    if ($Environment -eq "prod") {
        Write-Host "  - 应用地址: https://yourdomain.com"
        Write-Host "  - 管理后台: https://yourdomain.com/admin/"
        Write-Host "  - API文档: https://yourdomain.com/swagger/"
    }
    else {
        Write-Host "  - 应用地址: http://localhost"
        Write-Host "  - 管理后台: http://localhost/admin/"
        Write-Host "  - API文档: http://localhost/swagger/"
        Write-Host "  - 直接访问: http://localhost:8000"
    }
    
    Write-Host ""
    Log-Info "常用命令:"
    Write-Host "  - 查看日志: docker-compose logs -f"
    Write-Host "  - 停止服务: docker-compose down"
    Write-Host "  - 重启服务: docker-compose restart"
    Write-Host "  - 进入容器: docker-compose exec web bash"
}

# 主函数
function Main {
    Log-Info "开始部署 CardVerification 项目 - 环境: $Environment"
    
    Test-Requirements
    New-Directories
    Start-Services
    Wait-ForServices
    Invoke-Migrations
    Invoke-CollectStatic
    New-SuperUser
    Show-DeploymentInfo
}

# 执行主函数
Main
