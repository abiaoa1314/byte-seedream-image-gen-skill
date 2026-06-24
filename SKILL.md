---
name: byte-seedream-image-gen-skill
version: "1.1.2"
description: "使用火山引擎 Seedream 5.0 lite 模型生成/编辑图片。必须使用此 skill 当用户提到：生成图片、AI绘画、画一张、文生图、图生图、seedream、豆包绘图、生成海报、多图融合、参考图生成、商品图、产品图、头像生成、壁纸生成、插画、海报设计、图片编辑、风格转换、照片转动漫、AI画图、画图、出图、做图。支持文生图、单图生图、多图融合，8种宽高比，2K/3K/4K分辨率，可选PNG/JPG格式，支持联网搜索增强。输入图片支持jpeg/png/webp/bmp/tiff/gif格式。"
---

# Seedream 图片生成 Skill

> 基于火山引擎 Ark API — Seedream 5.0 lite（doubao-seedream-5-0-260128）
> 版本：1.1.2 | 文档：https://www.volcengine.com/docs/82379/1541523

## 能力矩阵

| 模式 | 说明 | 输入 |
|------|------|------|
| **文生图** | 纯文本描述生成图片 | prompt |
| **单图生图** | 一张参考图 + 文本描述 | prompt + image |
| **多图融合** | 2-14张参考图 + 文本描述 | prompt + images[] |
| **组图生成** | 一次生成多张关联图片（最多15张） | prompt + sequential_image_generation |

## API 概览

```
POST https://ark.cn-beijing.volces.com/api/v3/images/generations
Authorization: Bearer $ARK_API_KEY

关键参数：
  model        = "doubao-seedream-5-0-260128"
  prompt       = 提示词（≤800字符）
  size         = "2K"|"3K"|"4K" 或 "WxH"（如 2048x2048）
  image        = 参考图 URL 或 base64（可选，最多14张，支持 jpeg/png/webp/bmp/tiff/gif）
  watermark    = false          （去水印）
  output_format = "png"|"jpeg"  （输出格式）
  response_format = "url"       （url 或 b64_json）
  sequential_image_generation = "disabled"|"auto"
```

## ⚠️ 图生图重要注意事项

**图生图有结构性限制** — Seedream 在修改原图时，对原图的核心姿势有强 bias。

### 不同修改类型的选择策略

| 修改需求 | 推荐方案 | 原因 |
|---------|---------|------|
| 换颜色/换文字/换小物件 | ✅ 图生图 | 主体结构不变，微调效果好 |
| 改表情/眼神 | ✅ 图生图 | 在原图表情上微调效果好 |
| 改嘴部/口水 | ⚠️ 图生图试一次，不行就文生图 | 嘴巴细节敏感 |
| 改大幅姿势（手离开桌面等） | ❌ 用文生图 + 多图融合 | 图生图会让手"钉"在原位置 |
| 完全重画场景 | ✅ 文生图 | 不被原图束缚 |

**重姿势时使用 `--latest-upload` 配合文生图 prompt**：

```bash
# ❌ 错误：5 轮图生图都改不动
python3 scripts/generate.py --prompt "把手挪开" --image /path/to/orig.png

# ✅ 正确：跳开图生图，用详细描述重新画
python3 scripts/generate.py \
  --prompt "【详细描述整个画面，包括你想要的姿势】" \
  --latest-upload  # 顺便让脚本确认上传目录
```

### `--latest-upload` 参数

工作场景：用户从 UI 拖一张图到对话，沙箱里的脚本读不到。脚本会自动扫描 `/root/uploads/`，找出最新上传的图片作为参考。

```bash
python3 scripts/generate.py --prompt "..." --latest-upload
```

文件排序规则：按修改时间倒序取第一个，用 `file` 命令验证是真实图片（避免后缀伪造）。

## 使用流程

### Step 1: 确认 API Key

脚本会按以下优先级查找 API Key：
1. `--api-key` 命令行参数
2. 配置文件 `~/.config/seedream/credentials`
3. 环境变量 `VOLCENGINE_ARK_SEEDREAM_API_KEY`
4. 首次运行时自动提示输入并保存

首次使用时，脚本会提示输入 API Key 并自动保存到配置文件，后续运行无需重复输入。

```
API Key 获取地址：
https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey

获取后执行：
export VOLCENGINE_ARK_SEEDREAM_API_KEY="你的key"
```

脚本内部优先级：`--api-key` 参数 > 配置文件 > 环境变量。

### Step 2: 确认需求并生成

与用户确认以下信息后调用脚本：

- **模式**：文生图 / 图生图 / 多图融合 / 组图
- **尺寸**：1:1 / 3:4 / 4:3 / 16:9 / 9:16 / 3:2 / 2:3 / 21:9（默认 1:1）
- **分辨率**：2K / 3K / 4K（默认 2K）
- **格式**：png / jpeg（默认 png）
- **数量**：1张 或组图（最多15张）

### Step 3: 调用脚本

```bash
python3 <skill-directory>/scripts/generate.py \
  --prompt "描述文本" \
  --ratio "16:9" \
  --resolution "2K" \
  --format "png"
```

**图生图时**追加 `--image` 参数：

```bash
python3 <skill-directory>/scripts/generate.py \
  --prompt "描述文本" \
  --image "/path/to/ref.png"
```

**多图融合时**传入多个 `--image`：

```bash
python3 <skill-directory>/scripts/generate.py \
  --prompt "融合描述" \
  --image "/path/to/a.png" \
  --image "/path/to/b.png"
```

**组图生成时**追加 `--group` 和 `--count`：

```bash
python3 <skill-directory>/scripts/generate.py \
  --prompt "故事连续性描述" \
  --group \
  --count 4
```

### Step 4: 展示结果

告知用户：
- 生成图片的本地路径
- 实际分辨率、Token 消耗

## 分辨率速查

| 比例 | 2K | 3K | 4K |
|------|-----|-----|-----|
| 1:1 | 2048x2048 | 3072x3072 | 4096x4096 |
| 4:3 | 2304x1728 | 3456x2592 | 4704x3520 |
| 3:4 | 1728x2304 | 2592x3456 | 3520x4704 |
| 16:9 | 2848x1600 | 4096x2304 | 5504x3040 |
| 9:16 | 1600x2848 | 2304x4096 | 3040x5504 |
| 3:2 | 2496x1664 | 3744x2496 | 4992x3328 |
| 2:3 | 1664x2496 | 2496x3744 | 3328x4992 |
| 21:9 | 3136x1344 | 4704x2016 | 6240x2656 |

## 边界条件

### 用户输入校验

| 场景 | 检测方法 | 处理动作 |
|------|---------|---------|
| API Key 未配置 | 检测所有来源 | 交互式输入提示，自动保存到配置文件 |
| API Key 无效 | 401/403 响应 | 报错「Key 失效或配额不足」，建议去火山引擎控制台检查 |
| API Key 配置文件损坏 | JSON 解析失败 | 提示重新输入 API Key |
| API Key 配额耗尽 | 429 响应 | 报错「调用频率过高」，建议等 1 分钟或联系火山引擎提升配额 |
| 提示词超长 | `len(prompt) > 800` | 截断到 800 字符 + ⚠️ 警告 |
| 提示词为空 | 仅含空格/换行 | 报错「提示词不能为空」 |
| 比例/分辨率不合法 | 不在枚举值内 | argparse 拦截，提示可选值 |
| 参考图数量超限 | `> 14` 张 | 报错并 exit 1 |
| 组图数量超限 | `--count > 15` 或 `< 1` | 报错并 exit 1 |
| 参考图不存在 | `image_to_data_uri` FileNotFoundError | 报错具体路径 |
| 参考图格式不支持 | 非 jpeg/png/webp/bmp/tiff/gif | 报错「不支持的图片格式，支持：jpeg/png/webp/bmp/tiff/gif」 |
| 参考图是损坏文件 | 上传过程中读到 0 字节 | 报错「文件为空或损坏」 |
| `--latest-upload` 找不到 | `/root/uploads/` 为空或无图 | ⚠️ 警告，强制退化为纯文生图 |

### API 调用异常

| 场景 | 表现 | 处理动作 |
|------|------|---------|
| **网络超时** | `urlopen` timeout 120s | 报错「网络连接超时，3秒后自动重试 1 次」，仍失败则退出 |
| **连接被拒** | ConnectionRefusedError | 报错「无法连接到 ark.cn-beijing.volces.com」，检查网络/防火墙 |
| **429 限流** | HTTP 429 | 报错「触发限流，等待 60 秒后重试」 |
| **5xx 服务端错误** | HTTP 500/502/503/504 | 报错原始状态码 + 响应内容，建议等几分钟重试 |
| **4xx 参数错误** | HTTP 400 | 解析响应 body 里的 `error.message`，告知用户具体原因 |
| **返回空 data** | `data: []` | 报错「API 返回数据为空」，可能是 prompt 触发安全审核 |
| **单张图生成失败** | `item.error` 存在 | ⚠️ 警告 + 列出失败原因，其他图继续下载 |

### 资源与存储

| 场景 | 检测 | 处理 |
|------|------|------|
| **磁盘空间不足** | 生成前检查 `shutil.disk_usage(out_dir).free < 500MB`（4K PNG 单张约 5-15MB） | 报错「剩余空间 X MB，不足以生成 Y 张，建议改 2K 或清理磁盘」 |
| **输出目录无写权限** | `mkdir` 抛 PermissionError | 报错并提示加 `sudo` 或换 `--output-dir` |
| **图片下载失败** | `urlopen` timeout 60s 或 HTTPError | ⚠️ 警告 + 告知「URL 24h 内有效，必要时可在浏览器手动下载」 |

### 内容安全

| 场景 | 处理 |
|------|------|
| Prompt 触发安全审核 | API 返回 `error.code` 提示内容违规，告知用户修改 prompt |
| 生成图片触发审核 | `item.error.code` 含 `content_filter`，跳过该张，其他继续 |

### 错误码速查

| HTTP 状态码 | 含义 | 处理 |
|------------|------|------|
| 400 | 请求参数错误 | 检查 prompt、image、size 格式 |
| 401 | API Key 无效 | 重新获取 Key |
| 403 | 权限不足 | 检查火山引擎账号是否开通对应模型 |
| 404 | 资源不存在 | 可能是模型名称写错 |
| 429 | 调用频率超限 | 降低调用频率或申请提额 |
| 500 | 服务端内部错误 | 等几分钟重试 |
| 502/503/504 | 服务暂时不可用 | 火山引擎维护中，稍后重试 |

## 文件说明

- `scripts/generate.py` — 核心生成脚本
- `references/prompt-guide.md` — Seedream 提示词编写指南（按需查阅）

> 提示词编写遇到困难时，Read `references/prompt-guide.md` 获取参考。
