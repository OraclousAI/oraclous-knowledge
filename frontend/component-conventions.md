# Component Conventions

## File and folder structure

- `src/components/ui/` — shadcn-derived primitives
- `src/components/<domain>/` — domain components grouped by feature area
- `src/features/<feature>/` — feature folders (pages, hooks, feature-local components)
- `src/pages/` — route-level page components
- `src/lib/` — pure utilities, no React
- `src/api/` — generated OpenAPI types and typed API client

## Component shape

- Function components only
- Named exports for shared components
- Co-located types — props interface in same file, named `<Component>Props`
- One component per file by default

## Accessibility minimums

- Every interactive element is keyboard-reachable
- Every input has a label (visible or `aria-label`)
- Focus rings are never removed without an equivalent replacement
- Modal dialogs trap focus and restore it on close
