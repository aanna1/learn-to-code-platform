/**
 * Content model. These types mirror the on-disk schema under
 * src/content/languages/<lang>/ (course.json, module.json, quiz.json, hints.json,
 * and the .mdx / .py lesson files). They are the contract the loader (below),
 * the lesson renderer (Phase 3), and the seed content (Phase 4) all build against.
 */

export type LessonType = "lecture" | "exercise";

/** A module entry as listed in course.json. */
export interface CourseModuleRef {
  id: string;
  title: string;
  order: number;
}

/** Parsed course.json. */
export interface Course {
  language: string;
  displayName: string;
  tagline: string;
  modules: CourseModuleRef[];
}

/** A lesson entry as listed in module.json. */
export interface LessonRef {
  id: string;
  title: string;
  type: LessonType;
  order: number;
}

/** Parsed module.json. */
export interface ModuleManifest {
  id: string;
  title: string;
  description: string;
  lessons: LessonRef[];
}

export interface QuizOption {
  text: string;
  correct: boolean;
  explanation: string;
}

export interface QuizQuestion {
  question: string;
  options: QuizOption[];
}

/** Parsed quiz.json. */
export interface Quiz {
  questions: QuizQuestion[];
}

/** Parsed hints.json. */
export interface Hints {
  hints: string[];
}

/** A fully-loaded lecture lesson. `mdxSource` is raw MDX compiled by the renderer. */
export interface LectureContent {
  meta: LessonRef;
  mdxSource: string;
  quiz: Quiz | null;
}

/** A fully-loaded exercise lesson. */
export interface ExerciseContent {
  meta: LessonRef;
  promptMdxSource: string;
  starter: string;
  solution: string;
  tests: string;
  hints: Hints;
}
