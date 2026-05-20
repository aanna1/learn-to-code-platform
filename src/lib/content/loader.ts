import { readFileSync } from "node:fs";
import { join } from "node:path";
import type {
  Course,
  ExerciseContent,
  Hints,
  LectureContent,
  LessonRef,
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
 *       <lessonId>/exercise/        # exercise lesson
 *         prompt.mdx
 *         starter.py
 *         solution.py
 *         tests.py
 *         hints.json
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

function readText(path: string): string {
  return readFileSync(path, "utf8");
}

function byOrder<T extends { order: number }>(items: readonly T[]): T[] {
  return [...items].sort((a, b) => a.order - b.order);
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
    quiz = readJson<Quiz>(join(dir, "quiz.json"));
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

  return {
    meta,
    promptMdxSource: readText(join(dir, "prompt.mdx")),
    starter: readText(join(dir, "starter.py")),
    solution: readText(join(dir, "solution.py")),
    tests: readText(join(dir, "tests.py")),
    hints: readJson<Hints>(join(dir, "hints.json")),
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
