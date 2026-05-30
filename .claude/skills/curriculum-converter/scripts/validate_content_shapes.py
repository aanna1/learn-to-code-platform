#!/usr/bin/env python3
"""Validate that a converted module's JSON files match the loader's interfaces.

The build reads these files at prerender time and indexes into them
(`quiz.questions.length`, `hints.hints`, ...). A bare array PARSES as valid JSON
but is the WRONG SHAPE, so a plain `json.load` check passes while the build still
crashes with "Cannot read properties of undefined (reading 'length')". This script
checks shape, not just parseability.

Interfaces enforced (src/lib/content/types.ts):
  Hints  = { "hints": string[] }
  Quiz   = { "questions": QuizQuestion[] }
  QuizQuestion = { "question": string, "options": QuizOption[] }
  QuizOption   = { "text": string, "correct": bool, "explanation": string }

Usage:
  python scripts/validate_content_shapes.py <dir> [<dir> ...]
  # e.g. the live module tree AND the flat staging folder:
  python scripts/validate_content_shapes.py \
    "src/content/languages/python/modules/05-loops" "curriculum/Python Module 5"

Exits non-zero and prints every problem if any file is the wrong shape.
"""
import json, sys, glob, os

errors = []

def check_hints(path, data):
    if not (isinstance(data, dict) and isinstance(data.get("hints"), list)):
        errors.append(f'{path}: hints.json must be an OBJECT {{ "hints": [...] }}, '
                      f'got {type(data).__name__} (a bare array breaks the build)')
        return
    for i, h in enumerate(data["hints"]):
        if not isinstance(h, str):
            errors.append(f'{path}: hints[{i}] must be a string, got {type(h).__name__}')

def check_quiz(path, data):
    if not (isinstance(data, dict) and isinstance(data.get("questions"), list)):
        errors.append(f'{path}: quiz.json must be an OBJECT {{ "questions": [...] }}, '
                      f'got {type(data).__name__} (a bare array crashes the lecture page)')
        return
    for i, q in enumerate(data["questions"]):
        if not isinstance(q, dict):
            errors.append(f'{path}: questions[{i}] must be an object'); continue
        if not isinstance(q.get("question"), str):
            errors.append(f'{path}: questions[{i}] needs a string "question" key '
                          f'(NOT "text" — that key is for options)')
        opts = q.get("options")
        if not isinstance(opts, list) or not opts:
            errors.append(f'{path}: questions[{i}].options must be a non-empty array'); continue
        n_correct = 0
        for j, o in enumerate(opts):
            if not isinstance(o, dict):
                errors.append(f'{path}: questions[{i}].options[{j}] must be an object'); continue
            for key, typ in (("text", str), ("correct", bool), ("explanation", str)):
                if not isinstance(o.get(key), typ):
                    errors.append(f'{path}: questions[{i}].options[{j}] needs '
                                  f'"{key}": {typ.__name__}')
            if o.get("correct") is True:
                n_correct += 1
        if n_correct != 1:
            errors.append(f'{path}: questions[{i}] must have exactly one correct option, '
                          f'found {n_correct}')

# any file whose name ends in these suffixes is checked by the matching validator
HINTS_SUFFIXES = ("hints.json",)
QUIZ_SUFFIXES = ("quiz.json",)

def validate_dir(d):
    files = glob.glob(os.path.join(d, "**", "*.json"), recursive=True)
    for f in files:
        base = os.path.basename(f)
        try:
            data = json.load(open(f))
        except Exception as e:
            errors.append(f"{f}: not valid JSON — {e}"); continue
        if base.endswith(HINTS_SUFFIXES):
            check_hints(f, data)
        elif base.endswith(QUIZ_SUFFIXES):
            check_quiz(f, data)

def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    for d in argv[1:]:
        if not os.path.isdir(d):
            errors.append(f"{d}: not a directory"); continue
        validate_dir(d)
    if errors:
        print("CONTENT SHAPE ERRORS (%d):" % len(errors))
        for e in errors: print("  - " + e)
        return 1
    print("OK — all hints.json / quiz.json match the loader interfaces.")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
