import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.metrics.pairwise import cosine_similarity

# =================配置区域=================
# 数据库连接字符串 (请根据你的实际配置修改)
# 格式: mysql+pymysql://用户名:密码@主机:端口/数据库名
DB_URI = 'mysql+pymysql://root:mysql_bhjbrr@192.168.1.86:3306/house_price_trade_system'
engine = create_engine(DB_URI)

# 目标：为哪个房源做推荐？(例如：house_id = 1001)
TARGET_HOUSE_ID = 1
# 推荐数量
TOP_N = 30


# =========================================

def get_interaction_data(engine):
    """
    从数据库读取交互数据并合并
    """
    print("正在读取数据库...")

    # 1. 读取收藏表
    df_fav = pd.read_sql("SELECT user_id, house_id FROM favorites", engine)
    # 标记行为类型，收藏权重设为 1
    if not df_fav.empty:
        df_fav['score'] = 1

        # 2. 读取评价表 (只取显示且评分>=3的)
    df_rev = pd.read_sql("SELECT user_id, house_id, score FROM reviews WHERE status=1 AND score >= 3", engine)

    # 3. 合并数据
    # 如果同一个用户既收藏又评价了同一个房源，取最高分或简单合并去重
    df_all = pd.concat([df_fav, df_rev], ignore_index=True)

    # 去重：保留每个用户对每个房源的最高分 (简单处理：直接去重，因为收藏和评价可能重复)
    # 这里我们假设只要有过交互就算，不区分具体分值，或者你可以按 user_id, house_id 分组求平均分
    df_interactions = df_all.drop_duplicates(subset=['user_id', 'house_id'])

    print(f"共读取到 {len(df_interactions)} 条有效交互记录。")
    return df_interactions


def build_item_cf_model(df_interactions):
    """
    构建 ItemCF 模型并计算相似度矩阵
    """
    # 1. 构建 用户-物品 评分矩阵 (User-Item Matrix)
    # 行：user_id, 列：house_id, 值：1 (存在交互即为1)
    user_item_matrix = df_interactions.pivot_table(
        index='user_id',
        columns='house_id',
        values='score',
        fill_value=0
    )

    # 2. 转置得到 物品-用户 矩阵 (Item-User Matrix)
    # 这样每一行代表一个房源，每一列代表一个用户
    item_user_matrix = user_item_matrix.T

    print(f"物品-用户矩阵形状: {item_user_matrix.shape}")

    # 3. 计算余弦相似度
    # cosine_similarity 计算的是行与行之间的相似度
    item_similarity_matrix = cosine_similarity(item_user_matrix)

    # 将结果转换回 DataFrame，方便查看
    # 索引和列名都是 house_id
    similarity_df = pd.DataFrame(
        item_similarity_matrix,
        index=item_user_matrix.index,
        columns=item_user_matrix.index
    )

    return similarity_df


def recommend_top30(similarity_df, target_house_id, top_n=30):
    """
    根据相似度矩阵推荐 Top N
    """
    if target_house_id not in similarity_df.index:
        return f"房源 {target_house_id} 没有足够的交互数据，无法计算相似度（冷启动）。"

    # 获取目标房源与其他所有房源的相似度
    # sort_values 升序排列，取最后 top_n+1 个（包含自己），然后去掉自己
    similar_scores = similarity_df[target_house_id].sort_values(ascending=False)

    # 排除掉自己 (相似度为1.0的那个)
    similar_scores = similar_scores.drop(labels=target_house_id, errors='ignore')

    # 取 Top N
    top_recommendations = similar_scores.head(top_n)

    return top_recommendations


# =================主执行流程=================

def get_recommend_houses_list():
    # 1. 获取数据
    df_data = get_interaction_data(engine)

    if df_data.empty:
        print("数据为空，无法进行推荐。")
    else:
        # 2. 训练模型 (计算相似度矩阵)
        sim_matrix = build_item_cf_model(df_data)

        # 3. 获取推荐结果
        result = recommend_top30(sim_matrix, TARGET_HOUSE_ID, TOP_N)

        # 4. 打印结果
        print(f"\n--- 针对房源 {TARGET_HOUSE_ID} 的 Top {TOP_N} 相似房源推荐 ---")
        if isinstance(result, pd.Series):
            print(result)
            # 将index转为房源id列表
            result = result.index.tolist()
            print(result)
        else:
            print(result)
            return None

if __name__ == "__main__":
    get_recommend_houses_list()

