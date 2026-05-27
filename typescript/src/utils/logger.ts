/**
 * Structured logger with API key redaction.
 *
 * Supports debug / info / warn / error levels and automatically
 * masks anything that looks like an API key or bearer token.
 */

export type LogLevel = "debug" | "info" | "warn" | "error";

const LOG_PRIORITY: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
};

const KEY_PATTERN = /(sk-[a-zA-Z0-9]{10,}|Bearer\s+[a-zA-Z0-9._-]{20,})/g;

function redact(message: string): string {
  return message.replace(KEY_PATTERN, "[REDACTED]");
}

export class Logger {
  private readonly minLevel: LogLevel;
  private readonly prefix: string;

  constructor(minLevel: LogLevel = "info", prefix = "ahf-ai") {
    this.minLevel = minLevel;
    this.prefix = prefix;
  }

  private shouldLog(level: LogLevel): boolean {
    return LOG_PRIORITY[level] >= LOG_PRIORITY[this.minLevel];
  }

  private emit(level: LogLevel, message: string, data?: Record<string, unknown>): void {
    if (!this.shouldLog(level)) return;
    const timestamp = new Date().toISOString();
    const safe = redact(message);
    const entry = { timestamp, level, prefix: this.prefix, message: safe, ...data };
    const fn = level === "error" ? console.error : level === "warn" ? console.warn : console.log;
    fn(JSON.stringify(entry));
  }

  debug(msg: string, data?: Record<string, unknown>): void { this.emit("debug", msg, data); }
  info(msg: string, data?: Record<string, unknown>): void { this.emit("info", msg, data); }
  warn(msg: string, data?: Record<string, unknown>): void { this.emit("warn", msg, data); }
  error(msg: string, data?: Record<string, unknown>): void { this.emit("error", msg, data); }
}
