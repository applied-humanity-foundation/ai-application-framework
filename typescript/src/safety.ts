/**
 * Safety filter pipeline for input and output text.
 *
 * Detects PII patterns (emails, phone numbers, SSNs, credit cards)
 * and applies configurable safety levels for content filtering.
 */

import type { SafetyLevel, SafetyResult } from "./types/index.js";

const PII_PATTERNS: Record<string, RegExp> = {
  email: /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g,
  phone: /\b(\+?1[-.\s]?)?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})\b/g,
  ssn: /\b\d{3}-\d{2}-\d{4}\b/g,
  creditCard: /\b(?:\d[ -]*?){13,16}\b/g,
  ipAddress: /\b(?:\d{1,3}\.){3}\d{1,3}\b/g,
};

const BLOCKED_PHRASES = [
  "ignore previous instructions",
  "ignore all previous",
  "disregard your instructions",
  "override safety",
];

export class SafetyFilter {
  private readonly level: SafetyLevel;

  constructor(level: SafetyLevel = "medium") {
    this.level = level;
  }

  checkInput(text: string): SafetyResult {
    if (this.level === "none") {
      return { isSafe: true, flags: [], details: {} };
    }
    const flags: string[] = [];
    const details: Record<string, string> = {};
    const lower = text.toLowerCase();

    // Prompt injection detection (medium+)
    if (this.level !== "low") {
      for (const phrase of BLOCKED_PHRASES) {
        if (lower.includes(phrase)) {
          flags.push("prompt_injection");
          details["prompt_injection"] = `Detected blocked phrase: "${phrase}"`;
          break;
        }
      }
    }

    return { isSafe: flags.length === 0, flags, details };
  }

  checkOutput(text: string): SafetyResult {
    if (this.level === "none") {
      return { isSafe: true, flags: [], details: {} };
    }
    const flags: string[] = [];
    const details: Record<string, string> = {};
    let filteredText = text;

    // PII detection and redaction (low+)
    for (const [name, pattern] of Object.entries(PII_PATTERNS)) {
      const matches = text.match(pattern);
      if (matches && matches.length > 0) {
        flags.push(`pii_${name}`);
        details[`pii_${name}`] = `Found ${matches.length} instance(s)`;
        // Redact in high/maximum modes
        if (this.level === "high" || this.level === "maximum") {
          filteredText = filteredText.replace(pattern, `[REDACTED_${name.toUpperCase()}]`);
        }
      }
    }

    return {
      isSafe: flags.length === 0,
      flags,
      filteredText: filteredText !== text ? filteredText : undefined,
      details,
    };
  }
}
