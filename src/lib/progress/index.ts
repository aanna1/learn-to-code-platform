/**
 * Progress + autosave, backed by localStorage. ALL localStorage access for the
 * app goes through this module so the key schema lives in exactly one place and
 * is easy to migrate later (bump SCHEMA_VERSION and add a migration).
 *
 * Two storage areas:
 *   - One JSON blob per language holds completion + quiz + last-visited state.
 *   - Saved exercise code lives under per-lesson keys so frequent autosaves don't
 *     rewrite the whole progress blob on every keystroke.
 *
 * Every function is SSR-safe: on the server (no window) reads return sensible
 * defaults and writes are no-ops.
 */

const SCHEMA_VERSION = "v1";
const NS = `ltcp:${SCHEMA_VERSION}`;

function progressKey(languageId: string): string {
  return `${NS}:progress:${languageId}`;
}

function codeKey(languageId: string, moduleId: string, lessonId: string): string {
  return `${NS}:code:${languageId}:${moduleId}:${lessonId}`;
}

/** Composite lesson key within a language's progress blob. */
function lessonKey(moduleId: string, lessonId: string): string {
  return `${moduleId}/${lessonId}`;
}

export interface QuizResult {
  bestScore: number;
  total: number;
  attempts: number;
}

export interface LessonProgress {
  completed: boolean;
  /** Present once the lesson's quiz has been attempted at least once. */
  quiz?: QuizResult;
}

export interface LessonLocation {
  moduleId: string;
  lessonId: string;
}

interface LanguageProgress {
  lessons: Record<string, LessonProgress>;
  lastVisited?: LessonLocation;
}

function hasStorage(): boolean {
  return typeof window !== "undefined" && !!window.localStorage;
}

function readLanguageProgress(languageId: string): LanguageProgress {
  if (!hasStorage()) return { lessons: {} };
  try {
    const raw = window.localStorage.getItem(progressKey(languageId));
    if (!raw) return { lessons: {} };
    const parsed = JSON.parse(raw) as LanguageProgress;
    return { lessons: parsed.lessons ?? {}, lastVisited: parsed.lastVisited };
  } catch {
    return { lessons: {} };
  }
}

function writeLanguageProgress(languageId: string, data: LanguageProgress): void {
  if (!hasStorage()) return;
  try {
    window.localStorage.setItem(progressKey(languageId), JSON.stringify(data));
  } catch {
    // storage full or unavailable — progress is best-effort, so swallow.
  }
}

// ---------------------------------------------------------------------------
// Completion
// ---------------------------------------------------------------------------

export function isLessonComplete(
  languageId: string,
  moduleId: string,
  lessonId: string,
): boolean {
  const data = readLanguageProgress(languageId);
  return data.lessons[lessonKey(moduleId, lessonId)]?.completed ?? false;
}

export function setLessonComplete(
  languageId: string,
  moduleId: string,
  lessonId: string,
  completed = true,
): void {
  const data = readLanguageProgress(languageId);
  const key = lessonKey(moduleId, lessonId);
  const existing = data.lessons[key] ?? { completed: false };
  data.lessons[key] = { ...existing, completed };
  writeLanguageProgress(languageId, data);
}

/** Lesson keys ("module/lesson") that are marked complete, for outline checkmarks. */
export function getCompletedLessonKeys(languageId: string): string[] {
  const data = readLanguageProgress(languageId);
  return Object.entries(data.lessons)
    .filter(([, value]) => value.completed)
    .map(([key]) => key);
}

// ---------------------------------------------------------------------------
// Quiz results
// ---------------------------------------------------------------------------

export function recordQuizResult(
  languageId: string,
  moduleId: string,
  lessonId: string,
  score: number,
  total: number,
): QuizResult {
  const data = readLanguageProgress(languageId);
  const key = lessonKey(moduleId, lessonId);
  const existing = data.lessons[key] ?? { completed: false };
  const prior = existing.quiz;
  const quiz: QuizResult = {
    bestScore: Math.max(prior?.bestScore ?? 0, score),
    total,
    attempts: (prior?.attempts ?? 0) + 1,
  };
  data.lessons[key] = { ...existing, quiz };
  writeLanguageProgress(languageId, data);
  return quiz;
}

export function getQuizResult(
  languageId: string,
  moduleId: string,
  lessonId: string,
): QuizResult | undefined {
  const data = readLanguageProgress(languageId);
  return data.lessons[lessonKey(moduleId, lessonId)]?.quiz;
}

// ---------------------------------------------------------------------------
// Last-visited
// ---------------------------------------------------------------------------

export function setLastVisited(
  languageId: string,
  moduleId: string,
  lessonId: string,
): void {
  const data = readLanguageProgress(languageId);
  data.lastVisited = { moduleId, lessonId };
  writeLanguageProgress(languageId, data);
}

export function getLastVisited(languageId: string): LessonLocation | undefined {
  return readLanguageProgress(languageId).lastVisited;
}

// ---------------------------------------------------------------------------
// Exercise code autosave
// ---------------------------------------------------------------------------

export function saveCode(
  languageId: string,
  moduleId: string,
  lessonId: string,
  code: string,
): void {
  if (!hasStorage()) return;
  try {
    window.localStorage.setItem(codeKey(languageId, moduleId, lessonId), code);
  } catch {
    // best-effort
  }
}

export function loadCode(
  languageId: string,
  moduleId: string,
  lessonId: string,
): string | null {
  if (!hasStorage()) return null;
  try {
    return window.localStorage.getItem(codeKey(languageId, moduleId, lessonId));
  } catch {
    return null;
  }
}

export function clearCode(
  languageId: string,
  moduleId: string,
  lessonId: string,
): void {
  if (!hasStorage()) return;
  try {
    window.localStorage.removeItem(codeKey(languageId, moduleId, lessonId));
  } catch {
    // best-effort
  }
}
