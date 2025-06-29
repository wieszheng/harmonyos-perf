# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/28 13:02
@Author   : wieszheng
@Software : PyCharm
"""
from typing import Union, List, Dict, Optional, Tuple

import cv2
import numpy as np
from loguru import logger


def imread(file_path: str) -> np.ndarray:
    """
    读取图片
    :param file_path: 图片路径
    :return: OpenCV格式的图片对象
    """
    return cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)


def _create_sift(edge_threshold=100, contrast_threshold=0.04, sigma=1.6) -> cv2.SIFT:
    """
    创建SIFT特征检测器
    :param edge_threshold:
    :param contrast_threshold:
    :param sigma:
    :return:
    """
    if hasattr(cv2, 'SIFT_create'):
        return cv2.SIFT_create(
            edgeThreshold=edge_threshold,
            contrastThreshold=contrast_threshold,
            sigma=sigma
        )
    else:
        return cv2.xfeatures2d.SIFT_create(edgeThreshold=edge_threshold)


def template_match(
        source_image: Union[str, np.ndarray],
        template_image: Union[str, np.ndarray],
        threshold: float = 0.8
) -> Optional[Tuple[int, int]]:
    """
    模板匹配，返回匹配度最大的中心坐标
    :param source_image: 源图像
    :param template_image: 模板图像
    :param threshold: 匹配阈值
    :return: 中心坐标 (x, y) 或 None
    """
    # 读取图像
    if isinstance(source_image, str):
        source_img = imread(source_image)
    else:
        source_img = source_image.copy()

    if isinstance(template_image, str):
        template_img = imread(template_image)
    else:
        template_img = template_image.copy()

    # 执行模板匹配
    result = cv2.matchTemplate(source_img, template_img, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    logger.debug("实际最大相似度为 %.2f, 期望相似度为 %.2f  %s" % (max_val, threshold, template_image))
    if max_val >= threshold:
        template_h, template_w = template_img.shape[:2]
        center_x = max_loc[0] + template_w // 2
        center_y = max_loc[1] + template_h // 2
        return center_x, center_y

    return None


def sift_match(
        source_image: Union[str, np.ndarray],
        template_image: Union[str, np.ndarray],
        min_match_count: int = 10,
        good_ratio: float = 0.7
) -> Optional[Tuple[int, int]]:
    """
    SIFT匹配，返回匹配度最大的中心坐标
    :param source_image: 源图像
    :param template_image: 模板图像
    :param min_match_count: 最小匹配特征点数
    :param good_ratio: 良好匹配比例
    :return: 中心坐标 (x, y) 或 None
    """
    # 读取图像
    if isinstance(source_image, str):
        source_img = imread(source_image)
    else:
        source_img = source_image.copy()

    if isinstance(template_image, str):
        template_img = imread(template_image)
    else:
        template_img = template_image.copy()

    sift = _create_sift()
    kp_sch, des_sch = sift.detectAndCompute(template_img, None)
    kp_src, des_src = sift.detectAndCompute(source_img, None)

    if des_sch is None or des_src is None or len(kp_sch) < 2 or len(kp_src) < 2:
        return None

    FLANN_INDEX_KDTREE = 0
    flann_matcher = cv2.FlannBasedMatcher({'algorithm': FLANN_INDEX_KDTREE, 'trees': 5}, dict(checks=50))
    matches = flann_matcher.knnMatch(des_sch, des_src, k=2)

    # 测试筛选好的匹配点
    good_matches = []
    for match_pair in matches:
        if len(match_pair) == 2:
            m, n = match_pair
            if m.distance < good_ratio * n.distance:
                good_matches.append(m)
    logger.debug("匹配到 %d 个相同特征点, 期望最小匹配点数为 %d" % (len(good_matches), min_match_count))
    if len(good_matches) < min_match_count:
        return None

    # 提取匹配点的坐标
    src_pts = np.float32([kp_sch[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    img_pts = np.float32([kp_src[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    # 计算单应性矩阵
    H, mask = cv2.findHomography(src_pts, img_pts, cv2.RANSAC, 5.0)

    if H is None:
        return None

    # 计算模板图像的四个角点
    h, w = template_img.shape[:2]
    pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)

    # 变换到源图像中的位置
    dst = cv2.perspectiveTransform(pts, H)

    # 计算中心点
    center_x = int(np.mean(dst[:, 0, 0]))
    center_y = int(np.mean(dst[:, 0, 1]))

    return center_x, center_y


def find_image(source_image: Union[str, np.ndarray],
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
        return template_match(source_image, template_image, threshold=threshold)
    elif method.lower() == 'sift':
        min_match_count = kwargs.get('min_match_count', 10)
        good_ratio = kwargs.get('good_ratio', 0.7)
        return sift_match(source_image, template_image,
                          min_match_count=min_match_count,
                          good_ratio=good_ratio)
    else:
        raise ValueError(f"不支持的匹配方法: {method}")


if __name__ == '__main__':
    source_path = "../tmp/2.png"
    template_path = "../tmp/213.png"
    result = find_image(source_path, template_path, method='sift', min_match_count=16)
    print(result)
    result = find_image(source_path, template_path, min_match_count=16)
    print(result)
