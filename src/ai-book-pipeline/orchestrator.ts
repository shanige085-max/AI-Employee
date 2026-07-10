import type { AiBookJobService, Logger, PipelineTask, ProgressEventPublisher, RetryService, TaskOrchestrator } from './interfaces.js';
import type { AiBookPipelineContext } from './types.js';

export class DefaultTaskOrchestrator implements TaskOrchestrator {
  constructor(private readonly jobService: AiBookJobService, private readonly retry: RetryService, private readonly events: ProgressEventPublisher, private readonly logger: Logger) {}

  async run(context: AiBookPipelineContext, tasks: readonly PipelineTask[]): Promise<AiBookPipelineContext> {
    let current = context;
    for (const task of tasks) {
      current = { ...current, job: await this.jobService.markRunning(current.job, task.stage as AiBookPipelineContext['job']['stage']) };
      await this.events.publish({ jobId: current.job.id, stage: task.stage, status: 'started', message: `${task.stage} started`, timestamp: new Date() });
      try {
        current = await this.retry.run(task.stage, () => task.execute(current));
        await this.events.publish({ jobId: current.job.id, stage: task.stage, status: 'completed', message: `${task.stage} completed`, timestamp: new Date() });
      } catch (error) {
        this.logger.error('AI book pipeline task failed', { jobId: current.job.id, stage: task.stage, error: String(error) });
        current = { ...current, job: await this.jobService.markFailed(current.job) };
        await this.events.publish({ jobId: current.job.id, stage: task.stage, status: 'failed', message: `${task.stage} failed`, timestamp: new Date(), data: { error: String(error) } });
        throw error;
      }
    }
    return { ...current, job: await this.jobService.markCompleted(current.job) };
  }
}
