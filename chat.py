from openai import OpenAI

client = OpenAI(
    api_key=open(".env").read().split("=")[1].strip(),
    base_url="https://api.deepseek.com"
)

messages = []

while True:
    q = input("\n你: ")
    if q == "退出":
        break

    messages.append({"role": "user", "content": q})

    stream = client.chat.completions.create(
        model="deepseek-chat", messages=messages, stream=True
    )

    full = ""

    for chunk in stream:
        piece = chunk.choices[0].delta.content or ""
        full += piece
        print(piece, end="", flush=True)

    messages.append({"role": "assistant", "content": "full"})