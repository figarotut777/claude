/**
 * Business Date Utilities
 * Handles overnight operations (12:00 PM - 04:00 AM next day)
 *
 * Core concept:
 * - Club opens at 12:00 (noon) and closes at 04:00 (next day)
 * - If current time is between 00:00-04:00, business date is PREVIOUS day
 * - Example: 02:00 AM Nov 16 → business date is Nov 15
 */

import { startOfDay, parseISO, format, addDays, isBefore, isAfter, setHours, setMinutes } from 'date-fns';

// Club operational hours
const OPENING_HOUR = parseInt(process.env.CLUB_OPENING_HOUR || '12');
const CLOSING_HOUR = parseInt(process.env.CLUB_CLOSING_HOUR || '4');

/**
 * Get business date for a given datetime
 * @param {Date|string} datetime - The datetime to convert
 * @returns {Date} - Business date (start of day)
 */
export function getBusinessDate(datetime = new Date()) {
  const dt = typeof datetime === 'string' ? parseISO(datetime) : new Date(datetime);
  const hour = dt.getHours();

  // If time is between midnight and closing hour (00:00-04:00),
  // business date is previous day
  if (hour >= 0 && hour < CLOSING_HOUR) {
    const businessDate = new Date(dt);
    businessDate.setDate(businessDate.getDate() - 1);
    return startOfDay(businessDate);
  }

  return startOfDay(dt);
}

/**
 * Check if a time is within operational hours for a business date
 * @param {Date} datetime - The datetime to check
 * @param {Date} businessDate - The business date
 * @returns {boolean}
 */
export function isWithinOperatingHours(datetime, businessDate) {
  const dt = new Date(datetime);
  const hour = dt.getHours();

  const bizDate = startOfDay(businessDate);
  const dtBusinessDate = getBusinessDate(dt);

  // Must be on the same business date
  if (bizDate.getTime() !== dtBusinessDate.getTime()) {
    return false;
  }

  // Check if hour is valid (12:00-23:59 or 00:00-04:00)
  return (hour >= OPENING_HOUR && hour <= 23) || (hour >= 0 && hour < CLOSING_HOUR);
}

/**
 * Get opening datetime for a business date
 * @param {Date|string} businessDate - Business date
 * @returns {Date} - Opening datetime (12:00 PM)
 */
export function getOpeningTime(businessDate) {
  const date = typeof businessDate === 'string' ? parseISO(businessDate) : new Date(businessDate);
  const opening = startOfDay(date);
  opening.setHours(OPENING_HOUR, 0, 0, 0);
  return opening;
}

/**
 * Get closing datetime for a business date
 * @param {Date|string} businessDate - Business date
 * @returns {Date} - Closing datetime (04:00 AM next day)
 */
export function getClosingTime(businessDate) {
  const date = typeof businessDate === 'string' ? parseISO(businessDate) : new Date(businessDate);
  const closing = startOfDay(date);
  closing.setDate(closing.getDate() + 1); // Next day
  closing.setHours(CLOSING_HOUR, 0, 0, 0);
  return closing;
}

/**
 * Check if two bookings overlap
 * @param {Object} booking1 - {startDatetime, endDatetime}
 * @param {Object} booking2 - {startDatetime, endDatetime}
 * @returns {boolean}
 */
export function checkTimeOverlap(booking1, booking2) {
  const start1 = new Date(booking1.startDatetime);
  const end1 = new Date(booking1.endDatetime);
  const start2 = new Date(booking2.startDatetime);
  const end2 = new Date(booking2.endDatetime);

  // Overlap if: start1 < end2 AND end1 > start2
  return isBefore(start1, end2) && isAfter(end1, start2);
}

/**
 * Format business date for display
 * @param {Date} businessDate
 * @returns {string} - e.g., "2024-11-15"
 */
export function formatBusinessDate(businessDate) {
  return format(businessDate, 'yyyy-MM-dd');
}

/**
 * Get time label for timeline (in minutes since opening)
 * Used for UI positioning
 * @param {Date} datetime
 * @returns {number} - Minutes since opening (0 = 12:00, 960 = 04:00)
 */
export function getMinutesSinceOpening(datetime) {
  const dt = new Date(datetime);
  const hour = dt.getHours();
  const minute = dt.getMinutes();

  // If time is 00:00-04:00 (next day), add 24 hours
  if (hour >= 0 && hour < CLOSING_HOUR) {
    return (hour + 24 - OPENING_HOUR) * 60 + minute;
  }

  // Otherwise, calculate from opening hour
  return (hour - OPENING_HOUR) * 60 + minute;
}

/**
 * Get total operational minutes in a day
 * @returns {number} - e.g., 960 (16 hours)
 */
export function getTotalOperatingMinutes() {
  // From 12:00 to 04:00 next day = 16 hours = 960 minutes
  return (24 - OPENING_HOUR + CLOSING_HOUR) * 60;
}

/**
 * Convert minutes since opening to datetime
 * @param {Date|string} businessDate
 * @param {number} minutes - Minutes since opening
 * @returns {Date}
 */
export function minutesToDatetime(businessDate, minutes) {
  const date = typeof businessDate === 'string' ? parseISO(businessDate) : new Date(businessDate);
  const opening = getOpeningTime(date);

  const result = new Date(opening);
  result.setMinutes(result.getMinutes() + minutes);

  return result;
}

/**
 * Validate booking time constraints
 * @param {Date} startDatetime
 * @param {Date} endDatetime
 * @returns {Object} - {valid: boolean, error?: string}
 */
export function validateBookingTime(startDatetime, endDatetime) {
  const start = new Date(startDatetime);
  const end = new Date(endDatetime);

  // End must be after start
  if (!isAfter(end, start)) {
    return { valid: false, error: 'End time must be after start time' };
  }

  // Both must be on same business date
  const startBizDate = getBusinessDate(start);
  const endBizDate = getBusinessDate(end);

  if (startBizDate.getTime() !== endBizDate.getTime()) {
    return { valid: false, error: 'Booking cannot span multiple business dates' };
  }

  // Both must be within operating hours
  if (!isWithinOperatingHours(start, startBizDate)) {
    return { valid: false, error: 'Start time is outside operating hours' };
  }

  if (!isWithinOperatingHours(end, endBizDate)) {
    return { valid: false, error: 'End time is outside operating hours' };
  }

  // Minimum booking duration: 30 minutes
  const durationMinutes = (end.getTime() - start.getTime()) / (1000 * 60);
  if (durationMinutes < 30) {
    return { valid: false, error: 'Minimum booking duration is 30 minutes' };
  }

  return { valid: true };
}

export default {
  getBusinessDate,
  isWithinOperatingHours,
  getOpeningTime,
  getClosingTime,
  checkTimeOverlap,
  formatBusinessDate,
  getMinutesSinceOpening,
  getTotalOperatingMinutes,
  minutesToDatetime,
  validateBookingTime,
  OPENING_HOUR,
  CLOSING_HOUR
};
