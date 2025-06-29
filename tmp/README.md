# 图像匹配工具

这个工具提供了两种图像匹配算法：模板匹配和SIFT特征匹配，用于在大图中查找小图的位置并返回坐标。

## 功能特性

- **模板匹配**: 使用OpenCV的模板匹配算法，适合查找完全相同的图像
- **SIFT特征匹配**: 使用SIFT特征点进行匹配，适合查找相似但不完全相同的图像
- **支持中文路径**: 自动处理中文文件路径
- **多种匹配方法**: 支持多种OpenCV模板匹配方法
- **批量查找**: 可以查找多个匹配结果
- **灵活参数**: 可调节匹配阈值、最小匹配点数等参数
- **可视化显示**: 在图像上绘制匹配结果，直观显示匹配位置
- **结果保存**: 可以将匹配结果保存为图像文件
- **自动缩放**: 大分辨率图像自动缩放以适应屏幕显示
- **自定义显示尺寸**: 可自定义最大显示尺寸

## 安装依赖

```bash
pip install opencv-python numpy
```

## 基本使用

### 1. 简单模板匹配

```python
from debug import ImageMatcher

matcher = ImageMatcher()

# 查找图像并返回中心坐标
result = matcher.find_image(
    source_image="大图路径.png", 
    template_image="小图路径.png", 
    method='template', 
    threshold=0.8
)

if result:
    x, y = result
    print(f"找到目标，中心坐标: ({x}, {y})")
```

### 2. 简单SIFT匹配

```python
result = matcher.find_image(
    source_image="大图路径.png", 
    template_image="小图路径.png", 
    method='sift', 
    min_match_count=10
)

if result:
    x, y = result
    print(f"找到目标，中心坐标: ({x}, {y})")
```

### 3. 可视化匹配结果

```python
# 显示匹配结果（自动弹出窗口）
result = matcher.show_match_result(
    source_image="大图路径.png",
    template_image="小图路径.png",
    method='template',
    threshold=0.8
)

# 显示所有匹配结果
all_results = matcher.show_all_matches(
    source_image="大图路径.png",
    template_image="小图路径.png",
    method='template',
    threshold=0.7,
    max_results=5
)
```

### 4. 自定义可视化

```python
# 获取匹配结果
results = matcher.template_match(source_image, template_image, threshold=0.8)

# 自定义绘制
img = matcher.draw_matches(source_image, results, "自定义标题", wait_key=False)

# 添加自定义内容
cv2.putText(img, "自定义文本", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

# 显示或保存
cv2.imshow("结果", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
```

### 5. 自定义显示尺寸

```python
# 使用自定义显示尺寸
matcher.show_match_result(
    source_image, template_image, 
    method='template', 
    threshold=0.8
)

# 或者直接使用draw_matches方法
results = matcher.template_match(source_image, template_image, threshold=0.8)
matcher.draw_matches(
    source_image, results, 
    "匹配结果", 
    max_display_size=(1200, 800)  # 自定义最大显示尺寸
)
```

## 参数说明

### 模板匹配参数

- `threshold`: 匹配阈值 (0-1)，值越大要求越严格，默认0.8
- `method`: 匹配方法，可选值：
  - `cv2.TM_CCOEFF_NORMED` (默认，推荐)
  - `cv2.TM_CCORR_NORMED`
  - `cv2.TM_SQDIFF_NORMED`
- `max_results`: 最大返回结果数，默认1

### SIFT匹配参数

- `min_match_count`: 最小匹配特征点数，默认10
- `good_ratio`: 良好匹配比例 (Lowe's ratio)，默认0.7
- `max_results`: 最大返回结果数，默认1

### 可视化参数

- `window_name`: 窗口名称，默认"匹配结果"
- `wait_key`: 是否等待按键，默认True
- `max_display_size`: 最大显示尺寸 (width, height)，默认(1920, 1080)

### 缩放参数

- `max_display_size`: 最大显示尺寸，超过此尺寸的图像会自动缩放
- `scale`: 缩放比例，1.0表示不缩放
- `interpolation`: 插值方法，默认cv2.INTER_AREA（适合缩小）

## 返回结果格式

### 单个匹配结果

```python
# 返回坐标元组
(x, y)  # 中心坐标
```

### 多个匹配结果

```python
[
    {
        'center': (x, y),           # 中心坐标
        'top_left': (x, y),         # 左上角坐标 (仅模板匹配)
        'rectangle': [(x1,y1), (x2,y2), (x3,y3), (x4,y4)],  # 矩形四个角点
        'confidence': 0.95,         # 置信度
        'method': 'template',       # 匹配方法
        'match_count': 15           # 匹配特征点数 (仅SIFT)
    },
    # ... 更多结果
]
```

## 可视化功能

### 显示内容

- **矩形框**: 显示匹配区域的边界
- **中心点**: 显示匹配区域的中心位置
- **角点**: 显示矩形的四个角点
- **标签**: 显示匹配方法和序号
- **置信度**: 显示匹配的置信度分数
- **缩放信息**: 显示缩放比例和原始尺寸

### 颜色编码

- **绿色**: 模板匹配结果
- **蓝色**: SIFT匹配结果
- **白色**: 中心点外圈

### 自动缩放功能

- **智能缩放**: 大分辨率图像自动缩放以适应屏幕
- **保持比例**: 缩放时保持原始宽高比
- **坐标同步**: 匹配结果坐标自动同步缩放
- **信息显示**: 显示缩放比例和原始尺寸信息

### 使用方法

```python
# 基础可视化（自动缩放）
matcher.show_match_result(source_image, template_image, method='template')

# 批量可视化（自动缩放）
matcher.show_all_matches(source_image, template_image, method='sift')

# 自定义显示尺寸
matcher.draw_matches(source_image, results, "标题", max_display_size=(1200, 800))

# 自定义可视化
img = matcher.draw_matches(source_image, results, "标题", wait_key=False)
# 进行自定义处理...
cv2.imshow("结果", img)
cv2.waitKey(0)
```

## 使用示例

### 运行基础示例

```bash
python simple_example.py
```

### 运行可视化演示

```bash
python visual_demo.py
```

### 运行完整演示

```bash
python debug.py
```

## 注意事项

1. **图像格式**: 支持常见的图像格式 (PNG, JPG, BMP等)
2. **中文路径**: 自动处理中文文件路径
3. **内存使用**: 大图像会占用较多内存，建议适当调整图像尺寸
4. **匹配精度**: 
   - 模板匹配适合查找完全相同的图像
   - SIFT匹配适合查找相似但不完全相同的图像
5. **性能考虑**: SIFT算法比模板匹配更耗时，但更灵活
6. **显示窗口**: 可视化功能会弹出OpenCV窗口，按任意键关闭

## 常见问题

### Q: 匹配不到目标怎么办？
A: 可以尝试：
- 降低阈值 (template匹配) 或减少最小匹配点数 (SIFT匹配)
- 检查图像是否清晰，是否有足够的特征点
- 尝试不同的匹配方法

### Q: 匹配结果不准确怎么办？
A: 可以尝试：
- 提高阈值以获得更精确的匹配
- 使用SIFT匹配处理旋转、缩放等变换
- 检查模板图像是否合适

### Q: 处理速度慢怎么办？
A: 可以尝试：
- 缩小图像尺寸
- 使用模板匹配替代SIFT匹配
- 调整SIFT参数减少特征点数量

### Q: 可视化窗口不显示怎么办？
A: 可以尝试：
- 确保系统支持图形界面
- 检查OpenCV是否正确安装
- 在服务器环境中可能需要配置显示设置

### Q: 图像太大看不全怎么办？
A: 可以尝试：
- 使用自动缩放功能（默认已启用）
- 自定义最大显示尺寸：`max_display_size=(1200, 800)`
- 使用不同的显示尺寸：`(800, 600)`, `(600, 400)` 等
- 保存缩放后的图像用于查看

### Q: 缩放后坐标不准确怎么办？
A: 可以尝试：
- 缩放功能会自动同步坐标，返回的坐标是原始图像上的坐标
- 如果需要缩放后的坐标，可以手动计算：`scaled_x = original_x * scale`
- 缩放信息会显示在图像底部 