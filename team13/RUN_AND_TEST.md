# اجرا و تست — team13

همهٔ دستورات از **ریشهٔ پروژه** (پوشهٔ حاوی `manage.py`) اجرا شوند.

**پروژهٔ گروهی:** هیچ فایلی در app404، core یا خارج از team13 نیاز به تغییر ندارد. فقط در `.env` ریشهٔ پروژه می‌توانید `TEAM_APPS=team13` قرار دهید (جزئیات: `team13/INTEGRATION.md`).

---


### مرحله ۱ — باز کردن ترمینال در ریشهٔ پروژه
  ```powershell
  cd C:\Users\iliya\OneDrive\Desktop\soft7\soft-axiom
  ```

### مرحله ۲ — نصب وابستگی‌ها
```powershell
pip install -r requirements.txt
pip install -r team13/requirements.txt
```

### مرحله ۳ — مایگریشن (ساخت جداول دیتابیس)
```powershell
py -3.11 manage.py makemigrations team13
py -3.11 manage.py migrate
```

### مرحله ۴ — بارگذاری داده در دیتابیس
- پوشهٔ داده: **team13/temp_data_inseart** (با فایل‌های hotels.json، hospitals.json، restaurants.json). در صورت نبود، اسکریپت به‌ترتیب **team13/temp_data** یا ریشهٔ پروژه را هم بررسی می‌کند.

```powershell
py -3.11 team13/load_temp_data.py --clear
```

(جایگزین: `py -3.11 manage.py loaddata_team13_csv --clear` فقط برای CSV در team13/temp_data)

### مرحله ۵ — اجرای سرور
```powershell
py -3.11 manage.py runserver
```
وقتی پیام `Starting development server at http://127.0.0.1:8000/` را دیدید، سرور آماده است.

### مرحله ۶ — باز کردن در مرورگر
- آدرس صفحهٔ اصلی: **http://127.0.0.1:8000/team13/**
- برای توقف سرور در ترمینال: **Ctrl+C** یا **Ctrl+Break**

---

## دستورات دیگر (مرجع)

```powershell
# فقط بارگذاری (بدون پاک‌کردن)
py -3.11 team13/load_temp_data.py

# بارگذاری از مسیر دلخواه
py -3.11 team13/load_temp_data.py --path path/to/folder
```

---

## لینک‌های تست

| صفحه      | آدرس |
|-----------|------|
| اصلی      | http://127.0.0.1:8000/team13/ |
| مکان‌ها   | http://127.0.0.1:8000/team13/places/ |
| رویدادها  | http://127.0.0.1:8000/team13/events/ |
| مسیریابی  | http://127.0.0.1:8000/team13/routes/ |
| امداد     | http://127.0.0.1:8000/team13/emergency/ |

JSON: `?format=json` به انتهای آدرس اضافه کنید.
