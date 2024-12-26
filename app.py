import telepot
import re
import json
from flask import Flask, request
from pathlib import Path

# Bot sozlamalari
USERNAME = "mathruz"
TOKEN = "7726647298:AAE4_O-N6KMSaWObeMzIKsHZtEAqWxlju6s"
SECRET = "test"
URL = f"https://{USERNAME}.pythonanywhere.com/{SECRET}"
ANSWERS_CHANNEL_ID = "-1002286694169"
RESULTS_CHANNEL_ID = "-1002447423828"
ANSWERS_FILE = Path("answers.json")

telepot.api.set_proxy('http://proxy.server:3128')
bot = telepot.Bot(TOKEN)
bot.setWebhook(URL, max_connections=10)

# Fayl mavjud bo'lmasa, uni yaratib bo'sh lug'atni saqlaymiz
def initialize_answers_file():
    if not ANSWERS_FILE.exists():
        with open(ANSWERS_FILE, "w") as f:
            json.dump({}, f, indent=4)

# Javoblarni yuklash funksiyasi
def load_answers():
    with open(ANSWERS_FILE, "r") as f:
        return json.load(f)

# Javoblarni saqlash funksiyasi
def save_answers(answers):
    with open(ANSWERS_FILE, "w") as f:
        json.dump(answers, f, indent=4)

# Javoblarni yuklash funksiyasi
def fetch_answers_from_json():
    if ANSWERS_FILE.exists():
        with open(ANSWERS_FILE, "r") as f:
            return json.load(f)
    return {}

def processing(msg):
    try:
        if 'chat' in msg and msg['chat']['type'] == 'channel':
            return

        user_id = msg['from']['id']
        username = msg['from'].get('username', 'foydalanuvchi')

        if 'text' in msg:
            text = msg['text'].strip().lower()

            # Start komandasi
            if text == "/start":
                welcome_text = (
                    "Botga hush kelibsiz, iltimos javoblaringizni yuboring, "
                    "12350|bcddcadcacbdcdddbadb kabi foymatda jo'natashingiz kerak."
                )
                bot.sendMessage(user_id, welcome_text)                

            # Restart komandasi
            elif text == "/restart":
                welcome_text = (
                    "Botni restart qildik, iltimos javoblaringizni yuboring, "
                    "12350|bcddcadcacbdcdddbadb kabi foymatda jo'natashingiz kerak."
                )
                bot.sendMessage(user_id, welcome_text)                

            # #answer komandasi
            elif text.startswith("#answer"):
                text = text.replace("#answer", "").strip()

                if re.match(r'^\d{5}\|[abcd]{20}$', text):
                    test_id, right_answers = text.split('|')

                    initialize_answers_file()
                    answers = load_answers()

                    answers[test_id] = right_answers
                    save_answers(answers)

                    bot.sendMessage(user_id, f"Javoblar saqlandi: {test_id} -> {right_answers}")
                else:
                    error_message = (
                        "Noto'g'ri formatda javob yuborildi. Bot javoblarni saqlay olmadi. "
                        "Iltimos, javoblaringizni quyidagi formatda yuboring: 12350|bcddcadcacbdcdddbadb"
                    )
                    bot.sendMessage(user_id, error_message)                

            # Test natijalarini qayta ishlash
            elif re.match(r'^\d{5}\|[abcd]{20}$', text):
                test_id, user_answers = text.split('|')

                answers = fetch_answers_from_json()

                if test_id in answers:
                    correct_answers = answers[test_id]
                    result = []
                    correct_count = 0

                    for i, (user_ans, correct_ans) in enumerate(zip(user_answers, correct_answers), start=1):
                        if user_ans == correct_ans:
                            result.append(f"{i}. {user_ans} ✅ (To'g'ri)")
                            correct_count += 1
                        else:
                            result.append(f"{i}. {user_ans} ❌ (Noto'g'ri - to'g'ri javob: {correct_ans})")

                    total_questions = len(correct_answers)
                    percentage = (correct_count / total_questions) * 100

                    channel_result = f"Foydalanuvchi({user_id}) @{username} ning {test_id} bo'yicha natijasi:\n" + '\n'.join(result)
                    bot.sendMessage(RESULTS_CHANNEL_ID, channel_result)

                    user_result = f"To'g'ri javoblar: {correct_count}/{total_questions} ({percentage:.0f}%)"
                    bot.sendMessage(user_id, user_result)
                else:
                    bot.sendMessage(user_id, "Test ID topilmadi. Iltimos, mavjud test IDni yuboring.")                    
            else:
                # Noto'g'ri format
                bot.sendMessage(user_id, "Noto'g'ri formatda javob yuborildi. Iltimos, javoblaringizni quyidagi formatda yuboring: 12350|bcddcadcacbdcdddbadb")            
    except Exception as e:
        bot.sendMessage(user_id, f"Xatolik yuz berdi (processing): {str(e)}")

app = Flask(__name__)

@app.route(f'/{SECRET}', methods=["POST"])
def webhook():
    try:
        update = request.get_json()
        if "message" in update:
            processing(update['message'])
        elif 'callback_query' in update:
            processing(update['callback_query'])
        return 'OK'
    except Exception as e:
        bot.sendMessage(RESULTS_CHANNEL_ID, f"Xatolik yuz berdi (webhook): {str(e)}")
        return 'ERROR'

if __name__ == "__main__":
    app.run()
