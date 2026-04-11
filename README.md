# 002_yalhardware

YAL Hardware 是一个前后端分离的硬件产品展示与下单项目，包含：

- `frontend/`：基于 Vue 3 + TypeScript + Vite 的商城前台与后台管理前端
- `backend/`：基于 Django + Django REST Framework 的 API 服务

项目覆盖了产品展示、分类浏览、购物车、订单、评论、内容管理和基础后台管理流程。

## 项目结构

```text
002_yalhardware/
├─ frontend/                  # Vue 3 前端
│  ├─ public/
│  ├─ src/
│  │  ├─ api/
│  │  ├─ components/
│  │  ├─ composables/
│  │  ├─ layouts/
│  │  ├─ router/
│  │  ├─ services/
│  │  ├─ stores/
│  │  ├─ types/
│  │  └─ views/
│  ├─ package.json
│  └─ vite.config.ts
├─ backend/                   # Django 后端
│  ├─ apps/
│  │  ├─ content/
│  │  ├─ inventory/
│  │  ├─ orders/
│  │  ├─ products/
│  │  ├─ reviews/
│  │  ├─ system/
│  │  └─ users/
│  ├─ config/
│  │  ├─ settings.py
│  │  ├─ urls.py
│  │  └─ wsgi.py
│  ├─ manage.py
│  └─ requirements.txt
└─ README.md
```

## 技术栈

### 前端

- Vue 3
- TypeScript
- Vite
- Vue Router
- Pinia
- Axios
- Element Plus
- Swiper
- Vue Easy Lightbox

### 后端

- Django 5
- Django REST Framework
- Simple JWT
- django-cors-headers
- SQLite（本地默认）
- PostgreSQL（生产环境，`DATABASE_URL`）
- Cloudinary / 本地文件存储

## 主要功能

- 首页内容展示与推荐位管理
- 产品分类、列表、详情页
- 款式选择、购物车、下单与支付流转
- 订单状态流转与订单详情
- 评论系统
- 后台产品、内容、订单、库存等管理

## 本地开发

### 1. 启动后端

进入后端目录：

```bash
cd backend
```

建议使用虚拟环境，然后安装依赖：

```bash
pip install -r requirements.txt
```

执行数据库迁移：

```bash
python manage.py migrate
```

启动开发服务：

```bash
python manage.py runserver
```

默认地址：

```text
http://127.0.0.1:8000
```

### 2. 启动前端

进入前端目录：

```bash
cd frontend
```

安装依赖：

```bash
npm install
```

启动开发服务：

```bash
npm run dev
```

默认地址：

```text
http://localhost:5173
```

## 前端环境变量

当前前端已使用的环境变量见 `frontend/.env` 和 `frontend/.env.production`：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_BYPASS_USER_AUTH=true
VITE_BYPASS_ADMIN_AUTH=true
```

生产环境示例：

```env
VITE_API_BASE_URL=https://yalhardware-backend.onrender.com
VITE_BYPASS_USER_AUTH=false
VITE_BYPASS_ADMIN_AUTH=false
```

说明：

- `VITE_API_BASE_URL`：前端请求的后端 API 根地址
- `VITE_BYPASS_USER_AUTH`：本地测试时是否跳过前台用户认证
- `VITE_BYPASS_ADMIN_AUTH`：本地测试时是否跳过后台认证

## 后端环境变量

后端配置主要在 `backend/config/settings.py`。当前代码支持以下关键环境变量：

```env
DJANGO_ENV=development
DJANGO_BYPASS_USER_AUTH=true
DJANGO_TEST_GUEST_EMAIL=guest@test.local
DJANGO_TEST_GUEST_USERNAME=guest@test.local
DATABASE_URL=
CLOUDINARY_URL=
```

说明：

- `DJANGO_ENV=production` 时会关闭 `DEBUG`
- `DATABASE_URL` 存在时使用 PostgreSQL，否则默认使用本地 SQLite
- `CLOUDINARY_URL` 存在时启用 Cloudinary 文件存储
- `DJANGO_BYPASS_USER_AUTH` 用于本地测试订单相关免登录流程

## 常用命令

### 前端

```bash
npm run dev
npm run build
npm run preview
npm run lint
npm run type-check
npm run test:unit
```

### 后端

```bash
python manage.py runserver
python manage.py migrate
python manage.py makemigrations
python manage.py createsuperuser
```

## 部署说明

### 前端

- 构建工具：Vite
- `package.json` 中包含 `deploy` 脚本
- 历史配置显示前端支持部署到 GitHub Pages

### 后端

- 生产环境支持 Render / Gunicorn
- 数据库支持 PostgreSQL
- 文件存储支持 Cloudinary

## 开发说明

- 前端和后端是独立目录，依赖、启动命令和部署方式互不共享
- 本地开发默认是前端 `5173` + 后端 `8000`
- 后端默认允许 `localhost:5173` 和局域网开发地址跨域
- 项目当前仓库中包含 `frontend/node_modules/`、`backend/venv/`、`backend/db.sqlite3` 等本地开发产物，提交前建议根据团队规范确认是否保留

## 许可证

MIT
