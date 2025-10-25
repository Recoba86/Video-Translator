# راهنمای رفع مشکل Bidirectional Text (راست به چپ و چپ به راست)

## مشکل چیست؟

وقتی در زیرنویس فارسی، کلمات انگلیسی قرار می‌گیرند، به خاطر اختلاف جهت نوشتار:
- **فارسی**: راست به چپ (RTL - Right-to-Left)
- **انگلیسی**: چپ به راست (LTR - Left-to-Right)

ترتیب کلمات و فاصله‌ها بهم می‌ریزد.

### مثال مشکل:

**قبل از فیکس:**
```
من T-Y-O-Lو P-SOLهستم
```

**بعد از فیکس:**
```
من T-Y-O-L و P-SOL هستم
```

## راه حل چیست؟

### ۱. **RLM (Right-to-Left Mark)** - کاراکتر غیر‌قابل رؤیت

کاراکتر یونیکد `U+200F` که جهت متن را مشخص می‌کند:
```
من ‏TESOL‏ هستم
    ↑     ↑
   RLM   RLM
```

### ۲. **فاصله‌گذاری خودکار**

قبل و بعد از کلمات انگلیسی، فاصله اضافه می‌شود:
- `TYOLهستم` → `TYOL هستم`
- `TESOLو` → `TESOL و`

## چطور کار می‌کند؟

### در کد (`bidi_fixer.py`):

```python
from bidi_fixer import fix_bidi_text

# متن مشکل‌دار
text = "من T-Y-O-Lو P-SOLهستم"

# فیکس خودکار
fixed = fix_bidi_text(text)
# نتیجه: "من ‏T-Y-O-L‏ و ‏P-SOL‏ هستم"
```

### در پروسه ویدئو:

فیکس به صورت خودکار در دو مرحله اعمال می‌شود:

#### ۱. **هنگام ایجاد زیرنویس SRT:**
```python
def generate_srt(self, segments, output_path):
    for segment in segments:
        # فیکس خودکار قبل از نوشتن
        fixed_text = fix_bidi_text(segment['text'])
        f.write(f"{fixed_text}\n\n")
```

#### ۲. **هنگام ایجاد زیرنویس ASS:**
```python
def generate_ass(self, segments, output_path):
    for segment in segments:
        # فیکس خودکار
        fixed_text = fix_bidi_text(segment['text'])
        text = fixed_text.replace('\n', '\\N')
```

## چه چیزهایی فیکس می‌شود؟

### ✅ کلمات انگلیسی:
- `TESOL`, `TEYL`, `Python`, `MacBook`

### ✅ مخفف‌ها با خط‌فاصله:
- `T-Y-O-L`, `P-SOL`, `AI-powered`

### ✅ ایمیل و URL:
- `test@email.com`
- `github.com`

### ✅ اعداد انگلیسی:
- `2024`, `123-456`

## تست دستی

برای تست فیکسر:

```bash
source venv/bin/activate
python bidi_fixer.py
```

**نتیجه:**
```
=== Bidi Fix Test Results ===

Original: من T-Y-O-Lو P-SOLهستم
Fixed:    من ‏T-Y-O-L‏ و ‏P-SOL‏ هستم
Hex:      \u0645\u0646 \u200fT-Y-O-L\u200f \u0648 \u200fP-SOL\u200f \u0647\u0633\u062a\u0645
```

## تقویت پرامپت Gemini

در `video_processor_gemini.py`، به پرامپت ترجمه این قوانین اضافه شده:

```python
IMPORTANT - HANDLING ENGLISH WORDS:
8. For English acronyms, names, or technical terms that must stay in English:
   - Separate them with spaces: "من T-Y-O-L و P-SOL هستم"
   - NOT joined: "من T-Y-O-Lو P-SOLهستم"
   - Add ‏ (RLM - Right-to-Left Mark) before/after English text if needed
9. If translation includes English words, structure it clearly:
   - Example: "من یک معلم TESOL هستم" (with proper spacing)
```

این باعث می‌شود Gemini از همان ابتدا فاصله‌گذاری بهتری داشته باشد.

## نتیجه نهایی

حالا زیرنویس‌ها:
- ✅ **فاصله‌گذاری صحیح** بین کلمات فارسی و انگلیسی
- ✅ **جهت درست** برای نمایش متن
- ✅ **خوانایی بالا** در تمام player ها
- ✅ **کار با اکثر فونت‌ها** (Vazir, Sahel, Yekan، و...)

## نکات مهم

### ۱. UTF-8 Encoding
همیشه فایل‌های زیرنویس با `utf-8` باز/ذخیره شوند:
```python
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
```

### ۲. RLM قابل رؤیت نیست
کاراکتر `U+200F` در ادیتور دیده نمی‌شود، اما روی نمایش تأثیر دارد.

### ۳. برای مشاهده Hex:
```python
text = "من ‏TESOL‏ هستم"
print(text.encode('unicode-escape'))
# b'\u0645\u0646 \u200fTESOL\u200f \u0647\u0633\u062a\u0645'
```

## مثال‌های بیشتر

### قبل و بعد:

| قبل (مشکل‌دار) | بعد (فیکس شده) |
|---|---|
| `من TYOLهستم` | `من ‏TYOL‏ هستم` |
| `این TESOLو TEYLاست` | `این ‏TESOL‏ و ‏TEYL‏ است` |
| `معلم P-SOLبا مدرک` | `معلم ‏P-SOL‏ با مدرک` |

## پشتیبانی Player ها

این فیکس با تمام player های رایج کار می‌کند:
- ✅ VLC Media Player
- ✅ MPV
- ✅ QuickTime Player (macOS)
- ✅ Windows Media Player
- ✅ YouTube Player
- ✅ مرورگرهای وب (Chrome, Firefox, Safari)

## ارتقاء آینده

در صورت نیاز می‌توان:
- افزودن پشتیبانی از زبان‌های دیگر (عربی، عبری)
- تنظیم سطح aggressiveness فیکس
- افزودن LRE/RLE برای کنترل دقیق‌تر
