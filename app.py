import os
import pytz
import requests
import socket
import time
from datetime import datetime
from typing import Any, Optional

# IRC server and channel configuration
server = "irc.underworld.no"  # Replace with your IRC server
port = 6667                   # Typical port for IRC
nickname = "newsly"           # Desired bot nickname
channel = "#tuesdaynews"      # Target channel

# news API configuration
news_api_key = os.environ["NEWS_API_KEY"]
timezone = os.environ.get("TIMEZONE", "America/Los_Angeles")

# app configuration
last_published_at = None
delay = os.environ.get("DELAY", 1)
enable_irc = os.environ.get("IRC", False)


def connect_to_irc():
    """Connect to the IRC server and join the specified channel."""
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc.connect((server, port))

    irc.send(f"NICK {nickname}\r\n".encode("utf-8"))
    irc.send(f"USER {nickname} 0 * :News Bot\r\n".encode("utf-8"))
    time.sleep(2)
    irc.send(f"JOIN {channel}\r\n".encode("utf-8"))
    return irc


def get_latest_news(
    last_published_at: Optional[datetime] = None,
) -> tuple[list[Any], datetime]:
    """Fetch the latest news articles from NewsAPI."""
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={news_api_key}"
    response = requests.get(url)
    articles = response.json().get("articles", [])

    # Filter new articles by comparing publish time
    new_articles = []
    for article in articles:
        published_at = article["publishedAt"]
        if last_published_at is None or published_at > last_published_at:
            new_articles.append(article)

    if new_articles:
        # Update last published date to the latest article
        last_published_at = new_articles[0]["publishedAt"]

    return new_articles, last_published_at


def convert_to_local_timezone(utc_time_str, timezone=timezone):
    """Convert UTC time string to local timezone."""
    # Parse the UTC datetime string
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    utc_time = utc_time.replace(tzinfo=pytz.UTC)

    # Convert to local timezone
    local_timezone = pytz.timezone(timezone)
    local_time = utc_time.astimezone(local_timezone)
    return local_time.strftime("%Y-%m-%d %H:%M:%S %Z")


def send_message(irc, message):
    """Send a message to irc or stdout"""
    if irc:
        irc.send(f"PRIVMSG {channel} :{message}\r\n".encode("utf-8"))
    else:
        print(message)


def main(
    enable_irc: bool = enable_irc,
    last_published_at: datetime = last_published_at,
    delay: int = delay,
):
    irc = connect_to_irc() if enable_irc else None
    time.sleep(2)

    try:
        while True:
            articles, last_published_at = get_latest_news(last_published_at)
            articles.reverse()
            for article in articles:
                title = article["title"]
                url = article["url"]
                date = convert_to_local_timezone(article["publishedAt"])
                clr = ("\033[32m", "\033[0m", "\033[31m", "\033[0m")
                if enable_irc:
                    clr = ("\x0303", "\x03", "x0302", "x03")
                message = f"{clr[0]}{date}{clr[1]}: {clr[2]}{title}{clr[3]} - {url}"
                send_message(irc, message)
                time.sleep(2)  # Small delay between messages to avoid spam

            # Wait a while before checking for new news articles
            time.sleep(delay * 60)
    except KeyboardInterrupt:
        if irc:
            print("Disconnecting from IRC...")
            irc.send("QUIT\r\n".encode("utf-8"))
            irc.close()


if __name__ == "__main__":
    main()
