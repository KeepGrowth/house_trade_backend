"""
将需要比较的两个句子各自变成字符级向量；
计算句子之间的余弦相似度，得分区间在-1~1之间，越靠近1，表示两句话的描述越相似。
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter


# ---------------------- 核心：无语料库的文本相似度计算函数 ----------------------
def ngram_chars(s: str, n: int = 2) -> list:
    """生成字符级N-Gram（默认2-gram，适合中文短文本）"""
    if not isinstance(s, str) or len(s) < n:
        return []
    return [s[i:i + n] for i in range(len(s) - n + 1)]


def calculate_cosine_similarity(s1: str, s2: str, n: int = 2) -> float:
    """
    无语料库的字符级N-Gram余弦相似度计算
    :param s1: 目标文本（基准）
    :param s2: 待匹配文本
    :param n: N-Gram维度，默认2
    :return: 相似度分数（0~1）
    """
    # 空值处理
    if not s1 or not s2:
        return 0.0

    # 生成N-Gram
    g1 = ngram_chars(s1, n)
    g2 = ngram_chars(s2, n)

    # 无有效N-Gram时返回0
    if not g1 or not g2:
        return 0.0

    # 构建全局N-Gram集合
    all_grams = list(set(g1 + g2))

    # 生成向量（词频计数）
    v1 = np.array([Counter(g1)[g] for g in all_grams])
    v2 = np.array([Counter(g2)[g] for g in all_grams])

    # 计算余弦相似度
    score = cosine_similarity([v1], [v2])[0][0]
    # 处理浮点精度问题（避免负数）
    return max(0.0, min(1.0, float(score)))
