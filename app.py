from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

# ---- BSE Filing Fetcher ----
def get_bse_filings(stock_name):
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://www.bseindia.com/',
        'Origin': 'https://www.bseindia.com'
    }

    scrip_map = {
        "INFY": "500209",
        "TCS": "532540",
        "RELIANCE": "500325",
        "SBIN": "500112",
        "HDFC": "500010",
        "ICICIBANK": "532174"
        # Add more as needed
    }

    scrip_code = scrip_map.get(stock_name.upper())
    if not scrip_code:
        return [f"No BSE code found for {stock_name}. Try: INFY, TCS, RELIANCE, etc."]

    api_url = f"https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w?strCat=-1&strPrevDate=&strScrip={scrip_code}&strSearch=P&strToDate=&strType=C"

    try:
        res = requests.get(api_url, headers=headers, timeout=10)
        if res.status_code != 200:
            return [f"BSE API error: status {res.status_code}"]

        data = res.json()
        filings = data.get("Table", [])[:3]

        if not filings:
            return [f"No recent filings found for {stock_name}."]

        links = [f"📄 *{item['NEWSSUB']}*\n➡ https://www.bseindia.com{item['ATTACHMENTNAME']}" for item in filings]
        return links

    except Exception as e:
        return [f"Error fetching filings: {e}"]

# ---- Main Twilio WhatsApp Bot ----
@app.route("/sms", methods=["POST"])
def sms_reply():
    msg = MessagingResponse()
    incoming_msg = request.form.get("Body").strip()

    if incoming_msg.upper().startswith("BSE"):
        parts = incoming_msg.split()
        if len(parts) >= 2:
            stock = parts[1]
            msg.body(f"Fetching latest BSE filings for {stock}...")
            filings = get_bse_filings(stock)
            for f in filings:
                msg.message(f)
        else:
            msg.body("Send like: *BSE INFY* to get recent BSE filings.")

    else:
        msg.body("Send *BSE INFY* or *BSE TCS* to get latest company filings.")

    return str(msg)

if __name__ == "__main__":
    app.run()
