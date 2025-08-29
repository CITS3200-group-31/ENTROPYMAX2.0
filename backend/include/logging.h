#ifndef LOGGING_H
#define LOGGING_H

/**
 * @file logging.h
 * @brief API for the logging system.
 *
 * Defines log levels and declares the log_message function.
 */

#include <stdarg.h>
#include <stdio.h>

typedef enum { LOG_DEBUG, LOG_INFO, LOG_WARN, LOG_ERROR } log_level_t;

/**
 * Log a message with the given log level.
 *
 * Calling the function with an invalid log level, invalid format string,
 * or invalid arguments results in undefined behavior.
 *
 * @param level The severity level (e.g., LOG_INFO)
 * @param fmt A printf-style format string
 * - ... Format arguments
 */
void log_message(log_level_t level, const char *fmt, ...);

#endif