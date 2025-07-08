from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

watchlist = set()

def get_bse_filings(symbol):
    # Dummy response for demo purposes
    return f"Latest BSE filings for {symbol}: [sample data]"

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').strip().upper()
    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg.startswith("ADD "):
        symbol = incoming_msg[4:].strip()
        watchlist.add(symbol)
        msg.body(f"✅ Added {symbol} to your watchlist.")
    elif incoming_msg.startswith("REMOVE "):
        symbol = incoming_msg[7:].strip()
        watchlist.discard(symbol)
        msg.body(f"❌ Removed {symbol} from your watchlist.")
    elif incoming_msg.startswith("NEWS ") or incoming_msg.startswith("FILINGS "):
        symbol = incoming_msg.split()[1].strip()
        response = get_bse_filings(symbol)
        msg.body(response)
    elif incoming_msg == "LIST":
        if not watchlist:
            msg.body("Your watchlist is empty.")
        else:
            msg.body("📋 Watchlist: " + ", ".join(sorted(watchlist)))
    else:
        msg.body("Send commands like:
ADD TCS
REMOVE TCS
NEWS TCS
LIST")

    return str(resp)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)