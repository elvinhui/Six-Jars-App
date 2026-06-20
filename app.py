# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
import plotly.express as px
from app_utils import fetch_ticker_data, get_exchange_rate, generate_pdf_report
import math

st.set_page_config(page_title="Six Jars FIRE", page_icon="🍯", layout="centered")

hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden !important;}
header {visibility: hidden !important;}
[data-testid="stAppDeployButton"] {display: none !important;}
[data-testid="stToolbar"] {display: none !important;}
.viewerBadge_container {display: none !important;}
[data-testid="stBottom"] {display: none !important;}
a[href="https://streamlit.io/cloud"] {display: none !important;}
/* hide fullscreen button */
button[title="View fullscreen"] {display: none !important;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets.get("APP_PASSWORD", "fire"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter Password / 请输入密码", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Enter Password / 请输入密码", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect / 密码错误")
        return False
    else:
        return True

# if not check_password():
#     st.stop()

# --- Language Selection ---
lang = st.radio("Language / 语言", ["English", "中文"], horizontal=True)

# --- Translations Dictionary ---
t = {
    "title": "🍯 六个罐子 (Six Jars) FIRE App" if lang == "中文" else "🍯 Six Jars FIRE App",
    "subtitle": "极简理财工具，助你早日实现财务自由。 *无数据库设计，刷新即焚，保护隐私。*" if lang == "中文" else "Minimalist FIRE tool. *No database, privacy focused.*",
    "h1": "1. 财务信息 (Financial Info)" if lang == "中文" else "1. Financial Info",
    "income_prompt": "💰 请输入本月总收入" if lang == "中文" else "💰 Enter Monthly Income",
    "currency_prompt": "货币 (Currency)" if lang == "中文" else "Currency",
    "adv_opt": "⚙️ 高级选项：调整罐子比例" if lang == "中文" else "⚙️ Advanced: Adjust Jar Percentages",
    "adv_desc": "默认采用经典的 6 Jars 比例。确保总和等于 100%。" if lang == "中文" else "Standard 6 Jars allocation. Must sum to 100%.",
    "err_pct": "比例总和必须为 100%！当前总和为" if lang == "中文" else "Sum must be 100%! Current sum:",
    "h2": "2. 资金分配 (Allocation)" if lang == "中文" else "2. Allocation",
    "pie_title": "资金分配概览" if lang == "中文" else "Allocation Overview",
    "h3": "3. 🌟 智能定投指令 (Action Engine)" if lang == "中文" else "3. 🌟 Action Engine",
    "engine_desc": "系统将根据您的 **财务自由账户 (FFA)** 金额，为您生成本月定投建议。" if lang == "中文" else "Generates a monthly investment plan based on your **Financial Freedom Account (FFA)**.",
    "ticker_prompt": "推荐投资标的 (Ticker)" if lang == "中文" else "Recommended Ticker",
    "custom_prompt": "请输入股票代码" if lang == "中文" else "Enter custom ticker",
    "fractional_prompt": "☑️ 允许购买碎股 (Allow Fractional Shares)" if lang == "中文" else "☑️ Allow Fractional Shares",
    "gen_btn": "生成定投建议" if lang == "中文" else "Generate Action Plan",
    "fetching": "获取实时股价和汇率中..." if lang == "中文" else "Fetching live data...",
    "fetch_err_price": "获取股价失败，请稍后再试。" if lang == "中文" else "Failed to fetch price. Try again later.",
    "fetch_err_fx": "获取汇率失败。请检查网络。" if lang == "中文" else "Failed to fetch exchange rate.",
    "calc_done": "计算完成！" if lang == "中文" else "Calculation Complete!",
    "h_plan": "### 💡 本月定投建议" if lang == "中文" else "### 💡 Monthly Action Plan",
    "plan_ffa": "您的 FFA 账户本月有" if lang == "中文" else "Your FFA account has",
    "plan_price": "当前市价约为" if lang == "中文" else "Current market price is roughly",
    "plan_fx": "参考汇率：" if lang == "中文" else "Reference FX:",
    "plan_buy": "建议您打开券商 App，买入" if lang == "中文" else "Recommendation: Buy",
    "plan_shares": "股" if lang == "中文" else "shares of",
    "plan_remain": "剩余的" if lang == "中文" else "Remaining",
    "plan_save": "可留存在账户中作为下月备用金。" if lang == "中文" else "can be saved for next month.",
    "plan_nofunds": "您的资金不足以买入 1 股整股。" if lang == "中文" else "Insufficient funds for 1 full share.",
    "plan_wait": "建议将资金保留到下个月一起定投。" if lang == "中文" else "Save these funds for next month's investment.",
    "h4": "4. 生成本月报告 (Export)" if lang == "中文" else "4. Export Report",
    "dl_btn": "📥 下载 PDF 报告" if lang == "中文" else "📥 Download PDF",
    
    # Jar Names
    "j_nec": "必需支出 (NEC)" if lang == "中文" else "Necessities (NEC)",
    "j_ffa": "财务自由 (FFA)" if lang == "中文" else "Financial Freedom (FFA)",
    "j_edu": "教育学习 (EDU)" if lang == "中文" else "Education (EDU)",
    "j_ltss": "长期储蓄 (LTSS)" if lang == "中文" else "Long-term Savings (LTSS)",
    "j_play": "玩乐享受 (PLAY)" if lang == "中文" else "Play (PLAY)",
    "j_give": "赠与奉献 (GIVE)" if lang == "中文" else "Give (GIVE)",
    
    # Jar Descs
    "d_nec": "用于日常开销，如房租、水电、吃饭。" if lang == "中文" else "For daily expenses like rent, food, bills.",
    "d_ffa": "只能用来买生钱的资产，打死也不能花！" if lang == "中文" else "Only for buying income-generating assets. Never spend!",
    "d_edu": "投资自己的大脑，买书、上课。" if lang == "中文" else "Invest in your brain. Books, courses, etc.",
    "d_ltss": "为未来的大笔开销做准备，如买车、旅游。" if lang == "中文" else "For future large purchases (car, vacation).",
    "d_play": "每个月必须花光，去吃顿好的，或者按摩。" if lang == "中文" else "Must be spent every month. Treat yourself!",
    "d_give": "用于慈善捐款或者给家人的礼物。" if lang == "中文" else "For charities or gifts to family/friends."
}

# --- Main App ---
st.title(t["title"])
st.markdown(t["subtitle"])

st.header(t["h1"])
col1, col2 = st.columns([2, 1])

with col1:
    income = st.number_input(t["income_prompt"], min_value=0.0, value=5000.0, step=100.0)

with col2:
    base_currency = st.selectbox(t["currency_prompt"], ["SGD", "MYR", "USD", "CNY", "EUR", "HKD"])

with st.expander(t["adv_opt"]):
    st.markdown(t["adv_desc"])
    j_col1, j_col2 = st.columns(2)
    with j_col1:
        nec_pct = st.number_input(t["j_nec"], min_value=0, max_value=100, value=55, step=1)
        ffa_pct = st.number_input(t["j_ffa"], min_value=0, max_value=100, value=10, step=1)
        edu_pct = st.number_input(t["j_edu"], min_value=0, max_value=100, value=10, step=1)
    with j_col2:
        ltss_pct = st.number_input(t["j_ltss"], min_value=0, max_value=100, value=10, step=1)
        play_pct = st.number_input(t["j_play"], min_value=0, max_value=100, value=10, step=1)
        give_pct = st.number_input(t["j_give"], min_value=0, max_value=100, value=5, step=1)

    total_pct = nec_pct + ffa_pct + edu_pct + ltss_pct + play_pct + give_pct
    if total_pct != 100:
        st.error(f"{t['err_pct']} {total_pct}%。")
        st.stop()

# It's important that FFA is the second item (index 1) because utils.py hardcodes it for the PDF
jars_data = [
    {"name": t["j_nec"], "percent": nec_pct, "desc": t["d_nec"]},
    {"name": t["j_ffa"], "percent": ffa_pct, "desc": t["d_ffa"]},
    {"name": t["j_edu"], "percent": edu_pct, "desc": t["d_edu"]},
    {"name": t["j_ltss"], "percent": ltss_pct, "desc": t["d_ltss"]},
    {"name": t["j_play"], "percent": play_pct, "desc": t["d_play"]},
    {"name": t["j_give"], "percent": give_pct, "desc": t["d_give"]}
]

for jar in jars_data:
    jar["amount"] = income * (jar["percent"] / 100.0)

st.header(t["h2"])
labels = [j["name"] for j in jars_data]
values = [j["amount"] for j in jars_data]

fig = px.pie(names=labels, values=values, hole=0.4, title=t["pie_title"])
st.plotly_chart(fig, width='stretch')

cols = st.columns(3)
for i, jar in enumerate(jars_data):
    with cols[i % 3]:
        st.markdown(f"**{jar['name']} - {jar['percent']}%**")
        st.markdown(f"### {base_currency} {jar['amount']:.2f}")
        st.caption(jar['desc'])
        st.write("---")

st.header(t["h3"])
st.markdown(t["engine_desc"])

c1, c2 = st.columns(2)
with c1:
    predefined_tickers = {
        "CSPX.L (S&P 500)": "CSPX.L",
        "VWRA.L (All-World)": "VWRA.L",
        "VOO (S&P 500)": "VOO",
        "QQQ (Nasdaq 100)": "QQQ",
        "Custom / 自定义": "CUSTOM"
    }
    ticker_choice = st.selectbox(t["ticker_prompt"], list(predefined_tickers.keys()))
    allow_fractional = st.checkbox(t["fractional_prompt"], value=False)

with c2:
    if ticker_choice == "Custom / 自定义":
        target_ticker = st.text_input(t["custom_prompt"], value="AAPL")
    else:
        target_ticker = predefined_tickers[ticker_choice]

ffa_amount = jars_data[1]["amount"] # FFA is index 1

if st.button(t["gen_btn"]):
    with st.spinner(t["fetching"]):
        price, currency, err = fetch_ticker_data(target_ticker)
        
        if err:
            st.warning(err)
        elif price is None:
            st.warning(t["fetch_err_price"])
        else:
            fx_rate = 1.0
            if base_currency != currency:
                fx_rate = get_exchange_rate(base_currency, currency)
                if fx_rate is None:
                    st.warning(t["fetch_err_fx"])
                    fx_rate = 1.0

            ffa_in_target_curr = ffa_amount * fx_rate
            
            # Calculate shares
            if allow_fractional:
                shares_to_buy = round(ffa_in_target_curr / price, 4)
                cost_in_target_curr = ffa_in_target_curr # We spend it all
                remaining_in_target_curr = 0.0
            else:
                shares_to_buy = math.floor(ffa_in_target_curr / price)
                cost_in_target_curr = shares_to_buy * price
                remaining_in_target_curr = ffa_in_target_curr - cost_in_target_curr
                
            remaining_in_base_curr = remaining_in_target_curr / fx_rate if fx_rate != 0 else 0

            st.success(t["calc_done"])
            st.markdown(t["h_plan"])
            st.markdown(f"> {t['plan_ffa']} **{base_currency} {ffa_amount:.2f}**.")
            st.markdown(f"> 您选定的 **{target_ticker}** {t['plan_price']} **{currency} {price:.2f}**.")
            
            if base_currency != currency:
                st.markdown(f"> *({t['plan_fx']} 1 {base_currency} = {fx_rate:.4f} {currency})*")
            
            st.markdown("---")
            if shares_to_buy > 0:
                st.markdown(f"#### 👉 {t['plan_buy']} **{shares_to_buy}** {t['plan_shares']} {target_ticker}。")
                if not allow_fractional:
                    st.markdown(f"#### 💰 {t['plan_remain']} **{base_currency} {remaining_in_base_curr:.2f}** {t['plan_save']}")
            else:
                st.markdown(f"#### ⚠️ {t['plan_nofunds']}")
                st.markdown(f"#### 💰 {t['plan_wait']}")
                
            st.header(t["h4"])
            pdf_bytes = generate_pdf_report(
                income=income,
                currency=base_currency,
                jars=jars_data,
                ffa_ticker=target_ticker,
                ffa_price=price,
                ffa_currency=currency,
                shares_to_buy=shares_to_buy,
                remaining_cash=remaining_in_base_curr,
                lang=lang
            )
            
            st.download_button(
                label=t["dl_btn"],
                data=pdf_bytes,
                file_name="Six_Jars_Report.pdf",
                mime="application/pdf"
            )

st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)

