import json
from openai import OpenAI

client = OpenAI(
    api_key=open(".env").read().split("=")[1].strip(),
    base_url="https://api.deepseek.com"
)

# 模拟一段真实的招聘信息(以后可以换成你从BOSS直聘上爬的JD)
jd = """招聘Python开发实习生,工作地点厦门,要求熟悉Docker和MySQL,
每周可实习4天以上,转正机会大。"""

resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content":
        f"从下面的招聘信息中抽取信息,严格输出JSON,格式为:"
        f'{{"岗位":"","城市":"","技能":[],"亮点":[]}}\n\n{jd}'}],
    response_format={"type": "json_object"}   # 强制模型输出合法JSON
)

# 把模型返回的JSON文字解析成Python字典
data = json.loads(resp.choices[0].message.content)

# 按字段取值,验证真的能用
print("岗位:", data["岗位"])
print("城市:", data["城市"])
print("技能:", data["技能"])
print("亮点:", data["亮点"])