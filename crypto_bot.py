# =============================================================================
#    *** بوت Market Byte - الإصدار 2.5 (مبسط وآمن) ***
#
#  (جديد) تم حذف API الأخبار (NEWS_API_KEY) بالكامل.
#  (جديد) تم حذف API العملات الاحترافي (COINGECKO_API_KEY) والعودة للواجهة العامة.
#  (جديد) تم استبدال مهمة الأخبار بـ "أعلى حجم تداول" (مثل v1.5).
#  (يحافظ على خدعة رفع الصورة + الخطة الاحتياطية v2.4).
# =============================================================================

import requests
import os
import sys
import datetime

# --- [1] الإعدادات والمفاتيح السرية (المبسطة) ---
try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
    CHANNEL_USERNAME = os.environ['CHANNEL_USERNAME'] # يجب أن يبدأ بـ @
except KeyError as e:
    print(f"!!! خطأ: متغير البيئة الأساسي غير موجود: {e}")
    sys.exit(1)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
# (مبسط v2.5) العودة للواجهة العامة (لا تحتاج مفتاح)
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"

# (مبسط v2.5) قائمة المراقبة لا تزال تعمل
ALERT_WATCHLIST = ['bitcoin', 'ethereum', 'solana', 'binancecoin']
ALERT_THRESHOLD_PERCENT = 3.0 

# --- [2] الدوال المساعدة (إرسال الرسائل) ---
# (هذه الدوال آمنة وتعمل بشكل جيد - لا تغيير)
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
        return True
    except requests.exceptions.RequestException as e:
        print(f"!!! فشل إرسال (التقرير المصور): {getattr(response, 'text', 'لا يوجد رد')}")
        return False

def post_text_to_telegram(text_content):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = { 'chat_id': CHANNEL_USERNAME, 'text': text_content, 'parse_mode': 'HTML', 'disable_web_page_preview': True }
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        print(">>> تم إرسال (التقرير النصي) بنجاح!")
    except requests.exceptions.RequestException as e:
        print(f"!!! فشل إرسال (التقرير النصي): {getattr(response, 'text', 'لا يوجد رد')}")

# --- [3] دوال تنسيق التقرير (Helpers) ---
# (لا تغيير هنا)
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

# --- [4] دوال "المهام" (مبسطة لـ v2.5 - لا توجد مفاتيح API) ---

# [المهمة 0: فحص التنبيهات]
def run_price_alert_job():
    print("--- بدء مهمة [A. فحص التنبيهات الدورية] ---")
    try:
        ids = ",".join(ALERT_WATCHLIST)
        url = f"{COINGECKO_API_URL}/simple/price"
        # (v2.5) لا نحتاج مفتاح API هنا
        params = {'ids': ids, 'vs_currencies': 'usd', 'include_24hr_change': 'true'}
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
                icon = "🚨"; direction_icon = "🟢" if change > 0 else "🔴"
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
        # (v2.5) لا نحتاج مفتاح API هنا
        params = {'vs_currency': 'usd', 'order': 'market_cap_desc', 'per_page': 5, 'page': 1, 'sparkline': 'false'}
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        for coin in data:
            name = coin.get('name', 'N/A'); symbol = coin.get('symbol', '').upper()
            price = format_price(coin.get('current_price'))
            change = format_change_percent(coin.get('price_change_percentage_24h'), "24h")
            market_cap = format_large_number(coin.get('market_cap'))
            total_volume = format_large_number(coin.get('total_volume'))
            image_url = coin.get('image')
            report = f"📊 <b>تقرير السوق (العملات الرائدة)</b>\n\n<b>{name} ({symbol})</b>\n"
            report += f"💰 السعر: {price}\n📊 24س تغير: {change}\n"
            report += f"🏦 القيمة السوقية: {market_cap}\n📈 حجم التداول: {total_volume}\n"
            report += f"\n---\n<i>*تابعنا للمزيد من {CHANNEL_USERNAME}*</i>"
            if image_url:
                success = post_photo_to_telegram(image_url, report)
                if not success:
                    print("... (v2.4 Fallback) فشل إرسال الصورة، جاري الإرسال كنص...")
                    post_text_to_telegram(report)
            else:
                post_text_to_telegram(report)
    except Exception as e:
        print(f"!!! فشلت مهمة (تقرير السوق): {e}")

# [المهمة 2: أكبر الرابحين (اليومي)]
def run_gainers_job():
    print("--- بدء مهمة [2. أكبر الرابحين (Top 3 Daily)] ---")
    try:
        url = f"{COINGECKO_API_URL}/coins/markets"
        # (v2.5) نعود لطريقة v1.5 لجلب الرابحين (لا تحتاج مفتاح)
        params = {'vs_currency': 'usd', 'order': 'price_change_percentage_24h_desc', 'per_page': 3, 'page': 1, 'sparkline': 'false'}
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        for coin in data:
            name = coin.get('name', 'N/A'); symbol = coin.get('symbol', '').upper()
            price = format_price(coin.get('current_price'))
            change = format_change_percent(coin.get('price_change_percentage_24h'), "24h")
            market_cap = format_large_number(coin.get('market_cap'))
            total_volume = format_large_number(coin.get('total_volume'))
            image_url = coin.get('image')
            report = f"🚀 <b>أكبر الرابحين (آخر 24 ساعة)</b>\n\n<b>{name} ({symbol})</b>\n"
            report += f"💰 السعر: {price}\n📊 24س تغير: {change}\n"
            report += f"🏦 القيمة السوقية: {market_cap}\n📈 حجم التداول: {total_volume}\n"
            report += f"\n---\n<i>*تابعنا للمزيد من {CHANNEL_USERNAME}*</i>"
            if image_url:
                success = post_photo_to_telegram(image_url, report)
                if not success:
                    print("... (v2.4 Fallback) فشل إرسال الصورة، جاري الإرسال كنص...")
                    post_text_to_telegram(report)
            else:
                post_text_to_telegram(report)
    except Exception as e:
        print(f"!!! فشلت مهمة (أكبر الرابحين): {e}")

# [المهمة 3: أكبر الخاسرين (اليومي)]
def run_losers_job():
    print("--- بدء مهمة [3. أكبر الخاسرين (Top 3 Daily)] ---")
    try:
        url = f"{COINGECKO_API_URL}/coins/markets"
        params = {'vs_currency': 'usd', 'order': 'price_change_percentage_24h_asc', 'per_page': 3, 'page': 1, 'sparkline': 'false'}
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        for coin in data:
            name = coin.get('name', 'N/A'); symbol = coin.get('symbol', '').upper()
            price = format_price(coin.get('current_price'))
            change = format_change_percent(coin.get('price_change_percentage_24h'), "24h")
            market_cap = format_large_number(coin.get('market_cap'))
            total_volume = format_large_number(coin.get('total_volume'))
            image_url = coin.get('image')
            report = f"📉 <b>أكبر الخاسرين (آخر 24 ساعة)</b>\n\n<b>{name} ({symbol})</b>\n"
            report += f"💰 السعر: {price}\n📊 24س تغير: {change}\n"
            report += f"🏦 القيمة السوقية: {market_cap}\n📈 حجم التداول: {total_volume}\n"
            report += f"\n---\n<i>*تابعنا للمزيد من {CHANNEL_USERNAME}*</i>"
            if image_url:
                success = post_photo_to_telegram(image_url, report)
                if not success:
                    print("... (v2.4 Fallback) فشل إرسال الصورة، جاري الإرسال كنص...")
                    post_text_to_telegram(report)
            else:
                post_text_to_telegram(report)
    except Exception as e:
        print(f"!!! فشلت مهمة (أكبر الخاسرين): {e}")
        
# [المهمة 4: أعلى حجم تداول (جديد v2.5 - بديل الأخبار)]
def run_volume_job():
    print("--- بدء مهمة [4. أعلى حجم تداول (Top 3)] ---")
    try:
        url = f"{COINGECKO_API_URL}/coins/markets"
        params = {'vs_currency': 'usd', 'order': 'volume_desc', 'per_page': 3, 'page': 1, 'sparkline': 'false'}
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        for coin in data:
            name = coin.get('name', 'N/A'); symbol = coin.get('symbol', '').upper()
            price = format_price(coin.get('current_price'))
            change = format_change_percent(coin.get('price_change_percentage_24h'), "24h")
            market_cap = format_large_number(coin.get('market_cap'))
            total_volume = format_large_number(coin.get('total_volume'))
            image_url = coin.get('image')
            report = f"📈 <b>الأعلى في حجم التداول (آخر 24 ساعة)</b>\n\n<b>{name} ({symbol})</b>\n"
            report += f"💰 السعر: {price}\n📊 24س تغير: {change}\n"
            report += f"🏦 القيمة السوقية: {market_cap}\n📈 حجم التداول: {total_volume}\n"
            report += f"\n---\n<i>*تابعنا للمزيد من {CHANNEL_USERNAME}*</i>"
            if image_url:
                success = post_photo_to_telegram(image_url, report)
                if not success:
                    print("... (v2.4 Fallback) فشل إرسال الصورة، جاري الإرسال كنص...")
                    post_text_to_telegram(report)
            else:
                post_text_to_telegram(report)
    except Exception as e:
        print(f"!!! فشلت مهمة (أعلى حجم تداول): {e}")

# [المهمة 5: الملخص الأسبوعي]
def run_weekly_summary_job():
    print("--- بدء مهمة [5. الملخص الأسبوعي (Top 3/3)] ---")
    try:
        url = f"{COINGECKO_API_URL}/coins/markets"
        params = {'vs_currency': 'usd', 'order': 'market_cap_desc', 'per_page': 100, 'page': 1, 'sparkline': 'false', 'price_change_percentage': '7d'}
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        valid_data = [c for c in data if c.get('price_change_percentage_7d_in_currency') is not None]
        gainers = sorted(valid_data, key=lambda x: x['price_change_percentage_7d_in_currency'], reverse=True)[:3]
        losers = sorted(valid_data, key=lambda x: x['price_change_percentage_7d_in_currency'])[:3]
        
        for coin in gainers:
            report = f"🏆 <b>ملخص الأسبوع: أكبر الرابحين</b>\n\n<b>{coin.get('name', 'N/A')} ({coin.get('symbol', '').upper()})</b>\n"
            report += f"💰 السعر: {format_price(coin.get('current_price'))}\n🗓️ 7أيام تغير: {format_change_percent(coin.get('price_change_percentage_7d_in_currency'), '7d')}\n"
            report += f"🏦 القيمة السوقية: {format_large_number(coin.get('market_cap'))}\n\n---\n<i>*تابعنا للمزيد من {CHANNEL_USERNAME}*</i>"
            success = post_photo_to_telegram(coin.get('image'), report)
            if not success: post_text_to_telegram(report)

        for coin in losers:
            report = f"📉 <b>ملخص الأسبوع: أكبر الخاسرين</b>\n\n<b>{coin.get('name', 'N/A')} ({coin.get('symbol', '').upper()})</b>\n"
            report += f"💰 السعر: {format_price(coin.get('current_price'))}\n🗓️ 7أيام تغير: {format_change_percent(coin.get('price_change_percentage_7d_in_currency'), '7d')}\n"
            report += f"🏦 القيمة السوقية: {format_large_number(coin.get('market_cap'))}\n\n---\n<i>*تابعنا للمزيد من {CHANNEL_USERNAME}*</i>"
            success = post_photo_to_telegram(coin.get('image'), report)
            if not success: post_text_to_telegram(report)
            
    except Exception as e:
        print(f"!!! فشلت مهمة (الملخص الأسبوعي): {e}")

# --- [5] التشغيل الرئيسي (الذكي v2.5) ---
def main():
    print("==========================================")
    print(f"بدء تشغيل (v2.5 - بوت Market Byte - مبسط وآمن)...")
    
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
        print(">>> (v2.5) ليلاً: تم جدولة [أعلى حجم تداول] (بدل الأخبار)")
        job_to_run = run_volume_job # <-- (جديد v2.5)
        
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

