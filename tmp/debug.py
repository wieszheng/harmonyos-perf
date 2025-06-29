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
from typing import List, Tuple, Optional, Dict, Union


class ImageMatcher:
    """图像匹配器类，支持模板匹配和SIFT特征匹配"""
    
    def __init__(self):
        self.sift = self._create_sift()
        self.flann_matcher = self._create_flann_matcher()
    
    def _create_sift(self, edge_threshold=100, contrast_threshold=0.04, sigma=1.6):
        """创建SIFT特征检测器"""
        if hasattr(cv2, 'SIFT_create'):
            return cv2.SIFT_create(
                edgeThreshold=edge_threshold,
                contrastThreshold=contrast_threshold,
                sigma=sigma
            )
        else:
            return cv2.xfeatures2d.SIFT_create(edgeThreshold=edge_threshold)
    
    def _create_flann_matcher(self):
        """创建FLANN特征匹配器"""
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        return cv2.FlannBasedMatcher(index_params, search_params)
    
    def imread(self, file_path: str) -> np.ndarray:
        """
        读取图片
        :param file_path: 图片路径
        :return: OpenCV格式的图片对象
        """
        return cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    
    def template_match(self, 
                      source_image: Union[str, np.ndarray], 
                      template_image: Union[str, np.ndarray],
                      threshold: float = 0.8,
                      method: int = cv2.TM_CCOEFF_NORMED,
                      max_results: int = 1) -> List[Dict]:
        """
        模板匹配算法
        :param source_image: 源图像（大图）
        :param template_image: 模板图像（小图）
        :param threshold: 匹配阈值
        :param method: 匹配方法
        :param max_results: 最大返回结果数
        :return: 匹配结果列表
        """
        # 读取图像
        if isinstance(source_image, str):
            source_img = self.imread(source_image)
        else:
            source_img = source_image.copy()
            
        if isinstance(template_image, str):
            template_img = self.imread(template_image)
        else:
            template_img = template_image.copy()
        
        # 执行模板匹配
        result = cv2.matchTemplate(source_img, template_img, method)

        # 获取模板尺寸
        template_h, template_w = template_img.shape[:2]
        
        # 查找所有匹配位置
        locations = np.where(result >= threshold)
        matches = []
        
        for pt in zip(*locations[::-1]):  # 转换坐标
            x, y = pt
            center_x = x + template_w // 2
            center_y = y + template_h // 2
            
            # 计算置信度
            confidence = result[y, x]
            
            # 构建矩形坐标
            rectangle = [
                (x, y),  # 左上角
                (x + template_w, y),  # 右上角
                (x + template_w, y + template_h),  # 右下角
                (x, y + template_h)  # 左下角
            ]
            
            matches.append({
                'center': (center_x, center_y),
                'top_left': (x, y),
                'rectangle': rectangle,
                'confidence': float(confidence),
                'method': 'template'
            })
        
        # 按置信度排序并限制结果数量
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        return matches[:max_results]
    
    def sift_match(self, 
                   source_image: Union[str, np.ndarray], 
                   template_image: Union[str, np.ndarray],
                   min_match_count: int = 10,
                   good_ratio: float = 0.7,
                   max_results: int = 1) -> List[Dict]:
        """
        SIFT特征匹配算法
        :param source_image: 源图像
        :param template_image: 模板图像
        :param min_match_count: 最小匹配特征点数
        :param good_ratio: 良好匹配比例
        :param max_results: 最大返回结果数
        :return: 匹配结果列表
        """
        # 读取图像
        if isinstance(source_image, str):
            source_img = self.imread(source_image)
        else:
            source_img = source_image.copy()
            
        if isinstance(template_image, str):
            template_img = self.imread(template_image)
        else:
            template_img = template_image.copy()
        
        # 检测SIFT特征点和描述符
        kp1, des1 = self.sift.detectAndCompute(template_img, None)
        kp2, des2 = self.sift.detectAndCompute(source_img, None)
        
        if des1 is None or des2 is None or len(kp1) < 2 or len(kp2) < 2:
            return []
        
        # 特征匹配
        matches = self.flann_matcher.knnMatch(des1, des2, k=2)
        
        # 应用Lowe's ratio测试筛选好的匹配点
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < good_ratio * n.distance:
                    good_matches.append(m)
        
        if len(good_matches) < min_match_count:
            return []
        
        # 提取匹配点的坐标
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        
        # 计算单应性矩阵
        H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        
        if H is None:
            return []
        
        # 计算模板图像的四个角点
        h, w = template_img.shape[:2]
        pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
        
        # 变换到源图像中的位置
        dst = cv2.perspectiveTransform(pts, H)
        
        # 计算中心点
        center_x = int(np.mean(dst[:, 0, 0]))
        center_y = int(np.mean(dst[:, 0, 1]))
        
        # 构建矩形坐标
        rectangle = [(int(dst[i, 0, 0]), int(dst[i, 0, 1])) for i in range(4)]
        
        # 计算置信度
        confidence = len(good_matches) / len(matches)
        
        return [{
            'center': (center_x, center_y),
            'rectangle': rectangle,
            'confidence': confidence,
            'method': 'sift',
            'match_count': len(good_matches)
        }]
    
    def draw_matches(self, 
                    source_image: Union[str, np.ndarray], 
                    matches: List[Dict],
                    window_name: str = "匹配结果",
                    wait_key: bool = True,
                    max_display_size: Tuple[int, int] = (1920, 1080)) -> np.ndarray:
        """
        在源图像上绘制匹配结果
        :param source_image: 源图像
        :param matches: 匹配结果列表
        :param window_name: 窗口名称
        :param wait_key: 是否等待按键
        :param max_display_size: 最大显示尺寸 (width, height)
        :return: 绘制了匹配结果的图像
        """
        # 读取图像
        if isinstance(source_image, str):
            img = self.imread(source_image)
        else:
            img = source_image.copy()
        
        # 检查是否需要缩放
        original_height, original_width = img.shape[:2]
        max_width, max_height = max_display_size
        
        # 计算缩放比例
        scale_x = max_width / original_width if original_width > max_width else 1.0
        scale_y = max_height / original_height if original_height > max_height else 1.0
        scale = min(scale_x, scale_y)
        
        # 如果需要缩放
        if scale < 1.0:
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            img = cv2.resize(img, (new_width, new_height))
            
            # 缩放匹配结果坐标
            scaled_matches = []
            for match in matches:
                scaled_match = match.copy()
                
                # 缩放中心点
                if 'center' in scaled_match:
                    x, y = scaled_match['center']
                    scaled_match['center'] = (int(x * scale), int(y * scale))
                
                # 缩放左上角点
                if 'top_left' in scaled_match:
                    x, y = scaled_match['top_left']
                    scaled_match['top_left'] = (int(x * scale), int(y * scale))
                
                # 缩放矩形坐标
                if 'rectangle' in scaled_match:
                    scaled_rectangle = []
                    for pt in scaled_match['rectangle']:
                        x, y = pt
                        scaled_rectangle.append((int(x * scale), int(y * scale)))
                    scaled_match['rectangle'] = scaled_rectangle
                
                scaled_matches.append(scaled_match)
            
            matches = scaled_matches
            print(f"图像已缩放: {original_width}x{original_height} -> {new_width}x{new_height} (缩放比例: {scale:.2f})")
        
        # 为不同方法设置不同颜色
        colors = {
            'template': (0, 255, 0),    # 绿色
            'sift': (255, 0, 0)         # 蓝色
        }
        
        for i, match in enumerate(matches):
            method = match.get('method', 'template')
            color = colors.get(method, (0, 255, 255))
            
            # 绘制矩形框
            if 'rectangle' in match:
                rectangle = match['rectangle']
                if len(rectangle) == 4:
                    # 绘制矩形
                    pts = np.array(rectangle, np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    cv2.polylines(img, [pts], True, color, 2)
                    
                    # 绘制角点
                    for pt in rectangle:
                        cv2.circle(img, pt, 5, color, -1)
            
            # 绘制中心点
            if 'center' in match:
                center = match['center']
                cv2.circle(img, center, 8, color, -1)
                cv2.circle(img, center, 10, (255, 255, 255), 2)
                
                # 添加标签
                label = f"{method.upper()}-{i+1}"
                cv2.putText(img, label, (center[0] + 15, center[1] - 15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                # 显示置信度
                if 'confidence' in match:
                    conf_text = f"Conf: {match['confidence']:.3f}"
                    cv2.putText(img, conf_text, (center[0] + 15, center[1] + 15), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # 添加缩放信息
        if scale < 1.0:
            info_text = f"缩放比例: {scale:.2f} (原始尺寸: {original_width}x{original_height})"
            cv2.putText(img, info_text, (10, img.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # 显示图像
        cv2.imshow(window_name, img)
        if wait_key:
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        return img
    
    def show_match_result(self, 
                         source_image: Union[str, np.ndarray], 
                         template_image: Union[str, np.ndarray],
                         method: str = 'template',
                         **kwargs) -> Optional[Tuple[int, int]]:
        """
        查找图像并显示匹配结果
        :param source_image: 源图像
        :param template_image: 模板图像
        :param method: 匹配方法
        :param kwargs: 其他参数
        :return: 中心坐标或None
        """
        # 执行匹配
        if method.lower() == 'template':
            threshold = kwargs.get('threshold', 0.8)
            results = self.template_match(source_image, template_image, threshold=threshold)
        elif method.lower() == 'sift':
            min_match_count = kwargs.get('min_match_count', 10)
            good_ratio = kwargs.get('good_ratio', 0.7)
            results = self.sift_match(source_image, template_image, 
                                    min_match_count=min_match_count, 
                                    good_ratio=good_ratio)
        else:
            raise ValueError(f"不支持的匹配方法: {method}")
        
        if results:
            # 显示匹配结果
            window_name = f"{method.upper()} 匹配结果"
            self.draw_matches(source_image, results, window_name)
            
            # 返回最佳匹配的坐标
            return results[0]['center']
        else:
            return None
    
    def show_all_matches(self, 
                        source_image: Union[str, np.ndarray], 
                        template_image: Union[str, np.ndarray],
                        method: str = 'template',
                        **kwargs) -> List[Dict]:
        """
        查找所有匹配结果并显示
        :param source_image: 源图像
        :param template_image: 模板图像
        :param method: 匹配方法
        :param kwargs: 其他参数
        :return: 匹配结果列表
        """
        results = self.find_all_matches(source_image, template_image, method, **kwargs)
        
        if results:
            # 显示匹配结果
            window_name = f"{method.upper()} 所有匹配结果"
            self.draw_matches(source_image, results, window_name)
            
            # 打印结果信息
            print(f"\n=== {method.upper()} 所有匹配结果 ===")
            print(f"找到 {len(results)} 个匹配:")
            for i, result in enumerate(results):
                print(f"结果 {i+1}: 中心点={result['center']}, 置信度={result['confidence']:.3f}")
                if 'match_count' in result:
                    print(f"  匹配特征点数: {result['match_count']}")
        else:
            print(f"{method.upper()} 匹配未找到任何目标")
        
        return results
    
    def find_image(self, 
                   source_image: Union[str, np.ndarray], 
                   template_image: Union[str, np.ndarray],
                   method: str = 'template',
                   **kwargs) -> Optional[Tuple[int, int]]:
        """
        查找图像并返回中心坐标
        :param source_image: 源图像
        :param template_image: 模板图像
        :param method: 匹配方法 ('template' 或 'sift')
        :param kwargs: 其他参数
        :return: 中心坐标 (x, y) 或 None
        """
        if method.lower() == 'template':
            threshold = kwargs.get('threshold', 0.8)
            results = self.template_match(source_image, template_image, threshold=threshold)
        elif method.lower() == 'sift':
            min_match_count = kwargs.get('min_match_count', 10)
            good_ratio = kwargs.get('good_ratio', 0.7)
            results = self.sift_match(source_image, template_image, 
                                    min_match_count=min_match_count, 
                                    good_ratio=good_ratio)
        else:
            raise ValueError(f"不支持的匹配方法: {method}")
        
        if results:
            return results[0]['center']
        return None
    
    def find_all_matches(self, 
                        source_image: Union[str, np.ndarray], 
                        template_image: Union[str, np.ndarray],
                        method: str = 'template',
                        **kwargs) -> List[Dict]:
        """
        查找所有匹配结果
        :param source_image: 源图像
        :param template_image: 模板图像
        :param method: 匹配方法
        :param kwargs: 其他参数
        :return: 匹配结果列表
        """
        if method.lower() == 'template':
            threshold = kwargs.get('threshold', 0.8)
            max_results = kwargs.get('max_results', 10)
            return self.template_match(source_image, template_image, 
                                     threshold=threshold, max_results=max_results)
        elif method.lower() == 'sift':
            min_match_count = kwargs.get('min_match_count', 10)
            good_ratio = kwargs.get('good_ratio', 0.7)
            max_results = kwargs.get('max_results', 10)
            return self.sift_match(source_image, template_image, 
                                 min_match_count=min_match_count, 
                                 good_ratio=good_ratio, 
                                 max_results=max_results)
        else:
            raise ValueError(f"不支持的匹配方法: {method}")


def demo():
    """演示函数"""
    matcher = ImageMatcher()
    
    # 示例图片路径（请根据实际情况修改）
    source_path = "../tmp/2.png"
    template_path = "../tmp/213.png"

    print("=== 模板匹配演示 ===")
    try:
        # 模板匹配并显示结果
        template_result = matcher.show_match_result(source_path, template_path, method='template', threshold=0.8)
        if template_result:
            print(f"模板匹配找到坐标: {template_result}")
        else:
            print("模板匹配未找到目标")
        
        # 查找所有模板匹配结果并显示
        all_template_results = matcher.show_all_matches(source_path, template_path, method='template', threshold=0.7)
        print(f"找到 {len(all_template_results)} 个模板匹配结果")
        
        print("\n=== SIFT匹配演示 ===")
        # SIFT匹配并显示结果
        sift_result = matcher.show_match_result(source_path, template_path, method='sift', min_match_count=8)
        if sift_result:
            print(f"SIFT匹配找到坐标: {sift_result}")
        else:
            print("SIFT匹配未找到目标")
        
        # 查找所有SIFT匹配结果并显示
        all_sift_results = matcher.show_all_matches(source_path, template_path, method='sift', min_match_count=5)
        print(f"找到 {len(all_sift_results)} 个SIFT匹配结果")
            
    except Exception as e:
        print(f"演示过程中出现错误: {e}")


if __name__ == '__main__':
    demo()
