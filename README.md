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

## 技术方案

### 系统架构设计
#### 分层架构
- **表示层**：基于Bootstrap和Django模板系统，提供响应式用户界面
- **业务逻辑层**：使用Django视图和服务组件处理业务逻辑
- **数据访问层**：通过Django ORM提供统一的数据访问接口
- **基础设施层**：包含缓存、日志、消息队列等基础服务

#### 微服务考量
- 初期采用单体架构，便于快速开发和部署
- 预留后期微服务拆分的接口设计和数据隔离
- API层设计采用REST风格，便于未来服务拆分

### 数据库设计
#### 核心数据模型
- **品种管理**：存储作物品种信息、特性和关联图片
- **种植技术**：包含技术指南、步骤和关联作物品种
- **病虫害防治**：记录病虫害信息、症状特征和防治方法
- **土壤类型**：管理不同土壤特性和适宜作物
- **用户与权限**：基于Django认证系统，扩展用户角色和权限控制

#### 性能优化策略
- 合理索引设计，优化常用查询字段
- 大文本字段使用专用索引(如PostgreSQL的GIN索引)
- 采用数据分区策略，处理时间序列数据
- 定期数据库维护计划(VACUUM、ANALYZE)

### 前端实现策略
#### UI/UX设计原则
- 移动优先的响应式设计，适配多种设备尺寸
- 简洁明了的用户界面，减少认知负担
- 关注易用性和无障碍性，支持多种操作方式

#### 前端性能优化
- 资源合并与压缩(CSS/JS打包)
- 图片懒加载和WebP格式优化
- 关键CSS内联，非关键资源异步加载
- 使用Service Worker实现离线缓存
- 前端缓存策略优化(localStorage, sessionStorage)

### 系统安全
#### 安全措施
- 数据输入验证和消毒，防止XSS攻击
- CSRF防护，所有表单添加CSRF令牌
- SQL注入防护，使用ORM参数化查询
- 密码安全存储，基于PBKDF2算法加密
- 基于角色的访问控制(RBAC)

#### 数据保护
- 敏感数据加密存储
- 完整的数据备份和恢复方案
- 数据访问审计日志

### 扩展性设计
#### 可扩展点
- 插件化内容系统，支持新知识类型扩展
- 事件驱动架构，关键操作发布事件供订阅者消费
- 可配置化的工作流程，支持内容审核流程定制

#### API设计
- RESTful API设计，便于第三方集成
- API版本控制，支持平滑升级
- 完善的API文档和SDK示例

### 部署与运维
#### 部署方案
- Docker容器化部署，保证环境一致性
- Nginx + Gunicorn生产环境部署
- 媒体文件对象存储分离(可选S3兼容存储)
- 数据库主从复制，提高读操作性能

#### 监控与运维
- 应用性能监控(New Relic/Prometheus)
- 错误跟踪与报警(Sentry)
- 日志集中管理(ELK Stack)
- 自动化部署流水线(CI/CD)

### 测试策略
- 单元测试(Django TestCase)
- 集成测试(API功能测试)
- UI自动化测试(Selenium)
- 性能负载测试(Locust)

### 迭代规划
#### 第一阶段(MVP)
- 核心内容管理系统
- 基础用户认证与权限
- 响应式前端设计

#### 第二阶段
- 高级搜索功能
- 用户互动功能(评论、收藏)
- 内容推荐系统

#### 第三阶段
- 专家问答系统
- 社区功能
- 移动应用开发

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
