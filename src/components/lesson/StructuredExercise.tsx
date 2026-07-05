"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Button } from "@/components/ui/Button";
import { TestResults } from "@/components/ide/TestResults";
import { gradeStructured } from "@/lib/structured/grade";
import type {
  ErdValue,
  StructuredAnswer,
  StructuredField,
  StructuredQuestion,
} from "@/lib/structured/types";
import type { SubmitResult } from "@/lib/languages/types";
import {
  isLessonComplete,
  loadCode,
  saveCode,
  setLastVisited,
  setLessonComplete,
} from "@/lib/progress";

interface StructuredExerciseProps {
  languageId: string;
  moduleId: string;
  lessonId: string;
  question: StructuredQuestion;
  /** Canonical answer (ships to the client — same as query exercises' solution/tests). */
  answer: StructuredAnswer;
  hints: string[];
}

/**
 * Track-2 renderer. Renders each structured field as a constrained input, grades
 * the whole set on Submit with the SAME pure comparators the headless grader uses
 * (src/lib/structured/grade.ts), surfaces per-field pass/fail through the shared
 * <TestResults>, and marks the lesson complete when every field passes. No engine,
 * no worker — grading is synchronous, pure JavaScript.
 */
export function StructuredExercise({
  languageId,
  moduleId,
  lessonId,
  question,
  answer,
  hints,
}: StructuredExerciseProps) {
  const [values, setValues] = useState<StructuredAnswer>(() => initialValues(question));
  const [draft, setDraft] = useState("");
  const [result, setResult] = useState<SubmitResult | null>(null);
  const [completed, setCompleted] = useState(false);
  const [hintsShown, setHintsShown] = useState(0);

  const draftKey = useMemo(() => `${lessonId}::draft`, [lessonId]);

  useEffect(() => {
    setLastVisited(languageId, moduleId, lessonId);
    setCompleted(isLessonComplete(languageId, moduleId, lessonId));
    const savedDraft = loadCode(languageId, moduleId, draftKey);
    if (savedDraft) setDraft(savedDraft);
  }, [languageId, moduleId, lessonId, draftKey]);

  const setField = useCallback((id: string, value: unknown) => {
    setValues((prev) => ({ ...prev, [id]: value as StructuredAnswer[string] }));
  }, []);

  const onDraftChange = useCallback(
    (text: string) => {
      setDraft(text);
      saveCode(languageId, moduleId, draftKey, text);
    },
    [languageId, moduleId, draftKey],
  );

  const handleSubmit = useCallback(() => {
    const graded = gradeStructured(question, answer, values);
    setResult(graded);
    if (graded.allPassed) {
      setLessonComplete(languageId, moduleId, lessonId, true);
      setCompleted(true);
    }
  }, [question, answer, values, languageId, moduleId, lessonId]);

  return (
    <div className="space-y-8">
      {completed ? (
        <div className="rounded-md border border-success/40 bg-success/10 px-3 py-1.5 text-sm font-medium text-success">
          ✓ You&apos;ve completed this exercise. Feel free to keep refining your answer.
        </div>
      ) : null}

      {question.draft ? (
        <section className="rounded-lg border border-border bg-surface p-4">
          <h3 className="text-sm font-semibold text-text">Draft it first (not graded)</h3>
          <p className="mt-1 text-sm text-muted">{question.draft}</p>
          <textarea
            value={draft}
            onChange={(e) => onDraftChange(e.target.value)}
            rows={5}
            spellCheck={false}
            className="mt-3 w-full resize-y rounded-md border border-border bg-bg p-3 font-mono text-sm text-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
            placeholder="Work it out here before you fill in the graded answer below…"
          />
        </section>
      ) : null}

      <div className="space-y-8">
        {question.fields.map((field) => (
          <FieldView
            key={field.id}
            field={field}
            value={values[field.id]}
            onChange={(v) => setField(field.id, v)}
          />
        ))}
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <Button variant="primary" onClick={handleSubmit}>
          Submit answer
        </Button>
        {hints.length > 0 && hintsShown < hints.length ? (
          <Button
            variant="ghost"
            onClick={() => setHintsShown((n) => Math.min(n + 1, hints.length))}
          >
            {hintsShown === 0 ? "Show a hint" : "Next hint"}
          </Button>
        ) : null}
      </div>

      {hintsShown > 0 ? (
        <ul className="space-y-2 rounded-md border border-border bg-surface p-4 text-sm text-muted">
          {hints.slice(0, hintsShown).map((h, i) => (
            <li key={i} className="flex gap-2">
              <span aria-hidden="true">💡</span>
              <span>{h}</span>
            </li>
          ))}
        </ul>
      ) : null}

      {result ? <TestResults result={result} /> : null}
    </div>
  );
}

// ---------------------------------------------------------------------------
// initial per-field empty values
// ---------------------------------------------------------------------------

function initialValues(question: StructuredQuestion): StructuredAnswer {
  const out: StructuredAnswer = {};
  for (const field of question.fields) {
    switch (field.type) {
      case "single-select":
        out[field.id] = "";
        break;
      case "multi-select":
      case "token-set":
        out[field.id] = [];
        break;
      case "matching":
      case "partition":
        out[field.id] = {};
        break;
      case "erd-spec":
        out[field.id] = { entities: [], relationships: [] } as ErdValue;
        break;
    }
  }
  return out;
}

// ---------------------------------------------------------------------------
// field views
// ---------------------------------------------------------------------------

function FieldShell({
  field,
  children,
}: {
  field: StructuredField;
  children: React.ReactNode;
}) {
  return (
    <section>
      <h3 className="text-sm font-semibold text-text">{field.label}</h3>
      {field.help ? <p className="mt-1 text-sm text-muted">{field.help}</p> : null}
      <div className="mt-3">{children}</div>
    </section>
  );
}

function FieldView({
  field,
  value,
  onChange,
}: {
  field: StructuredField;
  value: unknown;
  onChange: (v: unknown) => void;
}) {
  switch (field.type) {
    case "single-select":
      return (
        <FieldShell field={field}>
          <div className="space-y-2">
            {field.options.map((opt) => (
              <label key={opt} className="flex cursor-pointer items-center gap-2 text-sm text-text">
                <input
                  type="radio"
                  name={field.id}
                  checked={value === opt}
                  onChange={() => onChange(opt)}
                  className="accent-[rgb(var(--accent))]"
                />
                {opt}
              </label>
            ))}
          </div>
        </FieldShell>
      );

    case "multi-select": {
      const selected = Array.isArray(value) ? (value as string[]) : [];
      return (
        <FieldShell field={field}>
          <div className="space-y-2">
            {field.options.map((opt) => (
              <label key={opt} className="flex cursor-pointer items-center gap-2 text-sm text-text">
                <input
                  type="checkbox"
                  checked={selected.includes(opt)}
                  onChange={(e) =>
                    onChange(
                      e.target.checked
                        ? [...selected, opt]
                        : selected.filter((s) => s !== opt),
                    )
                  }
                  className="accent-[rgb(var(--accent))]"
                />
                {opt}
              </label>
            ))}
          </div>
        </FieldShell>
      );
    }

    case "token-set": {
      const lines = Array.isArray(value) ? (value as string[]) : [];
      return (
        <FieldShell field={field}>
          <textarea
            value={lines.join("\n")}
            onChange={(e) => onChange(e.target.value.split("\n"))}
            rows={5}
            spellCheck={false}
            placeholder={field.placeholder ?? "One per line…"}
            className="w-full resize-y rounded-md border border-border bg-bg p-3 font-mono text-sm text-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
          />
        </FieldShell>
      );
    }

    case "matching": {
      const map = (value && typeof value === "object" ? value : {}) as Record<string, string>;
      return (
        <FieldShell field={field}>
          <div className="space-y-2">
            {field.left.map((leftItem) => (
              <div key={leftItem} className="flex flex-wrap items-center gap-2 text-sm">
                <span className="min-w-[12rem] flex-1 font-mono text-text">{leftItem}</span>
                <select
                  value={map[leftItem] ?? ""}
                  onChange={(e) => onChange({ ...map, [leftItem]: e.target.value })}
                  className="rounded-md border border-border bg-bg px-2 py-1 text-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
                >
                  <option value="">— choose —</option>
                  {field.options.map((opt) => (
                    <option key={opt} value={opt}>
                      {opt}
                    </option>
                  ))}
                </select>
              </div>
            ))}
          </div>
        </FieldShell>
      );
    }

    case "partition": {
      // Internal state is item → target; the graded value is target → items[].
      const groups = (value && typeof value === "object" ? value : {}) as Record<string, string[]>;
      const itemTarget = (item: string): string => {
        for (const [target, items] of Object.entries(groups)) {
          if (Array.isArray(items) && items.includes(item)) return target;
        }
        return "";
      };
      const assign = (item: string, target: string) => {
        const next: Record<string, string[]> = {};
        for (const t of field.targets) {
          const kept = (groups[t] ?? []).filter((x) => x !== item);
          if (t === target && target) kept.push(item);
          if (kept.length > 0) next[t] = kept;
        }
        onChange(next);
      };
      return (
        <FieldShell field={field}>
          <div className="space-y-2">
            {field.items.map((item) => (
              <div key={item} className="flex flex-wrap items-center gap-2 text-sm">
                <span className="min-w-[10rem] flex-1 font-mono text-text">{item}</span>
                <select
                  value={itemTarget(item)}
                  onChange={(e) => assign(item, e.target.value)}
                  className="rounded-md border border-border bg-bg px-2 py-1 text-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
                >
                  <option value="">— unassigned —</option>
                  {field.targets.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </div>
            ))}
          </div>
        </FieldShell>
      );
    }

    case "erd-spec":
      return (
        <FieldShell field={field}>
          <ErdEditor
            value={(value as ErdValue) ?? { entities: [], relationships: [] }}
            cardinalities={field.cardinalities ?? ["1:1", "1:N", "N:M"]}
            onChange={onChange}
          />
        </FieldShell>
      );

    default:
      return null;
  }
}

// ---------------------------------------------------------------------------
// ERD editor (structured, not a canvas)
// ---------------------------------------------------------------------------

function ErdEditor({
  value,
  cardinalities,
  onChange,
}: {
  value: ErdValue;
  cardinalities: string[];
  onChange: (v: ErdValue) => void;
}) {
  const entities = value.entities ?? [];
  const relationships = value.relationships ?? [];
  const entityNames = entities.map((e) => e.name).filter((n) => n.trim().length > 0);

  const update = (patch: Partial<ErdValue>) => onChange({ entities, relationships, ...patch });

  const addEntity = () => update({ entities: [...entities, { name: "", attributes: [] }] });
  const removeEntity = (i: number) => update({ entities: entities.filter((_, idx) => idx !== i) });
  const setEntity = (i: number, next: ErdValue["entities"][number]) =>
    update({ entities: entities.map((e, idx) => (idx === i ? next : e)) });

  const addRel = () =>
    update({
      relationships: [
        ...relationships,
        { from: "", to: "", cardinality: cardinalities[0] ?? "1:N", identifying: false },
      ],
    });
  const removeRel = (i: number) =>
    update({ relationships: relationships.filter((_, idx) => idx !== i) });
  const setRel = (i: number, next: ErdValue["relationships"][number]) =>
    update({ relationships: relationships.map((r, idx) => (idx === i ? next : r)) });

  const inputCls =
    "rounded-md border border-border bg-bg px-2 py-1 text-sm text-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent";

  return (
    <div className="space-y-5">
      {/* Entities */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wide text-muted">Entities</span>
          <Button size="sm" variant="secondary" onClick={addEntity}>
            + Entity
          </Button>
        </div>
        {entities.map((ent, i) => (
          <div key={i} className="rounded-md border border-border bg-surface p-3">
            <div className="flex items-center gap-2">
              <input
                value={ent.name}
                onChange={(e) => setEntity(i, { ...ent, name: e.target.value })}
                placeholder="entity name (table)"
                className={`flex-1 font-mono ${inputCls}`}
              />
              <Button size="sm" variant="danger" onClick={() => removeEntity(i)}>
                Remove
              </Button>
            </div>
            <div className="mt-2 space-y-1.5 pl-1">
              {ent.attributes.map((attr, ai) => (
                <div key={ai} className="flex items-center gap-2 text-sm">
                  <input
                    value={attr.name}
                    onChange={(e) =>
                      setEntity(i, {
                        ...ent,
                        attributes: ent.attributes.map((a, idx) =>
                          idx === ai ? { ...a, name: e.target.value } : a,
                        ),
                      })
                    }
                    placeholder="attribute"
                    className={`flex-1 font-mono ${inputCls}`}
                  />
                  <label className="flex items-center gap-1 text-xs text-muted">
                    <input
                      type="checkbox"
                      checked={attr.pk === true}
                      onChange={(e) =>
                        setEntity(i, {
                          ...ent,
                          attributes: ent.attributes.map((a, idx) =>
                            idx === ai ? { ...a, pk: e.target.checked } : a,
                          ),
                        })
                      }
                      className="accent-[rgb(var(--accent))]"
                    />
                    PK
                  </label>
                  <button
                    type="button"
                    onClick={() =>
                      setEntity(i, {
                        ...ent,
                        attributes: ent.attributes.filter((_, idx) => idx !== ai),
                      })
                    }
                    className="text-muted hover:text-danger"
                    aria-label="Remove attribute"
                  >
                    ✕
                  </button>
                </div>
              ))}
              <button
                type="button"
                onClick={() => setEntity(i, { ...ent, attributes: [...ent.attributes, { name: "" }] })}
                className="text-xs font-medium text-accent-strong hover:text-accent"
              >
                + attribute
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Relationships */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wide text-muted">
            Relationships
          </span>
          <Button size="sm" variant="secondary" onClick={addRel} disabled={entityNames.length < 1}>
            + Relationship
          </Button>
        </div>
        {relationships.map((rel, i) => (
          <div key={i} className="flex flex-wrap items-center gap-2 rounded-md border border-border bg-surface p-3 text-sm">
            <EntitySelect value={rel.from} names={entityNames} onChange={(v) => setRel(i, { ...rel, from: v })} cls={inputCls} />
            <select
              value={rel.cardinality}
              onChange={(e) => setRel(i, { ...rel, cardinality: e.target.value })}
              className={inputCls}
            >
              {cardinalities.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
            <EntitySelect value={rel.to} names={entityNames} onChange={(v) => setRel(i, { ...rel, to: v })} cls={inputCls} />
            <label className="flex items-center gap-1 text-xs text-muted">
              <input
                type="checkbox"
                checked={rel.identifying === true}
                onChange={(e) => setRel(i, { ...rel, identifying: e.target.checked })}
                className="accent-[rgb(var(--accent))]"
              />
              identifying
            </label>
            <Button size="sm" variant="danger" onClick={() => removeRel(i)}>
              Remove
            </Button>
          </div>
        ))}
      </div>
    </div>
  );
}

function EntitySelect({
  value,
  names,
  onChange,
  cls,
}: {
  value: string;
  names: string[];
  onChange: (v: string) => void;
  cls: string;
}) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)} className={`font-mono ${cls}`}>
      <option value="">— entity —</option>
      {names.map((n) => (
        <option key={n} value={n}>
          {n}
        </option>
      ))}
    </select>
  );
}
