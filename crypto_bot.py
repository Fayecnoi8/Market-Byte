# =============================================================================
#    *** بوت Market Byte - الإصدار 6.0 (إصلاح Demo Key) ***
#
#  (جديد) تم اكتشاف المشكلة بفضل ملف HTML الخاص بالمستخدم!
#  المفتاح ليس (Pro) بل (Demo)، ويجب إرساله كرابط (parameter)
#  وليس كـ (header)، ويستخدم الرابط العام (api) وليس (pro-api).
# =============================================================================

import requests
import os
import sys
import datetime
import locale

# --- [1] الإعدادات والمفاتيح السرية (الاحترافية) ---
try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
    CHANNEL_USERNAME = os.environ['CHANNEL_USERNAME'] # يجب أن يبدأ بـ @
    COINGECKO_API_KEY = os.environ['COINGECKO_API_KEY'] # (v6.0) هذا هو مفتاح "Demo"
    
except KeyError as e:
    print(f"!!! خطأ: متغير البيئة الأساسي غير موجود: {e}")
    print("!!! هل تذكرت إضافة (BOT_TOKEN, CHANNEL_USERNAME, COINGECKO_API_KEY)؟")
    sys.exit(1)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
# (v6.0) العودة إلى الرابط العام (كما في ملف HTML)
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"

# (v6.0) هذا هو اسم المفتاح الذي سيتم إرساله في الرابط
# (مستخرج من ملف HTML: x_cg_demo_api_key)
API_KEY_PARAM_NAME = 'x_cg_demo_api_key'

# (إعدادات مهمة التنبيهات)
ALERT_WATCHLIST = ['bitcoin', 'ethereum', 'solana']
ALERT_THRESHOLD_PERCENT = 3.0 

# (إعداد لغة عربية للتاريخ)
try:
    locale.setlocale(locale.LC_TIME, 'ar_SA.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'ar_EG.UTF-8')
    except locale.Error:
        print("... تحذير: لم يتم العثور على اللغة العربية (ar_SA/ar_EG)، سيتم استخدام التاريخ الافتراضي.")


# --- [2] الدوال المساعدة (إرسال الرسائل - آمنة) ---
# ... (الدوال post_photo_to_telegram و post_text_to_telegram لم تتغير) ...

def post_photo_to_telegram(image_url, text_caption):
    """(آمن) إرسال صورة + نص (مع خدعة الرفع)"""
    print(f"... جاري إرسال (التقرير المصور) إلى {CHANNEL_USERNAME} ...")
    response = None 
    try:
        print(f"   ... (1/2) جاري تحميل الصورة من: {image_url}")
        image_response = requests.get(image_url, timeout=30)
        image_response.raise_for_status()
        image_data = image_response.content
        
        url = f"{TELEGRAM_API_URL}/sendPhoto"
        payload = { 'chat_id': CHANNEL_USERNAME, 'caption': text_caption, 'parse_mode': 'HTML'}
        content_type = 'image/png' if '.png' in image_url else 'image/jpeg'
        files = {'photo': ('coin_image', image_data, content_type)}
        
        print("   ... (2/2) جاري رفع الصورة إلى تيليجرام ...")
        response = requests.post(url, data=payload, files=files, timeout=60)
        response.raise_for_status()
        print(">>> تم إرسال (التقرير المصور) بنجاح!")
        return True # نجح
    except requests.exceptions.RequestException as e:
        error_message = getattr(response, 'text', 'لا يوجد رد من تيليجرام')
        print(f"!!! فشل إرسال (التقرير المصور): {e} - {error_message}")
        return False # فشل

def post_text_to_telegram(text_content):
    """(آمن) إرسال نص فقط (للتنبيهات أو كخطة احتياطية)"""
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = { 'chat_id': CHANNEL_USERNAME, 'text': text_content, 'parse_mode': 'HTML', 'disable_web_page_preview': True }
    response = None 
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        print(">>> تم إرسال (التقرير النصي) بنجاح!")
    except requests.exceptions.RequestException as e:
        error_message = getattr(response, 'text', 'لا يوجد رد من تيليجرام')
        print(f"!!! فشل إرسال (التقرير النصي): {e} - {error_message}")

# --- [3] دوال تنسيق التقرير (Helpers) ---
# ... (الدوال format_price, format_change_percent, format_large_number لم تتغير) ...

def format_price(price):
    if price is None: return "N/A"
    if price < 1: return f"${price:.8f}" 
    else: return f"${price:,.2f}"

def format_change_percent(change):
    if change is None: return "(N/A)"
    if change >= 0: return f"(📊 🟢 +{change:.2f}%)"
    else: return f"(📊 🔴 {change:.2f}%)"
    
def format_large_number(num):
    if num is None: return "N/A"
    if num >= 1_000_000_000:
        return f"${(num / 1_000_000_000):.2f}B" 
    elif num >= 1_000_000:
        return f"${(num / 1_000_000):.2f}M" 
    else:
        return f"${num:,.0f}"

# --- [4] تعريف المهام (v6.0 - إصلاح Demo Key) ---

# [المهمة 1: النشر اليومي 8 صباحاً]
def run_daily_top_15_job():
    print("--- بدء مهمة [1. النشر اليومي (Top 15)] ---")
    
    # 1. إرسال العنوان (مع التاريخ واليوم)
    try:
        today = datetime.datetime.now()
        date_str = today.strftime("📊 <b>أفضل 15 عملة لهذا اليوم (%A، %d %B %Y)</b>")
        post_text_to_telegram(date_str)
    except Exception as e:
        print(f"!!! فشل إرسال رسالة العنوان: {e}")

    # 2. جلب وإرسال أفضل 15 عملة
    response = None 
    try:
        url = f"{COINGECKO_API_URL}/coins/markets"
        # (v6.0) هذا هو الإصلاح الأهم! إضافة المفتاح كـ "param"
        params = {
            'vs_currency': 'usd', 
            'order': 'market_cap_desc', 
            'per_page': 15, 
            'page': 1, 
            'sparkline': 'false',
            API_KEY_PARAM_NAME: COINGECKO_API_KEY # (v6.0) الإصلاح هنا
        }
        
        # (v6.0) لا نحتاج "headers" بعد الآن
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status() 
        data = response.json()
        
        print(f"... (API Demo) تم جلب {len(data)} عملة بنجاح.")
        
        for idx, coin in enumerate(data, 1):
            name = coin.get('name', 'N/A')
            symbol = coin.get('symbol', '').upper()
            price = format_price(coin.get('current_price'))
            change = format_change_percent(coin.get('price_change_percentage_24h'))
            market_cap = format_large_number(coin.get('market_cap'))
            total_volume = format_large_number(coin.get('total_volume'))
            image_url = coin.get('image')
            
            report = f"<b>{idx}. {name} ({symbol})</b>\n\n"
            report += f"💰 السعر: {price}\n"
            report += f"📊 24س تغير: {change}\n"
            report += f"🏦 القيمة السوقية: {market_cap}\n"
            report += f"📈 حجم التداول: {total_volume}\n"
            report += f"\n---\n<i>*تابعنا للمزيد من {CHANNEL_USERNAME}*</i>"
            
            if image_url:
                success = post_photo_to_telegram(image_url, report)
                if not success:
                    print("... فشل إرسال الصورة، جاري الإرسال كنص احتياطي...")
                    post_text_to_telegram(report)
            else:
                print(f"!!! لا يوجد رابط صورة لـ {name}. جاري إرسال نص فقط.")
                post_text_to_telegram(report)
        
    except Exception as e:
        error_message = getattr(response, 'text', 'لا يوجد رد من API')
        print(f"!!! فشل جلب أو معالجة بيانات (تقرير السوق): {e} - {error_message}")
        post_text_to_telegram(f"🚨 حدث خطأ أثناء جلب بيانات السوق اليومية. يرجى المراجعة.")

# [المهمة 2: فحص التنبيهات كل 6 ساعات]
def run_price_alert_job():
    print("--- بدء مهمة [2. فحص التنبيهات الدورية] ---")
    response = None 
    try:
        ids = ",".join(ALERT_WATCHLIST)
        url = f"{COINGECKO_API_URL}/simple/price"
        # (v6.0) الإصلاح الثاني هنا! إضافة المفتاح كـ "param"
        params = {
            'ids': ids, 
            'vs_currencies': 'usd', 
            'include_24hr_change': 'true',
            API_KEY_PARAM_NAME: COINGECKO_API_KEY # (v6.0) الإصلاح هنا
        }
        
        # (v6.0) لا نحتاج "headers"
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        print(f"... (API Demo) تم جلب بيانات التنبيهات لـ {len(data)} عملة.")
        
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
        error_message = getattr(response, 'text', 'لا يوجد رد من API')
        print(f"!!! فشلت مهمة (فحص التنبيهات): {e} - {error_message}")

# --- [5] التشغيل الرئيسي (v6.0) ---
# ... (دالة main() لم تتغير عن v5.2، فهي ذكية وصحيحة) ...

def main():
    print("==========================================")
    print(f"بدء تشغيل (v6.0 - بوت Market Byte - إصلاح Demo Key)...")
    
    current_hour_utc = datetime.datetime.now(datetime.timezone.utc).hour
    print(f"الساعة الحالية (UTC): {current_hour_utc}")

    is_manual_run = os.environ.get('GITHUB_EVENT_NAME') == 'workflow_dispatch'

    # --- تحديد المهمة ---
    
    # 1. إذا كانت الساعة 5:00 UTC (8 صباحاً بغداد)
    if current_hour_utc == 5:
        print(">>> (الوقت: 5:00 UTC) - تم تحديد [النشر اليومي].")
        run_daily_top_15_job()

    # 2. إذا كانت الساعة 0, 6, 12, أو 18 UTC
    elif current_hour_utc in [0, 6, 12, 18]:
        print(f">>> (الوقت: {current_hour_utc}:00 UTC) - تم تحديد [فحص التنبيهات].")
        run_price_alert_job()

    # 3. إذا كان تشغيلاً يدوياً (للاختبار)
    elif is_manual_run:
        print(">>> (تشغيل يدوي للاختبار) - سيتم تشغيل [النشر اليومي].")
        run_daily_top_15_job()

    # 4. أي وقت آخر
    else:
        print(f"... (الوقت: {current_hour_utc}:00 UTC) - لا توجد مهمة مجدولة لهذا الوقت. تخطي.")

    print("==========================================")
    print("... اكتملت المهمة.")

if __name__ == "__main__":
    main()

