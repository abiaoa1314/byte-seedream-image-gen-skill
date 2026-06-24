# Seedream 提示词编写指南

> 参考：https://www.volcengine.com/docs/82379/1829186

## 基本原则

1. **主体 + 场景 + 风格** — 三个要素至少覆盖两个
2. **先主后次** — 最重要的信息放最前面
3. **具体而非抽象** — "金色夕阳下的古镇石板路" 优于 "美丽的风景"
4. **中英文均可**，英文对风格词汇更精准

## 通用模板

### 文生图
```
[主体描述]，[场景/环境]，[光线/氛围]，[构图/视角]，[风格/参考]，[画质关键词]
```

### 图生图
```
基于参考图，[希望改变/保留的内容]，[新增元素]，[风格/氛围]
```

### 多图融合
```
融合以下元素：[图1的特征] + [图2的特征]，[统一风格]，[场景描述]
```

## 风格关键词速查

| 类别 | 关键词 |
|------|--------|
| **摄影** | photorealistic, 8K, cinematic lighting, shallow depth of field, studio lighting, medium format |
| **插画** | digital illustration, flat design, watercolor style, oil painting, line art |
| **3D** | 3D render, C4D, octane render, isometric, claymation style |
| **日系** | アニメ風, anime style, manga style, 浮世絵 |
| **国风** | 水墨画, 工笔画, 中国风, 敦煌壁画风, 山水画 |
| **UI/产品** | product shot, clean background, minimal, e-commerce, white background |
| **海报** | poster design, typography, bold colors, graphic design |

## 画质增强词

```
high quality, detailed, sharp focus, professional lighting, masterpiece,
8K resolution, intricate details, ultra realistic, HDR
```

## 反面示例

| ❌ 差 | ✅ 好 |
|-------|------|
| 一只猫 | 一只橘色短毛猫坐在窗台上，午后阳光从百叶窗缝隙洒入，柔和的逆光，50mm f/1.4 镜头效果 |
| 科技感背景 | 深蓝色渐变背景，蓝色光纤网络线条悬浮交错，未来科技感，4K 细节丰富 |
| 把图片p好看点 | 增强画面暖色调，背景虚化为柔光散景，提升对比度和饱和度，移除右下角杂物 |

## 组图提示词技巧

组图需要 **叙事连续性**，提示词中应包含：

1. **统一设定**："同一角色、同一场景、不同角度" 或 "连续动作分解"
2. **递进描述**：按时间/空间顺序组织
3. **明确张数暗示**："四格漫画"、"分步骤教程"、"故事板6帧"

### 组图示例
```
一个女孩从种下种子到花朵绽放的四格漫画，日系水彩风格，同一场景同一角色，
第一格：女孩在花盆中埋下种子；第二格：种子发芽长出小苗；第三格：植物长出花苞；
第四格：花朵完全绽放女孩微笑。统一暖色调，简洁背景。
```
