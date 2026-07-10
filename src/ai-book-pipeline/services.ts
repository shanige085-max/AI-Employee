import type { AnswerGeneratorService, BookPlannerService, CoverGeneratorService, KeywordResearchService, PdfBuilderService, PinterestPublisherService, PuzzleGeneratorService, SeoGeneratorService, TopicSelectionService, WordpressPublisherService } from './interfaces.js';
import type { AiBookPipelineContext, AnswerManifest, BookPlan, CoverManifest, KeywordResearch, PdfManifest, PublicationReceipt, PuzzleManifest, SeoMetadata, TopicSelection } from './types.js';

export class RuleBasedTopicSelectionService implements TopicSelectionService {
  async selectTopic(context: AiBookPipelineContext): Promise<TopicSelection> {
    const normalized = context.job.request.prompt.trim();
    return { title: normalized || 'Untitled Puzzle Book', audience: normalized.toLowerCase().includes('kids') ? 'kids' : 'general', theme: normalized.toLowerCase().includes('maze') ? 'maze' : 'puzzle' };
  }
}

export class PlaceholderKeywordResearchService implements KeywordResearchService {
  async researchKeywords(topic: TopicSelection): Promise<KeywordResearch> {
    return { primaryKeyword: `${topic.audience} ${topic.theme} book`, secondaryKeywords: [`${topic.theme} activity book`, `${topic.audience} puzzles`], notes: 'Interface-only placeholder; replace with marketplace and SEO integrations.' };
  }
}

export class DefaultBookPlannerService implements BookPlannerService {
  async planBook(topic: TopicSelection, _research: KeywordResearch): Promise<BookPlan> { return { title: topic.title, subtitle: `${topic.audience} ${topic.theme} activity book`, pageCount: 120, puzzleCount: 100 }; }
}

export class PlaceholderPuzzleGeneratorService implements PuzzleGeneratorService {
  async generatePuzzles(plan: BookPlan): Promise<PuzzleManifest> { return { puzzleIds: Array.from({ length: plan.puzzleCount }, (_, index) => `puzzle-${index + 1}`), status: 'planned-only' }; }
}

export class PlaceholderAnswerGeneratorService implements AnswerGeneratorService {
  async generateAnswers(puzzles: PuzzleManifest): Promise<AnswerManifest> { return { answerIds: puzzles.puzzleIds.map((id) => `${id}-answer`), status: 'planned-only' }; }
}

export class PlaceholderCoverGeneratorService implements CoverGeneratorService {
  async generateCover(plan: BookPlan): Promise<CoverManifest> { return { title: plan.title, status: 'planned-only' }; }
}

export class PlaceholderSeoGeneratorService implements SeoGeneratorService {
  async generateSeo(plan: BookPlan, research: KeywordResearch): Promise<SeoMetadata> { return { title: plan.title, description: `${plan.title} - ${research.primaryKeyword}`, keywords: [research.primaryKeyword, ...research.secondaryKeywords] }; }
}

export class PlaceholderPdfBuilderService implements PdfBuilderService {
  async buildPdf(context: AiBookPipelineContext): Promise<PdfManifest> { return { fileName: `${context.job.id}.pdf`, status: 'planned-only' }; }
}

export class PlaceholderWordpressPublisherService implements WordpressPublisherService {
  async publishToWordpress(): Promise<PublicationReceipt> { return { platform: 'wordpress', status: 'planned-only' }; }
}

export class PlaceholderPinterestPublisherService implements PinterestPublisherService {
  async publishToPinterest(): Promise<PublicationReceipt> { return { platform: 'pinterest', status: 'planned-only' }; }
}
