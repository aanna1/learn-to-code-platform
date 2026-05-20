import { notFound } from "next/navigation";
import Link from "next/link";
import { getLanguageIds, hasLanguage } from "@/lib/languages/registry";
import { compileMdx } from "@/lib/content/mdx";
import { mdxComponents } from "@/components/lesson/mdxComponents";
import { LessonLanguageProvider } from "@/components/lesson/LessonLanguageProvider";
import { LectureFooter } from "@/components/lesson/LectureFooter";
import { ExercisePane } from "@/components/lesson/ExercisePane";
import {
  getExercise,
  getLecture,
  getLessonNeighbors,
  getLessonRef,
  listLessonParams,
  type LessonNavLink,
} from "@/lib/content/loader";

/** One static page per (language, module, lesson) across the whole registry. */
export function generateStaticParams() {
  const params: { language: string; module: string; lesson: string }[] = [];
  for (const language of getLanguageIds()) {
    for (const { module, lesson } of listLessonParams(language)) {
      params.push({ language, module, lesson });
    }
  }
  return params;
}

interface PageProps {
  params: { language: string; module: string; lesson: string };
}

function lessonHref(languageId: string, link: LessonNavLink): string {
  return `/learn/${languageId}/${link.moduleId}/${link.lessonId}`;
}

function PrevNext({
  languageId,
  prev,
  next,
  className = "",
}: {
  languageId: string;
  prev: LessonNavLink | null;
  next: LessonNavLink | null;
  className?: string;
}) {
  return (
    <nav className={`flex items-center justify-between gap-4 text-sm ${className}`}>
      {prev ? (
        <Link
          href={lessonHref(languageId, prev)}
          className="min-w-0 truncate text-muted hover:text-text"
        >
          ← {prev.title}
        </Link>
      ) : (
        <span />
      )}
      {next ? (
        <Link
          href={lessonHref(languageId, next)}
          className="min-w-0 truncate text-right font-medium text-accent-strong hover:text-accent"
        >
          {next.title} →
        </Link>
      ) : (
        <span />
      )}
    </nav>
  );
}

export default async function LessonPage({ params }: PageProps) {
  const { language, module: moduleId, lesson: lessonId } = params;
  if (!hasLanguage(language)) notFound();

  const ref = getLessonRef(language, moduleId, lessonId);
  if (!ref) notFound();

  const { moduleManifest, prev, next } = getLessonNeighbors(language, moduleId, lessonId);

  if (ref.type === "lecture") {
    const lecture = getLecture(language, moduleId, lessonId);
    const Content = await compileMdx(lecture.mdxSource);

    return (
      <main className="mx-auto max-w-3xl px-6 py-10">
        <Link href={`/learn/${language}`} className="text-sm text-muted hover:text-text">
          ← {moduleManifest.title}
        </Link>

        <article className="mt-6">
          <h1 className="text-3xl font-bold tracking-tight">{ref.title}</h1>
          <LessonLanguageProvider languageId={language}>
            <Content components={mdxComponents} />
          </LessonLanguageProvider>
        </article>

        <LectureFooter
          languageId={language}
          moduleId={moduleId}
          lessonId={lessonId}
          quiz={lecture.quiz}
        />

        <PrevNext
          languageId={language}
          prev={prev}
          next={next}
          className="mt-12 border-t border-border pt-6"
        />
      </main>
    );
  }

  const exercise = getExercise(language, moduleId, lessonId);
  const Prompt = await compileMdx(exercise.promptMdxSource);

  return (
    <div className="flex flex-col md:h-[calc(100vh-3.5rem)] md:overflow-hidden">
      <header className="shrink-0 border-b border-border px-4 py-2.5">
        <div className="mx-auto flex max-w-6xl items-center gap-4">
          <Link
            href={`/learn/${language}`}
            className="shrink-0 text-sm text-muted hover:text-text"
          >
            ← {moduleManifest.title}
          </Link>
          <PrevNext languageId={language} prev={prev} next={next} className="ml-auto flex-1 justify-end gap-6" />
        </div>
      </header>

      <div className="mx-auto grid w-full max-w-6xl flex-1 grid-cols-1 md:min-h-0 md:grid-cols-2">
        <article className="px-6 py-8 md:overflow-y-auto md:border-r md:border-border">
          <h1 className="text-2xl font-bold tracking-tight">{ref.title}</h1>
          <LessonLanguageProvider languageId={language}>
            <Prompt components={mdxComponents} />
          </LessonLanguageProvider>
        </article>

        <div className="min-h-0 p-3 md:p-4">
          <ExercisePane
            languageId={language}
            moduleId={moduleId}
            lessonId={lessonId}
            exercise={{
              starter: exercise.starter,
              solution: exercise.solution,
              tests: exercise.tests,
              hints: exercise.hints.hints,
            }}
          />
        </div>
      </div>
    </div>
  );
}
