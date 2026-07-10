from puzzle_ai_employee.models import Book, PublishStatus
from puzzle_ai_employee.puzzle_engine import CrosswordEngine, MazeEngine, PuzzleRequest, WordSearchEngine
from puzzle_ai_employee.task_queue import AITaskQueue, JobStatus
from puzzle_ai_employee.templates import TemplateKey, TemplateManager


def test_puzzle_engines_create_blueprints_without_generating_content():
    request = PuzzleRequest(topic="dinosaurs", difficulty="easy", age_group="kids")

    for engine in (MazeEngine(), WordSearchEngine(), CrosswordEngine()):
        blueprint = engine.create_blueprint(request)

        assert blueprint.engine_id == engine.metadata.engine_id
        assert blueprint.puzzle_type == engine.puzzle_type
        assert blueprint.steps
        assert engine.metadata.capabilities["generates_content"] is False


def test_template_manager_contains_required_templates():
    manager = TemplateManager()

    assert len(manager.list_templates()) == 6
    assert manager.get(TemplateKey.KIDS_MAZE).display_name == "Kids Maze"
    assert manager.get("adults_crossword").puzzle_type == "crossword"


def test_book_model_tracks_publish_status():
    book = Book(
        title="Animal Mazes",
        subtitle="Fun paths for kids",
        age_group="kids",
        topic="animals",
        difficulty="easy",
    )

    assert book.publish_status == PublishStatus.DRAFT
    book.mark_status(PublishStatus.READY)
    assert book.publish_status == PublishStatus.READY


def test_ai_task_queue_tracks_progress_and_recovers_errors():
    queue = AITaskQueue()
    attempts = {"count": 0}

    def flaky_task(record):
        attempts["count"] += 1
        record.progress.update(1, total=2, message="Started")
        if attempts["count"] == 1:
            raise RuntimeError("temporary failure")
        record.progress.update(2, total=2, message="Done")

    job = queue.enqueue("flaky", flaky_task)

    first = queue.run_next()
    assert first is not None
    assert first.status == JobStatus.RETRYING
    assert queue.get_job(job.job_id).error == "temporary failure"

    second = queue.run_next()
    assert second is not None
    assert second.status == JobStatus.COMPLETED
    assert second.progress.percent == 100.0
