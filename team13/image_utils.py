# آپلود، بهینه‌سازی و ذخیرهٔ تمام تصاویر کاربر در team13/static/team13/images_user
# ورودی: هر فرمت تصویر (JPEG, PNG, GIF, WebP, BMP و ...) — خروجی: همیشه JPEG بهینه با نام یکتا

import io
import uuid
from pathlib import Path

# حداکثر طول ضلع تصویر بعد از تغییر اندازه (پیکسل)
MAX_SIDE = 1600
# کیفیت ذخیره JPEG (۱–۱۰۰)
JPEG_QUALITY = 82
# حداکثر حجم خروجی تقریبی (بایت)
MAX_OUTPUT_BYTES = 800 * 1024  # 800 KB
# حداکثر حجم ورودی (بایت)
MAX_INPUT_BYTES = 20 * 1024 * 1024  # 20 MB


def get_images_user_dir():
    """مسیر پوشهٔ ذخیرهٔ تصاویر کاربر — همهٔ تصاویر اینجا ذخیره می‌شوند."""
    return Path(__file__).resolve().parent / "static" / "team13" / "images_user"


def _ensure_images_user_dir():
    """اطمینان از وجود پوشهٔ images_user."""
    d = get_images_user_dir()
    d.mkdir(parents=True, exist_ok=True)
    return d


def compress_and_save_image(file_content, original_filename=None):
    """
    هر فرمت تصویر را می‌گیرد، بهینه و فشرده می‌کند و در images_user با نام یکتا (.jpg) ذخیره می‌کند.

    - file_content: بایت‌های فایل (bytes یا شیء با متد read)
    - original_filename: اختیاری؛ برای تشخیص نوع ورودی (در صورت خطا استفاده نمی‌شود)

    برمی‌گرداند: (safe_filename, relative_url) مثلاً ("a1b2c3.jpg", "/static/team13/images_user/a1b2c3.jpg")
    در صورت خطا: (None, None)
    """
    try:
        from PIL import Image
    except ImportError:
        return None, None

    if isinstance(file_content, bytes):
        data = file_content
    else:
        data = file_content.read() if hasattr(file_content, "read") else file_content
    if not data or len(data) > MAX_INPUT_BYTES:
        return None, None

    try:
        img = Image.open(io.BytesIO(data))
    except Exception:
        return None, None

    # نرمال‌سازی حالت برای خروجی JPEG
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    elif img.mode != "RGB":
        img = img.convert("RGB")

    w, h = img.size
    if w > MAX_SIDE or h > MAX_SIDE:
        if w >= h:
            new_w = MAX_SIDE
            new_h = int(h * MAX_SIDE / w)
        else:
            new_h = MAX_SIDE
            new_w = int(w * MAX_SIDE / h)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    upload_dir = _ensure_images_user_dir()
    safe_name = f"{uuid.uuid4().hex}.jpg"
    out_path = upload_dir / safe_name

    quality = JPEG_QUALITY
    for _ in range(3):
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        buf.seek(0)
        if buf.getbuffer().nbytes <= MAX_OUTPUT_BYTES:
            break
        quality = max(40, quality - 15)
    out_path.write_bytes(buf.getvalue())
    relative_url = f"/static/team13/images_user/{safe_name}"
    return safe_name, relative_url


def save_raw_to_images_user(file_content, ext=".jpg"):
    """
    در صورت شکست فشرده‌سازی، بایت‌های تصویر را مستقیم در images_user ذخیره می‌کند.
    نام فایل: uuid + ext (امن و یکتا).
    برمی‌گرداند: (safe_filename, relative_url) یا (None, None)
    """
    if not file_content or len(file_content) > MAX_INPUT_BYTES:
        return None, None
    ext = (ext or ".jpg").lower()
    if not ext.startswith("."):
        ext = "." + ext
    if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        ext = ".jpg"
    upload_dir = _ensure_images_user_dir()
    safe_name = f"{uuid.uuid4().hex}{ext}"
    out_path = upload_dir / safe_name
    try:
        out_path.write_bytes(file_content)
    except Exception:
        return None, None
    relative_url = f"/static/team13/images_user/{safe_name}"
    return safe_name, relative_url
