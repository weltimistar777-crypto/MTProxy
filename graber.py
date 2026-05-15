import os
import subprocess
from datetime import datetime, timedelta
from telethon import TelegramClient, events

# --- НАСТРОЙКИ ---
API_ID = '37161438'
API_HASH = 'd11eb8e7380d599d14083e2ee5b7b0c0'
CHANNEL_USERNAME = 'mtproto_all' 

PROXY_FILE = 'proxy.txt'
ARCHIVE_FILE = 'archives.txt'
CHECKPOINT_FILE = 'last_id.txt'
CLEAN_DATE_FILE = 'last_clean.txt'

client = TelegramClient('session_name', API_ID, API_HASH)

def check_cleanup():
    """Проверяет, прошло ли 5 дней с последней очистки архива"""
    now = datetime.now()
    if os.path.exists(CLEAN_DATE_FILE):
        with open(CLEAN_DATE_FILE, 'r') as f:
            last_clean = datetime.fromisoformat(f.read().strip())
    else:
        last_clean = now

    if (now - last_clean).days >= 5:
        print("🧹 Прошло 5 дней. Чистим архив...")
        with open(ARCHIVE_FILE, 'w') as f:
            f.write(f"# Archive cleaned on {now.strftime('%Y-%m-%d')}\n")
        with open(CLEAN_DATE_FILE, 'w') as f:
            f.write(now.isoformat())
    elif not os.path.exists(CLEAN_DATE_FILE):
        with open(CLEAN_DATE_FILE, 'w') as f:
            f.write(now.isoformat())

def move_to_archive():
    """Переносит текущие прокси из основного файла в архив"""
    if os.path.exists(PROXY_FILE):
        with open(PROXY_FILE, 'r') as f:
            old_data = f.read().strip()
        
        if old_data:
            with open(ARCHIVE_FILE, 'a') as f:
                f.write(f"\n# Added to archive: {datetime.now().date()}\n")
                f.write(old_data + "\n")
            print("📦 Старые прокси перенесены в архив.")

async def main():
    check_cleanup() # Проверка даты очистки
    
    last_id = 0
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as f:
            last_id = int(f.read().strip())

    new_proxies = []
    current_max_id = last_id

    print(f"🔍 Ищем новинки с сообщения №{last_id}...")

    async for message in client.iter_messages(CHANNEL_USERNAME, min_id=last_id, reverse=True):
        if message.reply_markup:
            for row in message.reply_markup.rows:
                for button in row.buttons:
                    if hasattr(button, 'url') and 'proxy?' in button.url:
                        new_proxies.append(button.url)
        current_max_id = max(current_max_id, message.id)

    if new_proxies:
        move_to_archive() # Сначала бэкапим старое в архив
        
        # Перезаписываем основной файл только новыми прокси
        with open(PROXY_FILE, 'w') as f:
            f.write(f"# Latest update: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            for proxy in new_proxies:
                f.write(f"{proxy}\n")
        
        with open(CHECKPOINT_FILE, 'w') as f:
            f.write(str(current_max_id))
        
        print(f"✨ В proxy.txt добавлено {len(new_proxies)} новых ссылок.")
        
        # Отправляем всё на GitHub
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Auto-update: fresh proxies and archive sync"], check=True)
            subprocess.run(["git", "push"], check=True)
            print("✅ GitHub обновлен!")
        except:
            print("❌ Ошибка Git.")
    else:
        print("☕ Ничего нового не нашлось.")

with client:
    client.loop.run_until_complete(main())

