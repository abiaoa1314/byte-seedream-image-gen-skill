#!/usr/bin/env python3
"""
Seedream 5.0 lite 图片生成脚本
调用火山引擎 Ark API: POST /api/v3/images/generations

版本: 1.1.2
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# ── 常量 ──────────────────────────────────────────────
VERSION = "1.1.2"
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL_NAME = "doubao-seedream-5-0-260128"

# 环境变量名（长名称避免冲突）
ENV_API_KEY = "VOLCENGINE_ARK_SEEDREAM_API_KEY"

# 配置文件路径
CONFIG_DIR = Path.home() / ".config" / "seedream"
CREDENTIALS_FILE = CONFIG_DIR / "credentials"

# 宽高比 → 分辨率映射（2K/3K/4K）
SIZE_MAP = {
    "1:1":  {"2K": "2048x2048", "3K": "3072x3072", "4K": "4096x4096"},
    "4:3":  {"2K": "2304x1728", "3K": "3456x2592", "4K": "4704x3520"},
    "3:4":  {"2K": "1728x2304", "3K": "2592x3456", "4K": "3520x4704"},
    "16:9": {"2K": "2848x1600", "3K": "4096x2304", "4K": "5504x3040"},
    "9:16": {"2K": "1600x2848", "3K": "2304x4096", "4K": "3040x5504"},
    "3:2":  {"2K": "2496x1664", "3K": "3744x2496", "4K": "4992x3328"},
    "2:3":  {"2K": "1664x2496", "3K": "2496x3744", "4K": "3328x4992"},
    "21:9": {"2K": "3136x1344", "3K": "4704x2016", "4K": "6240x2656"},
}


def load_credentials() -> str | None:
    """从配置文件加载 API Key"""
    if not CREDENTIALS_FILE.exists():
        return None
    try:
        data = json.loads(CREDENTIALS_FILE.read_text(encoding="utf-8"))
        return data.get("api_key")
    except Exception:
        return None


def save_credentials(api_key: str) -> None:
    """保存 API Key 到配置文件"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data = {"api_key": api_key, "source": "seedream-skill"}
    CREDENTIALS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    # 设置文件权限（仅当前用户可读写）
    try:
        import stat
        CREDENTIALS_FILE.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except Exception:
        pass


def get_api_key(cli_key: str | None) -> str:
    """
    获取 API Key，优先级：
    1. --api-key 命令行参数
    2. 配置文件 ~/.config/seedream/credentials
    3. 环境变量 VOLCENGINE_ARK_SEEDREAM_API_KEY
    4. 交互式输入并保存
    """
    # 1. 命令行参数
    if cli_key:
        return cli_key

    # 2. 配置文件
    file_key = load_credentials()
    if file_key:
        return file_key

    # 3. 环境变量
    env_key = os.environ.get(ENV_API_KEY)
    if env_key:
        return env_key

    # 4. 交互式输入
    print("╔══════════════════════════════════════════════════════╗")
    print("║  首次使用需要配置火山引擎 API Key                   ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║  获取地址:                                           ║")
    print("║  https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey  ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()
    api_key = input("请粘贴你的 API Key（输入后自动保存）: ").strip()

    if not api_key:
        print("❌ API Key 不能为空", file=sys.stderr)
        sys.exit(1)

    # 保存到配置文件
    save_credentials(api_key)
    print(f"✅ API Key 已保存到: {CREDENTIALS_FILE}")
    print()

    return api_key


def image_to_data_uri(filepath: str) -> str:
    """将本地图片转为 data URI"""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"图片文件不存在: {filepath}")
    ext = path.suffix.lower().lstrip(".")
    mime_map = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp",
                "bmp": "bmp", "tiff": "tiff", "tif": "tiff", "gif": "gif"}
    if ext not in mime_map:
        supported = ", ".join(sorted(mime_map.keys()))
        raise ValueError(f"不支持的图片格式: {ext}，支持的格式: {supported}")
    mime = mime_map[ext]
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/{mime};base64,{data}"


def find_latest_upload() -> Path | None:
    """查找 /root/uploads/ 目录中最近上传的图片（排除非图片文件）"""
    upload_dir = Path("/root/uploads")
    if not upload_dir.exists():
        return None
    IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff", ".tif"}
    images = []
    for f in upload_dir.iterdir():
        if f.is_file() and f.suffix.lower() in IMAGE_EXTS:
            # file 命令的真实类型
            import subprocess
            try:
                mime_result = subprocess.run(
                    ["file", "--mime-type", "-b", str(f)],
                    capture_output=True, text=True, timeout=2
                )
                mime = mime_result.stdout.strip()
                if "image" not in mime:
                    continue
            except Exception:
                continue
            images.append(f)
    if not images:
        return None
    # 按修改时间排序，取最新
    images.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return images[0]


def get_output_dir() -> Path:
    """确定输出目录：优先当前工作目录下的 seedream-output"""
    cwd = Path.cwd()
    try:
        out = cwd / "seedream-output"
        out.mkdir(parents=True, exist_ok=True)
        # 验证可写
        test_file = out / ".write_test"
        test_file.write_text("ok")
        test_file.unlink()
        return out
    except PermissionError:
        print(f"❌ 没有写权限: {out}", file=sys.stderr)
        print("请换一个有写权限的目录，或用 sudo 提升权限", file=sys.stderr)
        sys.exit(1)


def check_disk_space(out_dir: Path, ratio: str, resolution: str, count: int) -> None:
    """检查磁盘空间是否足够"""
    import shutil
    # 估算单张大小（4K 最大约 15MB，2K 约 3MB）
    size_map_mb = {"2K": 3, "3K": 7, "4K": 15}
    per_image = size_map_mb.get(resolution, 5)
    needed_mb = per_image * count * 1.2  # 1.2 倍冗余
    try:
        free_mb = shutil.disk_usage(out_dir).free / 1024 / 1024
        if free_mb < needed_mb:
            print(f"❌ 磁盘空间不足: 剩余 {free_mb:.0f}MB，需要至少 {needed_mb:.0f}MB", file=sys.stderr)
            print(f"建议: 改 2K 分辨率，或换到空间充足的目录（--output-dir）", file=sys.stderr)
            sys.exit(1)
    except Exception:
        pass  # 检查失败不阻塞


def call_ark_api(args: argparse.Namespace) -> dict:
    """调用 Ark API 生成图片"""
    # ── API Key ──
    api_key = get_api_key(args.api_key)

    # ── 尺寸 ──
    resolution = args.resolution  # "2K" | "3K" | "4K"
    if resolution not in ("2K", "3K", "4K"):
        print(f"❌ 不支持的分辨率: {resolution}，可选值: 2K, 3K, 4K", file=sys.stderr)
        sys.exit(1)

    ratio = args.ratio
    if ratio not in SIZE_MAP:
        print(f"❌ 不支持的宽高比: {ratio}", file=sys.stderr)
        print(f"可选值: {', '.join(SIZE_MAP.keys())}", file=sys.stderr)
        sys.exit(1)

    size = SIZE_MAP[ratio][resolution]

    # ── 构建请求体 ──
    body: dict = {
        "model": MODEL_NAME,
        "prompt": args.prompt[:800],
        "size": size,
        "n": 1,
        "response_format": "url",
        "watermark": False,
        "output_format": args.format,
    }

    # 参考图
    images = []
    if args.image:
        for img_path in args.image:
            if img_path.startswith("http://") or img_path.startswith("https://"):
                images.append(img_path)
            elif img_path.startswith("data:"):
                images.append(img_path)
            else:
                images.append(image_to_data_uri(img_path))

    if images:
        body["image"] = images[0] if len(images) == 1 else images

    # 组图
    if args.group:
        body["sequential_image_generation"] = "auto"
        body["sequential_image_generation_options"] = {"max_images": args.count}

    # 联网搜索
    if args.search:
        body["tools"] = [{"type": "web_search"}]

    # ── 发送请求 ──
    print(f"🎨 正在生成图片...")
    print(f"   模式: {'组图' if args.group else '单图'} | 尺寸: {ratio} {resolution} ({size}) | 格式: {args.format}")
    if images:
        print(f"   参考图: {len(images)} 张")
    if args.search:
        print(f"   联网搜索: 已开启")
    print()

    req = urllib.request.Request(
        f"{ARK_BASE_URL}/images/generations",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8") if e.fp else ""
        # 针对不同错误码给出友好提示
        hint = {
            401: "→ API Key 无效或过期，请去火山引擎控制台检查",
            403: "→ 权限不足或账号未开通 Seedream 模型服务",
            404: "→ 模型名称错误或资源不存在",
            429: "→ 触发限流，等待 60 秒后重试，或申请提升配额",
            500: "→ 火山引擎服务端内部错误，建议稍后重试",
            502: "→ 服务暂时不可用（火山引擎维护中）",
            503: "→ 服务暂时不可用（火山引擎维护中）",
            504: "→ 服务响应超时（火山引擎负载较高）",
        }.get(e.code, "")
        raise RuntimeError(f"API 调用失败 (HTTP {e.code}): {err_body}\n{hint}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"网络错误: {e}\n→ 检查网络连接和防火墙设置")
    except TimeoutError:
        raise RuntimeError("API 请求超时（120s）\n→ 检查网络或稍后重试")



def download_image(url: str, out_dir: Path, index: int = 0, fmt: str = "png") -> Path:
    """下载图片到本地"""
    timestamp = int(time.time())
    ext = fmt if fmt in ("png", "jpeg") else "png"
    filename = f"seedream-{timestamp}-{index:02d}.{ext}"
    filepath = out_dir / filename

    req = urllib.request.Request(url, headers={"User-Agent": "seedream-skill/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        filepath.write_bytes(resp.read())

    return filepath


def main():
    parser = argparse.ArgumentParser(description="Seedream 5.0 lite 图片生成")
    parser.add_argument("--version", action="version", version=f"seedream-skill {VERSION}")
    parser.add_argument("--prompt", required=True, help="提示词（≤800字符）")
    parser.add_argument("--ratio", default="1:1",
                        choices=list(SIZE_MAP.keys()), help="宽高比（默认 1:1）")
    parser.add_argument("--resolution", default="2K",
                        choices=["2K", "3K", "4K"], help="分辨率（默认 2K）")
    parser.add_argument("--format", default="png",
                        choices=["png", "jpeg"], help="输出格式（默认 png）")
    parser.add_argument("--image", action="append", default=None,
                        help="参考图路径/URL（可多次指定，最多14张）")
    parser.add_argument("--group", action="store_true",
                        help="开启组图模式")
    parser.add_argument("--count", type=int, default=10,
                        help="组图最大数量（默认 10，最多 15）")
    parser.add_argument("--search", action="store_true",
                        help="开启联网搜索增强")
    parser.add_argument("--api-key", help=f"API Key（优先于配置文件和环境变量 {ENV_API_KEY}）")
    parser.add_argument("--output-dir", help="输出目录（默认 ./seedream-output）")
    parser.add_argument("--no-download", action="store_true",
                        help="不下载图片，只返回 URL")
    parser.add_argument("--latest-upload", action="store_true",
                        help="自动使用 /root/uploads/ 目录下最新的图片作为参考图（解决 UI 上传图访问问题）")

    args = parser.parse_args()

    # ── 自动从 /root/uploads/ 捕获最新图 ──
    if args.latest_upload:
        latest = find_latest_upload()
        if latest:
            print(f"📎 自动使用最新上传图: {latest}")
            if args.image is None:
                args.image = []
            args.image.insert(0, str(latest))
        else:
            print("⚠️  /root/uploads/ 目录下没有找到图片", file=sys.stderr)

    # 校验
    if args.image and len(args.image) > 14:
        print("❌ 参考图数量不能超过 14 张", file=sys.stderr)
        sys.exit(1)
    if args.count < 1 or args.count > 15:
        print("❌ 组图数量范围: 1-15", file=sys.stderr)
        sys.exit(1)
    if len(args.prompt) > 800:
        print(f"⚠️  提示词过长（{len(args.prompt)}字符），将截断到800字符")
    if not args.prompt.strip():
        print("❌ 提示词不能为空", file=sys.stderr)
        sys.exit(1)

    # 磁盘空间检查
    out_dir = Path(args.output_dir) if args.output_dir else get_output_dir()
    count_estimate = args.count if args.group else 1
    check_disk_space(out_dir, args.ratio, args.resolution, count_estimate)

    # 调用 API
    try:
        result = call_ark_api(args)
    except RuntimeError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)

    # 处理结果
    data_list = result.get("data", [])
    if not data_list:
        print("❌ API 返回数据为空", file=sys.stderr)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)

    out_dir = Path(args.output_dir) if args.output_dir else get_output_dir()

    success_count = 0
    for i, item in enumerate(data_list):
        if "error" in item:
            err = item["error"]
            print(f"⚠️  第 {i+1} 张图片生成失败: [{err.get('code')}] {err.get('message')}")
            continue

        url = item.get("url", "")
        actual_size = item.get("size", args.ratio)

        if args.no_download:
            print(f"📷 图片 {i+1}: {url} ({actual_size})")
            success_count += 1
        else:
            try:
                filepath = download_image(url, out_dir, i, args.format)
                print(f"✅ 图片 {i+1}: {filepath} ({actual_size})")
                success_count += 1
            except Exception as e:
                print(f"⚠️  图片 {i+1} 下载失败: {e}")

    # 摘要
    usage = result.get("usage", {})
    print(f"\n📊 摘要: 成功 {success_count}/{len(data_list)} 张 | "
          f"Token: {usage.get('total_tokens', 'N/A')} | "
          f"模型: {result.get('model', MODEL_NAME)}")

    if not args.no_download:
        print(f"📁 输出目录: {out_dir}")


if __name__ == "__main__":
    main()
