import requests
BOT_TOKEN = '8388787458:AAHio7R_c6R2mddfSdf2gW-29npO_j-Sywc'
CHAT_ID = '7825502104'

message = "Hello! Đây là tin nhắn gửi bằng Python 🚀"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

data = {
    "chat_id": CHAT_ID,
    "text": message
}

response = requests.post(url, data=data)

print(response.json())