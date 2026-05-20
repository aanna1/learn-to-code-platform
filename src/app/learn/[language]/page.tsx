import { notFound } from "next/navigation";
import { getLanguageIds, hasLanguage } from "@/lib/languages/registry";
import { getResolvedCourse } from "@/lib/content/loader";
import { CourseOutlineView } from "@/components/lesson/CourseOutlineView";

/** Pre-render one outline page per registered language. */
export function generateStaticParams() {
  return getLanguageIds().map((language) => ({ language }));
}

interface PageProps {
  params: { language: string };
}

/**
 * Course outline for a language: every module and its lessons, with free
 * navigation (no gating). Completion checkmarks and "continue where you left off"
 * are layered on by the client view from localStorage.
 */
export default function CourseOutlinePage({ params }: PageProps) {
  const { language } = params;
  if (!hasLanguage(language)) notFound();

  const { course, modules } = getResolvedCourse(language);
  return <CourseOutlineView languageId={language} course={course} modules={modules} />;
}
