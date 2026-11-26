from openai import OpenAI

client = OpenAI(
    api_key=open(".env").read().split("=")[1].strip(),
    base_url="https://api.deepseek.com"
)

stream = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "用一句话解释什么是大语言模型"}],
    stream=True,
)

for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="", flush=True)