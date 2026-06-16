import yfinance as yf
from fpdf import FPDF
import math

def fetch_ticker_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        try:
            info = ticker.info
            if 'regularMarketPrice' in info and info['regularMarketPrice'] is not None:
                price = info['regularMarketPrice']
            elif 'currentPrice' in info and info['currentPrice'] is not None:
                price = info['currentPrice']
            elif 'previousClose' in info and info['previousClose'] is not None:
                price = info['previousClose']
            else:
                hist = ticker.history(period="1d")
                if hist.empty:
                    return None, None, f"Could not find recent price data for '{ticker_symbol}'."
                price = hist['Close'].iloc[-1]
            
            currency = info.get('currency', 'USD')
            return float(price), currency, None
            
        except Exception as e:
            return None, None, f"Error fetching details for '{ticker_symbol}'. Is it a valid Yahoo Finance ticker?"
            
    except Exception as e:
        return None, None, f"Invalid ticker '{ticker_symbol}'."

def get_exchange_rate(from_curr, to_curr):
    if from_curr == to_curr:
        return 1.0
        
    pair = f"{from_curr}{to_curr}=X"
    try:
        ticker = yf.Ticker(pair)
        hist = ticker.history(period="1d")
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
        return None
    except:
        return None

def generate_pdf_report(income, currency, jars, ffa_ticker, ffa_price, ffa_currency, shares_to_buy, remaining_cash, lang="中文"):
    pdf = FPDF()
    pdf.add_page()
    
    try:
        pdf.add_font("simhei", "", "simhei.ttf")
        font_name = "simhei"
    except:
        font_name = "helvetica" # Fallback if font missing
        
    # Translations
    t = {
        "title": "Your Six Jars FIRE Report" if lang == "English" else "您的六个罐子 FIRE 报告",
        "income": f"Total Monthly Income: {income:.2f} {currency}" if lang == "English" else f"本月总收入: {income:.2f} {currency}",
        "jar_name": "Jar Name" if lang == "English" else "罐子名称",
        "percent": "Percentage" if lang == "English" else "比例",
        "amount": f"Amount ({currency})" if lang == "English" else f"金额 ({currency})",
        "ffa_plan": "FFA Action Plan (Investment)" if lang == "English" else "FFA 定投计划 (投资)",
        "ffa_has": f"Your Financial Freedom Account (FFA) has {jars[1]['amount']:.2f} {currency}." if lang == "English" else f"您的财务自由账户 (FFA) 本月有 {jars[1]['amount']:.2f} {currency}。",
        "target": f"Target Ticker: {ffa_ticker}" if lang == "English" else f"目标标的: {ffa_ticker}",
        "price": f"Current Price: {ffa_price:.2f} {ffa_currency}" if lang == "English" else f"当前市价: {ffa_price:.2f} {ffa_currency}",
        "buy": f"Recommendation: Buy {shares_to_buy} shares of {ffa_ticker}." if lang == "English" else f"建议操作: 买入 {shares_to_buy} 股 {ffa_ticker}。",
        "remain": f"Remaining Cash: {remaining_cash:.2f} {currency}" if lang == "English" else f"剩余现金: {remaining_cash:.2f} {currency}",
        "nofunds": "Insufficient funds to buy a full share this month. Save it for next month!" if lang == "English" else "本月资金不足以买入 1 股整股，建议存入下月一并定投！",
        "disclaimer": "This is for informational purposes only, not financial advice." if lang == "English" else "本报告仅供参考，不构成任何投资理财建议。"
    }
    
    pdf.set_font(font_name, size=16)
    pdf.cell(w=200, h=10, text=t["title"], new_x="LMARGIN", new_y="NEXT", align='C')
    
    pdf.set_font(font_name, size=12)
    pdf.cell(w=200, h=10, text=t["income"], new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10)
    
    pdf.cell(w=80, h=10, text=t["jar_name"], border=1)
    pdf.cell(w=40, h=10, text=t["percent"], border=1, align='C')
    pdf.cell(w=60, h=10, text=t["amount"], border=1, align='R')
    pdf.ln(10)
    
    for jar in jars:
        pdf.cell(w=80, h=10, text=jar['name'], border=1)
        pdf.cell(w=40, h=10, text=f"{jar['percent']}%", border=1, align='C')
        pdf.cell(w=60, h=10, text=f"{jar['amount']:.2f}", border=1, align='R')
        pdf.ln(10)
        
    pdf.ln(10)
    
    pdf.set_font(font_name, size=14)
    pdf.cell(w=200, h=10, text=t["ffa_plan"], new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font(font_name, size=12)
    pdf.multi_cell(w=190, h=10, text=t["ffa_has"])
    pdf.multi_cell(w=190, h=10, text=t["target"])
    pdf.multi_cell(w=190, h=10, text=t["price"])
    
    pdf.ln(5)
    pdf.multi_cell(w=190, h=10, text=t["buy"])
    if shares_to_buy > 0:
        pdf.multi_cell(w=190, h=10, text=t["remain"])
    else:
        pdf.multi_cell(w=190, h=10, text=t["nofunds"])
        
    pdf.ln(10)
    pdf.set_font(font_name, size=10)
    pdf.cell(w=200, h=10, text=t["disclaimer"], new_x="LMARGIN", new_y="NEXT", align='C')
    
    return bytes(pdf.output())
