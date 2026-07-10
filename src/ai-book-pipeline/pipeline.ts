import type { AiBookJobService, AiBookPipeline, AnswerGeneratorService, BookPlannerService, CoverGeneratorService, KeywordResearchService, PdfBuilderService, PinterestPublisherService, PipelineTask, PuzzleGeneratorService, SeoGeneratorService, TaskOrchestrator, TopicSelectionService, WordpressPublisherService } from './interfaces.js';
import type { AiBookPipelineContext, AiBookRequest } from './types.js';

export interface AiBookPipelineServices {
  readonly jobService: AiBookJobService;
  readonly orchestrator: TaskOrchestrator;
  readonly topicSelection: TopicSelectionService;
  readonly keywordResearch: KeywordResearchService;
  readonly bookPlanner: BookPlannerService;
  readonly puzzleGenerator: PuzzleGeneratorService;
  readonly answerGenerator: AnswerGeneratorService;
  readonly coverGenerator: CoverGeneratorService;
  readonly seoGenerator: SeoGeneratorService;
  readonly pdfBuilder: PdfBuilderService;
  readonly wordpressPublisher: WordpressPublisherService;
  readonly pinterestPublisher: PinterestPublisherService;
}

export class DefaultAiBookPipeline implements AiBookPipeline {
  constructor(private readonly services: AiBookPipelineServices) {}

  async start(request: AiBookRequest): Promise<AiBookPipelineContext> {
    const job = await this.services.jobService.createJob(request);
    return this.services.orchestrator.run({ job }, this.createTasks());
  }

  private createTasks(): readonly PipelineTask[] {
    return [
      { stage: 'topic-selection', execute: async (context) => ({ ...context, topic: await this.services.topicSelection.selectTopic(context) }) },
      { stage: 'keyword-research', execute: async (context) => ({ ...context, keywordResearch: await this.services.keywordResearch.researchKeywords(required(context.topic, 'topic'), context) }) },
      { stage: 'book-planner', execute: async (context) => ({ ...context, bookPlan: await this.services.bookPlanner.planBook(required(context.topic, 'topic'), required(context.keywordResearch, 'keywordResearch'), context) }) },
      { stage: 'puzzle-generator', execute: async (context) => ({ ...context, puzzleManifest: await this.services.puzzleGenerator.generatePuzzles(required(context.bookPlan, 'bookPlan'), context) }) },
      { stage: 'answer-generator', execute: async (context) => ({ ...context, answerManifest: await this.services.answerGenerator.generateAnswers(required(context.puzzleManifest, 'puzzleManifest'), context) }) },
      { stage: 'cover-generator', execute: async (context) => ({ ...context, coverManifest: await this.services.coverGenerator.generateCover(required(context.bookPlan, 'bookPlan'), context) }) },
      { stage: 'seo-generator', execute: async (context) => ({ ...context, seoMetadata: await this.services.seoGenerator.generateSeo(required(context.bookPlan, 'bookPlan'), required(context.keywordResearch, 'keywordResearch'), context) }) },
      { stage: 'pdf-builder', execute: async (context) => ({ ...context, pdfManifest: await this.services.pdfBuilder.buildPdf(context) }) },
      { stage: 'wordpress-publisher', execute: async (context) => ({ ...context, wordpressReceipt: await this.services.wordpressPublisher.publishToWordpress(context) }) },
      { stage: 'pinterest-publisher', execute: async (context) => ({ ...context, pinterestReceipt: await this.services.pinterestPublisher.publishToPinterest(context) }) },
    ];
  }
}

function required<T>(value: T | undefined, name: string): T {
  if (value === undefined) throw new Error(`Pipeline dependency missing: ${name}`);
  return value;
}
