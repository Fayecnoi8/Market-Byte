# =============================================================================
#    *** بوت Market Byte - الإصدار 2.3 (Pro Crypto API) ***
#
#  (يستخدم COINGECKO_API_KEY وواجهة Pro API بدلاً من العامة)
#  (يحافظ على جميع الميزات الأخرى من v2.2)
# =============================================================================

import requests
import os
import sys
import datetime

# --- [1] الإعدادات والمفاتيح السرية ---
try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
    CHANNEL_USERNAME = os.environ['CHANNEL_USERNAME'] # يجب أن يبدأ بـ @
    
    # (v2.2) مفتاح API الأخبار الاحترافي
    NEWS_API_KEY = os.environ['NEWS_API_KEY'] 
    
    # (جديد v2.3) مفتاح API العملات الاحترافي
    COINGECKO_API_KEY = os.environ['COINGECKO_API_KEY']

except KeyError as e:
    print(f"!!! خطأ: متغير البيئة الأساسي غير موجود: {e}")
    print("!!! هل تذكرت إضافة 'NEWS_API_KEY' و 'COINGECKO_API_KEY' إلى GitHub Secrets؟")
    sys.exit(1)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# (مطور v2.3) استخدام واجهة Pro API للعملات
COINGECKO_API_URL = "https://pro-api.coingecko.com/api/v3"

# (v2.2) رابط API الأخبار الاحترافي
NEWS_API_URL = (
    "https://newsapi.org/v2/everything?"
    "q=(عملات رقمية OR بيتكوين OR إيثريوم OR بلوكتشين)"
    "&language=ar"
    "&sortBy=publishedAt"
    "&pageSize=3" 
)

# (v2.1) إعدادات التنبيهات الدورية
ALERT_WATCHLIST = ['bitcoin', 'ethereum', 'solana', 'binancecoin']
ALERT_THRESHOLD_PERCENT = 3.0 


# --- [2] الدوال المساعدة (إرسال الرسائل) ---
# (لا يوجد تغيير في هذه الدوال)
def post_photo_to_telegram(image_url, text_caption):
    print(f"... جاري إرسال (التقرير المصور) إلى {CHANNEL_USERNAME} ...")
    try:
        print(f"   ... (1/2) جاري تحميل الصورة من: {image_url}")
        image_response = requests.get(image_url, timeout=30)
        image_response.raise_for_status()
        image_data = image_response.content
        url = f"{TELEGRAM_API_URL}/sendPhoto"
        payload = { 'chat_id': CHANNEL_USERNAME, 'caption': text_caption, 'parse_mode': 'HTML'}
        files = {'photo': ('coin.jpg', image_data, 'image/jpeg')}
        print("   ... (2/2) جاري رفع الصورة إلى تيليجرام ...")
        response = requests.post(url, data=payload, files=files, timeout=60)
        response.raise_for_status()
        print(">>> تم إرسال (التقرير المصور) بنجاح!")
    except requests.exceptions.RequestException as e:
        print(f"!!! فشل إرسال (التقرير المصور): {getattr(response, 'text', 'لا يوجد رد')}")

def post_text_to_telegram(text_content):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = { 
        'chat_id': CHANNEL_USERNAME, 
        'text': text_content, 
        'parse_mode': 'HTML',
        'disable_web_page_preview': True 
    }
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        print(">>> تم إرسال (التقرير النصي) بنجاح!")
    except requests.exceptions.RequestException as e:
        print(f"!!! فشل إرسال (التقرير النصي): {getattr(response, 'text', 'لا يوجد رد')}")


# --- [3] دوال تنسيق التقرير (Helpers) ---
# (لا يوجد تغيير في هذه الدوال)
def format_price(price):
    if price is None: return "N/A"
    if price < 1: return f"${price:.8f}"
    else: return f"${price:,.2f}"

def format_change_percent(change, timeframe="24h"):
    icon = "📊" 
    if timeframe == "7d": icon = "🗓️"
    if change is None: return "(N/A)"
    if change >= 0: return f"({icon} 🟢 +{change:.2f}%)"
    else: return f"({icon} 🔴 {change:.2f}%)"
    
def format_large_number(num):
    if num is None: return "N/A"
    if num >= 1_000_000_000: return f"${(num / 1_000_000_000):.2f}B"
    elif num >= 1_000_000: return f"${(num / 1_000_000):.2f}M"
    else: return f"${num:,.0f}"

# --- [4] دوال "المهام" (محدثة لـ v2.3) ---

# [المهمة 0: فحص التنبيهات (v2.1)]
def run_price_alert_job():
    print("--- بدء مهمة [A. فحص التنبيهات الدورية] ---")
    try:
        ids = ",".join(ALERT_WATCHLIST)
        url = f"{COINGECKO_API_URL}/simple/price"
        params = {
            'ids': ids,
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'x_cg_pro_api_key': COINGECKO_API_KEY # (مفتاح Pro v2.3)
        }
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        alerts_sent = 0
        for coin_id, info in data.items():
            change = info.get('usd_24h_change', 0)
            price = info.get('usd', 0)
            if change is None: continue
            
            if abs(change) >= ALERT_THRESHOLD_PERCENT:
                print(f"!!! تنبيه: {coin_id} تغير بنسبة {change}%. جاري إرسال التنبيه.")
                icon = "🚨"
                direction_icon = "🟢" if change > 0 else "🔴"
                price_formatted = format_price(price)
                alert_text = f"{icon} <b>تنبيه حركة سعرية</b> {icon}\n\n"
                alert_text += f"<b>{coin_id.capitalize()} ({coin_id.upper()})</b>\n"
                alert_text += f"💰 السعر الحالي: {price_formatted}\n"
                alert_text += f"📊 التغير (24س): {direction_icon} {change:.2f}%\n"
                alert_text += f"\n---\n<i>*تابعنا للمزيد من {CHANNEL_USERNAME}*</i>"
                post_text_to_telegram(alert_text)
                alerts_sent += 1
                
        if alerts_sent == 0:
            print("... (تنبيهات): لا توجد تغيرات سعرية كبيرة في قائمة المراقبة.")
            
    except Exception as e:
        print(f"!!! فشلت مهمة (فحص التنبيهات): {e}")

# [المهمة 1: تقرير السوق العام]
def run_market_cap_job():
    print("--- بدء مهمة [1. تقرير السوق العام (Top 5)] ---")
    try:
        url = f"{COINGECKO_API_URL}/coins/markets"
        params = {
            'vs_currency': 'usd', 
            'order': 'market_cap_desc', 
            'per_page': 5, 
            'page': 1, 
            'sparkline': 'false',
            'x_cg_pro_api_key': COINGECKO_API_KEY # (مفتاح Pro v2.3)
        }
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        for idx, coin in enumerate(data, 1):
            name = coin.get('name', 'N/A')
            symbol = coin.get('symbol', '').upper()
            price = format_price(coin.get('current_price'))
            change = format_change_percent(coin.get('price_change_percentage_24h'), "24h")
            market_cap = format_large_number(coin.get('market_cap'))
            total_volume = format_large_number(coin.get('total_volume'))
            image_url = coin.get('image')
            report = f"📊 <b>تقرير السوق (العملات الرائدة)</b>\n\n"
            report += f"<b>{name} ({symbol})</b>\n"
            report += f"💰 السعر: {price}\n"
            report += f"📊 24س تغير: {change}\n"
            report += f"🏦 القيمة السوقية: {market_cap}\n"
            report += f"📈 حجم التداول: {total_volume}\n"
            report += f"\n---\n<i>*تابعنا للمزيد من {CHANNEL_USERNAME}*</i>"
            
            if image_url:
                post_photo_to_telegram(image_url, report)
            else:
                post_text_to_telegram(report)
        
    except Exception as e:
        print(f"!!! فشلت مهمة (تقرير السوق): {e}")

# [المهمة 2: أكبر الرابحين (اليومي)]
def run_gainers_job():
    print("--- بدء مهمة [2. أكبر الرابحين (Top 3 Daily)] ---")
    try:
        url = f"{COINGECKO_API_URL}/search/trending"
        # (مطور v2.3) إضافة المفتاح لطلبات الترند
        params = {'x_cg_pro_api_key': COINGECKO_API_KEY} 
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json().get('coins', [])
        
        top_gainers = sorted(
            [c['item'] for c in data if c.get('item', {}).get('price_change_percentage_24h_in_currency', 0) > 0],
            key=lambda x: x.get('price_change_percentage_24h_in_currency', 0),
            reverse=True
        )[:3]
        
        for coin in top_gainers:
            name = coin.get('name', 'N/A')
            symbol = coin.get('symbol', '').upper()
            price = format_price(coin.get('data', {}).get('price'))
            change_raw = coin.get('data', {}).get('price_change_percentage_24h_in_currency', {}).get('usd', 0)
            change = format_change_percent(change_raw, "24h")
            market_cap = format_large_number(coin.get('data', {}).get('market_cap_usd'))
            total_volume = format_large_number(coin.get('data', {}).get('total_volume_usd'))
            image_url = coin.get('large') 
            report = f"🚀 <b>الأكثر رواجاً ورابحاً (آخر 24 ساعة)</b>\n\n"
            report += f"<b>{name} ({symbol})</b>\n"
            report += f"💰 السعر: {price}\n"
            report += f"📊 24س تغير: {change}\n"
            report += f"🏦 القيمة السوقية: {market_cap}\n"
            report += f"📈 حجم التداول: {total_volume}\n"
            report += f"\n---\n<i>*تابعنا للمزيد من {CHANNEL_USERNAME}*</i>"
            
            if image_url:
                post_photo_to_telegram(image_url, report)
            else:
                post_text_to_telegram(report)
        
    except Exception as e:
        print(f"!!! فشلت مهمة (أكبر الرابحين): {e}")

# [المهمة 3: أكبر الخاسرين (اليومي)]
def run_losers_job():
    print("--- بدء مهمة [3. أكبر الخاسرين (Top 3 Daily)] ---")
    try:
        url = f"{COINGECKO_API_URL}/coins/markets"
        params = {
            'vs_currency': 'usd', 
            'order': 'price_change_percentage_24h_asc', 
            'per_page': 3, 
            'page': 1, 
            'sparkline': 'false',
            'x_cg_pro_api_key': COINGECKO_API_KEY # (مفتاح Pro v2.3)
        }
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        for coin in data:
            name = coin.get('name', 'N/A')
            symbol = coin.get('symbol', '').upper()
            price = format_price(coin.get('current_price'))
            change = format_change_percent(coin.get('price_change_percentage_24h'), "24h")
            market_cap = format_large_number(coin.get('market_cap'))
            total_volume = format_large_number(coin.get('total_volume'))
            image_url = coin.get('image')
            report = f"📉 <b>أكبر الخاسرين (آخر 24 ساعة)</b>\n\n"
            report += f"<b>{name} ({symbol})</b>\n"
            report += f"💰 السعر: {price}\n"
            report += f"📊 24س تغير: {change}\n"
            report += f"🏦 القيمة السوقية: {market_cap}\n"
            report += f"📈 حجم التداول: {total_volume}\n"
            report += f"\n---\n<i>*تابعنا للمزيد من {CHANNEL_USERNAME}*</i>"
            
            if image_url:
                post_photo_to_telegram(image_url, report)
            else:
                post_text_to_telegram(report)
        
    except Exception as e:
        print(f"!!! فشلت مهمة (أكبر الخاسرين): {e}")
        
# [المهمة 4: الأخبار العاجلة (v2.2)]
def run_news_job():
    print("--- بدء مهمة [4. الأخبار العاجلة (NewsAPI.org)] ---")
    try:
        full_url = f"{NEWS_API_URL}&apiKey={NEWS_API_KEY}"
        response = requests.get(full_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        articles = data.get('articles', [])
        if not articles:
            print("... لا توجد أخبار جديدة (NewsAPI).")
            return

        report = "📰 <b>أخبار عاجلة من السوق</b>\n\n"
        for article in articles:
            title = article.get('title', 'لا يوجد عنوان')
            link = article.get('url', '#')
            source_name = article.get('source', {}).get('name', 'المصدر')
            report += f"⚡️ <b>{title}</b>\n"
            report += f"(المصدر: {source_name})\n"
            report += f"<a href='{link}'>اقرأ المزيد...</a>\n\n"
        report += f"---\n<i>*تابعنا للمزيد من {CHANNEL_USERNAME}*</i>"
        
        post_text_to_telegram(report)
        
    except Exception as e:
        print(f"!!! فشلت مهمة (الأخبار العاجلة): {e}")

# [المهمة 5: الملخص الأسبوعي]
def run_weekly_summary_job():
    print("--- بدء مهمة [5. الملخص الأسبوعي (Top 3/3)] ---")
    try:
        url = f"{COINGECKO_API_URL}/coins/markets"
        params = {
            'vs_currency': 'usd', 'order': 'market_cap_desc', 
            'per_page': 100, 'page': 1, 'sparkline': 'false',
            'price_change_percentage': '7d',
            'x_cg_pro_api_key': COINGECKO_API_KEY # (مفتاح Pro v2.3)
        }
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        valid_data = [c for c in data if c.get('price_change_percentage_7d_in_currency') is not None]
        gainers = sorted(valid_data, key=lambda x: x['price_change_percentage_7d_in_currency'], reverse=True)[:3]
        losers = sorted(valid_data, key=lambda x: x['price_change_percentage_7d_in_currency'])[:3]
        
        for coin in gainers:
            report = f"🏆 <b>ملخص الأسبوع: أكبر الرابحين</b>\n\n"
            report += f"<b>{coin.get('name', 'N/A')} ({coin.get('symbol', '').upper()})</b>\n"
            report += f"💰 السعر: {format_price(coin.get('current_price'))}\n"
            report += f"🗓️ 7أيام تغير: {format_change_percent(coin.get('price_change_percentage_7d_in_currency'), '7d')}\n"
            report += f"🏦 القيمة السوقية: {format_large_number(coin.get('market_cap'))}\n"
            report += f"\n---\n<i>*تابعنا للمزيد من {CHANNEL_USERNAME}*</i>"
            post_photo_to_telegram(coin.get('image'), report)

        for coin in losers:
            report = f"📉 <b>ملخص الأسبوع: أكبر الخاسرين</b>\n\n"
            report += f"<b>{coin.get('name', 'N/A')} ({coin.get('symbol', '').upper()})</b>\n"
            report += f"💰 السعر: {format_price(coin.get('current_price'))}\n"
            report += f"🗓️ 7أيام تغير: {format_change_percent(coin.get('price_change_percentage_7d_in_currency'), '7d')}\n"
            report += f"🏦 القيمة السوقية: {format_large_number(coin.get('market_cap'))}\n"
            report += f"\n---\n<i>*تابعنا للمزيد من {CHANNEL_USERNAME}*</i>"
            post_photo_to_telegram(coin.get('image'), report)
            
    except Exception as e:
        print(f"!!! فشلت مهمة (الملخص الأسبوعي): {e}")


# --- [5] التشغيل الرئيسي (الذكي v2.3) ---
def main():
    print("==========================================")
    print(f"بدء تشغيل (v2.3 - بوت Market Byte - Pro API)...")
    
    today_utc = datetime.datetime.now(datetime.timezone.utc)
    current_hour_utc = today_utc.hour
    current_day_utc = today_utc.weekday() # (Monday=0, Sunday=6)
    
    print(f"الوقت الحالي (UTC): الساعة {current_hour_utc}, اليوم {current_day_utc}")
    
    # --- الخطوة 1: تشغيل فحص التنبيهات دائماً ---
    try:
        run_price_alert_job()
    except Exception as e:
        print(f"!!! فشل فحص التنبيهات الأولي: {e}")
    
    print("------------------------------------------")
    print("... اكتمل فحص التنبيهات، جاري تحديد المهمة المجدولة...")
    
    # --- الخطوة 2: تحديد وتشغيل المهمة المجدولة الرئيسية ---
    job_to_run = None
    
    if current_hour_utc == 5: # 8:00 صباحاً (توقيت بغداد)
        if current_day_utc == 6: # (6 هو يوم الأحد)
            print(">>> الأحد صباحاً: تم جدولة [الملخص الأسبوعي]")
            job_to_run = run_weekly_summary_job
        else:
            print(">>> (يوم عادي) صباحاً: تم جدولة [تقرير السوق العام]")
            job_to_run = run_market_cap_job
            
    elif current_hour_utc == 11: # 2:00 ظهراً (توقيت بغداد)
        print(">>> ظهراً: تم جدولة [أكبر الرابحين]")
        job_to_run = run_gainers_job
        
    elif current_hour_utc == 17: # 8:00 مساءً (توقيت بغداد)
        print(">>> مساءً: تم جدولة [أكبر الخاسرين]")
        job_to_run = run_losers_job
        
    elif current_hour_utc == 23: # 2:00 صباحاً (توقيت بغداد)
        print(">>> صباحاً: تم جدولة [الأخبار العاجلة]")
        job_to_run = run_news_job
        
    else:
        print(f">>> (تشغيل يدوي/اختبار في الساعة {current_hour_utc}) سيتم تشغيل [تقرير السوق العام] (بعد التنبيهات)")
        job_to_run = run_market_cap_job

    print("==========================================")
    
    if job_to_run:
        job_to_run()
    else:
        print("... لا توجد مهمة مجدولة لهذا الوقت (باستثناء التنبيهات).")

if __name__ == "__main__":
    main()

