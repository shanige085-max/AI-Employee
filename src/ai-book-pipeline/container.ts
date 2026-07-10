import { DefaultAiBookJobService } from './job-service.js';
import { DefaultTaskOrchestrator } from './orchestrator.js';
import { DefaultAiBookPipeline } from './pipeline.js';
import { ConsoleLogger, ExponentialBackoffRetryService, InMemoryAiBookJobRepository, LoggingProgressEventPublisher } from './infrastructure.js';
import { DefaultBookPlannerService, PlaceholderAnswerGeneratorService, PlaceholderCoverGeneratorService, PlaceholderKeywordResearchService, PlaceholderPdfBuilderService, PlaceholderPinterestPublisherService, PlaceholderPuzzleGeneratorService, PlaceholderSeoGeneratorService, PlaceholderWordpressPublisherService, RuleBasedTopicSelectionService } from './services.js';
import type { AiBookPipelineServices } from './pipeline.js';

export function createAiBookPipelineContainer(overrides: Partial<AiBookPipelineServices> = {}): DefaultAiBookPipeline {
  const logger = new ConsoleLogger();
  const repository = new InMemoryAiBookJobRepository();
  const jobService = overrides.jobService ?? new DefaultAiBookJobService(repository, logger);
  const retry = new ExponentialBackoffRetryService(logger);
  const events = new LoggingProgressEventPublisher(logger);
  const orchestrator = overrides.orchestrator ?? new DefaultTaskOrchestrator(jobService, retry, events, logger);

  return new DefaultAiBookPipeline({
    jobService,
    orchestrator,
    topicSelection: overrides.topicSelection ?? new RuleBasedTopicSelectionService(),
    keywordResearch: overrides.keywordResearch ?? new PlaceholderKeywordResearchService(),
    bookPlanner: overrides.bookPlanner ?? new DefaultBookPlannerService(),
    puzzleGenerator: overrides.puzzleGenerator ?? new PlaceholderPuzzleGeneratorService(),
    answerGenerator: overrides.answerGenerator ?? new PlaceholderAnswerGeneratorService(),
    coverGenerator: overrides.coverGenerator ?? new PlaceholderCoverGeneratorService(),
    seoGenerator: overrides.seoGenerator ?? new PlaceholderSeoGeneratorService(),
    pdfBuilder: overrides.pdfBuilder ?? new PlaceholderPdfBuilderService(),
    wordpressPublisher: overrides.wordpressPublisher ?? new PlaceholderWordpressPublisherService(),
    pinterestPublisher: overrides.pinterestPublisher ?? new PlaceholderPinterestPublisherService(),
  });
}
