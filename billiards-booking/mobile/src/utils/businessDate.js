/**
 * Business Date Utilities for Mobile App
 * Mirrors backend logic for consistent behavior
 */

import { format, startOfDay, addDays, parseISO } from 'date-fns';

const OPENING_HOUR = 12;
const CLOSING_HOUR = 4;

/**
 * Get business date for a given datetime
 * @param {Date|string} datetime
 * @returns {Date} - Business date (start of day)
 */
export function getBusinessDate(datetime = new Date()) {
  const dt = typeof datetime === 'string' ? parseISO(datetime) : new Date(datetime);
  const hour = dt.getHours();

  if (hour >= 0 && hour < CLOSING_HOUR) {
    const businessDate = new Date(dt);
    businessDate.setDate(businessDate.getDate() - 1);
    return startOfDay(businessDate);
  }

  return startOfDay(dt);
}

/**
 * Format business date for API calls
 * @param {Date} businessDate
 * @returns {string} - e.g., "2024-11-15"
 */
export function formatBusinessDate(businessDate) {
  return format(businessDate, 'yyyy-MM-dd');
}

/**
 * Get opening time for a business date
 * @param {Date} businessDate
 * @returns {Date}
 */
export function getOpeningTime(businessDate) {
  const opening = startOfDay(businessDate);
  opening.setHours(OPENING_HOUR, 0, 0, 0);
  return opening;
}

/**
 * Get closing time for a business date
 * @param {Date} businessDate
 * @returns {Date}
 */
export function getClosingTime(businessDate) {
  const closing = startOfDay(businessDate);
  closing.setDate(closing.getDate() + 1);
  closing.setHours(CLOSING_HOUR, 0, 0, 0);
  return closing;
}

/**
 * Get minutes since opening for timeline positioning
 * @param {Date} datetime
 * @returns {number}
 */
export function getMinutesSinceOpening(datetime) {
  const dt = new Date(datetime);
  const hour = dt.getHours();
  const minute = dt.getMinutes();

  if (hour >= 0 && hour < CLOSING_HOUR) {
    return (hour + 24 - OPENING_HOUR) * 60 + minute;
  }

  return (hour - OPENING_HOUR) * 60 + minute;
}

/**
 * Get total operating minutes
 * @returns {number}
 */
export function getTotalOperatingMinutes() {
  return (24 - OPENING_HOUR + CLOSING_HOUR) * 60; // 960 minutes (16 hours)
}

/**
 * Format time for display
 * @param {Date} datetime
 * @returns {string} - e.g., "14:30"
 */
export function formatTime(datetime) {
  return format(datetime, 'HH:mm');
}

/**
 * Format datetime for display
 * @param {Date} datetime
 * @returns {string} - e.g., "15 Nov, 14:30"
 */
export function formatDateTime(datetime) {
  return format(datetime, 'dd MMM, HH:mm');
}

/**
 * Generate time labels for timeline
 * Returns array of time labels (e.g., ["12:00", "13:00", ..., "04:00"])
 * @returns {Array<{label: string, minutes: number}>}
 */
export function getTimeLabels() {
  const labels = [];
  const totalMinutes = getTotalOperatingMinutes();

  for (let minutes = 0; minutes <= totalMinutes; minutes += 60) {
    const hour = Math.floor(minutes / 60) + OPENING_HOUR;
    const displayHour = hour >= 24 ? hour - 24 : hour;
    labels.push({
      label: `${displayHour.toString().padStart(2, '0')}:00`,
      minutes
    });
  }

  return labels;
}

export default {
  getBusinessDate,
  formatBusinessDate,
  getOpeningTime,
  getClosingTime,
  getMinutesSinceOpening,
  getTotalOperatingMinutes,
  formatTime,
  formatDateTime,
  getTimeLabels,
  OPENING_HOUR,
  CLOSING_HOUR
};
