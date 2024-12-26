import telepot
import re
import json
from flask import Flask, request
from pathlib import Path
from datetime import datetime

# Bot sozlamalari
USERNAME = "mathruz"
TOKEN = "7726647298:AAE4_O-N6KMSaWObeMzIKsHZtEAqWxlju6s"
SECRET = "test"
URL = f"https://{USERNAME}.pythonanywhere.com/{SECRET}"
ANSWERS_CHANNEL_ID = "-1002286694169"
RESULTS_CHANNEL_ID = "-1002447423828"
ANSWERS_FILE = Path("answers.json")

# Bot xabarlari
WELCOME_MESSAGE = (
    "👋 <b>Botga hush kelibsiz!</b>\n"
    "📝 <i>Iltimos, javoblaringizni quyidagi formatda yuboring:</i>\n"
    "<code>12350|bcddcadcacbdcdddbadb</code>"
)
RESTART_MESSAGE = (
    "🔄 <b>Bot qayta ishga tushirildi!</b>\n"
    "📝 <i>Iltimos, javoblaringizni quyidagi formatda yuboring:</i>\n"
    "<code>12350|bcddcadcacbdcdddbadb</code>"
)
ERROR_MESSAGE = (
    "❌ <b>Xato formatda javob yuborildi!</b>\n"
    "⚠️ <i>Iltimos, quyidagi formatga mos ravishda yuboring:</i>\n"
    "<code>12350|bcddcadcacbdcdddbadb</code>"
)
INVALID_TEST_ID_MESSAGE = (
    "❌ <b>Test ID topilmadi!</b>\n"
    "⚠️ <i>Iltimos, mavjud Test ID bilan qayta yuboring.</i>"
)
INVALID_FORMAT_MESSAGE = (
    "❌ <b>Xato formatda javob yuborildi!</b>\n"
    "⚠️ <i>Iltimos, quyidagi formatga mos ravishda yuboring:</i>\n"
    "<code>12350|bcddcadcacbdcdddbadb</code>"
)
PROCESSING_ERROR_MESSAGE = (
    "⚠️ <b>Xatolik yuz berdi:</b> <i>{error_message}</i>"
)
WEBHOOK_ERROR_MESSAGE = (
    "⚠️ <b>Webhook xatosi:</b> <i>{error_message}</i>"
)
ANSWER_SAVED_MESSAGE = (
    "✅ <b>Javoblar saqlandi!</b>\n"
    "🆔 <b>Test ID:</b> <code>{test_id}</code>\n"
    "📋 <b>Javoblar:</b> <code>{right_answers}</code>"
)
ANSWER_CHANNEL_MESSAGE = (
    "🆔 <b>Test ID:</b> <code>{test_id}</code>\n"
    "📋 <b>Javoblar:</b>\n{formatted_answers}\n"
    "⏰ <b>Saqlangan vaqt:</b> <i>{current_date_time}</i>"
)
RESULT_CHANNEL_MESSAGE = (
    "👤 <b>Foydalanuvchi ma'lumotlari:</b>\n"
    "🪪 <b>Ism:</b> <i>{first_name}</i>\n"
    "🪪 <b>Familiya:</b> <i>{last_name}</i>\n"
    "💻 <b>Username:</b> @{username}\n"
    "🆔 <b>User ID:</b> <code>{user_id}</code>\n"
    "⏰ <b>Jo'natgan vaqt:</b> <i>{submission_time}</i>\n"
    "\n📊 <b>Test natijalari:</b>\n"
    "🆔 <b>Test ID:</b> <code>{test_id}</code>\n"
    "📋 <b>Natijalar:</b>\n{results}\n"
    "✅ <b>To'g'ri javoblar:</b> <i>{correct_count}/{total_questions}</i> ({percentage:.0f}%)"
)
USER_RESULT_MESSAGE = (
    "📊 <b>Sizning natijalaringiz:</b>\n"
    "✅ <b>To'g'ri javoblar:</b> <i>{correct_count}/{total_questions}</i> ({percentage:.0f}%)"
)
CORRECT_ANSWER_MESSAGE = "{i}. {user_ans} ✅ <i>(To'g'ri)</i>"
WRONG_ANSWER_MESSAGE = "{i}. {user_ans} ❌ <i>(Noto'g'ri - to'g'ri javob: {correct_ans})</i>"
TEST_SUCCESS_MESSAGE = "✅ <b>Bot muvaffaqiyatli ishlayapti!</b>"

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
        username = msg['from'].get('username', 'Nomalum')
        first_name = msg['from'].get('first_name', 'Nomalum')
        last_name = msg['from'].get('last_name', 'Nomalum')

        if 'text' in msg:
            text = msg['text'].strip().lower()

            # Start komandasi
            if text == "/start":
                bot.sendMessage(user_id, WELCOME_MESSAGE, parse_mode="HTML")

            # Restart komandasi
            elif text == "/restart":
                bot.sendMessage(user_id, RESTART_MESSAGE, parse_mode="HTML")

            # #answer komandasi
            elif text.startswith("#answer"):
                text = text.replace("#answer", "").strip()

                if re.match(r'^\d{5}\|[abcd]{20}$', text):
                    test_id, right_answers = text.split('|')

                    initialize_answers_file()
                    answers = load_answers()

                    answers[test_id] = right_answers
                    save_answers(answers)

                    bot.sendMessage(user_id, ANSWER_SAVED_MESSAGE.format(test_id=test_id, right_answers=right_answers), parse_mode="HTML")

                    # Javoblarni ANSWERS_CHANNEL_ID'ga yuborish
                    formatted_answers = '\n'.join(f"{i+1}) {ans}" for i, ans in enumerate(right_answers))
                    current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    answer_message = ANSWER_CHANNEL_MESSAGE.format(
                        test_id=test_id, formatted_answers=formatted_answers, current_date_time=current_date_time
                    )
                    bot.sendMessage(ANSWERS_CHANNEL_ID, answer_message, parse_mode="HTML")
                else:
                    bot.sendMessage(user_id, ERROR_MESSAGE, parse_mode="HTML")

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
                            result.append(CORRECT_ANSWER_MESSAGE.format(i=i, user_ans=user_ans))
                            correct_count += 1
                        else:
                            result.append(WRONG_ANSWER_MESSAGE.format(i=i, user_ans=user_ans, correct_ans=correct_ans))

                    total_questions = len(correct_answers)
                    percentage = (correct_count / total_questions) * 100
                    submission_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    channel_result = RESULT_CHANNEL_MESSAGE.format(
                        first_name=first_name,
                        last_name=last_name,
                        username=username,
                        user_id=user_id,
                        submission_time=submission_time,
                        test_id=test_id,
                        results='\n'.join(result),
                        correct_count=correct_count,
                        total_questions=total_questions,
                        percentage=percentage
                    )
                    bot.sendMessage(RESULTS_CHANNEL_ID, channel_result, parse_mode="HTML")

                    user_result = USER_RESULT_MESSAGE.format(
                        correct_count=correct_count, total_questions=total_questions, percentage=percentage
                    )
                    bot.sendMessage(user_id, user_result, parse_mode="HTML")
                else:
                    bot.sendMessage(user_id, INVALID_TEST_ID_MESSAGE, parse_mode="HTML")
            else:
                # Noto'g'ri format
                bot.sendMessage(user_id, INVALID_FORMAT_MESSAGE, parse_mode="HTML")
    except Exception as e:
        bot.sendMessage(user_id, PROCESSING_ERROR_MESSAGE.format(error_message=str(e)), parse_mode="HTML")

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
        bot.sendMessage(RESULTS_CHANNEL_ID, WEBHOOK_ERROR_MESSAGE.format(error_message=str(e)), parse_mode="HTML")
        return 'ERROR'

@app.route(f'/{SECRET}', methods=["GET"])
def test():
    return TEST_SUCCESS_MESSAGE

if __name__ == "__main__":
    app.run()
