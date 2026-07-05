import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import type {
  Course,
  ExerciseContent,
  Hints,
  LectureContent,
  LessonRef,
  ModelingContent,
  ModuleManifest,
  Quiz,
} from "@/lib/content/types";

/**
 * Generic, language-agnostic content loader. It reads from
 * src/content/languages/<languageId>/ at build time. Every function here runs in
 * server components / generateStaticParams during static export, so Node's fs is
 * available and the cost is paid once at build, never in the browser.
 *
 * On-disk contract (adding a module requires zero code changes — just files):
 *
 *   src/content/languages/<lang>/
 *     course.json
 *     modules/<moduleId>/
 *       module.json
 *       <lessonId>/                 # lecture lesson
 *         lecture.mdx
 *         quiz.json                 # optional
 *       <lessonId>/exercise/        # exercise lesson (text-runtime languages, e.g. Python/C)
 *         prompt.mdx
 *         starter.py
 *         solution.py
 *         tests.py
 *         hints.json
 *
 * SQL (and any result-set language) uses a parallel exercise bundle instead of
 * the .py trio — detected by the presence of `starter.sql`, so the loader stays
 * language-agnostic (it branches on files present, never on a language id):
 *
 *       <lessonId>/exercise/
 *         prompt.mdx
 *         schema.sql                # fixture: CREATE TABLE + INSERT seed rows
 *         starter.sql               # starter query (fails >= 1 test)
 *         solution.sql              # reference query (passes all tests)
 *         tests.json                # { "cases": SqlTestCase[] } — result-set comparison
 *         hints.json
 *
 * The runtime's run()/runTests() take `code` and `tests` as plain strings, so the
 * loader normalizes the SQL bundle into the shared ExerciseContent shape:
 *   - `starter`/`solution` = schema.sql prepended to starter.sql/solution.sql, so a
 *     fresh in-memory DB seeds itself when the learner presses Run (the runtime does
 *     not seed schema.sql separately on Run — the fixture must reach the DB via the
 *     editor code).
 *   - `tests` = JSON.stringify({ schema, cases }) — the SqlTestsPayload the sql.js
 *     worker parses. Grading re-seeds `schema` on a fresh DB per case, peels that same
 *     schema prefix back off the editor code to recover the learner's query, then runs
 *     schema → (optional per-case setup) → query — the order scripts/sql/grade_check.mjs
 *     uses, so a case's `setup` fixture-variation lands between the schema and the query.
 *     Fresh DB per case ⇒ cases stay isolated and order-independent.
 */

function contentRoot(languageId: string): string {
  return join(process.cwd(), "src", "content", "languages", languageId);
}

function moduleDir(languageId: string, moduleId: string): string {
  return join(contentRoot(languageId), "modules", moduleId);
}

function readJson<T>(path: string): T {
  return JSON.parse(readFileSync(path, "utf8")) as T;
}

/**
 * Read hints.json, tolerating both authoring shapes: the canonical
 * `{ "hints": [...] }` object and a bare `[...]` array (several modules were authored
 * that way). Either yields a `Hints`; anything unexpected yields an empty list rather
 * than an undefined `hints` that would crash the exercise renderer downstream.
 */
function readHints(path: string): Hints {
  const raw = JSON.parse(readFileSync(path, "utf8")) as unknown;
  if (Array.isArray(raw)) return { hints: raw as string[] };
  if (raw && typeof raw === "object" && Array.isArray((raw as { hints?: unknown }).hints)) {
    return { hints: (raw as { hints: string[] }).hints };
  }
  return { hints: [] };
}

/**
 * Read quiz.json, tolerating both authoring shapes: the canonical
 * `{ "questions": [...] }` object and a bare `[...]` array of questions (one module
 * was authored that way). Either yields a `Quiz`; anything unexpected yields an empty
 * quiz rather than an undefined `questions` that would crash the lecture renderer.
 */
function readQuiz(path: string): Quiz {
  const raw = JSON.parse(readFileSync(path, "utf8")) as unknown;
  if (Array.isArray(raw)) return { questions: raw as Quiz["questions"] };
  if (raw && typeof raw === "object" && Array.isArray((raw as { questions?: unknown }).questions)) {
    return { questions: (raw as Quiz).questions };
  }
  return { questions: [] };
}

function readText(path: string): string {
  return readFileSync(path, "utf8");
}

function byOrder<T extends { order: number }>(items: readonly T[]): T[] {
  return [...items].sort((a, b) => a.order - b.order);
}

/** Raw cheatsheet.mdx for a language (compiled by the cheat-sheet route). */
export function getCheatsheet(languageId: string): string {
  return readText(join(contentRoot(languageId), "cheatsheet.mdx"));
}

/** Read and parse course.json for a language. Modules come back in display order. */
export function getCourse(languageId: string): Course {
  const course = readJson<Course>(join(contentRoot(languageId), "course.json"));
  return { ...course, modules: byOrder(course.modules) };
}

/** Read and parse module.json for one module. Lessons come back in display order. */
export function getModule(languageId: string, moduleId: string): ModuleManifest {
  const manifest = readJson<ModuleManifest>(join(moduleDir(languageId, moduleId), "module.json"));
  return { ...manifest, lessons: byOrder(manifest.lessons) };
}

/** Find a lesson's metadata within its module, or undefined if it isn't listed. */
export function getLessonRef(
  languageId: string,
  moduleId: string,
  lessonId: string,
): LessonRef | undefined {
  return getModule(languageId, moduleId).lessons.find((lesson) => lesson.id === lessonId);
}

/** Load a lecture lesson (lecture.mdx + optional quiz.json). */
export function getLecture(
  languageId: string,
  moduleId: string,
  lessonId: string,
): LectureContent {
  const meta = requireLessonRef(languageId, moduleId, lessonId, "lecture");
  const dir = join(moduleDir(languageId, moduleId), lessonId);
  const mdxSource = readText(join(dir, "lecture.mdx"));

  let quiz: Quiz | null = null;
  try {
    quiz = readQuiz(join(dir, "quiz.json"));
  } catch {
    // quiz.json is optional; a lecture without one just has no end-of-lesson quiz.
    quiz = null;
  }

  return { meta, mdxSource, quiz };
}

/** Load an exercise lesson (prompt.mdx + starter/solution/tests + hints.json). */
export function getExercise(
  languageId: string,
  moduleId: string,
  lessonId: string,
): ExerciseContent {
  const meta = requireLessonRef(languageId, moduleId, lessonId, "exercise");
  const dir = join(moduleDir(languageId, moduleId), lessonId, "exercise");

  // SQL-style bundle (schema.sql + starter/solution.sql + tests.json). Detected by
  // file presence so the loader never branches on the language id.
  if (existsSync(join(dir, "starter.sql"))) {
    return readSqlExercise(meta, dir);
  }

  return {
    meta,
    promptMdxSource: readText(join(dir, "prompt.mdx")),
    starter: readText(join(dir, "starter.py")),
    solution: readText(join(dir, "solution.py")),
    tests: readText(join(dir, "tests.py")),
    hints: readHints(join(dir, "hints.json")),
  };
}

/**
 * Read a SQL exercise bundle and normalize it into the shared ExerciseContent shape.
 * See the on-disk contract note at the top of this file for how the schema is both
 * prepended to the editor code (for Run) and passed in the tests payload (for the
 * grader's schema → setup → query re-seed).
 */
function readSqlExercise(meta: LessonRef, dir: string): ExerciseContent {
  const schema = existsSync(join(dir, "schema.sql"))
    ? readText(join(dir, "schema.sql")).trimEnd()
    : "";
  const withSchema = (body: string): string =>
    schema ? `${schema}\n\n${body}` : body;

  // tests.json is authored as { "cases": [...] } (or a bare [...] of cases). The
  // schema is ALSO passed in the tests payload (not only prepended to the editor):
  // the grader peels the schema prefix off the editor code and re-seeds it per case,
  // so a case's `setup` can run BETWEEN the schema and the learner's query — the
  // schema → setup → query order that scripts/sql/grade_check.mjs uses. Run (which
  // has no cases/setup) still relies on the schema being in the editor code.
  const rawTests = JSON.parse(readFileSync(join(dir, "tests.json"), "utf8")) as unknown;
  const cases = Array.isArray(rawTests)
    ? rawTests
    : rawTests && typeof rawTests === "object" && Array.isArray((rawTests as { cases?: unknown }).cases)
      ? (rawTests as { cases: unknown[] }).cases
      : [];

  return {
    meta,
    promptMdxSource: readText(join(dir, "prompt.mdx")),
    starter: withSchema(readText(join(dir, "starter.sql"))),
    solution: withSchema(readText(join(dir, "solution.sql"))),
    tests: JSON.stringify({ schema, cases }),
    hints: readHints(join(dir, "hints.json")),
  };
}

/**
 * Load a Track-2 "modeling" lesson (structured exercise). Same folder position as
 * an exercise (`<lessonId>/exercise/`) but with question.json + answer.json instead
 * of the code trio. The route branches on the lesson `type` ("modeling"), never on
 * a language id.
 */
export function getModeling(
  languageId: string,
  moduleId: string,
  lessonId: string,
): ModelingContent {
  const meta = requireLessonRef(languageId, moduleId, lessonId, "modeling");
  const dir = join(moduleDir(languageId, moduleId), lessonId, "exercise");
  return {
    meta,
    promptMdxSource: readText(join(dir, "prompt.mdx")),
    question: readJson<unknown>(join(dir, "question.json")),
    answer: readJson<unknown>(join(dir, "answer.json")),
    hints: readHints(join(dir, "hints.json")),
  };
}

// ---------------------------------------------------------------------------
// Outline / navigation helpers
// ---------------------------------------------------------------------------

/** The course plus every module manifest, all in display order. */
export interface ResolvedCourse {
  course: Course;
  modules: ModuleManifest[];
}

/** Resolve the whole course tree in one call (course.json + every module.json). */
export function getResolvedCourse(languageId: string): ResolvedCourse {
  const course = getCourse(languageId);
  const modules = course.modules.map((ref) => getModule(languageId, ref.id));
  return { course, modules };
}

/** Every (module, lesson) pair for a language, in order — feeds generateStaticParams. */
export function listLessonParams(languageId: string): { module: string; lesson: string }[] {
  return getResolvedCourse(languageId).modules.flatMap((manifest) =>
    manifest.lessons.map((lesson) => ({ module: manifest.id, lesson: lesson.id })),
  );
}

export interface LessonNavLink {
  moduleId: string;
  lessonId: string;
  title: string;
}

export interface LessonNeighbors {
  moduleManifest: ModuleManifest;
  prev: LessonNavLink | null;
  next: LessonNavLink | null;
}

/**
 * The lesson's own module plus the previous/next lessons in the flattened course
 * order (crossing module boundaries), used for the in-lesson prev/next controls.
 */
export function getLessonNeighbors(
  languageId: string,
  moduleId: string,
  lessonId: string,
): LessonNeighbors {
  const { modules } = getResolvedCourse(languageId);

  const flat: LessonNavLink[] = modules.flatMap((manifest) =>
    manifest.lessons.map((lesson) => ({
      moduleId: manifest.id,
      lessonId: lesson.id,
      title: lesson.title,
    })),
  );

  const index = flat.findIndex((l) => l.moduleId === moduleId && l.lessonId === lessonId);
  const moduleManifest = modules.find((m) => m.id === moduleId);
  if (!moduleManifest) {
    throw new Error(`Module not found: ${languageId}/${moduleId}`);
  }

  return {
    moduleManifest,
    prev: index > 0 ? (flat[index - 1] ?? null) : null,
    next: index >= 0 && index < flat.length - 1 ? (flat[index + 1] ?? null) : null,
  };
}

function requireLessonRef(
  languageId: string,
  moduleId: string,
  lessonId: string,
  expected: LessonRef["type"],
): LessonRef {
  const ref = getLessonRef(languageId, moduleId, lessonId);
  if (!ref) {
    throw new Error(`Lesson not listed in module.json: ${languageId}/${moduleId}/${lessonId}`);
  }
  if (ref.type !== expected) {
    throw new Error(
      `Lesson ${languageId}/${moduleId}/${lessonId} is type "${ref.type}", expected "${expected}"`,
    );
  }
  return ref;
}
