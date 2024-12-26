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
    "Botga hush kelibsiz!\n"
    "Iltimos, javoblaringizni quyidagi formatda yuboring:\n"
    "12350|bcddcadcacbdcdddbadb"
)
RESTART_MESSAGE = (
    "Botni qayta ishga tushirdik.\n"
    "Javoblaringizni quyidagi formatda yuboring:\n"
    "12350|bcddcadcacbdcdddbadb"
)
ERROR_MESSAGE = (
    "Xato formatda javob yuborildi.\n"
    "Iltimos, javoblaringizni quyidagi formatga mos holda yuboring:\n"
    "12350|bcddcadcacbdcdddbadb"
)
INVALID_TEST_ID_MESSAGE = (
    "Ko'rsatilgan Test ID ma'lumotlar bazasida topilmadi.\n"
    "Iltimos, mavjud Test ID bilan qayta yuboring."
)
INVALID_FORMAT_MESSAGE = (
    "Noto'g'ri formatda javob yuborildi.\n"
    "Iltimos, javoblaringizni quyidagi formatga mos holda yuboring:\n"
    "12350|bcddcadcacbdcdddbadb"
)
PROCESSING_ERROR_MESSAGE = (
    "Xatolik yuz berdi (processing): {error_message}"
)
WEBHOOK_ERROR_MESSAGE = (
    "Xatolik yuz berdi (webhook): {error_message}"
)
ANSWER_SAVED_MESSAGE = (
    "Javoblar muvaffaqiyatli saqlandi:\n"
    "Test ID: {test_id}\n"
    "Javoblar: {right_answers}"
)
ANSWER_CHANNEL_MESSAGE = (
    "Test ID: {test_id}\n"
    "Javoblar:\n{formatted_answers}\n"
    "Saqlangan vaqt: {current_date_time}"
)
RESULT_CHANNEL_MESSAGE = (
    "Foydalanuvchi ma'lumotlari:\n"
    "Ism: {first_name}\n"
    "Familiya: {last_name}\n"
    "Username: @{username}\n"
    "User ID: {user_id}\n"
    "Jo'natgan vaqt: {submission_time}\n"
    "\nTest natijalari:\n"
    "Test ID: {test_id}\n"
    "Natijalar:\n{results}\n"
    "To'g'ri javoblar: {correct_count}/{total_questions} ({percentage:.0f}%)"
)
USER_RESULT_MESSAGE = (
    "Sizning natijalaringiz:\n"
    "To'g'ri javoblar: {correct_count}/{total_questions} ({percentage:.0f}%)"
)
CORRECT_ANSWER_MESSAGE = "{i}. {user_ans} ✅ (To'g'ri)"
WRONG_ANSWER_MESSAGE = "{i}. {user_ans} ❌ (Noto'g'ri - to'g'ri javob: {correct_ans})"
TEST_SUCCESS_MESSAGE = "Bot muvaffaqiyatli ishlayapti."

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
        first_name = msg['from'].get('first_name', 'Nomalum')
        last_name = msg['from'].get('last_name', 'Nomalum')

        if 'text' in msg:
            text = msg['text'].strip().lower()

            # Start komandasi
            if text == "/start":
                bot.sendMessage(user_id, WELCOME_MESSAGE)

            # Restart komandasi
            elif text == "/restart":
                bot.sendMessage(user_id, RESTART_MESSAGE)

            # #answer komandasi
            elif text.startswith("#answer"):
                text = text.replace("#answer", "").strip()

                if re.match(r'^\d{5}\|[abcd]{20}$', text):
                    test_id, right_answers = text.split('|')

                    initialize_answers_file()
                    answers = load_answers()

                    answers[test_id] = right_answers
                    save_answers(answers)

                    bot.sendMessage(user_id, ANSWER_SAVED_MESSAGE.format(test_id=test_id, right_answers=right_answers))

                    # Javoblarni ANSWERS_CHANNEL_ID'ga yuborish
                    formatted_answers = '\n'.join(f"{i+1}) {ans}" for i, ans in enumerate(right_answers))
                    current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    answer_message = ANSWER_CHANNEL_MESSAGE.format(
                        test_id=test_id, formatted_answers=formatted_answers, current_date_time=current_date_time
                    )
                    bot.sendMessage(ANSWERS_CHANNEL_ID, answer_message)
                else:
                    bot.sendMessage(user_id, ERROR_MESSAGE)

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
                    bot.sendMessage(RESULTS_CHANNEL_ID, channel_result)

                    user_result = USER_RESULT_MESSAGE.format(
                        correct_count=correct_count, total_questions=total_questions, percentage=percentage
                    )
                    bot.sendMessage(user_id, user_result)
                else:
                    bot.sendMessage(user_id, INVALID_TEST_ID_MESSAGE)
            else:
                # Noto'g'ri format
                bot.sendMessage(user_id, INVALID_FORMAT_MESSAGE)
    except Exception as e:
        bot.sendMessage(user_id, PROCESSING_ERROR_MESSAGE.format(error_message=str(e)))

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
        bot.sendMessage(RESULTS_CHANNEL_ID, WEBHOOK_ERROR_MESSAGE.format(error_message=str(e)))
        return 'ERROR'

@app.route(f'/{SECRET}', methods=["GET"])
def test():
    return TEST_SUCCESS_MESSAGE

if __name__ == "__main__":
    app.run()
