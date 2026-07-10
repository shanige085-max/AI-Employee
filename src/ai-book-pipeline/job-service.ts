import type { AiBookJobRepository, AiBookJobService, Logger } from './interfaces.js';
import type { AiBookJob, AiBookRequest, AiBookStage } from './types.js';

export class DefaultAiBookJobService implements AiBookJobService {
  constructor(private readonly repository: AiBookJobRepository, private readonly logger: Logger) {}

  async createJob(request: AiBookRequest): Promise<AiBookJob> {
    const job = await this.repository.create(request);
    this.logger.info('Created AI book job', { jobId: job.id, prompt: request.prompt });
    return job;
  }

  async markRunning(job: AiBookJob, stage: AiBookStage): Promise<AiBookJob> {
    return this.repository.update({ ...job, status: 'running', stage, attempts: job.attempts + 1 });
  }

  async markCompleted(job: AiBookJob): Promise<AiBookJob> { return this.repository.update({ ...job, status: 'completed', stage: 'completed' }); }
  async markFailed(job: AiBookJob): Promise<AiBookJob> { return this.repository.update({ ...job, status: 'failed' }); }
}
