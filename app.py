from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

user_watchlist = {}

@app.route("/whatsapp", methods=['POST'])
def whatsapp():
    incoming_msg = request.values.get('Body', '').strip().upper()
    sender = request.values.get('From', '')
    sender_id = sender.split(':')[-1]  # unique for each user

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
        msg.body(f"Fetching latest news for {stock}... [placeholder]")
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
