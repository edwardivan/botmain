from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_bse_filings(stock_name):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    search_url = f"https://www.bseindia.com/corporates/ann.aspx"
    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        return ["Error: Unable to access BSE site."]

    # For simplicity, we use BSE scrip code manually mapped
    scrip_map = {
        "INFY": "500209",  # Infosys
        "TCS": "532540",
        "RELIANCE": "500325",
        "SBIN": "500112",
        # Add more as needed
    }

    scrip_code = scrip_map.get(stock_name.upper())
    if not scrip_code:
        return [f"No BSE code found for {stock_name}. Try: INFY, TCS, RELIANCE, etc."]

    filings_url = f"https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w?strCat=-1&strPrevDate=&strScrip={scrip_code}&strSearch=P&strToDate=&strType=C"

    res = requests.get(filings_url, headers=headers)
    if res.status_code != 200:
        return ["Error fetching filings."]

    data = res.json()
    filings = data.get("Table", [])[:3]

    if not filings:
        return [f"No filings found for {stock_name}."]

    links = [f"📄 {item['NEWSSUB']}\n➡ https://www.bseindia.com{item['ATTACHMENTNAME']}" for item in filings]
    return links

@app.route("/whatsapp", methods=['POST'])
def whatsapp():
    incoming_msg = request.values.get('Body', '').strip().upper()
    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg.startswith("BSE "):
        stock = incoming_msg.split("BSE ", 1)[-1].strip()
        msg.body(f"🔍 Fetching latest BSE filings for *{stock}*...")
        filings = get_bse_filings(stock)
        for f in filings:
            msg.body(f)
    else:
        msg.body("Use format: BSE INFY")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
