# Telegram Bot for Test Evaluation

This project is a Telegram bot that facilitates test answer submissions and evaluations. The bot is hosted on PythonAnywhere, accessible at `https://www.pythonanywhere.com/user/mathruz/`.

---

## Features

1. **Welcome and Restart Commands**
   - Sends a welcome message when users send `/start`.
   - Restarts and resends instructions upon `/restart`.

2. **Submit Answers**
   - Users can submit answers in the format `12350|bcddcadcacbdcdddbadb`.
   - Correct answers are saved and stored in `answers.json`.

3. **Evaluate Results**
   - Users can submit their test answers, and the bot evaluates their submissions based on the correct answers saved.
   - Results are sent to both the user and a designated results channel.

4. **Channel Notifications**
   - Correct answers are sent to a specific answers channel.
   - Evaluation results are shared in a results channel.

5. **Error Handling**
   - The bot validates inputs and provides informative messages for incorrect formats or invalid Test IDs.

6. **Time Zone Support**
   - All timestamps are displayed in GMT+5.

---

## Hosting

The bot is hosted on PythonAnywhere at the following URL:
[PythonAnywhere Dashboard](https://www.pythonanywhere.com/user/mathruz/)

---

## Setup Instructions

### Prerequisites
- Python 3.9+
- Flask
- Telepot

### Installation
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```

2. Install dependencies:
   ```bash
   pip install flask telepot
   ```

3. Configure the bot:
   - Replace `USERNAME`, `TOKEN`, and `SECRET` with your bot's username, API token, and a unique secret string.
   - Update the `ANSWERS_CHANNEL_ID` and `RESULTS_CHANNEL_ID` with your Telegram channel IDs.

4. Create an `answers.json` file:
   - If the file does not exist, the bot will automatically create it.

5. Set up the webhook:
   - Configure the bot to use your PythonAnywhere URL as a webhook.

   ```python
   bot.setWebhook(URL, max_connections=10)
   ```

---

## Usage

### Commands
- **Start**: Send `/start` to receive a welcome message.
- **Restart**: Send `/restart` to reset the bot.
- **Submit Answers**: Send answers using the format `12350|bcddcadcacbdcdddbadb`.

### Examples
#### Submit Correct Answers
Command:
```
#answer 12350|abcdabcdabcdabcdabcd
```

Response:
- Saves the correct answers.
- Notifies the answers channel.

#### Submit Test Results
Command:
```
12350|abcdabcdabcdabcdabcd
```

Response:
- Evaluates the answers.
- Sends results to the user and the results channel.

---

## Error Handling
- **Invalid Format**: Notifies the user if their input does not match the required format.
- **Invalid Test ID**: Alerts the user if the Test ID is not found.
- **Processing Errors**: Reports unexpected issues with detailed error messages.

---

## API Endpoints

### Webhook Endpoint
- **URL**: `https://mathruz.pythonanywhere.com/<SECRET>`
- **Methods**: `POST`, `GET`

#### POST
- Processes incoming Telegram messages.

#### GET
- Returns a success message to verify bot functionality.

---

## Deployment
1. Upload the bot files to your PythonAnywhere account.
2. Configure the bot to set the webhook:
   ```python
   bot.setWebhook(URL, max_connections=10)
   ```
3. Run the Flask application on PythonAnywhere.

---

## Files
- `app.py`: Main bot logic.
- `answers.json`: Stores correct answers.

---

## License
This project is open-source and available under the [MIT License](LICENSE).

---

## Contact
For issues or inquiries, please reach out to [mathruz](https://www.pythonanywhere.com/user/mathruz/).

