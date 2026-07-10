import type {
  AiBookJob,
  AiBookPipelineContext,
  AiBookRequest,
  AnswerManifest,
  BookPlan,
  CoverManifest,
  KeywordResearch,
  PdfManifest,
  PublicationReceipt,
  PuzzleManifest,
  SeoMetadata,
  TopicSelection,
} from './types.js';

export interface Logger {
  info(message: string, data?: Record<string, unknown>): void;
  warn(message: string, data?: Record<string, unknown>): void;
  error(message: string, data?: Record<string, unknown>): void;
}

export interface RetryPolicy { readonly maxAttempts: number; readonly baseDelayMs: number; readonly backoffMultiplier: number; }
export interface RetryService { run<T>(operationName: string, operation: () => Promise<T>, policy?: Partial<RetryPolicy>): Promise<T>; }
export interface ProgressEventPublisher { publish(event: ProgressEvent): Promise<void>; }
export interface ProgressEvent { readonly jobId: string; readonly stage: string; readonly status: 'started' | 'completed' | 'failed'; readonly message: string; readonly timestamp: Date; readonly data?: Record<string, unknown>; }

export interface AiBookJobRepository { create(request: AiBookRequest): Promise<AiBookJob>; update(job: AiBookJob): Promise<AiBookJob>; findById(jobId: string): Promise<AiBookJob | undefined>; }
export interface AiBookJobService { createJob(request: AiBookRequest): Promise<AiBookJob>; markRunning(job: AiBookJob, stage: AiBookJob['stage']): Promise<AiBookJob>; markCompleted(job: AiBookJob): Promise<AiBookJob>; markFailed(job: AiBookJob): Promise<AiBookJob>; }
export interface PipelineTask { readonly stage: string; execute(context: AiBookPipelineContext): Promise<AiBookPipelineContext>; }
export interface TaskOrchestrator { run(context: AiBookPipelineContext, tasks: readonly PipelineTask[]): Promise<AiBookPipelineContext>; }

export interface TopicSelectionService { selectTopic(context: AiBookPipelineContext): Promise<TopicSelection>; }
export interface KeywordResearchService { researchKeywords(topic: TopicSelection, context: AiBookPipelineContext): Promise<KeywordResearch>; }
export interface BookPlannerService { planBook(topic: TopicSelection, research: KeywordResearch, context: AiBookPipelineContext): Promise<BookPlan>; }
export interface PuzzleGeneratorService { generatePuzzles(plan: BookPlan, context: AiBookPipelineContext): Promise<PuzzleManifest>; }
export interface AnswerGeneratorService { generateAnswers(puzzles: PuzzleManifest, context: AiBookPipelineContext): Promise<AnswerManifest>; }
export interface CoverGeneratorService { generateCover(plan: BookPlan, context: AiBookPipelineContext): Promise<CoverManifest>; }
export interface SeoGeneratorService { generateSeo(plan: BookPlan, research: KeywordResearch, context: AiBookPipelineContext): Promise<SeoMetadata>; }
export interface PdfBuilderService { buildPdf(context: AiBookPipelineContext): Promise<PdfManifest>; }
export interface WordpressPublisherService { publishToWordpress(context: AiBookPipelineContext): Promise<PublicationReceipt>; }
export interface PinterestPublisherService { publishToPinterest(context: AiBookPipelineContext): Promise<PublicationReceipt>; }
export interface AiBookPipeline { start(request: AiBookRequest): Promise<AiBookPipelineContext>; }
