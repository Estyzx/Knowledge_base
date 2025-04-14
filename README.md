# 农业智库知识平台

## 项目概述
农业智库是一个专注于农业知识管理与共享的Web平台，重点围绕农业种植领域，为农民、研究人员和爱好者提供全面的种植知识、病虫害防治、土壤管理等专业信息。

## 功能特点

### 技术特点
- 响应式设计，适配各种设备屏幕尺寸
  - 使用Bootstrap栅格系统进行布局
  - 移动优先设计理念
  - 媒体查询适配不同断点
  - 弹性图片和视频组件
- 优化的页面加载速度，采用延迟加载和缓存技术
- 专业内容审核流程，确保知识的准确性
- 用户交互友好的界面设计

## 技术架构

### 后端技术
- Django框架
- PostgreSQL/MySQL数据库
- Django ORM

### 前端技术
- Bootstrap 5 框架
  - 响应式栅格系统
  - 内置响应式组件和工具类
- jQuery
- HTML5/CSS3
  - 弹性盒布局(Flexbox)
  - CSS网格布局(Grid)
  - 视口相对单位(vw, vh, rem)
- JavaScript
  - 媒体查询监听
  - 动态内容加载
- SweetAlert2 (美化的提示框)
- FontAwesome 图标


## 项目结构
```
Knowledge_base/
├── article/                 # 文章系统应用
├── expert_qa/               # 专家问答系统
├── gannan_orange/           # 农业核心应用
│   ├── migrations/          # 数据库迁移文件
│   ├── templates/           # 模板文件
│   │   └── gannan_orange/   # 应用专用模板
│   ├── admin.py             # 管理后台配置
│   ├── models.py            # 数据模型定义
│   ├── views.py             # 视图处理函数
│   ├── urls.py              # URL路由配置
│   └── forms.py             # 表单定义
├── static/                  # 静态资源
│   ├── css/                 # 样式表
│   ├── js/                  # JavaScript文件
│   └── img/                 # 图片资源
├── templates/               # 全局模板
│   └── base.html            # 基础模板
├── media/                   # 用户上传的媒体文件
├── Knowledge_base/          # 项目配置目录
│   ├── settings.py          # 项目设置
│   ├── urls.py              # 主URL配置
│   └── wsgi.py              # WSGI配置
└── manage.py                # Django命令行工具
```

## 安装与部署

### 环境要求
- Python 3.8+
- Django 3.2+
- Node.js (用于前端资源构建，可选)

### 安装步骤
1. 克隆仓库
   ```bash
   git clone https://github.com/yourusername/Knowledge_base.git
   cd Knowledge_base
   ```

2. 创建并激活虚拟环境
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

4. 数据库迁移
   ```bash
   python manage.py migrate
   ```

5. 创建超级用户
   ```bash
   python manage.py createsuperuser
   ```

6. 运行开发服务器
   ```bash
   python manage.py runserver
   ```

7. 访问网站
   - 网站前台: http://127.0.0.1:8000/
   - 管理后台: http://127.0.0.1:8000/admin/

