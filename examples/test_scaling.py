# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/29 12:05
@Author   : wieszheng
@Software : PyCharm
"""

import cv2
import numpy as np

from tmp.debug import ImageMatcher
from utils.image_utils import ImageUtils


def test_scaling_functionality():
    """测试缩放功能"""
    print("=== 测试缩放功能 ===\n")
    
    matcher = ImageMatcher()
    
    # 测试图片路径
    source_path = "../tmp/2.png"
    template_path = "../tmp/answer.png"
    
    try:
        # 获取匹配结果
        results = matcher.template_match(source_path, template_path, threshold=0.7)
        
        if results:
            print(f"找到 {len(results)} 个匹配结果")
            
            # 测试不同显示尺寸
            display_sizes = [
                (1920, 1080),  # 大尺寸
                (1200, 800),   # 中等尺寸
                (800, 600),    # 小尺寸
                (600, 400),    # 超小尺寸
            ]
            
            for i, size in enumerate(display_sizes, 1):
                print(f"\n{i}. 测试显示尺寸: {size[0]}x{size[1]}")
                print("按任意键继续...")
                
                matcher.draw_matches(
                    source_path, results, 
                    f"测试尺寸 {size[0]}x{size[1]}", 
                    wait_key=True, 
                    max_display_size=size
                )
        else:
            print("未找到匹配结果")
            
    except Exception as e:
        print(f"测试失败: {e}")


def test_image_utils():
    """测试图像工具类"""
    print("\n=== 测试图像工具类 ===\n")
    
    try:
        # 创建测试图像
        test_image = np.random.randint(0, 255, (3000, 4000, 3), dtype=np.uint8)
        cv2.putText(test_image, "Test Image 3000x4000", (100, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        
        print("1. 测试图像缩放显示...")
        ImageUtils.show_image_with_scale(test_image, "测试图像工具", max_size=(800, 600))
        
        print("\n2. 测试图像网格...")
        # 创建多个测试图像
        images = []
        for i in range(4):
            img = np.random.randint(0, 255, (300, 400, 3), dtype=np.uint8)
            cv2.putText(img, f"Image {i+1}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            images.append(img)
        
        grid = ImageUtils.create_image_grid(images, max_cell_size=(200, 150))
        if grid is not None:
            ImageUtils.show_image_with_scale(grid, "图像网格", max_size=(1000, 600))
        
        print("\n3. 测试保存缩放图像...")
        success = ImageUtils.save_image_with_scale(test_image, "../tmp/test_utils_scaled.png", max_size=(800, 600))
        if success:
            print("✅ 保存成功")
        else:
            print("❌ 保存失败")
            
    except Exception as e:
        print(f"图像工具测试失败: {e}")


def test_coordinate_scaling():
    """测试坐标缩放"""
    print("\n=== 测试坐标缩放 ===\n")
    
    try:
        # 测试坐标
        test_coords = [(100, 200), (300, 400), (500, 600)]
        test_scale = 0.5
        
        print(f"原始坐标: {test_coords}")
        print(f"缩放比例: {test_scale}")
        
        # 缩放坐标
        scaled_coords = ImageUtils.scale_coordinates(test_coords, test_scale)
        print(f"缩放后坐标: {scaled_coords}")
        
        # 验证缩放
        for i, (orig, scaled) in enumerate(zip(test_coords, scaled_coords)):
            expected_x = int(orig[0] * test_scale)
            expected_y = int(orig[1] * test_scale)
            actual_x, actual_y = scaled
            
            if expected_x == actual_x and expected_y == actual_y:
                print(f"✅ 坐标 {i+1} 缩放正确")
            else:
                print(f"❌ 坐标 {i+1} 缩放错误: 期望({expected_x}, {expected_y}), 实际({actual_x}, {actual_y})")
                
    except Exception as e:
        print(f"坐标缩放测试失败: {e}")


def test_performance():
    """测试性能"""
    print("\n=== 测试性能 ===\n")
    
    matcher = ImageMatcher()
    
    source_path = "../tmp/2.png"
    template_path = "../tmp/answer.png"
    
    try:
        import time
        
        # 测试不同尺寸的性能
        sizes = [(1920, 1080), (1200, 800), (800, 600), (600, 400)]
        
        for size in sizes:
            print(f"测试尺寸: {size[0]}x{size[1]}")
            
            start_time = time.time()
            
            # 获取匹配结果
            results = matcher.template_match(source_path, template_path, threshold=0.7)
            
            if results:
                # 绘制结果
                matcher.draw_matches(source_path, results, "性能测试", 
                                   wait_key=False, max_display_size=size)
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            print(f"  耗时: {elapsed:.3f} 秒")
            
    except Exception as e:
        print(f"性能测试失败: {e}")


if __name__ == '__main__':
    print("图像缩放功能测试")
    print("=" * 40)
    
    # 运行所有测试
    test_scaling_functionality()
    test_image_utils()
    test_coordinate_scaling()
    test_performance()
    
    print("\n" + "=" * 40)
    print("所有测试完成！") 