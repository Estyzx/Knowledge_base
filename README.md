# 农业智库知识平台

## 项目概述
农业智库是一个专注于农业知识管理与共享的Web平台，重点围绕农业种植领域，为农民、研究人员和爱好者提供全面的种植知识、病虫害防治、土壤管理等专业信息。

## 功能特点

### 核心功能
- **品种库管理**：收录各类农业品种，详细记录其特性、生长条件和果实特征
- **种植技术**：提供从栽培到收获的全周期种植技术指导
- **病虫害防治**：识别常见病虫害，提供科学防治方法
- **土壤管理**：不同土壤类型的特性介绍、适宜作物和改良建议

### 技术特点
- 响应式设计，适配各种设备屏幕尺寸
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
- jQuery
- HTML5/CSS3
- JavaScript
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

## 使用指南

### 内容管理
1. 登录管理后台，使用超级用户账号
2. 添加、编辑各类内容(品种、种植技术、病虫害、土壤类型)
3. 审核用户提交的内容

### 内容浏览
1. 访问网站首页，查看分类信息
2. 使用搜索功能查找特定内容
3. 查看详细内容页面，获取完整信息

## 贡献指南
我们欢迎各种形式的贡献，包括但不限于：
- 提交新的内容条目
- 改进现有内容
- 修复错误
- 改进用户界面和用户体验

### 贡献流程
1. Fork 项目仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证
此项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式
- 项目维护者: [维护者姓名](mailto:contact@nongye.com)
- 项目网站: [www.nongye.com](http://www.nongye.com)


## 致谢
感谢所有为此项目做出贡献的人！
