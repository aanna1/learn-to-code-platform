import type { ComponentPropsWithoutRef, ReactNode } from "react";
import type { MDXComponents } from "mdx/types";
import { Runnable } from "@/components/lesson/Runnable";

/**
 * The tag→component map handed to compiled lesson MDX. It supplies the prose
 * styling (so authors write plain Markdown and get the site's typography) and the
 * custom components lectures can use: <Runnable> for inline editable/runnable code
 * and <Callout> for asides. We style elements by hand rather than pulling in the
 * Tailwind typography plugin, keeping the dependency surface small.
 */

function Code({ className, children, ...props }: ComponentPropsWithoutRef<"code">) {
  // Fenced blocks arrive as <code class="language-…"> inside <pre>; leave those
  // unboxed (the <pre> wrapper styles them). Only inline code gets the chip look.
  const isBlock = typeof className === "string" && className.startsWith("language-");
  if (isBlock) {
    return (
      <code className={`${className} font-mono`} {...props}>
        {children}
      </code>
    );
  }
  return (
    <code
      className="rounded bg-surface-raised px-1.5 py-0.5 font-mono text-[0.85em] text-accent-strong"
      {...props}
    >
      {children}
    </code>
  );
}

type CalloutType = "note" | "tip" | "warning";

const CALLOUT_STYLES: Record<CalloutType, string> = {
  note: "border-accent/40 bg-accent/10",
  tip: "border-highlight/40 bg-highlight/10",
  warning: "border-danger/40 bg-danger/10",
};

const CALLOUT_LABELS: Record<CalloutType, string> = {
  note: "Note",
  tip: "Tip",
  warning: "Heads up",
};

function Callout({ type = "note", children }: { type?: CalloutType; children: ReactNode }) {
  return (
    <div className={`my-5 rounded-md border p-4 text-sm ${CALLOUT_STYLES[type]}`}>
      <p className="mb-1 font-semibold">{CALLOUT_LABELS[type]}</p>
      <div className="space-y-2 [&_p]:m-0">{children}</div>
    </div>
  );
}

export const mdxComponents: MDXComponents = {
  h1: (props: ComponentPropsWithoutRef<"h1">) => (
    <h1 className="mt-2 text-2xl font-bold tracking-tight" {...props} />
  ),
  h2: (props: ComponentPropsWithoutRef<"h2">) => (
    <h2 className="mt-8 text-xl font-semibold tracking-tight" {...props} />
  ),
  h3: (props: ComponentPropsWithoutRef<"h3">) => (
    <h3 className="mt-6 text-lg font-semibold" {...props} />
  ),
  p: (props: ComponentPropsWithoutRef<"p">) => (
    <p className="mt-4 leading-relaxed text-text" {...props} />
  ),
  ul: (props: ComponentPropsWithoutRef<"ul">) => (
    <ul className="mt-4 list-disc space-y-1.5 pl-6 leading-relaxed" {...props} />
  ),
  ol: (props: ComponentPropsWithoutRef<"ol">) => (
    <ol className="mt-4 list-decimal space-y-1.5 pl-6 leading-relaxed" {...props} />
  ),
  li: (props: ComponentPropsWithoutRef<"li">) => <li className="pl-1" {...props} />,
  a: (props: ComponentPropsWithoutRef<"a">) => (
    <a className="text-accent-strong underline underline-offset-2 hover:text-accent" {...props} />
  ),
  strong: (props: ComponentPropsWithoutRef<"strong">) => (
    <strong className="font-semibold" {...props} />
  ),
  blockquote: (props: ComponentPropsWithoutRef<"blockquote">) => (
    <blockquote
      className="mt-4 border-l-4 border-border pl-4 italic text-muted"
      {...props}
    />
  ),
  hr: () => <hr className="my-8 border-border" />,
  code: Code,
  pre: (props: ComponentPropsWithoutRef<"pre">) => (
    <pre
      className="mt-4 overflow-auto rounded-md border border-border bg-surface-raised p-4 text-sm leading-relaxed"
      {...props}
    />
  ),
  Runnable,
  Callout,
};
