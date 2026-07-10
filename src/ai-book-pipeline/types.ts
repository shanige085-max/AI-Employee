export type AiBookStage =
  | 'request'
  | 'job'
  | 'topic-selection'
  | 'keyword-research'
  | 'book-planner'
  | 'puzzle-generator'
  | 'answer-generator'
  | 'cover-generator'
  | 'seo-generator'
  | 'pdf-builder'
  | 'wordpress-publisher'
  | 'pinterest-publisher'
  | 'completed';

export type AiBookJobStatus = 'queued' | 'running' | 'completed' | 'failed';

export interface AiBookRequest {
  readonly prompt: string;
  readonly requestedBy?: string;
  readonly metadata?: Record<string, unknown>;
}

export interface AiBookJob {
  readonly id: string;
  readonly request: AiBookRequest;
  readonly status: AiBookJobStatus;
  readonly stage: AiBookStage;
  readonly attempts: number;
  readonly createdAt: Date;
  readonly updatedAt: Date;
}

export interface TopicSelection { readonly title: string; readonly audience: string; readonly theme: string; }
export interface KeywordResearch { readonly primaryKeyword: string; readonly secondaryKeywords: readonly string[]; readonly notes: string; }
export interface BookPlan { readonly title: string; readonly subtitle?: string; readonly pageCount: number; readonly puzzleCount: number; }
export interface PuzzleManifest { readonly puzzleIds: readonly string[]; readonly status: 'planned-only'; }
export interface AnswerManifest { readonly answerIds: readonly string[]; readonly status: 'planned-only'; }
export interface CoverManifest { readonly title: string; readonly status: 'planned-only'; }
export interface SeoMetadata { readonly title: string; readonly description: string; readonly keywords: readonly string[]; }
export interface PdfManifest { readonly fileName: string; readonly status: 'planned-only'; }
export interface PublicationReceipt { readonly platform: 'wordpress' | 'pinterest'; readonly status: 'planned-only'; readonly externalId?: string; }

export interface AiBookPipelineContext {
  readonly job: AiBookJob;
  topic?: TopicSelection;
  keywordResearch?: KeywordResearch;
  bookPlan?: BookPlan;
  puzzleManifest?: PuzzleManifest;
  answerManifest?: AnswerManifest;
  coverManifest?: CoverManifest;
  seoMetadata?: SeoMetadata;
  pdfManifest?: PdfManifest;
  wordpressReceipt?: PublicationReceipt;
  pinterestReceipt?: PublicationReceipt;
}
