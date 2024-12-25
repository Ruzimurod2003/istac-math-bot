import telepot
import re
import random
import string
from flask import Flask, request

# Bot sozlamalari
USERNAME = "mathruz"
TOKEN = "7726647298:AAE4_O-N6KMSaWObeMzIKsHZtEAqWxlju6s"
SECRET = ''.join(random.choice(string.ascii_letters) for x in range(20))
URL = f"https://{USERNAME}.pythonanywhere.com/{SECRET}"
ANSWERS_CHANNEL_ID = "@IstacMathAnswers"  # Answers channel
RESULTS_CHANNEL_ID = "@IstacMathResults"  # Results channel

telepot.api.set_proxy('http://proxy.server:3128')
bot = telepot.Bot(TOKEN)
bot.setWebhook(URL, max_connections=10)

def fetch_answers_from_channel():
    answers = {}
    # Kanal xabarlar tarixini olish
    messages = bot.getChatHistory(ANSWERS_CHANNEL_ID, limit=100)
    
    for msg in messages:
        if 'text' in msg:
            text = msg['text']

            # Javob formatini tekshirish
            if re.match(r'^\d{5}\|[abcd]{20}$', text):
                test_id, correct_answers = text.split('|')
                answers[test_id] = correct_answers

    return answers

def processing(msg):
    if 'chat' in msg and msg['chat']['type'] == 'channel':
        return

    user_id = msg['from']['id']
    username = msg['from'].get('username', 'foydalanuvchi')

    answers = fetch_answers_from_channel()
    if 'text' in msg:
        text = msg['text']

        # Start komandasi
        if text.strip().lower() == "/start":
            welcome_text = (
                "Botga hush kelibsiz, iltimos javoblaringizni yuboring, "
                "12350|bcddcadcacbdcdddbadb kabi foymatda jo'natashingiz kerak."
            )
            bot.sendMessage(user_id, welcome_text)
            return
        
        # Tekshiruv formati
        if re.match(r'^\d{5}\|[abcd]{20}$', text):
            test_id, user_answers = text.split('|')

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

                # Natija
                total_questions = len(correct_answers)
                percentage = (correct_count / total_questions) * 100

                # Kanallarga xabar yuborish
                channel_result = f"Foydalanuvchi @{username} ning @{test_id} bo'yicha natijasi:\n" + '\n'.join(result)
                bot.sendMessage(RESULTS_CHANNEL_ID, channel_result)

                # Foydalanuvchiga xabar yuborish
                user_result = f"To'g'r javoblar: {correct_count}/{total_questions} ({percentage:.0f}%)"
                bot.sendMessage(user_id, user_result)
            else:
                # Noto'g'ri test ID
                bot.sendMessage(user_id, "Test ID topilmadi. Iltimos, mavjud test IDni yuboring.")
        else:
            # Noto'g'ri format
            bot.sendMessage(user_id, "Noto'g'ri formatda javob yuborildi. Iltimos, javoblaringizni quyidagi formatda yuboring: 12350|bcddcadcacbdcdddbadb")

app = Flask(__name__)

@app.route(f'/{SECRET}', methods=["POST"])
def webhook():
    update = request.get_json()
    if "message" in update:
        processing(update['message'])
    elif 'callback_query' in update:
        processing(update['callback_query'])
    return 'OK'

if __name__ == "__main__":
    app.run()
