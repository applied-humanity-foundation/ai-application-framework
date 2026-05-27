/**
 * Configuration management for the AHF AI Application Framework.
 *
 * Supports construction from environment variables, plain objects,
 * and programmatic builder patterns.
 */

import type { SafetyLevel } from "./types/index.js";

export interface ConfigOptions {
  provider: "openai" | "anthropic" | "custom";
  apiKey: string;
  model?: string;
  temperature?: number;
  maxTokens?: number;
  safetyLevel?: SafetyLevel;
  rateLimitRpm?: number;
  timeout?: number;
  verbose?: boolean;
  baseUrl?: string;
}

export class Config {
  readonly provider: "openai" | "anthropic" | "custom";
  readonly apiKey: string;
  readonly model: string;
  readonly temperature: number;
  readonly maxTokens: number;
  readonly safetyLevel: SafetyLevel;
  readonly rateLimitRpm: number;
  readonly timeout: number;
  readonly verbose: boolean;
  readonly baseUrl?: string;

  constructor(options: ConfigOptions) {
    this.provider = options.provider;
    this.apiKey = options.apiKey;
    this.model = options.model ?? (options.provider === "anthropic" ? "claude-sonnet-4-20250514" : "gpt-4o");
    this.temperature = options.temperature ?? 0.7;
    this.maxTokens = options.maxTokens ?? 2048;
    this.safetyLevel = options.safetyLevel ?? "medium";
    this.rateLimitRpm = options.rateLimitRpm ?? 60;
    this.timeout = options.timeout ?? 30_000;
    this.verbose = options.verbose ?? false;
    this.baseUrl = options.baseUrl;
  }

  static fromEnv(): Config {
    const provider = (process.env["AHF_PROVIDER"] as ConfigOptions["provider"]) ?? "openai";
    const apiKey = process.env["AHF_API_KEY"] ?? "";
    if (!apiKey) {
      throw new Error("AHF_API_KEY environment variable is required");
    }
    return new Config({
      provider,
      apiKey,
      model: process.env["AHF_MODEL"],
      temperature: process.env["AHF_TEMPERATURE"] ? Number(process.env["AHF_TEMPERATURE"]) : undefined,
      maxTokens: process.env["AHF_MAX_TOKENS"] ? Number(process.env["AHF_MAX_TOKENS"]) : undefined,
      safetyLevel: (process.env["AHF_SAFETY_LEVEL"] as SafetyLevel) ?? undefined,
      verbose: process.env["AHF_VERBOSE"] === "true",
    });
  }

  static fromObject(obj: ConfigOptions): Config {
    return new Config(obj);
  }
}
