# 即墨区利晨针织厂官网（第二版 · 静态网站）

面向国内外采购商展示工厂、针织面料类别与定制加工服务，并引导客户通过电话 / 微信询价。
纯静态网站，不需要服务器、数据库或构建工具，直接上传即可运行。

**已上线：<https://lichen631.github.io/lichen-knitting-website>**（GitHub Pages，国内可直连）

> 另有 Cloudflare Workers 镜像：<https://www.lichen-knitting.workers.dev> —— 该域名在大陆被 DNS 污染，**仅适合海外访问**，国内请用上面的 github.io 地址。

- 默认语言：简体中文；支持切换专业商务英文（`?lang=en` 可直接打开英文版）
- 全部资源本地化，**不依赖任何外部图片或 CDN**，中国大陆网络可直接打开
- 企业资料严格以《交接文档》第 3、4、5 节为准，不包含任何未确认信息

---

## 一、文件结构

```
index.html                  首页
about.html                  关于我们
products.html               产品中心
custom.html                 定制服务
contact.html                联系我们（含询价内容整理表单）
product-single-jersey.html  平纹针织面料详情页
product-double-knit.html    双面针织面料详情页
product-other.html          其他针织面料详情页
404.html                    404 页面（noindex，不进搜索结果）

assets/style.css            全站样式与响应式布局（已格式化、带分区注释）
assets/site.js              语言切换、移动导航、询价内容整理
assets/favicon.svg          蓝底白字“利”字浏览器图标
assets/img/                 工厂实拍照片、面料示意图、视频封面、图标 PNG
assets/video/               工厂实拍视频（已转为 H.264，浏览器可直接播放）
CREDITS.md                  图片与视频的来源和授权说明

robots.txt                  搜索引擎抓取规则
site.webmanifest            添加到主屏幕用的 PWA 清单（可选）
preview-local.bat           Windows 本地预览（双击运行）
preview-local.ps1           Windows 本地预览（PowerShell 版）
README.md                   本文件
```

### 关于图片与视频

本版已使用您提供的**真实设备照片和视频**（`由工厂提供`）：

| 文件 | 内容 | 用在哪 |
| --- | --- | --- |
| `factory-5.jpg` | 车间里的针织大圆机（5 号机） | 首页首屏 |
| `factory-8.jpg` | 双面机（8 号机） | 关于我们 |
| `poster-yarn-creel.jpg` | 纱架纱管（视频封面） | 首页视频 |
| `poster-machine-fabric.jpg` | 机器内织造画面（视频封面） | 关于我们视频 |
| `video/yarn-creel.mp4` | 设备运转短片 2.9 秒 | 首页「工厂实拍」 |
| `video/machine-fabric.mp4` | 织造过程短片 2.3 秒 | 关于我们「生产现场」 |

> **视频格式已转换**：原始视频是手机的 H.265/HEVC 编码，绝大多数浏览器（Chrome、
> Firefox、大部分安卓机）无法直接播放。已用 Windows 系统解码器转成
> **H.264/AAC** 并压到约 300–380 KB，任何浏览器都能播。
> 如以后要换新视频，请先转成 H.264 再用，否则很多访客只会看到封面图。

产品类别的三张面料图是 **CC0（公共领域）真实面料照片**，来自 Poly Haven / Wikimedia
Commons，可免费商用、无需署名。页面上明确标注为「示意图」，因为它们**不是本厂特定
批次的实拍**，只用于说明面料类别。来源与授权见 `CREDITS.md`。

替换图片的方法：把新图按同名覆盖到 `assets/img/` 即可；如果要改比例，建议保持
卡片图 **4:3**、宽图 **16:9**。替换后请同步更新 `assets/img` 对应 HTML 里的 `alt` 文字。

---

## 一点五、线上地址与发布

线上地址（国内可直连）：<https://lichen631.github.io/lichen-knitting-website>

海外镜像：<https://www.lichen-knitting.workers.dev>（大陆被污染，勿用于国内推广）

改完文件后双击项目根目录的 `更新并发布.bat` 即可重新发布；详细说明见项目根目录的《部署与更新说明.md》。

## 二、本地预览

**方式一（推荐）**：双击 `preview-local.bat`，浏览器会自动打开
`http://127.0.0.1:8000/index.html`。

**方式二**：直接双击 `index.html`。页面能正常显示，但部分浏览器在 `file://`
协议下会限制语言记忆功能，所以还是推荐方式一。

英文版预览：`http://127.0.0.1:8000/index.html?lang=en`

> 需要电脑上装有 Python 3。没有也可以直接双击 `index.html`。

---

## 三、本版本已完成的内容

### 1. 修复了第一版的缺陷

| 问题 | 第二版处理 |
| --- | --- |
| 复制出的询价内容是字面量 `\n`，不能换行 | 改为真实换行；并且只输出已填写的字段 |
| 7 处按钮在没有 JavaScript 时是空白 | 全部补上中文兜底文字，JS 失效也可用 |
| 导航栏没有“当前页”高亮（CSS 有 `.active` 但从未被设置） | 按当前路径自动设置 `.active` 与 `aria-current="page"` |
| 英文标题只翻译了一半（如 `Jimo Lichen Knitting Factory \| 针织面料定制与加工`） | 每页单独写英文标题，不再做字符串替换 |
| 移动端品牌副标题隐藏失效（内联 `display:block` 覆盖了媒体查询） | 内联样式改为 CSS 类 |
| 窄屏下页头挤成多行，“立即询价”被压成竖排 | 620px 以下隐藏页头按钮，品牌名保持单行 |
| 手机菜单打开后点击链接不关闭、不支持 Esc | 点击链接 / 点空白处 / 按 Esc / 窗口变宽均自动关闭 |
| 产品图使用 Unsplash 外链（国内慢或打不开，且可能失效） | 改为本地生成插图，零外部依赖 |

### 2. 英文 SEO 补齐

每页都有独立的、与页面内容匹配的中英双语元信息：

- `<title>`、`description`、`keywords`
- Open Graph：`og:type / og:site_name / og:title / og:description / og:image / og:locale`
- Twitter Card
- `robots` 指令（`404.html` 为 `noindex`）

切换语言时，标题、描述、关键词、OG 标签、图片 alt、表单 placeholder、
无障碍 `aria-label` 会同步切换。

### 3. 结构化数据（JSON-LD）

- 全站：`LocalBusiness`（名称、电话、地址、服务区域、语言）
- 首页：`FAQPage`（对应页面上可见的 7 条常见问题，内容与页面完全一致）
- 内页：`BreadcrumbList`（对应页面上的面包屑）

### 4. 首页改为「简短首页 + 子页面跳转」

按您的要求，首页不再是一条长滚动页面：

- 首屏是「标题 + 工厂实拍 + 两个按钮」
- **紧接着就是深蓝色联系条**：大号电话/微信、一键复制微信号、完整工厂地址、
  立即拨打、高德导航 —— 不用滚动就能看到联系方式和地址
- 再往下只有三块：产品类别、工厂实拍视频、三个子页面入口
- 设备清单、合作流程、询价准备、常见问题等详细内容全部放到
  「关于我们 / 产品中心 / 定制服务 / 联系我们」各自页面，用顶部导航跳转
- 首页总高度从约 4.3 屏压缩到 **约 2 屏**

### 5. 新增内容

- 首页新增**常见问题（FAQ）** 7 条，用原生 `<details>` 实现，无 JS 也能展开
- 产品中心新增**三类面料沟通口径对照表**
- 定制服务新增**询价准备清单**（必填信息 / 有帮助的补充信息）
- 联系我们新增**联系建议**卡片与“直接拨打电话”按钮
- 新增 404 页面、`robots.txt`、`site.webmanifest`

### 5. 无障碍与可用性

- 新增“跳到主要内容”跳转链接（键盘 Tab 第一站）
- 全站 `:focus-visible` 焦点样式
- 移动菜单按钮带 `aria-expanded` / `aria-controls`
- 表单状态通过 `aria-live` 播报
- 尊重 `prefers-reduced-motion`
- 新增打印样式

### 6. 性能与稳健性

- 所有图片标记 `width`/`height`，避免布局跳动
- 首屏图 `fetchpriority="high"`，其余 `loading="lazy"`
- 无外部字体、无外部脚本、无外部图片
- 全站 CSS/JS 各一个文件

---

## 四、询价表单说明（重要）

`contact.html` 的表单**不会提交到任何服务器，也不会保存任何客户资料**。
它只做一件事：把您填写的内容整理成一段文字，方便复制后通过电话 / 微信发出去。

- 点击“整理询价内容”后，页面会明确显示“本表单不会自动发送”
- 点击“复制询价内容”会写入剪贴板；若浏览器禁止剪贴板，会弹出文本框供手动复制
- 页面**不会**出现“发送成功”之类的虚假提示

如果将来需要真正收集询价，必须增加后端、数据库、登录认证、防垃圾提交和隐私告知，
不能只在静态页面里假装保存。详见交接文档第 8 节。

---

## 五、上线步骤

1. **审阅页面**：本地打开逐页检查文案、电话、地址、地图链接。
2. **替换真实照片**：把工厂 / 设备 / 面料实拍放进 `assets/img/`，替换占位图并更新 `alt`。
3. **核查地图链接**：确认 `https://surl.amap.com/GzwN9YCG7pf` 可长期访问且定位正确。
4. **选择免费平台并核查政策**：GitHub Pages / Cloudflare Pages / Netlify 等，
   需自行确认当前免费额度、私有仓库支持、HTTPS 与账号地区可用性。
   **未经您同意不要付费、不要购买域名。**
5. **绑定域名后设置站点地址**（可选，但强烈建议）：
   ```bash
   python tools/set_domain.py https://你的域名
   ```
   这会自动写入 `<link rel="canonical">`、`og:url`，并生成 `sitemap.xml`、
   在 `robots.txt` 里声明 Sitemap。
   > 目前**故意没有**写死域名：网站还没有域名，写假的绝对地址会误导搜索引擎。
   > 想撤销回到“未设置”状态：`python tools/set_domain.py --clear`
6. **部署后验收**：检查 HTTPS、手机端、所有页面链接、SEO 元信息、电话与地图链接。
   不要在任何代码或聊天中写入管理员密码、API 密钥或访问令牌。

---

## 六、维护与二次开发

### 直接改 HTML

`lichen_knitting_website/` 下的 `.html` 是最终交付物，可以直接用编辑器修改，改完上传即可。

### 用生成脚本改（推荐用于批量 / 结构性修改）

`tools/gen_site.py` 负责生成全部 9 个 HTML 页面，页头、页脚、`<head>` 由同一份代码产出，
所以不会出现“某页导航少一项”“某页忘记加 meta”这类不一致问题。

```bash
cd 项目根目录
python tools/gen_site.py          # 重新生成 lichen_knitting_website/ 下所有 HTML
python tools/check_site.py        # 校验：死链、重复标题、空按钮、禁写内容等
python tools/gen_assets.py        # 重新生成 assets/img/ 下的插图与图标
python tools/set_domain.py https://你的域名
```

> 注意：运行 `gen_site.py` 会**覆盖** `lichen_knitting_website/*.html`，手工改过的内容会丢失。
> 如果只想改一两句文案，直接改 HTML 更简单；如果要改页头 / 页脚 / SEO 结构，改脚本再重新生成。

### ### tools/ 里的其他脚本

| 脚本 | 作用 |
| --- | --- |
| `_diag.html` | 浏览器端布局 / 交互自测页（用法见下一节），测完不要上传 |
| `gen_handoff_docx.py` | 生成《交接文档（第二版）》Word 文档 |
| `package_site.py` | 把网站 + tools + 交接文档重新打包成 ZIP |

`tools/check_site.py` 会检查什么

- 本地链接 / 图片 / 脚本是否存在（无 404）
- 每页标题、描述是否唯一
- 每页是否都有中英双语元信息
- 是否存在“没有文字的空按钮”（第一版的缺陷回归测试）
- JSON-LD 是否合法
- **是否出现被禁止编造的内容**：邮箱、成立时间、产能、设备数量、固定价格、
  固定起订量、固定交期、免费打样、资质认证、客户案例、最佳性表述
- 图片是否有 `alt`，表单是否明确声明“不会发送”

当前状态：**全部检查通过**（仅有“尚无域名，故未生成 canonical / og:url”等提示性警告）。

### 浏览器交互自测（可选，给开发者用）

`tools/_diag.html` 是一个小型布局与交互自测页：复制到网站根目录后，用
`?page=index.html&act=layout`（或 `act=lang`、`act=form`）打开，它会在 390px 手机宽度下
检查横向溢出、页头是否保持单行，并测试语言切换和表单行为。测完即可删除，**不要上传到部署平台**。


---

## 七、明确没有做的部分（与交接文档一致）

- 没有编造邮箱、成立时间、产能、设备数量、价格、起订量、交期、免费打样、资质或客户案例
- 没有做询价后端、数据库、后台管理、登录认证
- 没有内嵌高德地图（目前是分享链接跳转；内嵌需先核查高德开放平台要求与密钥限制）
- 没有部署到公网、没有购买域名、没有产生任何费用
- 没有修改原始模板 `corporate-company.html`（本项目是独立新建的目录）