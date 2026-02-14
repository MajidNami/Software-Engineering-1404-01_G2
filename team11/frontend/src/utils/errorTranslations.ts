export const errorTranslations: Record<string, string> = {
  'Invalid JSON': 'فرمت JSON نامعتبر است.',
  'email is required': 'ایمیل الزامی است.',
  'password is required': 'رمز عبور الزامی است.',
  'invalid email format': 'فرمت ایمیل نامعتبر است.',
  'invalid password': 'رمز عبور نامعتبر است.',
  'age must be an integer': 'سن باید عدد صحیح باشد.',
  'age must be between 1 and 120': 'سن باید بین 1 تا 120 باشد.',
  'email already registered': 'این ایمیل قبلاً ثبت شده است.',
  'Invalid credentials': 'ایمیل یا رمز عبور اشتباه است.',
  'User disabled': 'حساب کاربری غیرفعال است.',
  'Missing refresh token': 'توکن تازه‌سازی یافت نشد.',
  'Invalid token': 'توکن نامعتبر است.',
};

export function translateError(raw?: unknown, fallback = 'خطایی رخ داد. لطفاً دوباره تلاش کنید.') {
  if (!raw) return fallback;

  if (typeof raw === 'object' && raw !== null) {
    const anyRaw: any = raw;
    const err = anyRaw.error ?? anyRaw.message ?? anyRaw.detail;
    if (typeof err === 'string') {
      const mapped = errorTranslations[err];
      if (mapped) return mapped;
      if (Array.isArray(anyRaw.details) && anyRaw.details.length > 0) {
        return `${err}: ${anyRaw.details.join(', ')}`;
      }
      return err;
    }
    return String(raw) || fallback;
  }

  if (typeof raw === 'string') {
    return errorTranslations[raw] || raw || fallback;
  }

  return String(raw) || fallback;
}

export default translateError;
