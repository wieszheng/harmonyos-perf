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
from typing import Tuple, Optional, Union


class ImageUtils:
    """图像工具类，提供缩放、显示等功能"""
    
    @staticmethod
    def get_screen_size() -> Tuple[int, int]:
        """获取屏幕尺寸"""
        try:
            # 尝试获取屏幕尺寸
            screen = cv2.getWindowImageRect("temp")
            cv2.destroyAllWindows()
            return (1920, 1080)  # 默认值
        except:
            return (1920, 1080)  # 默认值
    
    @staticmethod
    def calculate_scale_factor(image_size: Tuple[int, int], 
                             max_size: Tuple[int, int]) -> float:
        """
        计算缩放比例
        :param image_size: 图像尺寸 (width, height)
        :param max_size: 最大尺寸 (width, height)
        :return: 缩放比例
        """
        width, height = image_size
        max_width, max_height = max_size
        
        scale_x = max_width / width if width > max_width else 1.0
        scale_y = max_height / height if height > max_height else 1.0
        
        return min(scale_x, scale_y)
    
    @staticmethod
    def resize_image(image: np.ndarray, 
                    scale: float, 
                    interpolation: int = cv2.INTER_AREA) -> np.ndarray:
        """
        缩放图像
        :param image: 输入图像
        :param scale: 缩放比例
        :param interpolation: 插值方法
        :return: 缩放后的图像
        """
        if scale == 1.0:
            return image
        
        height, width = image.shape[:2]
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        return cv2.resize(image, (new_width, new_height), interpolation=interpolation)
    
    @staticmethod
    def scale_coordinates(coordinates: Union[Tuple[int, int], list], 
                         scale: float) -> Union[Tuple[int, int], list]:
        """
        缩放坐标
        :param coordinates: 坐标或坐标列表
        :param scale: 缩放比例
        :return: 缩放后的坐标
        """
        if scale == 1.0:
            return coordinates
        
        if isinstance(coordinates, tuple):
            x, y = coordinates
            return (int(x * scale), int(y * scale))
        elif isinstance(coordinates, list):
            if all(isinstance(item, tuple) for item in coordinates):
                # 坐标列表
                return [(int(x * scale), int(y * scale)) for x, y in coordinates]
            else:
                # 单个坐标列表
                return [int(coord * scale) for coord in coordinates]
        
        return coordinates
    
    @staticmethod
    def show_image_with_scale(image: np.ndarray, 
                             window_name: str = "图像",
                             max_size: Tuple[int, int] = (1920, 1080),
                             wait_key: bool = True) -> np.ndarray:
        """
        显示图像（自动缩放）
        :param image: 输入图像
        :param window_name: 窗口名称
        :param max_size: 最大显示尺寸
        :param wait_key: 是否等待按键
        :return: 显示的图像
        """
        height, width = image.shape[:2]
        scale = ImageUtils.calculate_scale_factor((width, height), max_size)
        
        if scale < 1.0:
            display_image = ImageUtils.resize_image(image, scale)
            print(f"图像已缩放: {width}x{height} -> {display_image.shape[1]}x{display_image.shape[0]} (缩放比例: {scale:.2f})")
        else:
            display_image = image.copy()
        
        # 添加缩放信息
        if scale < 1.0:
            info_text = f"缩放比例: {scale:.2f} (原始尺寸: {width}x{height})"
            cv2.putText(display_image, info_text, (10, display_image.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow(window_name, display_image)
        if wait_key:
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        return display_image
    
    @staticmethod
    def create_image_grid(images: list, 
                         grid_size: Tuple[int, int] = None,
                         max_cell_size: Tuple[int, int] = (400, 300)) -> np.ndarray:
        """
        创建图像网格
        :param images: 图像列表
        :param grid_size: 网格尺寸 (rows, cols)，如果为None则自动计算
        :param max_cell_size: 每个单元格的最大尺寸
        :return: 网格图像
        """
        if not images:
            return None
        
        n_images = len(images)
        
        if grid_size is None:
            # 自动计算网格尺寸
            cols = int(np.ceil(np.sqrt(n_images)))
            rows = int(np.ceil(n_images / cols))
        else:
            rows, cols = grid_size
        
        # 调整图像尺寸
        resized_images = []
        for img in images:
            height, width = img.shape[:2]
            scale = ImageUtils.calculate_scale_factor((width, height), max_cell_size)
            resized = ImageUtils.resize_image(img, scale)
            resized_images.append(resized)
        
        # 找到最大尺寸
        max_height = max(img.shape[0] for img in resized_images)
        max_width = max(img.shape[1] for img in resized_images)
        
        # 创建网格
        grid_height = rows * max_height
        grid_width = cols * max_width
        
        # 创建空白网格
        if len(resized_images[0].shape) == 3:
            grid = np.zeros((grid_height, grid_width, 3), dtype=np.uint8)
        else:
            grid = np.zeros((grid_height, grid_width), dtype=np.uint8)
        
        # 填充图像
        for i, img in enumerate(resized_images):
            row = i // cols
            col = i % cols
            
            y_start = row * max_height
            x_start = col * max_width
            y_end = y_start + img.shape[0]
            x_end = x_start + img.shape[1]
            
            grid[y_start:y_end, x_start:x_end] = img
        
        return grid
    
    @staticmethod
    def save_image_with_scale(image: np.ndarray, 
                             output_path: str,
                             max_size: Tuple[int, int] = (1920, 1080)) -> bool:
        """
        保存图像（可选择缩放）
        :param image: 输入图像
        :param output_path: 输出路径
        :param max_size: 最大尺寸
        :return: 是否保存成功
        """
        try:
            height, width = image.shape[:2]
            scale = ImageUtils.calculate_scale_factor((width, height), max_size)
            
            if scale < 1.0:
                save_image = ImageUtils.resize_image(image, scale)
                print(f"保存缩放图像: {width}x{height} -> {save_image.shape[1]}x{save_image.shape[0]}")
            else:
                save_image = image
            
            success = cv2.imwrite(output_path, save_image)
            if success:
                print(f"图像已保存到: {output_path}")
            return success
            
        except Exception as e:
            print(f"保存图像失败: {e}")
            return False


def demo_image_utils():
    """演示图像工具功能"""
    print("=== 图像工具演示 ===\n")
    
    # 创建测试图像
    test_image = np.random.randint(0, 255, (2000, 3000, 3), dtype=np.uint8)
    
    print("1. 测试图像缩放显示...")
    ImageUtils.show_image_with_scale(test_image, "测试图像", max_size=(800, 600))
    
    print("\n2. 测试图像网格...")
    # 创建多个测试图像
    images = []
    for i in range(6):
        img = np.random.randint(0, 255, (200, 300, 3), dtype=np.uint8)
        cv2.putText(img, f"Image {i+1}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        images.append(img)
    
    grid = ImageUtils.create_image_grid(images, max_cell_size=(200, 150))
    if grid is not None:
        ImageUtils.show_image_with_scale(grid, "图像网格", max_size=(1200, 800))
    
    print("\n3. 测试保存功能...")
    ImageUtils.save_image_with_scale(test_image, "../tmp/test_scaled.png", max_size=(800, 600))


if __name__ == '__main__':
    demo_image_utils() 