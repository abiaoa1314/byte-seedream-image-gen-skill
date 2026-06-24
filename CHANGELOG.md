# Changelog

## [1.1.2] - 2026-06-24

### Added
- API Key 本地持久化功能（保存到 ~/.config/seedream/credentials）
- 首次使用交互式输入引导
- 配置文件权限安全设置

### Changed
- 环境变量名改为 VOLCENGINE_ARK_SEEDREAM_API_KEY（避免冲突）
- API Key 查找优先级：命令行参数 > 配置文件 > 环境变量 > 交互输入
- 更新 SKILL.md 文档说明新的 API Key 处理方式

## [1.1.1] - 2026-06-24

### Added
- 文档化输入图片格式支持（jpeg/png/webp/bmp/tiff/gif）
- 添加输入格式验证错误处理

### Changed
- 更新 SKILL.md API 概览，明确输入格式支持
- 更新 description 添加输入格式说明

## [1.1.0] - 2026-06-24

### Added
- 版本号管理（SKILL.md 和脚本）
- 测试用例（evals/evals.json）
- LICENSE 文件
- CHANGELOG 文件
- 更多触发词（商品图、产品图、头像生成、壁纸生成等）

### Changed
- 优化 SKILL.md description，更加 "pushy"
- 改进脚本版本参数支持

## [1.0.0] - 2026-06-20

### Added
- 初始版本
- 文生图、图生图、多图融合、组图生成功能
- 8 种宽高比支持
- 2K/3K/4K 分辨率
- 联网搜索增强
- 完整的错误处理和边界条件
- 提示词编写指南
