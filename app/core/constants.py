"""Project-wide constants for PuzzleAI Employee."""

APP_NAME = "PuzzleAI Employee"
API_V1_PREFIX = "/api/v1"
DEFAULT_DATABASE_URL = "sqlite:///./puzzleai_employee.db"
DEFAULT_LOG_LEVEL = "INFO"
HEALTH_STATUS_OK = "ok"
SETTINGS_SAFE_FIELDS = (
    "app_name",
    "environment",
    "debug",
    "api_v1_prefix",
    "database_echo",
    "log_level",
    "background_jobs_enabled",
)
