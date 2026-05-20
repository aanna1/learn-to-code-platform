import { compile, run } from "@mdx-js/mdx";
import * as jsxRuntime from "react/jsx-runtime";
import type { ComponentType } from "react";
import type { MDXComponents } from "mdx/types";

/**
 * Compiles an MDX string into a React component at build time. Lesson MDX lives
 * on disk as data (loaded by src/lib/content/loader.ts), so we compile the raw
 * string here rather than importing it as a module. This runs only in server
 * components during static export — the heavy compile never reaches the browser.
 *
 * The returned component takes a `components` prop (the tag→component map from
 * mdxComponents.tsx), which is how lectures get inline <Runnable> blocks and
 * styled prose without the MDX author importing anything.
 */
export type MdxContent = ComponentType<{ components?: MDXComponents }>;

export async function compileMdx(source: string): Promise<MdxContent> {
  const compiled = await compile(source, {
    outputFormat: "function-body",
    development: false,
  });

  const { default: Content } = await run(compiled, {
    ...jsxRuntime,
    baseUrl: import.meta.url,
  });

  return Content as MdxContent;
}
