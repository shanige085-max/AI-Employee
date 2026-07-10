# AI Book Pipeline

The AI Book Pipeline is the production architecture for turning a natural-language request such as `Create Kids Maze Book` into a completed, publishable book workflow. This change intentionally does not implement AI text generation, puzzle generation, PDF rendering, or external publishing; every downstream integration is represented by an interface and a placeholder service.

## Workflow

1. Request
2. Job
3. Topic Selection
4. Keyword Research Service
5. Book Planner
6. Puzzle Generator
7. Answer Generator
8. Cover Generator
9. SEO Generator
10. PDF Builder
11. WordPress Publisher
12. Pinterest Publisher
13. Completed

## Architecture

- `types.ts` defines shared pipeline stages, job state, request payloads, and manifests.
- `interfaces.ts` defines service contracts, task orchestration, progress events, retry support, job persistence, and logging.
- `services.ts` provides safe placeholder implementations that create manifests only and never generate puzzles or AI content.
- `orchestrator.ts` runs ordered tasks, emits progress events, applies retry policy, logs failures, and marks jobs failed on unrecoverable errors.
- `container.ts` wires dependency injection and allows production implementations to replace any placeholder service.

## Extension Points

Replace the placeholder services behind these interfaces when the real integrations are ready:

- `KeywordResearchService`
- `PuzzleGeneratorService`
- `AnswerGeneratorService`
- `CoverGeneratorService`
- `SeoGeneratorService`
- `PdfBuilderService`
- `WordpressPublisherService`
- `PinterestPublisherService`

## Usage

```ts
import { createAiBookPipelineContainer } from './src/ai-book-pipeline/index.js';

const pipeline = createAiBookPipelineContainer();
const result = await pipeline.start({ prompt: 'Create Kids Maze Book' });
```

The result contains the completed job and all intermediate manifests. Generated puzzle, answer, cover, PDF, WordPress, and Pinterest artifacts are currently marked as `planned-only` by design.
