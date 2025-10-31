import requests
import os
import sys
import datetime

# --- [1] الإعدادات والمفاتيح السرية ---
try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
    CHANNEL_USERNAME = os.environ['CHANNEL_USERNAME'] # يجب أن يبدأ بـ @
except KeyError as e:
    print(f"!!! خطأ: متغير البيئة الأساسي غير موجود: {e}")
    sys.exit(1)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
# (نستخدم CoinGecko API المجاني 100% - لا يحتاج مفتاح)
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"

# --- [2] الدوال المساعدة (فقط إرسال النص) ---

def post_text_to_telegram(text_content):
    """
    (آمنة) إرسال رسالة نصية (للتقرير)
    """
    print(f"... جاري إرسال (التقرير) إلى {CHANNEL_USERNAME} ...")
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = { 
        'chat_id': CHANNEL_USERNAME, 
        'text': text_content, 
        'parse_mode': 'HTML' # سنستخدم HTML هنا لتمييز الألوان
    }
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        print(">>> تم إرسال (التقرير) بنجاح!")
    except requests.exceptions.RequestException as e:
        print(f"!!! فشل إرسال (التقرير): {e} - {getattr(response, 'text', 'لا يوجد رد')}")
        sys.exit(1) # إيقاف التشغيل بفشل إذا لم نتمكن من الإرسال

# --- [3] دوال "المهام" (خطة النشر المتنوعة) ---

def format_price(price):
    """تنسيق السعر بشكل جميل (مثل $0.001234 أو $65,123.50)"""
    if price < 1:
        return f"${price:.8f}" # للعملات الرخيصة جداً
    else:
        return f"${price:,.2f}" # للعملات الغالية

def format_change_percent(change):
    """تنسيق التغيير مع إضافة الرموز 🟢 🔴"""
    if change is None:
        return "(N/A)"
    if change >= 0:
        return f"(🟢 +{change:.2f}%)"
    else:
        return f"(🔴 {change:.2f}%)"

# [المهمة 1: تقرير السوق العام]
def run_market_cap_job():
    print("--- بدء مهمة [1. تقرير السوق العام (Top 5)] ---")
    try:
        url = f"{COINGECKO_API_URL}/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 5, # أعلى 5
            'page': 1,
            'sparkline': 'false'
        }
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        report = "📊 **تقرير السوق (أعلى 5 عملات)**\n\n"
        report += "--- (حسب القيمة السوقية) ---\n\n"
        
        for coin in data:
            name = coin.get('name', 'N/A')
            symbol = coin.get('symbol', '').upper()
            price = format_price(coin.get('current_price', 0))
            change = format_change_percent(coin.get('price_change_percentage_24h'))
            
            report += f"1. **{name} ({symbol}):** {price} {change}\n"
            
        report += f"\n---\n*تابعنا للمزيد من {CHANNEL_USERNAME}*"
        post_text_to_telegram(report)
        
    except Exception as e:
        print(f"!!! فشلت مهمة (تقرير السوق): {e}")

# [المهمة 2: أكبر الرابحين]
def run_gainers_job():
    print("--- بدء مهمة [2. أكبر الرابحين (Top 3)] ---")
    try:
        url = f"{COINGECKO_API_URL}/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'price_change_percentage_24h_desc', # الترتيب حسب "أكبر الرابحين"
            'per_page': 3, # أعلى 3
            'page': 1,
            'sparkline': 'false'
        }
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        report = "🚀 **أكبر الرابحين (آخر 24 ساعة)**\n\n"
        
        for coin in data:
            name = coin.get('name', 'N/A')
            symbol = coin.get('symbol', '').upper()
            price = format_price(coin.get('current_price', 0))
            change = format_change_percent(coin.get('price_change_percentage_24h'))
            
            report += f"1. **{name} ({symbol}):** {price} {change}\n"
            
        report += f"\n---\n*تابعنا للمزيد من {CHANNEL_USERNAME}*"
        post_text_to_telegram(report)
        
    except Exception as e:
        print(f"!!! فشلت مهمة (أكبر الرابحين): {e}")

# [المهمة 3: أكبر الخاسرين]
def run_losers_job():
    print("--- بدء مهمة [3. أكبر الخاسرين (Top 3)] ---")
    try:
        url = f"{COINGECKO_API_URL}/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'price_change_percentage_24h_asc', # الترتيب حسب "أكبر الخاسرين"
            'per_page': 3, # أسوأ 3
            'page': 1,
            'sparkline': 'false'
        }
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        report = "📉 **أكبر الخاسرين (آخر 24 ساعة)**\n\n"
        
        for coin in data:
            name = coin.get('name', 'N/A')
            symbol = coin.get('symbol', '').upper()
            price = format_price(coin.get('current_price', 0))
            change = format_change_percent(coin.get('price_change_percentage_24h'))
            
            report += f"1. **{name} ({symbol}):** {price} {change}\n"
            
        report += f"\n---\n*تابعنا للمزيد من {CHANNEL_USERNAME}*"
        post_text_to_telegram(report)
        
    except Exception as e:
        print(f"!!! فشلت مهمة (أكبر الخاسرين): {e}")

# --- [4] التشغيل الرئيسي (الذكي) ---
def main():
    print("==========================================")
    print(f"بدء تشغيل (v1.0 - بوت Market Byte)...")
    
    # (توقيت بغداد: 8ص, 2ظ, 8م, 2ص)
    # (بتوقيت UTC: 5, 11, 17, 23)
    current_hour_utc = datetime.datetime.now(datetime.timezone.utc).hour
    print(f"الساعة الحالية (UTC): {current_hour_utc}")
    
    job_to_run = None
    
    if current_hour_utc == 5: # 8:00 صباحاً (تقرير السوق)
        job_to_run = run_market_cap_job
    elif current_hour_utc == 11: # 2:00 ظهراً (أكبر الرابحين)
        job_to_run = run_gainers_job
    elif current_hour_utc == 17: # 8:00 مساءً (أكبر الخاسرين)
        job_to_run = run_losers_job
    elif current_hour_utc == 23: # 2:00 صباحاً (تقرير السوق)
        job_to_run = run_market_cap_job
    else:
        # هذا للتشغيل اليدوي (workflow_dispatch)
        print(">>> وقت غير مجدول (تشغيل يدوي). سيتم تشغيل 'تقرير السوق العام' للاختبار.")
        job_to_run = run_market_cap_job

    print("==========================================")
    
    if job_to_run:
        job_to_run()
    else:
        print("... لا توجد مهمة مجدولة لهذا الوقت.")

if __name__ == "__main__":
    main()
