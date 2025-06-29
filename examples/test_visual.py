# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/29 12:05
@Author   : wieszheng
@Software : PyCharm
"""

import cv2
from tmp.debug import ImageMatcher


def test_basic_visualization():
    """测试基础可视化功能"""
    print("=== 测试基础可视化功能 ===")
    
    matcher = ImageMatcher()
    
    # 测试图片路径
    source_path = "../tmp/2.png"
    template_path = "../tmp/answer.png"
    
    try:
        print("1. 测试模板匹配可视化...")
        result = matcher.show_match_result(
            source_path, template_path, 
            method='template', 
            threshold=0.7
        )
        
        if result:
            print(f"✅ 模板匹配成功，坐标: {result}")
        else:
            print("❌ 模板匹配失败")
        
        print("\n2. 测试SIFT匹配可视化...")
        result = matcher.show_match_result(
            source_path, template_path, 
            method='sift', 
            min_match_count=5
        )
        
        if result:
            print(f"✅ SIFT匹配成功，坐标: {result}")
        else:
            print("❌ SIFT匹配失败")
            
        print("\n✅ 基础可视化测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")


def test_custom_drawing():
    """测试自定义绘制功能"""
    print("\n=== 测试自定义绘制功能 ===")
    
    matcher = ImageMatcher()
    
    source_path = "../tmp/2.png"
    template_path = "../tmp/213.png"
    
    try:
        # 获取匹配结果
        template_results = matcher.template_match(source_path, template_path, threshold=0.7)
        sift_results = matcher.sift_match(source_path, template_path, min_match_count=5)
        
        # 合并结果
        all_results = template_results + sift_results
        
        if all_results:
            print(f"找到 {len(all_results)} 个匹配结果")
            
            # 自定义绘制
            img = matcher.draw_matches(source_path, all_results, "测试结果", wait_key=False)
            
            # 添加测试信息
            cv2.putText(img, "Test Visualization", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(img, f"Total Matches: {len(all_results)}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # 显示结果
            cv2.imshow("自定义测试结果", img)
            print("按任意键关闭窗口...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
            print("✅ 自定义绘制测试完成")
        else:
            print("❌ 未找到匹配结果")
            
    except Exception as e:
        print(f"❌ 自定义绘制测试失败: {e}")


def test_save_result():
    """测试保存结果功能"""
    print("\n=== 测试保存结果功能 ===")
    
    matcher = ImageMatcher()
    
    source_path = "../tmp/2.png"
    template_path = "../tmp/213.png"
    
    try:
        # 获取匹配结果
        results = matcher.template_match(source_path, template_path, threshold=0.7)
        
        if results:
            # 绘制结果
            result_img = matcher.draw_matches(source_path, results, wait_key=False)
            
            # 保存结果
            output_path = "../tmp/test_result.png"
            success = cv2.imwrite(output_path, result_img)
            
            if success:
                print(f"✅ 结果已保存到: {output_path}")
                
                # 显示保存的图像
                cv2.imshow("保存的测试结果", result_img)
                print("按任意键关闭窗口...")
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            else:
                print("❌ 保存失败")
        else:
            print("❌ 未找到匹配结果")
            
    except Exception as e:
        print(f"❌ 保存结果测试失败: {e}")


def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    
    matcher = ImageMatcher()
    
    try:
        # 测试不存在的文件
        result = matcher.show_match_result(
            "不存在的文件.png", 
            "不存在的模板.png", 
            method='template'
        )
        
        if result is None:
            print("✅ 错误处理正常")
        else:
            print("❌ 错误处理异常")
            
    except Exception as e:
        print(f"✅ 正确捕获异常: {e}")


if __name__ == '__main__':
    print("图像匹配可视化功能测试")
    print("=" * 40)
    
    # 运行所有测试
    test_basic_visualization()
    test_custom_drawing()
    test_save_result()
    test_error_handling()
    
    print("\n" + "=" * 40)
    print("所有测试完成！") 