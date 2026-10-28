# 即墨区利晨针织厂官网 / Lichen Knitting Factory Website

即墨区利晨针织厂（青岛即墨）企业官网：面向国内外采购商展示自有车间、针织设备、三类针织面料与定制加工服务，引导客户通过电话 / 微信询价。

- **线上地址：<https://www.lichen-knitting.workers.dev>**
- 纯静态网站：无需后端、数据库或构建工具，上传即用
- 简体中文默认，支持切换商务英文（`?lang=en` 可直接打开英文版）
- 全部图片 / 视频本地化，不依赖任何外部 CDN

![首页截图](docs/screenshot-home.jpg)

---

## 技术栈

| 项目 | 说明 |
| --- | --- |
| 前端 | 原生 HTML5 + CSS3 + 原生 JavaScript（无框架、无构建步骤） |
| 国际化 | `data-zh` / `data-en` 属性驱动，`assets/site.js` 运行时切换并记忆选择 |
| SEO | 每页独立中英双语 title / description / keywords、Open Graph、Twitter Card、canonical、`sitemap.xml` |
| 结构化数据 | JSON-LD：`LocalBusiness`、`FAQPage`、`BreadcrumbList` |
| 托管 | Cloudflare Workers 静态资源托管（HTTPS + 全球 CDN，免费套餐） |

## 目录结构

```
├── lichen_knitting_website/     ← 网站本体（部署时上传这一层的内容）
│   ├── index.html               首页（简短首页 + 醒目联系条）
│   ├── about.html               关于我们（含车间实拍与视频）
│   ├── products.html            产品中心
│   ├── custom.html              定制服务（含常见问题）
│   ├── contact.html             联系我们（含询价整理表单）
│   ├── product-*.html           三个产品详情页
│   ├── 404.html
│   ├── assets/style.css         全站样式（分区注释、响应式）
│   ├── assets/site.js           语言切换 / 移动导航 / 表单整理 / 复制按钮
│   ├── assets/img/              工厂实拍照片、面料图、视频封面、图标
│   ├── assets/video/            工厂实拍视频（H.264）
│   ├── robots.txt / sitemap.xml / site.webmanifest
│   ├── CREDITS.md               图片与视频的来源与授权
│   └── README.md                站点详细说明
├── tools/                       构建与校验工具（不参与部署）
│   ├── gen_site.py              由同一份模板生成全部 9 个页面
│   ├── gen_assets.py            生成品牌图标 PNG
│   ├── check_site.py            静态自检（死链 / SEO / 空按钮 / 禁写内容）
│   └── set_domain.py            绑定域名后写入 canonical 并生成 sitemap
├── site.config.json             站点配置（当前生产域名）
└── docs/
    ├── 部署说明.md              本地预览、重新生成与部署步骤
    └── screenshot-home.jpg
```

## 本地预览

```bash
# 方式一：直接打开
#   Windows 下双击 lichen_knitting_website/preview-local.bat

# 方式二：任意静态服务器
cd lichen_knitting_website
python -m http.server 8000
# 浏览器访问 http://127.0.0.1:8000/index.html
```

英文版：`http://127.0.0.1:8000/index.html?lang=en`

## 重新生成与自检

```bash
python tools/gen_site.py      # 重新生成全部 HTML（页头/页脚/SEO 统一，避免各页不一致）
python tools/check_site.py    # 自检：死链、重复标题、空按钮、JSON-LD、禁用表述、视频编码
python tools/gen_assets.py    # 重新生成 PNG 图标
python tools/set_domain.py https://your-domain   # 绑定自有域名后更新 canonical / sitemap
```

> `gen_site.py` 会覆盖 `lichen_knitting_website/*.html`；只改个别文案时直接编辑 HTML 更简单。

## 设计上的几个要点

1. **简短首页 + 子页面跳转**：首页只保留首屏、联系条、产品类别、工厂视频和三个入口；设备清单、流程、常见问题都在各自子页面，靠顶部导航跳转，不做单页长滚动。
2. **联系方式在首屏下方**：电话 / 微信 / 完整地址 / 一键拨打 / 高德导航，无需滚动即可看到。
3. **询价表单不假装发送**：纯静态页面，表单只把填写内容整理成文本供复制，页面明确声明「不会自动发送」，不显示虚假成功状态。
4. **视频必须是 H.264**：手机常见的 H.265/HEVC 在多数浏览器无法播放，仓库中的视频已转码。`check_site.py` 会检测并报错。
5. **不编造经营数据**：不展示固定价格、起订量、交期、产能、设备数量、成立时间、资质与客户案例；这些按实际沟通确认。

## 素材授权

工厂照片与视频版权归即墨区利晨针织厂所有；三张产品面料图为 CC0（公共领域）素材。
详见 [CREDITS.md](lichen_knitting_website/CREDITS.md)。

## 说明

本站是第一阶段静态展示网站，不包含后端、数据库、登录或后台管理。若将来需要在线收集询价，
需另外实现服务端接口、数据存储、鉴权与防垃圾提交，不能用静态页面代替。