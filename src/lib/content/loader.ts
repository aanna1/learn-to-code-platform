import type {
  Course,
  ExerciseContent,
  LectureContent,
  ModuleManifest,
} from "@/lib/content/types";

/**
 * Generic, language-agnostic content loader. It reads from
 * src/content/languages/<languageId>/ at build time (these run in server
 * components / generateStaticParams during static export, so Node's fs is
 * available). The same functions work for every language — adding a module is
 * just creating a folder, listing it in the parent JSON, and writing the files.
 *
 * PHASE 1: signatures and the directory contract are fixed here. The
 * implementations land alongside the lesson renderer (Phase 3) and are first
 * exercised by the seed lessons (Phase 4). The metadata loaders are simple
 * fs+JSON reads; the lecture/exercise loaders also read the .mdx/.py files.
 */

const PHASE_3_MARKER =
  "Content loader is implemented in Phase 3 (lesson renderer). This is a Phase 1 contract stub.";

/** Read and parse course.json for a language. */
export function getCourse(_languageId: string): Course {
  throw new Error(PHASE_3_MARKER);
}

/** Read and parse module.json for one module. */
export function getModule(_languageId: string, _moduleId: string): ModuleManifest {
  throw new Error(PHASE_3_MARKER);
}

/** Load a lecture lesson (lecture.mdx + optional quiz.json). */
export function getLecture(
  _languageId: string,
  _moduleId: string,
  _lessonId: string,
): LectureContent {
  throw new Error(PHASE_3_MARKER);
}

/** Load an exercise lesson (prompt.mdx + starter/solution/tests + hints.json). */
export function getExercise(
  _languageId: string,
  _moduleId: string,
  _lessonId: string,
): ExerciseContent {
  throw new Error(PHASE_3_MARKER);
}
