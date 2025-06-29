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
from debug import ImageMatcher


def demo_sift_vs_template():
    """演示SIFT和模板匹配在不同场景下的表现"""
    matcher = ImageMatcher()
    
    print("=== SIFT vs 模板匹配对比演示 ===\n")
    
    # 测试场景1: 完全相同的图像
    print("场景1: 完全相同的图像")
    try:
        source_path = "../tmp/2.png"
        template_path = "../tmp/213.png"
        
        # 模板匹配
        template_result = matcher.find_image(source_path, template_path, method='template', threshold=0.8)
        print(f"  模板匹配结果: {template_result}")
        
        # SIFT匹配
        sift_result = matcher.find_image(source_path, template_path, method='sift', min_match_count=8)
        print(f"  SIFT匹配结果: {sift_result}")
        
    except Exception as e:
        print(f"  错误: {e}")
    
    print("\n" + "="*50 + "\n")


def explain_sift_advantages():
    """解释SIFT算法的优势"""
    print("=== SIFT算法优势说明 ===\n")
    
    advantages = [
        {
            "场景": "图标大小变化",
            "描述": "当图标在大图中被放大或缩小时",
            "模板匹配": "❌ 无法匹配",
            "SIFT匹配": "✅ 可以匹配"
        },
        {
            "场景": "图标旋转",
            "描述": "当图标旋转一定角度时",
            "模板匹配": "❌ 无法匹配",
            "SIFT匹配": "✅ 可以匹配"
        },
        {
            "场景": "光照变化",
            "描述": "当图像亮度发生变化时",
            "模板匹配": "⚠️ 可能失败",
            "SIFT匹配": "✅ 相对稳定"
        },
        {
            "场景": "完全相同的图像",
            "描述": "查找完全相同的图像时",
            "模板匹配": "✅ 速度快，准确",
            "SIFT匹配": "✅ 准确但较慢"
        },
        {
            "场景": "文字识别",
            "描述": "查找文字内容时",
            "模板匹配": "✅ 适合固定字体",
            "SIFT匹配": "✅ 适合不同字体"
        },
        {
            "场景": "UI元素",
            "描述": "查找按钮、图标等UI元素",
            "模板匹配": "✅ 适合固定UI",
            "SIFT匹配": "✅ 适合动态UI"
        }
    ]
    
    for i, advantage in enumerate(advantages, 1):
        print(f"{i}. {advantage['场景']}")
        print(f"   {advantage['描述']}")
        print(f"   模板匹配: {advantage['模板匹配']}")
        print(f"   SIFT匹配: {advantage['SIFT匹配']}")
        print()


def sift_for_ui_elements():
    """演示SIFT在UI元素查找中的应用"""
    print("=== SIFT在UI元素查找中的应用 ===\n")
    
    ui_elements = [
        "按钮图标",
        "菜单项",
        "工具栏图标", 
        "状态指示器",
        "导航元素",
        "功能图标"
    ]
    
    print("SIFT算法特别适合查找以下UI元素：")
    for i, element in enumerate(ui_elements, 1):
        print(f"{i}. {element}")
    
    print("\n原因：")
    print("- UI元素经常会有大小变化（不同分辨率）")
    print("- 有时会有轻微的旋转或倾斜")
    print("- 在不同主题下可能有颜色变化")
    print("- SIFT可以处理这些变化")


def practical_tips():
    """实用建议"""
    print("\n=== 实用建议 ===\n")
    
    tips = [
        "1. 模板匹配适合：完全相同的图像，速度快",
        "2. SIFT匹配适合：相似但不完全相同的图像",
        "3. 对于UI自动化：建议先用模板匹配，失败时再用SIFT",
        "4. SIFT参数调整：",
        "   - min_match_count: 8-15 (越小越宽松)",
        "   - good_ratio: 0.6-0.8 (越小越严格)",
        "5. 性能优化：",
        "   - 缩小图像尺寸",
        "   - 使用ROI（感兴趣区域）",
        "   - 缓存特征点"
    ]
    
    for tip in tips:
        print(tip)


def create_test_scenario():
    """创建测试场景建议"""
    print("\n=== 测试场景建议 ===\n")
    
    scenarios = [
        {
            "名称": "图标查找",
            "描述": "在应用界面中查找功能图标",
            "推荐方法": "SIFT",
            "原因": "图标可能有大小变化"
        },
        {
            "名称": "文字查找", 
            "描述": "查找特定文字内容",
            "推荐方法": "模板匹配",
            "原因": "文字通常固定不变"
        },
        {
            "名称": "按钮查找",
            "描述": "查找可点击的按钮",
            "推荐方法": "SIFT",
            "原因": "按钮可能有状态变化"
        },
        {
            "名称": "截图对比",
            "描述": "对比两张截图是否相同",
            "推荐方法": "模板匹配",
            "原因": "速度快，适合批量处理"
        }
    ]
    
    for scenario in scenarios:
        print(f"场景: {scenario['名称']}")
        print(f"描述: {scenario['描述']}")
        print(f"推荐方法: {scenario['推荐方法']}")
        print(f"原因: {scenario['原因']}")
        print()


if __name__ == '__main__':
    explain_sift_advantages()
    sift_for_ui_elements()
    practical_tips()
    create_test_scenario()
    demo_sift_vs_template() 