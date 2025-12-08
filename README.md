# AutoDeployDocs - 自动化部署文档生成工具

## 简介
AutoDeployDocs 是一个旨在帮助开发和运维人员快速生成标准化部署文档的工具。它结合了现代化的 Web 界面和强大的文档生成引擎，让繁琐的文档编写工作变得简单高效。

通过可视化的配置管理和模板系统，用户可以定义部署步骤，并为每次发布创建具体的部署方案，最终一键导出 Word 格式的部署手册。

## 核心特性
- 🛠 **可视化配置**: 提供直观的界面编辑系统配置和参数。
- 📋 **方案管理**: 灵活创建、编辑和管理不同版本的部署方案。
- 📄 **模板引擎**: 基于 Word 模板 (`.docx`) 自动填充内容，支持复杂的格式保持。
- 🚀 **一键启动**: 内置自动化脚本，轻松启动整个应用。
- 📦 **静态部署**: 前端应用自动构建并由后端静态挂载，无需额外部署 Web 服务器。

## 技术栈
- **后端**: Python (FastAPI) - 提供高性能 API 和文档处理能力。
- **前端**: Vue 3 + Element Plus - 构建现代化的响应式用户界面。
- **文档处理**: python-docx - 用于生成和操作 Word 文档。

## 快速开始

### 1. 环境要求
请确保本地已安装以下环境：
- **Python**: 3.10 或更高版本
- **Node.js**: 16 或更高版本
- **Git**:用于版本控制（可选）

### 2. 初始化项目

首次使用前，请安装必要的依赖库。

**后端依赖:**
```bash
cd backend
pip install -r requirements.txt
```

**前端依赖:**
```bash
cd frontend
npm install
```

### 3. 启动应用

项目根目录下提供了便捷的一键启动脚本：

**Windows:**
直接双击运行 `start.bat` 或在命令行执行：
```bash
.\start.bat
```
*(脚本会自动重新构建前端资源并启动后端服务)*

启动成功后，请在浏览器访问：
👉 **http://localhost:8002**

### 4. 手动启动 (可选)
如果您希望分别控制前后端，也可以手动执行以下命令：

1. **构建前端:**
   ```bash
   cd frontend
   npm run build
   ```
   *构建产物将自动输出到 `backend/static` 目录。*

2. **启动后端:**
   ```bash
   cd backend
   python app.py
   ```

## 目录结构说明
```
AutoDeployDocs/
├── backend/            # Python 后端代码
│   ├── app.py          # 主应用程序入口
│   ├── core/           # 核心逻辑 (文档生成器等)
│   ├── routers/        # API 路由定义
│   └── static/         # 前端静态资源挂载点
├── frontend/           # Vue 3 前端代码
├── config/             # 配置文件存储
├── templates/          # Word 文档模板
├── init_templates.py   # 模板初始化脚本
└── start.bat           # 一键启动脚本
```

## 注意事项
- 默认服务监听端口为 **8002**。如需修改，请编辑 `backend/app.py` 中的 `uvicorn.run` 参数。
- 前端 API 请求已配置为相对路径，便于静态挂载部署。
