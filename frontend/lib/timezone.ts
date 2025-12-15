/**
 * Utility functions for date formatting with Bolivia timezone (UTC-4)
 */

/**
 * Formats a date string or Date object to Bolivia local time
 * @param date - The date to format (string or Date object)
 * @param options - Optional Intl.DateTimeFormatOptions
 * @returns Formatted date string in Bolivia timezone
 */
export function formatBoliviaTime(
    date: string | Date,
    options?: Intl.DateTimeFormatOptions
): string {
    // Fix: Backend sends UTC timestamps without 'Z' suffix
    // JavaScript interprets these as local time, causing double conversion
    // If string doesn't have timezone info, treat it as UTC by adding 'Z'
    let dateStr = date;
    if (typeof date === 'string' && !date.endsWith('Z') && !date.includes('+') && !date.includes('-', 10)) {
        // ISO format string without timezone -> add Z to mark as UTC
        dateStr = date + 'Z';
    }

    const dateObj = typeof dateStr === 'string' ? new Date(dateStr) : dateStr;

    // Manual conversion: Bolivia is UTC-4 (no DST)
    // Get UTC time and subtract 4 hours
    const FOUR_HOURS_MS = 4 * 60 * 60 * 1000;
    const boliviaTime = new Date(dateObj.getTime() - FOUR_HOURS_MS);

    // Extract components using UTC functions to avoid browser timezone issues
    const year = boliviaTime.getUTCFullYear();
    const month = String(boliviaTime.getUTCMonth() + 1).padStart(2, '0');
    const day = String(boliviaTime.getUTCDate()).padStart(2, '0');
    const hour = String(boliviaTime.getUTCHours()).padStart(2, '0');
    const minute = String(boliviaTime.getUTCMinutes()).padStart(2, '0');
    const second = String(boliviaTime.getUTCSeconds()).padStart(2, '0');

    // Format based on options - check specific formats first
    if (options?.month === 'short') {
        // Short format for headlines table
        const months = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
        return `${months[boliviaTime.getUTCMonth()]} ${day}, ${hour}:${minute}`;
    }

    // Check if time components are explicitly excluded
    const timeFieldsUndefined = options && options.hour === undefined && options.minute === undefined && options.second === undefined;
    const dateFieldsUndefined = options && options.year === undefined && options.month === undefined && options.day === undefined;

    if (timeFieldsUndefined && !dateFieldsUndefined) {
        // Date only - explicitly requested
        return `${day}/${month}/${year}`;
    } else if (dateFieldsUndefined && !timeFieldsUndefined) {
        // Time only - explicitly requested
        return `${hour}:${minute}:${second}`;
    } else {
        // Full format (default)
        return `${day}/${month}/${year}, ${hour}:${minute}:${second}`;
    }
}

/**
 * Formats a date to show only date components (no time)
 */
export function formatBoliviaDate(date: string | Date): string {
    return formatBoliviaTime(date, {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: undefined,
        minute: undefined,
        second: undefined,
    });
}

/**
 * Formats a date to show only time components (no date)
 */
export function formatBoliviaTimeOnly(date: string | Date): string {
    return formatBoliviaTime(date, {
        year: undefined,
        month: undefined,
        day: undefined,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
    });
}
