import { notFound } from "next/navigation";
import Link from "next/link";
import { getLanguage, getLanguageIds, hasLanguage } from "@/lib/languages/registry";
import { getCheatsheet } from "@/lib/content/loader";
import { compileMdx } from "@/lib/content/mdx";
import { mdxComponents } from "@/components/lesson/mdxComponents";
import { LessonLanguageProvider } from "@/components/lesson/LessonLanguageProvider";

/** One cheat-sheet page per registered language. */
export function generateStaticParams() {
  return getLanguageIds().map((language) => ({ language }));
}

interface PageProps {
  params: { language: string };
}

export default async function CheatsheetPage({ params }: PageProps) {
  const { language } = params;
  if (!hasLanguage(language)) notFound();

  const lang = getLanguage(language);
  const Content = await compileMdx(getCheatsheet(language));

  return (
    <main className="mx-auto max-w-3xl px-6 py-10">
      <Link href={`/learn/${language}`} className="text-sm text-muted hover:text-text">
        ← {lang?.config.displayName} course
      </Link>

      <article className="mt-6">
        <h1 className="text-3xl font-bold tracking-tight">
          {lang?.config.displayName} cheat sheet
        </h1>
        <LessonLanguageProvider languageId={language}>
          <Content components={mdxComponents} />
        </LessonLanguageProvider>
      </article>
    </main>
  );
}
