# =============================================================================
#    *** بوت Market Byte - الإصدار 1.4 (التقارير الاحترافية - صورة لكل عملة) ***
#
#  (ينفذ فكرتك: إرسال "صورة شعار العملة" الحقيقية لكل عملة مع التقرير كمقال)
#  (يستخدم CoinGecko API المجاني)
#  (يستخدم تنسيق HTML الصحيح للرسائل <b>)
# =============================================================================

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
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"

# --- [2] الدوال المساعدة (إرسال الصورة) ---

def post_photo_to_telegram(image_url, text_caption):
    """
    (آمنة) إرسال "صورة شعار العملة" مع "التقرير" كمقال (Caption)
    """
    print(f"... جاري إرسال (التقرير المصور) إلى {CHANNEL_USERNAME} ...")
    url = f"{TELEGRAM_API_URL}/sendPhoto"
    
    payload = { 
        'chat_id': CHANNEL_USERNAME, 
        'photo': image_url, # [فكرتك 100%] رابط صورة شعار العملة الحقيقي
        'caption': text_caption, # التقرير النصي كمقال
        'parse_mode': 'HTML' # نستخدم HTML
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        print(">>> تم إرسال (التقرير المصور) بنجاح!")
    except requests.exceptions.RequestException as e:
        print(f"!!! فشل إرسال (التقرير المصور): {e} - {getattr(response, 'text', 'لا يوجد رد')}")
        sys.exit(1)

# --- [3] دوال "المهام" (خطة النشر المتنوعة) ---

def format_price(price):
    if price is None: return "N/A"
    if price < 1: return f"${price:.8f}"
    else: return f"${price:,.2f}"

def format_change_percent(change):
    if change is None: return "(N/A)"
    if change >= 0: return f"(🟢 +{change:.2f}%)"
    else: return f"(🔴 {change:.2f}%)"

# [المهمة 1: تقرير السوق العام]
def run_market_cap_job():
    print("--- بدء مهمة [1. تقرير السوق العام (Top 5)] ---")
    try:
        url = f"{COINGECKO_API_URL}/coins/markets"
        params = {'vs_currency': 'usd', 'order': 'market_cap_desc', 'per_page': 5, 'page': 1, 'sparkline': 'false'}
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # [فكرتك] الآن سنرسل "منشوراً واحداً لكل عملة"
        for idx, coin in enumerate(data, 1):
            name = coin.get('name', 'N/A')
            symbol = coin.get('symbol', '').upper()
            price = format_price(coin.get('current_price'))
            change = format_change_percent(coin.get('price_change_percentage_24h'))
            market_cap = coin.get('market_cap')
            total_volume = coin.get('total_volume')
            image_url = coin.get('image') # [فكرتك 100%] جلب رابط صورة الشعار
            
            report = f"📊 <b>تقرير السوق (العملات الرائدة)</b>\n\n" # عنوان لكل منشور
            report += f"<b>{name} ({symbol})</b>\n"
            report += f"💰 السعر: {price}\n"
            report += f"📊 24س تغير: {change}\n"
            report += f"🏦 القيمة السوقية: ${market_cap:,.0f}B\n" if market_cap else "🏦 القيمة السوقية: N/A\n"
            report += f"📈 حجم التداول: ${total_volume:,.0f}B\n" if total_volume else "📈 حجم التداول: N/A\n"
            report += f"\n---\n<i>*تابعنا للمزيد من {CHANNEL_USERNAME}*</i>"
            
            if image_url: # نرسل الصورة إذا كانت موجودة
                post_photo_to_telegram(image_url, report)
            else: # وإلا نرسل نصاً فقط
                print(f"!!! لا يوجد رابط صورة لـ {name}. جاري إرسال نص فقط.")
                post_text_to_telegram(report) # (دالة جديدة مؤقتة لعدم وجود صورة)
        
    except Exception as e:
        print(f"!!! فشلت مهمة (تقرير السوق): {e}")

# [المهمة 2: أكبر الرابحين]
def run_gainers_job():
    print("--- بدء مهمة [2. أكبر الرابحين (Top 3)] ---")
    try:
        url = f"{COINGECKO_API_URL}/coins/markets"
        params = {'vs_currency': 'usd', 'order': 'price_change_percentage_24h_desc', 'per_page': 3, 'page': 1, 'sparkline': 'false'}
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        for idx, coin in enumerate(data, 1):
            name = coin.get('name', 'N/A')
            symbol = coin.get('symbol', '').upper()
            price = format_price(coin.get('current_price'))
            change = format_change_percent(coin.get('price_change_percentage_24h'))
            market_cap = coin.get('market_cap')
            total_volume = coin.get('total_volume')
            image_url = coin.get('image') # [فكرتك 100%] جلب رابط صورة الشعار
            
            report = f"🚀 <b>أكبر الرابحين (آخر 24 ساعة)</b>\n\n"
            report += f"<b>{name} ({symbol})</b>\n"
            report += f"💰 السعر: {price}\n"
            report += f"📊 24س تغير: {change}\n"
            report += f"🏦 القيمة السوقية: ${market_cap:,.0f}B\n" if market_cap else "🏦 القيمة السوقية: N/A\n"
            report += f"📈 حجم التداول: ${total_volume:,.0f}B\n" if total_volume else "📈 حجم التداول: N/A\n"
            report += f"\n---\n<i>*تابعنا للمزيد من {CHANNEL_USERNAME}*</i>"
            
            if image_url:
                post_photo_to_telegram(image_url, report)
            else:
                print(f"!!! لا يوجد رابط صورة لـ {name}. جاري إرسال نص فقط.")
                post_text_to_telegram(report)
        
    except Exception as e:
        print(f"!!! فشلت مهمة (أكبر الرابحين): {e}")

# [المهمة 3: أكبر الخاسرين]
def run_losers_job():
    print("--- بدء مهمة [3. أكبر الخاسرين (Top 3)] ---")
    try:
        url = f"{COINGECKO_API_URL}/coins/markets"
        params = {'vs_currency': 'usd', 'order': 'price_change_percentage_24h_asc', 'per_page': 3, 'page': 1, 'sparkline': 'false'}
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        for idx, coin in enumerate(data, 1):
            name = coin.get('name', 'N/A')
            symbol = coin.get('symbol', '').upper()
            price = format_price(coin.get('current_price'))
            change = format_change_percent(coin.get('price_change_percentage_24h'))
            market_cap = coin.get('market_cap')
            total_volume = coin.get('total_volume')
            image_url = coin.get('image') # [فكرتك 100%] جلب رابط صورة الشعار
            
            report = f"📉 <b>أكبر الخاسرين (آخر 24 ساعة)</b>\n\n"
            report += f"<b>{name} ({symbol})</b>\n"
            report += f"💰 السعر: {price}\n"
            report += f"📊 24س تغير: {change}\n"
            report += f"🏦 القيمة السوقية: ${market_cap:,.0f}B\n" if market_cap else "🏦 القيمة السوقية: N/A\n"
            report += f"📈 حجم التداول: ${total_volume:,.0f}B\n" if total_volume else "📈 حجم التداول: N/A\n"
            report += f"\n---\n<i>*تابعنا للمزيد من {CHANNEL_USERNAME}*</i>"
            
            if image_url:
                post_photo_to_telegram(image_url, report)
            else:
                print(f"!!! لا يوجد رابط صورة لـ {name}. جاري إرسال نص فقط.")
                post_text_to_telegram(report)
        
    except Exception as e:
        print(f"!!! فشلت مهمة (أكبر الخاسرين): {e}")
        
# [المهمة 4: أعلى حجم تداول]
def run_volume_job():
    print("--- بدء مهمة [4. أعلى حجم تداول (Top 3)] ---")
    try:
        url = f"{COINGECKO_API_URL}/coins/markets"
        params = {'vs_currency': 'usd', 'order': 'volume_desc', 'per_page': 3, 'page': 1, 'sparkline': 'false'}
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        for idx, coin in enumerate(data, 1):
            name = coin.get('name', 'N/A')
            symbol = coin.get('symbol', '').upper()
            price = format_price(coin.get('current_price')) # لجلب السعر لحجم التداول
            change = format_change_percent(coin.get('price_change_percentage_24h'))
            market_cap = coin.get('market_cap')
            total_volume = coin.get('total_volume')
            image_url = coin.get('image') # [فكرتك 100%] جلب رابط صورة الشعار
            
            report = f"📈 <b>الأعلى في حجم التداول (آخر 24 ساعة)</b>\n\n"
            report += f"<b>{name} ({symbol})</b>\n"
            report += f"💰 السعر: {price}\n"
            report += f"📊 24س تغير: {change}\n"
            report += f"🏦 القيمة السوقية: ${market_cap:,.0f}B\n" if market_cap else "🏦 القيمة السوقية: N/A\n"
            report += f"📈 حجم التداول: ${total_volume:,.0f}B\n" if total_volume else "📈 حجم التداول: N/A\n"
            report += f"\n---\n<i>*تابعنا للمزيد من {CHANNEL_USERNAME}*</i>"
            
            if image_url:
                post_photo_to_telegram(image_url, report)
            else:
                print(f"!!! لا يوجد رابط صورة لـ {name}. جاري إرسال نص فقط.")
                post_text_to_telegram(report)
        
    except Exception as e:
        print(f"!!! فشلت مهمة (أعلى حجم تداول): {e}")

# (دالة مؤقتة لإرسال نص فقط في حال عدم وجود صورة للعملة)
def post_text_to_telegram(text_content):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = { 
        'chat_id': CHANNEL_USERNAME, 
        'text': text_content, 
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        print(">>> تم إرسال (نص التقرير فقط) بنجاح!")
    except requests.exceptions.RequestException as e:
        print(f"!!! فشل إرسال (نص التقرير فقط): {e} - {getattr(response, 'text', 'لا يوجد رد')}")
        sys.exit(1)


# --- [4] التشغيل الرئيسي (الذكي) ---
def main():
    print("==========================================")
    print(f"بدء تشغيل (v1.4 - بوت Market Byte الاحترافي)...")
    
    current_hour_utc = datetime.datetime.now(datetime.timezone.utc).hour
    print(f"الساعة الحالية (UTC): {current_hour_utc}")
    
    job_to_run = None
    
    if current_hour_utc == 5: # 8:00 صباحاً (تقرير السوق)
        job_to_run = run_market_cap_job
    elif current_hour_utc == 11: # 2:00 ظهراً (أكبر الرابحين)
        job_to_run = run_gainers_job
    elif current_hour_utc == 17: # 8:00 مساءً (أكبر الخاسرين)
        job_to_run = run_losers_job
    elif current_hour_utc == 23: # 2:00 صباحاً (أعلى حجم تداول)
        job_to_run = run_volume_job
    else:
        print(">>> وقت غير مجدول (تشغيل يدوي). سيتم تشغيل 'تقرير السوق العام' للاختبار.")
        job_to_run = run_market_cap_job

    print("==========================================")
    
    if job_to_run:
        job_to_run()
    else:
        print("... لا توجد مهمة مجدولة لهذا الوقت.")

if __name__ == "__main__":
    main()

