# tom-substack-publisher

一个为技术从业者研究网关动态、生成中文图文稿并在人工确认后发布到 Substack 网页端的 Codex Skill。

## 安全定位

准备文章不等于授权发布。Skill 会先生成并验证本地产物，展示当前版本的 `content fingerprint`；只有用户明确确认该指纹后，才允许进入浏览器发布流程。任何正文、来源或图片变化都会使原确认失效。

## 能力范围

- 按 `Asia/Shanghai` 计算运行日之前两个完整自然日的新闻窗口。
- 同时覆盖网关架构、L4、L7/API、AI/LLM、推理、Agent/MCP、P4 与 NPL 八类主题的中英文检索。
- 选择一个有可靠来源、技术解释空间和实践价值的主题，生成约五分钟可读的中文文章。
- 通过 `ian-xiaohei-illustrations` 生成封面和解释性正文图，并用确定性渲染制作包含精确数据的事实图。
- 构建本地预览、验证来源与文章契约、计算指纹，并在获批后通过已登录的浏览器会话发布。

## 工作流

1. 计算前两个北京时间自然日的窗口，按八类主题执行中英文检索，核验原始发布日期、版本、数字和强断言。
2. 至少保留两个已验证来源，其中至少一个是第一方来源、一个是窗口内事件来源；若材料不足则停止。
3. 选择一个主题，撰写 1,800-2,600 个中文字符的文章，明确区分事实与技术判断。
4. 用 `ian-xiaohei-illustrations` 制作 16:9 封面与机制解释图；另用 HTML/SVG 等可复现方式制作事实图并逐项核对。
5. 运行 `build_preview.py` 与 `validate_article.py`，仅在验证结果为 `ok: true` 时展示预览和完整 `content fingerprint`。
6. 等待用户明确批准该指纹。批准后立即重新计算；如不一致则返回准备阶段。
7. 在 Substack 已登录会话中发布为网页文章，明确保持 `send_email=false`，随后核对公开 URL、正文、链接和图片。
8. 只有公开页面验证成功后才写入 `publish-receipt.json`。

## 目录结构

```text
tom-substack-publisher/
├── SKILL.md                         # Agent 的核心执行与停止条件
├── agents/openai.yaml               # Skill 界面元数据
├── assets/article-preview.css       # 本地文章预览样式
├── evals/evals.json                 # 非实时评估用例
├── references/
│   ├── research-matrix.md            # 检索范围、来源结构与选题规则
│   ├── article-contract.md           # 文章、图片、验证与确认契约
│   └── substack-browser-publish.md   # 受保护的浏览器发布步骤
├── scripts/
│   ├── build_preview.py              # 生成 article.html 与 preview.html
│   └── validate_article.py           # 校验产物并计算 SHA-256 指纹
└── tests/test_readme_contract.py      # README 与仓库卫生契约测试
```

每次运行的文章产物保存在 `/Users/tom/Desktop/substack/YYYY-MM-DD-topic-slug/`，而不是 Skill 仓库中。目录包含 `candidates.md`、`sources.json`、`article.md`、HTML 预览和 `images/`；发布成功并完成公开验证前，不应存在 `publish-receipt.json`。

## 安装

依赖如下：

- 支持 Skill 的 Codex 环境，以及可用的实时检索能力；
- Python 3.10 或更高版本；
- Pandoc，用于把 Markdown 转为经过清理的 HTML；
- `ian-xiaohei-illustrations` Skill；
- `browser:control-in-app-browser` Skill，以及用户已登录的 Substack 浏览器会话；
- 可将 HTML/SVG 稳定渲染为 PNG 的浏览器或 Playwright 环境。

将仓库放到当前约定路径：

```bash
git clone https://github.com/zhaotao19860/tom-substack-publisher.git \
  /Users/tom/.comate/skills/tom-substack-publisher
python3 --version
pandoc --version
```

当前版本不是可移植的软件包：`SKILL.md` 和文档约定了 `/Users/tom/.comate/skills/tom-substack-publisher` 与 `/Users/tom/Desktop/substack` 两个个人绝对路径。其他用户需要先一致地调整这些路径，再让 Codex 重新发现 Skill。

## 使用

可以直接用自然语言触发，例如：

> 使用 `$tom-substack-publisher`，研究北京时间前两个自然日的网关动态，准备一篇带图的五分钟中文 Substack 文章供我审核。先不要发布。

准备完成后，Skill 会报告标题、副标题、时间窗口、来源数量、事实风险、阅读时间、图片数量、预览路径和完整指纹。若希望发布，应明确引用并批准该次报告中的指纹；泛化的“以后都可以发布”不构成授权。

本地验证命令：

```bash
python3 /Users/tom/.comate/skills/tom-substack-publisher/scripts/build_preview.py RUN_DIR
python3 /Users/tom/.comate/skills/tom-substack-publisher/scripts/validate_article.py RUN_DIR --json
```

## 发布安全边界

- 仅批准当前文章、来源和图片集合对应的指纹；内容改变后必须重新验证和确认。
- 发布前必须确认目标 publication 和登录账号，登录与 CAPTCHA 由用户在浏览器中完成。
- 不读取、导出、打印或保存 Substack Cookie、密码、Token 或其他浏览器认证数据。
- 邮件、收件箱或订阅者投递必须关闭，发布不变量为 `send_email=false`。
- 编辑器保存状态、图片上传、投递选项或 UI 含义不清时立即停止；不对不确定的发布点击进行重试。
- 本地预览、编辑器保存或草稿都不算发布成功；必须打开公开 URL 完成核验。

## 开发与验证

运行仓库内契约测试：

```bash
python3 -m unittest discover -s /Users/tom/.comate/skills/tom-substack-publisher/tests -v
```

验证 Skill 结构：

```bash
python3 /Users/tom/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  /Users/tom/.comate/skills/tom-substack-publisher
```

常见问题：`pandoc is required` 表示本机缺少 Pandoc；`ok: false` 时应按 JSON 中的错误修正日期窗口、来源、字数或图片，而不是跳过验证；必需的插图 Skill、浏览器会话或明确的网页发布选项不可用时，流程会按安全契约停止。

## 已知限制

- 路径和输出位置带有个人环境假设，尚未参数化。
- 两日新闻窗口可能没有足够可靠的主题；此时 Skill 会保留研究产物并停止，而不会补造选题。
- Substack 编辑器和发布 UI 变化可能使自动化步骤失效，需要重新人工核对。
- AI 图片仍需人工检查解释性、文字、裁切、水印和事实准确性；一次重试后仍不合格会停止流程。
- 发布依赖用户现有的登录会话，无法代替人工完成登录、CAPTCHA 或账号选择。
