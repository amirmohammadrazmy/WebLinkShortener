# راهنمای نصب و اجرای برنامه کوتاه‌کننده لینک 2ad.ir

## پیش‌نیازها

### 1. نصب Python
- Python 3.8 یا بالاتر
- دانلود از: https://www.python.org/downloads/

### 2. نصب Chrome Browser
- دانلود از: https://www.google.com/chrome/

## مراحل نصب

### 1. دانلود فایل‌ها
تمام فایل‌های برنامه را دانلود کنید:
- `main.py`
- `url_shortener.py`
- `config.py`
- `utils.py`
- `config.json`

### 2. نصب کتابخانه‌ها
```bash
pip install selenium webdriver-manager
```

### 3. آماده‌سازی فایل‌های لینک
دو فایل متنی ایجاد کنید در پوشه `input/`:
- `input/download_links_480p.txt`
- `input/output_links.txt`

هر فایل باید حاوی لینک‌هایتان باشد (هر خط یک لینک).

## اجرای برنامه

### روش 1: اجرای ساده
```bash
python main.py --username your_email@example.com --password your_password
```

### روش 2: اجرای با تنظیمات
```bash
python main.py --username your_email@example.com --password your_password --batch-size 5 --delay 1.0 --verbose
```

### روش 3: اجرای headless (بدون نمایش مرورگر)
```bash
python main.py --username your_email@example.com --password your_password --headless
```

## تنظیمات

### گزینه‌های مهم:
- `--batch-size`: تعداد لینک‌های پردازش شده در هر دسته (پیش‌فرض: 10)
- `--delay`: تأخیر بین هر درخواست به ثانیه (پیش‌فرض: 2.0)
- `--headless`: اجرا بدون نمایش مرورگر
- `--verbose`: نمایش جزئیات بیشتر
- `--resume`: ادامه از آخرین checkpoint

## خروجی‌ها

### فایل‌های تولید شده:
- `output/shortened_urls_[تاریخ].csv`: لینک‌های کوتاه شده
- `output/checkpoint.json`: فایل checkpoint برای ادامه کار
- `logs/url_shortener_[تاریخ].log`: فایل لاگ

### فرمت فایل CSV:
```
timestamp,original_url,shortened_url,status
2025-07-18T20:30:00,https://example.com,https://2ad.ir/abc123,SUCCESS
```

## عیب‌یابی

### مشکلات رایج:
1. **ChromeDriver Error**: برنامه خودکار ChromeDriver را نصب می‌کند
2. **Timeout Error**: سرعت اینترنت کند - `--delay` را افزایش دهید
3. **Login Failed**: اطلاعات کاربری را بررسی کنید

### در صورت قطع شدن برنامه:
```bash
python main.py --username your_email@example.com --password your_password --resume
```

## تماس
در صورت بروز مشکل، فایل log را بررسی کنید.