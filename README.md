# Automatic Reddit Scraper

This bot is part of a larger project, the main repository for which can be found [here](<https://github.com/avkaz/code_review/tree/main>).  


This bot automatically scrapes memes from the ProgrammerHumor subreddit twice a day. It collects the latest memes and processes them for later use. To avoid Reddit's bot protection, the bot uses a proxy system that rotates IP addresses. It also sends status updates to a helper Telegram channel.

## Features

*   Scrapes the latest memes from the ProgrammerHumor subreddit.
*   Avoids IP blocks using a rotating IP proxy system.
*   Sends status updates about the scraping process to a Telegram channel.
*   Runs automatically twice a day.
*   Integrates with other parts of your meme automation system (e.g., Telegram posting, meme filtering).

## Prerequisites

*   **ScrapeOps API Key:** ScrapeOps provides the proxy service. You need to sign up and get an API key.  A free tier is available with 1000 free proxy requests, which is sufficient for this bot (4 requests per day). Sign up [here](<scrapeops_signup_link>). Paste the API key into `spider.py` on line 62:

    ```python
    'api_key': 'your_api_key_here',  # Replace with your actual key
    ```

*   **Telegram Bot Token:** Create a Telegram bot using BotFather and obtain the bot token.

*   **Telegram Channel ID:** Create a Telegram channel for status updates and get its ID.

## Setup Instructions

1.  **Clone the Repository:**

    ```bash
    git clone <repository_url>
    cd automatic-reddit-scraper
    ```

2.  **Install Docker:** If you don't have Docker installed, follow the official Docker installation guide: [https://www.docker.com/](https://www.docker.com/)

3.  **Add the ScrapeOps API Key:**
    *   Open `spider.py`.
    *   On line 62, replace `'your_api_key_here'` with your actual ScrapeOps API key.

4.  **Set up Telegram Bot and Channel:**
    *   In `main.py`, replace the placeholders with your Telegram bot token and channel ID:

    ```python
    bot_token = 'your_telegram_bot_token_here'  # Replace with your bot token
    bot = telebot.TeleBot(bot_token, parse_mode='HTML')

    chat_id = 'your_telegram_channel_id_here'  # Replace with your channel ID
    ```

5.  **Docker Setup:**

    *   **Build the Docker image:**

    ```bash
    docker build -t reddit-scraper .
    ```

    *   **Run the Docker container:**

    ```bash
    docker run -d --name reddit-scraper reddit-scraper
    ```

## Proxy System

The bot uses the ScrapeOps proxy system to rotate IP addresses and avoid Reddit blocking.  The free tier provides 1000 requests, which is enough for this bot's needs (4 requests/day). If you exceed your quota, you can create a new account for a new set of free proxies.

## Helper Telegram Channel

The bot sends status updates to the designated Telegram channel.  Ensure the Telegram bot and channel are correctly set up to receive these updates.

## Important Notes

*   Double-check your API key and Telegram credentials.
*   To change the scraping frequency or time intervals, modify the settings in `spider.py`.

## Troubleshooting

*   **Proxy Issues:** Verify your API key and check the ScrapeOps service status.
*   **Telegram Channel Issues:** Verify the bot token and channel ID in `main.py`.
*   **Reddit Blocking:** Consider increasing the number of proxies used per request or adjusting the proxy system's configuration.

## Main Repository

*   Main Project Repository: <https://github.com/avkaz/code_review/tree/main>
