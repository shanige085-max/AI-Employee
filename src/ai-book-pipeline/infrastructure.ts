import type { AiBookJobRepository, Logger, ProgressEvent, ProgressEventPublisher, RetryPolicy, RetryService } from './interfaces.js';
import type { AiBookJob, AiBookRequest } from './types.js';

export class ConsoleLogger implements Logger {
  info(message: string, data?: Record<string, unknown>): void { console.info(message, data ?? {}); }
  warn(message: string, data?: Record<string, unknown>): void { console.warn(message, data ?? {}); }
  error(message: string, data?: Record<string, unknown>): void { console.error(message, data ?? {}); }
}

export class InMemoryAiBookJobRepository implements AiBookJobRepository {
  private readonly jobs = new Map<string, AiBookJob>();

  async create(request: AiBookRequest): Promise<AiBookJob> {
    const now = new Date();
    const job: AiBookJob = { id: crypto.randomUUID(), request, status: 'queued', stage: 'request', attempts: 0, createdAt: now, updatedAt: now };
    this.jobs.set(job.id, job);
    return job;
  }

  async update(job: AiBookJob): Promise<AiBookJob> {
    const updated = { ...job, updatedAt: new Date() };
    this.jobs.set(updated.id, updated);
    return updated;
  }

  async findById(jobId: string): Promise<AiBookJob | undefined> { return this.jobs.get(jobId); }
}

export class LoggingProgressEventPublisher implements ProgressEventPublisher {
  constructor(private readonly logger: Logger) {}
  async publish(event: ProgressEvent): Promise<void> {
    this.logger.info('AI book pipeline progress', { ...event, timestamp: event.timestamp.toISOString() });
  }
}

export class ExponentialBackoffRetryService implements RetryService {
  private readonly defaults: RetryPolicy = { maxAttempts: 3, baseDelayMs: 250, backoffMultiplier: 2 };
  constructor(private readonly logger: Logger) {}

  async run<T>(operationName: string, operation: () => Promise<T>, policy?: Partial<RetryPolicy>): Promise<T> {
    const retryPolicy = { ...this.defaults, ...policy };
    let lastError: unknown;
    for (let attempt = 1; attempt <= retryPolicy.maxAttempts; attempt += 1) {
      try {
        return await operation();
      } catch (error) {
        lastError = error;
        this.logger.warn('Retryable pipeline operation failed', { operationName, attempt, maxAttempts: retryPolicy.maxAttempts, error: String(error) });
        if (attempt < retryPolicy.maxAttempts) {
          await this.sleep(retryPolicy.baseDelayMs * retryPolicy.backoffMultiplier ** (attempt - 1));
        }
      }
    }
    throw lastError;
  }

  private async sleep(delayMs: number): Promise<void> { await new Promise((resolve) => setTimeout(resolve, delayMs)); }
}
