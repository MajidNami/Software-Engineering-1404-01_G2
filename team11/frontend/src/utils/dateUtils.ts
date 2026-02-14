import { toJalaali } from 'jalaali-js';

// Convert Arabic/Western digits to Persian digits using locale
const toPersianDigits = (n: number) => n.toLocaleString('fa-IR');

// Pad with zero if needed (returns number string in Persian digits)
const pad = (val: number) => {
  return val < 10 ? `0${val}` : `${val}`;
};

/**
 * Format an ISO date string (YYYY-MM-DD or full ISO) to Jalali date string
 * Returns a string like '۱۴۰۴/۰۳/۰۵' (Persian digits)
 */
export const formatToJalali = (isoDate?: string | null): string | null => {
  if (!isoDate) return null;

  const d = new Date(isoDate);
  if (isNaN(d.getTime())) return null;

  const { jy, jm, jd } = toJalaali(d.getFullYear(), d.getMonth() + 1, d.getDate());

  // Use western padded numbers then convert to Persian digits
  const y = jy.toString();
  const m = pad(jm);
  const day = pad(jd);

  // Convert each segment to Persian digits using toLocaleString on numbers
  // building Persian segments by converting number strings to numbers first
  // (jy may be > 1000 so toLocaleString works directly)
  const yPers = Number(y).toLocaleString('fa-IR');
  const mPers = Number(m).toLocaleString('fa-IR', {minimumIntegerDigits:2, useGrouping:false});
  const dPers = Number(day).toLocaleString('fa-IR', {minimumIntegerDigits:2, useGrouping:false});

  return `${yPers}/${mPers}/${dPers}`;
};
