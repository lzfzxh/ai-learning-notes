# ===== 导入区:所有要用的工具箱,一次备齐 =====
import json                      # 解析模型传来的参数(JSON格式)
import requests                  # 发HTTP请求,查天气用
from datetime import datetime    # 查当前日期
from openai import OpenAI       # 调用DeepSeek

# ===== 连接 DeepSeek =====
client = OpenAI(
    api_key=open(".env").read().split("=")[1].strip(),
    base_url="https://api.deepseek.com"
)

# ===== 工具1:查日期(你的代码,模型只能"点单"不能执行)=====
def get_current_date():
    return datetime.now().strftime("%Y年%m月%d日 %A")

# ===== 工具2:查天气(两个参数:城市、日期)=====
def get_current_weather(city, date):
    try:
        # 调免费天气服务wttr.in,不需要注册任何账号
        r = requests.get(f"https://wttr.in/{city}?format=j1", timeout=10)
        w = r.json()["current_condition"][0]
        desc = w["weatherDesc"][0]["value"]       # 天气描述(英文,如Sunny)
        return f"{city} 当前气温 {w['temp_C']} 摄氏度,天气 {desc}"
    except Exception:
        # 网络不好时给演示数据,保证程序不崩
        return f"{city} {date}: 晴,18到26度(演示数据)"

# ===== 工具说明书:两张传单,一起递给模型 =====
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "获取今天的日期和星期几",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "查询某个城市某天的天气情况",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名,如厦门"},
                    "date": {"type": "string", "description": "日期,如2026-11-27"}
                },
                "required": ["city"]
            }
        }
    }
]

# ===== 工具执行总调度:模型点哪道菜,就做哪道菜 =====
def run_tool(name, args):
    if name == "get_current_date":
        return get_current_date()
    elif name == "get_current_weather":
        return get_current_weather(args["city"], args.get("date", "今天"))
    else:
        return f"工具{name}不存在"          # 防御:防止模型点菜单外的菜

# ===== 主循环 =====
messages = []
print("问吧(今天星期几/今天适合穿什么/我叫张三……),输入'退出'结束")

while True:
    q = input("\n你: ")
    if q == "退出":
        break

    messages.append({"role": "user", "content": q})

    # 第一次调用:带上工具说明书
    resp = client.chat.completions.create(
        model="deepseek-chat", messages=messages, tools=tools)
    msg = resp.choices[0].message

    if msg.tool_calls:
        # 模型点了单(可能一次点多个,用for逐个处理)
        messages.append(msg)                       # 点单条先记入本子
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)   # 解析模型填的参数
            result = run_tool(tc.function.name, args)  # 执行对应工具
            print(f"(调用工具 {tc.function.name},参数 {args})")
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })
        # 第二次调用:模型拿到工具结果,生成人话回答
        resp2 = client.chat.completions.create(
            model="deepseek-chat", messages=messages)
        answer = resp2.choices[0].message.content
    else:
        answer = msg.content                # 模型直接回答,不需要工具

    print(answer)
    messages.append({"role": "assistant", "content": answer})