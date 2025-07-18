# 🌐 راهنمای استقرار آنلاین کوتاه‌کننده لینک 2ad.ir

## مقدمه

این راهنما برای استقرار برنامه روی سرورهای آنلاین است که IP بهتری برای دسترسی به سایت‌های ایرانی دارند.

## پلتفرم‌های پیشنهادی

### 1. 🚂 Railway.app (توصیه اول)
**مزایا:**
- نصب آسان و سریع
- IP مناسب برای سایت‌های ایرانی
- رایگان برای استفاده معمولی

**مراحل:**
1. ثبت نام در [Railway.app](https://railway.app)
2. Connect کردن GitHub repository
3. Deploy automatic

**فایل‌های مورد نیاز:**
- `web_server.py` (اصلی)
- `url_shortener.py`
- `config.py`  
- `utils.py`
- `deploy_requirements.txt`
- `railway.json`
- `Procfile`

### 2. 🎨 Render.com (رایگان)
**مزایا:**
- سرویس رایگان قوی
- نصب خودکار از GitHub
- SSL رایگان

**مراحل:**
1. ثبت نام در [Render.com](https://render.com)
2. New Web Service
3. Connect GitHub repo
4. Environment: Python
5. Build Command: `pip install -r deploy_requirements.txt`
6. Start Command: `gunicorn web_server:app --bind 0.0.0.0:$PORT`

### 3. ☁️ DigitalOcean App Platform
**مزایا:**
- کیفیت سرور بالا
- IP‌های متنوع
- Docker support

**مراحل:**
1. ثبت نام در [DigitalOcean](https://digitalocean.com)
2. Apps → Create App
3. GitHub source
4. Auto-detect Docker یا Python

### 4. 💜 Heroku
**مراحل:**
1. ثبت نام در [Heroku](https://heroku.com)
2. New App
3. Deploy from GitHub
4. Add buildpacks:
   - `https://github.com/heroku/heroku-buildpack-google-chrome`
   - `https://github.com/heroku/heroku-buildpack-chromedriver`
   - `heroku/python`

## راه‌اندازی سریع

### مرحله 1: آماده‌سازی کد
1. تمام فایل‌های پروژه را در یک پوشه قرار دهید
2. یک repository در GitHub بسازید
3. فایل‌ها را upload کنید

### مرحله 2: انتخاب پلتفرم
بهترین انتخاب: **Railway.app**

### مرحله 3: استقرار
1. وارد Railway.app شوید
2. "New Project" → "Deploy from GitHub"
3. Repository خود را انتخاب کنید
4. منتظر deploy شدن بمانید
5. URL سایت شما آماده است!

## استفاده از سایت

1. **وارد شدن:** آدرس سایت deployed شده
2. **وارد کردن اطلاعات:**
   - نام کاربری 2ad.ir
   - رمز عبور
   - لیست URL ها
3. **تنظیمات:**
   - تعداد هر دسته: 5 (پیشنهادی)
   - تاخیر: 3 ثانیه (پیشنهادی)
4. **شروع پردازش:** کلیک روی "شروع پردازش"
5. **مشاهده پیشرفت:** نوار پیشرفت نمایش داده می‌شود
6. **دانلود نتایج:** پس از تکمیل، فایل CSV قابل دانلود است

## مزایای نسخه آنلاین

✅ **بدون نیاز به نصب:** فقط مرورگر کافی است
✅ **IP مناسب:** سرورهای خارجی با IP بهتر
✅ **رابط وب زیبا:** استفاده آسان
✅ **پردازش پس‌زمینه:** می‌توانید صفحه را ببندید
✅ **دانلود نتایج:** فایل CSV آماده
✅ **رایگان:** اکثر پلتفرم‌ها رایگان هستند

## نکات مهم

### امنیت
- اطلاعات کاربری در session محفوظ هستند
- رمز عبور رمزنگاری می‌شود
- اتصال HTTPS امن

### محدودیت‌ها
- حداکثر 1000 URL در هر بار
- timeout برای URL های خیلی طولانی
- محدودیت منابع سرور رایگان

### عیب‌یابی
اگر سایت کار نکرد:
1. چک کنید IP سرور مسدود نباشد
2. تعداد URL ها زیاد نباشد
3. تاخیر را بیشتر کنید
4. پلتفرم دیگر امتحان کنید

## خلاصه مراحل

1. **دانلود فایل‌ها از Replit**
2. **Upload به GitHub**
3. **Deploy در Railway.app**
4. **استفاده از رابط وب**
5. **دانلود نتایج**

**با این روش، برنامه شما 24/7 آنلاین و در دسترس خواهد بود!**