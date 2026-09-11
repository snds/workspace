// ─── AI Translation Engine — Validator ───────────────────────────────────────
// Heuristic validation pipeline for generated code. These are fast, offline
// checks — NOT actual compilation or type-checking.

import type {
  GeneratedFile,
  ValidationResult,
  ValidationError,
  ValidationWarning,
} from "./types";

// ─── Main entry point ───────────────────────────────────────────────────────

/**
 * Validate generated code for structural correctness.
 * Runs all heuristic validators and aggregates results.
 */
export function validateGenerated(files: GeneratedFile[]): ValidationResult {
  const errors: ValidationError[] = [];
  const warnings: ValidationWarning[] = [];

  for (const file of files) {
    validateImports(file, errors, warnings);
    validateSyntax(file, errors, warnings);
    validateComponentStructure(file, errors, warnings);
    validateTypeScript(file, errors, warnings);
  }

  // Cross-file validation: check that internal imports reference existing files
  validateCrossFileImports(files, errors, warnings);

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
}

// ─── Import validation ──────────────────────────────────────────────────────

/**
 * Check for common import errors: missing quotes, malformed paths,
 * duplicate imports.
 */
function validateImports(
  file: GeneratedFile,
  errors: ValidationError[],
  warnings: ValidationWarning[],
): void {
  const lines = file.content.split("\n");
  const seenImports = new Set<string>();

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    // Check import statements
    if (line.startsWith("import ")) {
      // Check for unmatched quotes
      const singleQuotes = (line.match(/'/g) ?? []).length;
      const doubleQuotes = (line.match(/"/g) ?? []).length;

      if (singleQuotes % 2 !== 0 && doubleQuotes % 2 !== 0) {
        errors.push({
          file: file.path,
          line: i + 1,
          message: "Import statement has unmatched quotes.",
          severity: "error",
        });
      }

      // Check for missing semicolons (if not a Vue/Svelte file)
      if (
        !file.path.endsWith(".vue") &&
        !file.path.endsWith(".svelte") &&
        !line.endsWith(";") &&
        !line.endsWith("{")
      ) {
        // Multi-line import, skip this check
        if (!line.includes("from")) continue;

        warnings.push({
          file: file.path,
          message: `Line ${i + 1}: Import may be missing a semicolon.`,
          suggestion: "Add a semicolon at the end of the import statement.",
        });
      }

      // Check for duplicate imports
      const fromMatch = line.match(/from\s+['"]([^'"]+)['"]/);
      if (fromMatch) {
        const importPath = fromMatch[1];
        if (seenImports.has(importPath)) {
          warnings.push({
            file: file.path,
            message: `Duplicate import from "${importPath}" at line ${i + 1}.`,
            suggestion: "Consolidate imports from the same module.",
          });
        }
        seenImports.add(importPath);
      }
    }
  }
}

// ─── Syntax validation ──────────────────────────────────────────────────────

/**
 * Basic syntax checks: matching brackets, valid JSX structure.
 */
function validateSyntax(
  file: GeneratedFile,
  errors: ValidationError[],
  _warnings: ValidationWarning[],
): void {
  const { content, path } = file;

  // Check matching brackets / braces / parentheses
  const bracketPairs: Record<string, string> = { "(": ")", "[": "]", "{": "}" };
  const closingBrackets = new Set(Object.values(bracketPairs));
  const stack: { char: string; line: number }[] = [];
  let inString = false;
  let stringChar = "";
  let inTemplateString = false;
  let inLineComment = false;
  let inBlockComment = false;
  let lineNumber = 1;

  for (let i = 0; i < content.length; i++) {
    const char = content[i];
    const prevChar = i > 0 ? content[i - 1] : "";

    // Track line numbers
    if (char === "\n") {
      lineNumber++;
      inLineComment = false;
      continue;
    }

    // Skip comments
    if (inLineComment) continue;
    if (inBlockComment) {
      if (char === "/" && prevChar === "*") {
        inBlockComment = false;
      }
      continue;
    }

    // Detect comment starts
    if (char === "/" && i + 1 < content.length) {
      if (content[i + 1] === "/") {
        inLineComment = true;
        continue;
      }
      if (content[i + 1] === "*") {
        inBlockComment = true;
        continue;
      }
    }

    // Track strings
    if (inString) {
      if (char === stringChar && prevChar !== "\\") {
        inString = false;
      }
      continue;
    }
    if (inTemplateString) {
      if (char === "`" && prevChar !== "\\") {
        inTemplateString = false;
      }
      continue;
    }
    if (char === '"' || char === "'") {
      inString = true;
      stringChar = char;
      continue;
    }
    if (char === "`") {
      inTemplateString = true;
      continue;
    }

    // Track brackets
    if (char in bracketPairs) {
      stack.push({ char, line: lineNumber });
    } else if (closingBrackets.has(char)) {
      if (stack.length === 0) {
        errors.push({
          file: path,
          line: lineNumber,
          message: `Unexpected closing bracket '${char}' with no matching opening bracket.`,
          severity: "error",
        });
      } else {
        const last = stack[stack.length - 1];
        if (bracketPairs[last.char] !== char) {
          errors.push({
            file: path,
            line: lineNumber,
            message: `Mismatched bracket: expected '${bracketPairs[last.char]}' but found '${char}'.`,
            severity: "error",
          });
        }
        stack.pop();
      }
    }
  }

  // Check for unclosed brackets
  for (const unclosed of stack) {
    errors.push({
      file: path,
      line: unclosed.line,
      message: `Unclosed bracket '${unclosed.char}' opened at line ${unclosed.line}.`,
      severity: "error",
    });
  }
}

// ─── Component structure validation ─────────────────────────────────────────

/**
 * Check that component files have proper exports and return JSX.
 */
function validateComponentStructure(
  file: GeneratedFile,
  errors: ValidationError[],
  warnings: ValidationWarning[],
): void {
  const { content, path, language } = file;

  // Only validate TSX/JSX files
  if (language !== "tsx" && language !== "jsx") return;

  // Skip test files, type files, and config files
  if (
    path.includes(".test.") ||
    path.includes(".spec.") ||
    path.includes(".d.ts") ||
    path.includes(".config.")
  ) {
    return;
  }

  // Check for at least one export
  const hasExport =
    content.includes("export default") ||
    content.includes("export function") ||
    content.includes("export const") ||
    content.includes("export {");

  if (!hasExport) {
    warnings.push({
      file: path,
      message: "Component file has no exports.",
      suggestion: "Add a named or default export for the component.",
    });
  }

  // Check for JSX return
  const hasJSX =
    content.includes("return (") ||
    content.includes("return <") ||
    content.includes("=> (") ||
    content.includes("=> <");

  if (!hasJSX) {
    warnings.push({
      file: path,
      message: "Component file does not appear to return JSX.",
      suggestion: "Ensure the component function returns JSX elements.",
    });
  }

  // Check for React import (only for non-Next.js/non-Vite projects where auto-import isn't available)
  // This is a soft warning — many modern setups don't need explicit React imports
  if (content.includes("React.") && !content.includes("import React")) {
    errors.push({
      file: path,
      line: 1,
      message: 'Uses "React." namespace but React is not imported.',
      severity: "warning",
    });
  }
}

// ─── TypeScript validation ──────────────────────────────────────────────────

/**
 * Check for obvious TypeScript errors: any usage, missing type annotations
 * on exported functions.
 */
function validateTypeScript(
  file: GeneratedFile,
  _errors: ValidationError[],
  warnings: ValidationWarning[],
): void {
  const { content, path, language } = file;

  // Only check TypeScript files
  if (language !== "typescript" && language !== "tsx") return;

  // Warn about `any` usage
  const anyMatches = content.match(/:\s*any\b/g);
  if (anyMatches && anyMatches.length > 0) {
    warnings.push({
      file: path,
      message: `Found ${anyMatches.length} usage(s) of the "any" type.`,
      suggestion: "Replace 'any' with specific types for better type safety.",
    });
  }

  // Warn about @ts-ignore / @ts-nocheck
  if (content.includes("@ts-ignore") || content.includes("@ts-nocheck")) {
    warnings.push({
      file: path,
      message: "Contains TypeScript suppression comments (@ts-ignore or @ts-nocheck).",
      suggestion: "Fix the underlying type error instead of suppressing it.",
    });
  }

  // Check for non-null assertions (!)
  const nonNullMatches = content.match(/\w+!/g);
  if (nonNullMatches && nonNullMatches.length > 3) {
    warnings.push({
      file: path,
      message: `Found ${nonNullMatches.length} non-null assertions (!). Consider using proper null checks.`,
      suggestion: "Use optional chaining (?.) or explicit null checks instead.",
    });
  }
}

// ─── Cross-file import validation ───────────────────────────────────────────

/**
 * Check that relative imports between generated files actually reference
 * files that exist in the generated set.
 */
function validateCrossFileImports(
  files: GeneratedFile[],
  _errors: ValidationError[],
  warnings: ValidationWarning[],
): void {
  const generatedPaths = new Set(files.map((f) => f.path));

  for (const file of files) {
    const importMatches = file.content.matchAll(/from\s+['"](\.[^'"]+)['"]/g);

    for (const match of importMatches) {
      const rawImportPath = match[1];

      // Resolve the import path relative to the file's directory
      const fileDir = file.path.substring(0, file.path.lastIndexOf("/"));
      const resolved = resolveRelativePath(fileDir, rawImportPath);

      // Check if the resolved path (with or without extension) exists
      const possiblePaths = [
        resolved,
        `${resolved}.ts`,
        `${resolved}.tsx`,
        `${resolved}.js`,
        `${resolved}.jsx`,
        `${resolved}/index.ts`,
        `${resolved}/index.tsx`,
      ];

      const found = possiblePaths.some((p) => generatedPaths.has(p));

      if (!found) {
        // Not necessarily an error — the file might exist in the real project
        // but we can warn about it
        warnings.push({
          file: file.path,
          message: `Relative import "${rawImportPath}" does not match any generated file.`,
          suggestion:
            "This import may reference an existing project file, or it may need to be generated.",
        });
      }
    }
  }
}

// ─── Path resolution helper ─────────────────────────────────────────────────

/** Resolve a relative import path against a directory. */
function resolveRelativePath(dir: string, importPath: string): string {
  const parts = dir ? dir.split("/") : [];
  const importParts = importPath.split("/");

  for (const segment of importParts) {
    if (segment === ".") {
      continue;
    } else if (segment === "..") {
      parts.pop();
    } else {
      parts.push(segment);
    }
  }

  return parts.join("/");
}
