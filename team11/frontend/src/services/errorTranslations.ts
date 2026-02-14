// Types for expected backend shapes
export type BackendValidationError = {
  error?: string;
  details?: string[];
  [key: string]: any;
};

export type BackendRaw = string | BackendValidationError | null | undefined;

export const TRANSLATIONS: Record<string, string> = {
  'Invalid JSON': 'JSON نامعتبر است.',
  'email is required': 'ایمیل الزامی است.',
  'password is required': 'رمز عبور الزامی است.',
  'invalid email format': 'فرمت ایمیل نامعتبر است.',
  'invalid password': 'رمز عبور نامعتبر است.',
  'age must be an integer': 'سن باید عدد باشد.',
  'age must be between 1 and 120': 'سن باید بین 1 تا 120 باشد.',
  'email already registered': 'این ایمیل قبلاً ثبت شده است.',
  'Invalid credentials': 'ایمیل یا رمز عبور اشتباه است.',
  'User disabled': 'حساب کاربری غیرفعال است.',
  'Missing refresh token': 'توکن تازه‌سازی وجود ندارد.',
  'Invalid token': 'توکن نامعتبر است.',
};

function isValidationError(obj: unknown): obj is BackendValidationError {
  return !!obj && typeof obj === 'object' && ('error' in (obj as any) || 'details' in (obj as any));
}

/**
 * Translate a backend error payload into a user-facing Persian string.
 * Returns null when no sensible translation is available.
 */
export function translateError(raw: BackendRaw): string | null {
  if (!raw) return null;

  if (typeof raw === 'string') {
    return TRANSLATIONS[raw] ?? raw;
  }

  if (isValidationError(raw)) {
    const { error, details } = raw;
    if (error && typeof error === 'string') {
      if (Array.isArray(details) && details.length) {
        const base = TRANSLATIONS[error] ?? error;
        return `${base} (${details.join('; ')})`;
      }
      return TRANSLATIONS[error] ?? error;
    }
  }

  // If payload has a message property (some libs) use it
  if (typeof (raw as any).message === 'string') {
    const msg = (raw as any).message as string;
    return TRANSLATIONS[msg] ?? msg;
  }

  return null;
}

export default translateError;
