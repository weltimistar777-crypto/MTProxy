import os
import subprocess
from telethon import TelegramClient, events

# --- НАСТРОЙКИ ---
API_ID = '37161438'
API_HASH = 'd11eb8e7380d599d14083e2ee5b7b0c0'
CHANNEL_USERNAME = 'mtproto_all'  # Твой канал
PROXY_FILE = 'new_proxy.txt'
CHECKPOINT_FILE = 'last_id.txt'

client = TelegramClient('session_name', API_ID, API_HASH)

def get_last_id():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as f:
            return int(f.read().strip())
    return 0

def save_last_id(msg_id):
    with open(CHECKPOINT_FILE, 'w') as f:
        f.write(str(msg_id))

def update_github():
    print("🚀 Отправка обновлений на GitHub...")
    try:
        subprocess.run(["git", "add", PROXY_FILE, CHECKPOINT_FILE], check=True)
        subprocess.run(["git", "commit", "-m", "Auto-update proxies from Telegram"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Данные на GitHub обновлены!")
    except Exception as e:
        print(f"❌ Ошибка Git: {e}")

async def main():
    last_id = get_last_id()
    new_proxies = []
    current_max_id = last_id

    print(f"🔍 Сканируем канал с сообщения №{last_id}...")

    async for message in client.iter_messages(CHANNEL_USERNAME, min_id=last_id, reverse=True):
        if message.reply_markup:
            # Разбираем кнопки (inline buttons)
            for row in message.reply_markup.rows:
                for button in row.buttons:
                    if hasattr(button, 'url') and 'proxy?' in button.url:
                        new_proxies.append(button.url)
        
        current_max_id = max(current_max_id, message.id)

    if new_proxies:
        with open(PROXY_FILE, 'a') as f:
            for proxy in new_proxies:
                f.write(f"{proxy}\n")
        
        save_last_id(current_max_id)
        print(f"✨ Найдено и добавлено новых прокси: {len(new_proxies)}")
        update_github()
    else:
        print("☕ Новых прокси пока нет.")

with client:
    client.loop.run_until_complete(main())

