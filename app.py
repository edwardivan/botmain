from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import feedparser

app = Flask(__name__)
user_watchlist = {}

def fetch_google_news(company):
    query = company.replace(" ", "+")
    feed_url = f"https://news.google.com/rss/search?q={query}+site:moneycontrol.com&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(feed_url)

    if not feed.entries:
        return f"No recent news found for {company}."

    news_items = []
    for entry in feed.entries[:3]:  # Get top 3
        title = entry.title
        link = entry.link
        news_items.append(f"- {title}\n{link}")

    return f"Latest news for *{company}*:\n\n" + "\n\n".join(news_items)

@app.route("/whatsapp", methods=['POST'])
def whatsapp():
    incoming_msg = request.values.get('Body', '').strip().upper()
    sender = request.values.get('From', '')
    sender_id = sender.split(':')[-1]

    resp = MessagingResponse()
    msg = resp.message()

    if sender_id not in user_watchlist:
        user_watchlist[sender_id] = set()

    if incoming_msg.startswith("ADD "):
        stock = incoming_msg.replace("ADD ", "")
        user_watchlist[sender_id].add(stock)
        msg.body(f"{stock} added to your watchlist.")
    elif incoming_msg.startswith("REMOVE "):
        stock = incoming_msg.replace("REMOVE ", "")
        if stock in user_watchlist[sender_id]:
            user_watchlist[sender_id].remove(stock)
            msg.body(f"{stock} removed from your watchlist.")
        else:
            msg.body(f"{stock} not found in your watchlist.")
    elif incoming_msg == "LIST":
        stocks = ", ".join(user_watchlist[sender_id]) or "No stocks in your watchlist."
        msg.body(f"Your watchlist: {stocks}")
    elif incoming_msg.startswith("NEWS "):
        stock = incoming_msg.replace("NEWS ", "")
        news = fetch_google_news(stock)
        msg.body(news)
    else:
        msg.body("""Send commands like:
ADD TCS
REMOVE INFY
NEWS RELIANCE
LIST
""")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
