/**
 * Core type definitions for the AHF AI Application Framework.
 */

export type SafetyLevel = "none" | "low" | "medium" | "high" | "maximum";

export interface ProviderConfig {
  provider: "openai" | "anthropic" | "custom";
  apiKey: string;
  model: string;
  baseUrl?: string;
  maxContextLength?: number;
}

export interface GenerateOptions {
  prompt: string;
  systemPrompt?: string;
  temperature?: number;
  maxTokens?: number;
  topP?: number;
  stopSequences?: string[];
}

export interface Usage {
  promptTokens: number;
  completionTokens: number;
  totalTokens: number;
  estimatedCost: number;
}

export interface GenerationResult {
  text: string;
  usage: Usage;
  model: string;
  finishReason: "stop" | "length" | "safety";
  safetyFiltered: boolean;
}

export interface SummaryOptions {
  maxLength?: number;
  format?: "paragraph" | "bullets";
  language?: string;
}

export interface SummaryResult {
  summary: string;
  originalLength: number;
  compressedLength: number;
  format: "paragraph" | "bullets";
  usage?: Usage;
}

export interface TranslationOptions {
  sourceLang?: string;
  targetLang: string;
  formality?: "formal" | "informal" | "neutral";
}

export interface TranslationResult {
  translatedText: string;
  sourceLang: string;
  targetLang: string;
  confidence: number;
  usage?: Usage;
}

export interface CategoryScore {
  name: string;
  confidence: number;
}

export interface ClassificationResult {
  categories: CategoryScore[];
  topCategory: string;
  usage?: Usage;
}

export interface SafetyResult {
  isSafe: boolean;
  flags: string[];
  filteredText?: string;
  details: Record<string, string>;
}

export interface Message {
  role: "system" | "user" | "assistant";
  content: string;
}
