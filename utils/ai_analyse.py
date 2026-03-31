import base64

from openai import OpenAI
import ollama
from ollama import Client
from ollama import AsyncClient
# 初始化客户端
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)


async def chat_with_ollama(model_name: str, user_prompt: str):
    """
    文本问答。
    :param model_name:
    :param user_prompt:
    :return:
    """

    system_content = """
    你是一个专业的二手房市场数据分析师。根据用户提供的后台统计数据，生成一段简洁、专业的总体运营情况描述（150字以内）.
    要求先总结整体市场活跃度，再分析供需关系（房源是否够卖），语气客观、专业。
    """
    try:
        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                # AI角色提示词
                {"role": "system",
                 "content": system_content},
                {"role": "user", "content": user_prompt}
            ],
            stream=False
        )

        # 获取回复内容
        content = response.choices[0].message.content
        return content

    except Exception as e:
        return f"发生错误: {e}"


def analyze_image_with_qwen(image_path, model_name="qwen3-vl:4b"):
    """
    图片问答。
    :param image_path:
    :param model_name:
    :return:
    """
    # 1. 读取并编码图片
    with open(image_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode('utf-8')

    # 确定图片格式 (简单判断后缀)
    suffix = image_path.split('.')[-1].lower()
    if suffix not in ['jpg', 'jpeg', 'png', 'webp']:
        suffix = 'jpeg'  # 默认

    image_url = f"data:image/{suffix};base64,{base64_image}"

    try:
        # 2. 发送请求
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "你是一名出色且专业的交通工程师，善于从各个角度解读图表，请根据这张图片的内容，深度分析图表所呈现的交通信息,200字左右，不需要markdown格式。"},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"调用失败: {e}"


async def chat_with_ollama1(model_name: str, user_prompt: str):
    system_content = """
    你是一个专业的二手房市场数据分析师。根据用户提供的后台统计数据，生成一段简洁、专业的总体运营情况描述（150字以内）.
    要求先总结整体市场活跃度，再分析供需关系（房源是否够卖），语气客观、专业。
    """

    try:
        # 使用 AsyncClient
        client = AsyncClient()
        response = await client.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_prompt}
            ]
        )

        content = response['message']['content']
        return content

    except Exception as e:
        return f"发生错误: {e}"


if __name__ == "__main__":
    model = "qwen3:4b"
    prompt = "天源路的平均拥堵率为0.125，平均通行效率为0.74，畅通时长占比为0.27，缓行时长占比为0.125"

    print(f"正在调用本地模型 {model} ...")
    result = chat_with_ollama(model, prompt)
    print("-" * 30)
    print(result)
    print("-" * 30)

    # img_file = "../save_figs/congested_counts.png"  # 替换为你的图片
    # # 如果 pull 失败，请改为 "qwen2.5-vl:7b" 或 "llava"
    # model_to_use = "qwen3-vl:4b"
    #
    # print(f"正在使用 {model_to_use} 识别图片...")
    # result = analyze_image_with_qwen(img_file, model_to_use)
    # print(result)
