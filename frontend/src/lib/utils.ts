import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { STATUS_COLORS, SYSTEM_STATUS_COLORS, VALIDATION, type CallStatus, type SystemStatusType } from './constants';

/**
 * Utility function to merge Tailwind CSS classes
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format duration in seconds to MM:SS format
 */
export const formatDuration = (seconds: number): string => {
  if (!seconds || seconds < 0) return '0:00';
  
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

/**
 * Format ISO string to localized date/time
 */
export const formatTime = (isoString: string): string => {
  try {
    return new Date(isoString).toLocaleString();
  } catch {
    return 'Invalid date';
  }
};

/**
 * Format relative time (e.g., "2 minutes ago")
 */
export const formatRelativeTime = (isoString: string): string => {
  try {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    
    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
    
    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  } catch {
    return 'Unknown';
  }
};

/**
 * Get status badge CSS classes with type safety
 */
export const getStatusBadgeClass = (status: CallStatus): string => {
  return STATUS_COLORS[status] || 'bg-gray-100 text-gray-800';
};

/**
 * Get system status indicator color
 */
export const getSystemStatusColor = (status: SystemStatusType): string => {
  return SYSTEM_STATUS_COLORS[status] || 'bg-gray-500';
};

/**
 * Validate phone number format
 */
export const isValidPhoneNumber = (phoneNumber: string): boolean => {
  return VALIDATION.PHONE_NUMBER_REGEX.test(phoneNumber);
};

/**
 * Format phone number for display
 */
export const formatPhoneNumber = (phoneNumber: string): string => {
  // Remove all non-digit characters except +
  const cleaned = phoneNumber.replace(/[^\d+]/g, '');
  
  // Basic US number formatting
  if (cleaned.startsWith('+1') && cleaned.length === 12) {
    const number = cleaned.slice(2);
    return `+1 (${number.slice(0, 3)}) ${number.slice(3, 6)}-${number.slice(6)}`;
  }
  
  return phoneNumber; // Return original if not a standard US number
};

/**
 * Calculate percentage with safe division
 */
export const calculatePercentage = (numerator: number, denominator: number): number => {
  if (denominator === 0) return 0;
  return Math.round((numerator / denominator) * 100 * 100) / 100; // Round to 2 decimal places
};

/**
 * Debounce function for performance optimization
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

/**
 * Throttle function for performance optimization
 */
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean;
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};