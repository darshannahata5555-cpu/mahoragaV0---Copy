"""
Step 0 Verification Script
Run from /backend directory: python verify_step0.py
"""
import os
import sys

# Ensure /backend is on the path so `app` and `celery_app` are importable
sys.path.insert(0, os.path.dirname(__file__))

results = []


def check(label: str, fn):
    try:
        fn()
        results.append((label, True))
        print(f"  PASS  {label}")
    except Exception as e:
        results.append((label, False))
        print(f"  FAIL  {label}")
        print(f"        {type(e).__name__}: {e}")


print("\n=== Step 0 Verification ===\n")

# 1. app.main
def _check_main():
    import app.main  # noqa: F401
check("Can import app.main", _check_main)

# 2. app.database
def _check_database():
    import app.database  # noqa: F401
check("Can import app.database", _check_database)

# 3. celery_app
def _check_celery():
    import celery_app  # noqa: F401
check("Can import celery_app", _check_celery)

# 4. app.models.job
def _check_models_job():
    import app.models.job  # noqa: F401
check("Can import app.models.job", _check_models_job)

# 5. app.schemas.job
def _check_schemas_job():
    import app.schemas.job  # noqa: F401
check("Can import app.schemas.job", _check_schemas_job)

# 6. app.api.jobs
def _check_api_jobs():
    import app.api.jobs  # noqa: F401
check("Can import app.api.jobs", _check_api_jobs)

# 7. app.workers.pipeline_worker
def _check_pipeline_worker():
    import app.workers.pipeline_worker  # noqa: F401
check("Can import app.workers.pipeline_worker", _check_pipeline_worker)

# 8. All service stubs
def _check_services():
    import app.services.subtitle_extractor  # noqa: F401
    import app.services.subtitle_parser     # noqa: F401
    import app.services.gemini_analyzer     # noqa: F401
    import app.services.job_service         # noqa: F401
check("Can import all service stubs", _check_services)

# 9. .env.example exists and contains all 8 required keys
def _check_env_example():
    env_path = os.path.join(os.path.dirname(__file__), ".env.example")
    assert os.path.exists(env_path), ".env.example not found"
    with open(env_path) as f:
        content = f.read()
    required_keys = [
        "GEMINI_API_KEY",
        "GEMINI_MODEL",
        "DATABASE_URL",
        "REDIS_URL",
        "PORT",
        "FRONTEND_URL",
        "OUTPUT_DIR",
        "APP_API_KEY",
    ]
    missing = [k for k in required_keys if k not in content]
    assert not missing, f"Missing keys in .env.example: {missing}"
check(".env.example exists and contains all 8 required keys", _check_env_example)

# 10. docker-compose.yml exists and contains both service names
def _check_docker_compose():
    dc_path = os.path.join(os.path.dirname(__file__), "..", "docker-compose.yml")
    dc_path = os.path.normpath(dc_path)
    assert os.path.exists(dc_path), f"docker-compose.yml not found at {dc_path}"
    with open(dc_path) as f:
        content = f.read()
    assert "postgres" in content, "docker-compose.yml missing 'postgres' service"
    assert "redis" in content, "docker-compose.yml missing 'redis' service"
check("docker-compose.yml has 'postgres' and 'redis' services", _check_docker_compose)

# Summary
passed = sum(1 for _, ok in results if ok)
print(f"\n{'='*35}")
print(f"  {passed}/10 checks passed.")
print(f"{'='*35}\n")

if passed < 10:
    sys.exit(1)
