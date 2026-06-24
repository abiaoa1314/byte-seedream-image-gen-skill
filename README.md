# byte-seedream-image-gen

> 火山引擎 Seedream 5.0 lite 图片生成 Skill

## 功能

- ✅ 文生图（纯文本生成图片）
- ✅ 单图生图（一张参考图 + 文本）
- ✅ 多图融合（2-14 张参考图 + 文本）
- ✅ 组图生成（一次生成最多 15 张关联图片）
- ✅ 8 种宽高比（1:1 / 3:4 / 4:3 / 16:9 / 9:16 / 3:2 / 2:3 / 21:9）
- ✅ 2K / 3K / 4K 分辨率
- ✅ PNG / JPEG 输出格式
- ✅ 联网搜索增强
- ✅ 输入图片支持 jpeg/png/webp/bmp/tiff/gif

## 安装

### GitHub

```bash
npx skills add abiaoa1314/byte-seedream-image-gen-skill
```

### 手动安装

1. 下载本仓库
2. 复制 `byte-seedream-image-gen-skill/` 到：
   - 项目级：`.opencode/skills/`
   - 全局：`~/.config/opencode/skills/` 或 `~/.claude/skills/` 或 `~/.agents/skills/`

## 配置

### 1. 获取火山引擎 API Key

访问：https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey

### 2. 保存 Key（三种方式）

**方式 1：首次运行自动保存**
直接运行脚本，会提示输入 API Key 并自动保存到 `~/.config/seedream/credentials`

**方式 2：环境变量**
```powershell
[Environment]::SetEnvironmentVariable("VOLCENGINE_ARK_SEEDREAM_API_KEY", "你的key", "User")
```

**方式 3：命令行参数**
```bash
python scripts/generate.py --prompt "..." --api-key "你的key"
```

## 使用示例

### 文生图
```bash
python scripts/generate.py --prompt "一只可爱的柴犬，樱花背景，高清细节"
```

### 图生图
```bash
python scripts/generate.py --prompt "换成夜晚场景" --image "原图.jpg"
```

### 多图融合
```bash
python scripts/generate.py --prompt "融合两张图的风格" --image "a.jpg" --image "b.jpg"
```

### 组图生成
```bash
python scripts/generate.py --prompt "春天的四个场景" --group --count 4
```

### 高级参数
```bash
python scripts/generate.py \
  --prompt "动漫风格大美女" \
  --ratio "3:4" \
  --resolution "4K" \
  --format "png" \
  --search  # 开启联网搜索
```

## 项目结构

```
byte-seedream-image-gen-skill/
├── SKILL.md                 # Skill 主文档（必读）
├── README.md                # 本文件
├── LICENSE                  # MIT 协议
├── CHANGELOG.md             # 版本历史
├── scripts/
│   └── generate.py          # 核心生成脚本
├── references/
│   └── prompt-guide.md      # 提示词编写指南
└── evals/
    └── evals.json           # 测试用例
```

## 文档

- 火山引擎 Seedream 官方文档：https://www.volcengine.com/docs/82379/1541523
- 提示词编写指南：见 `references/prompt-guide.md`
- 边界条件处理：见 `SKILL.md` 的「边界条件」章节

## 版本

v1.1.2 (2026-06-24)

## 许可

MIT License