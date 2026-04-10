from __future__ import annotations

import inspect
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def print_result(index: int, label: str, status: str) -> None:
    print(f"{index}. {label}: {status}")


def main() -> None:
    passed = 0

    # 1. pipeline_worker imports without errors
    try:
        from app.workers import pipeline_worker  # noqa: F401

        print_result(1, "pipeline_worker imports without errors", "PASS")
        passed += 1
    except Exception as exc:
        print_result(1, "pipeline_worker imports without errors", f"FAIL ({exc})")
        print(f"{passed}/10 checks passed.")
        return

    from app.workers import pipeline_worker
    from celery_app import celery_app

    # 2. run_pipeline registered task exists
    try:
        if "pipeline_worker.run_pipeline" in celery_app.tasks:
            print_result(2, "run_pipeline task is registered", "PASS")
            passed += 1
        else:
            print_result(2, "run_pipeline task is registered", "FAIL")
    except Exception as exc:
        print_result(2, "run_pipeline task is registered", f"FAIL ({exc})")

    # 3. run_pipeline signature accepts one job_id argument
    try:
        signature = inspect.signature(pipeline_worker.run_pipeline.run)
        params = list(signature.parameters.values())
        ok = len(params) == 1 and params[0].name == "job_id"
        if ok:
            print_result(3, "run_pipeline accepts single job_id arg", "PASS")
            passed += 1
        else:
            print_result(3, "run_pipeline accepts single job_id arg", f"FAIL ({signature})")
    except Exception as exc:
        print_result(3, "run_pipeline accepts single job_id arg", f"FAIL ({exc})")

    # 4. service imports present in pipeline_worker source
    try:
        source = inspect.getsource(pipeline_worker)
        required_terms = ("subtitle_extractor", "subtitle_parser", "gemini_analyzer")
        if all(term in source for term in required_terms):
            print_result(4, "pipeline_worker imports all 3 services", "PASS")
            passed += 1
        else:
            print_result(4, "pipeline_worker imports all 3 services", "FAIL")
    except Exception as exc:
        print_result(4, "pipeline_worker imports all 3 services", f"FAIL ({exc})")

    # 5. jobs.py router imports without errors
    try:
        from app.api.jobs import router

        print_result(5, "jobs.py router imports without errors", "PASS")
        passed += 1
    except Exception as exc:
        print_result(5, "jobs.py router imports without errors", f"FAIL ({exc})")
        print(f"{passed}/10 checks passed.")
        return

    # 6. router has required endpoints
    try:
        paths = {route.path for route in router.routes}
        required_paths = {"/api/jobs", "/api/jobs/{job_id}", "/api/jobs/{job_id}/transcript"}
        if required_paths.issubset(paths):
            print_result(6, "Router includes required endpoint paths", "PASS")
            passed += 1
        else:
            print_result(6, "Router includes required endpoint paths", f"FAIL ({sorted(paths)})")
    except Exception as exc:
        print_result(6, "Router includes required endpoint paths", f"FAIL ({exc})")

    # 7. POST route uses JobCreate as request body schema
    try:
        from app.schemas.job import JobCreate

        post_route = None
        for route in router.routes:
            if route.path == "/api/jobs" and "POST" in route.methods:
                post_route = route
                break
        if post_route is None:
            print_result(7, "POST route uses JobCreate body schema", "FAIL (route missing)")
        else:
            body_types = []
            for param in post_route.dependant.body_params:
                body_types.append(
                    getattr(param, "type_", None)
                    or getattr(param, "annotation", None)
                    or getattr(getattr(param, "field_info", None), "annotation", None)
                )
            if JobCreate in body_types:
                print_result(7, "POST route uses JobCreate body schema", "PASS")
                passed += 1
            else:
                print_result(7, "POST route uses JobCreate body schema", f"FAIL ({body_types})")
    except Exception as exc:
        print_result(7, "POST route uses JobCreate body schema", f"FAIL ({exc})")

    # 8. run_pipeline.delay is callable
    try:
        delay_attr = getattr(pipeline_worker.run_pipeline, "delay", None)
        if callable(delay_attr):
            print_result(8, "run_pipeline.delay is callable", "PASS")
            passed += 1
        else:
            print_result(8, "run_pipeline.delay is callable", "FAIL")
    except Exception as exc:
        print_result(8, "run_pipeline.delay is callable", f"FAIL ({exc})")

    # 9. main.py includes jobs router
    try:
        from app.main import app

        app_paths = {route.path for route in app.routes}
        if "/api/jobs" in app_paths:
            print_result(9, "main.py includes jobs router", "PASS")
            passed += 1
        else:
            print_result(9, "main.py includes jobs router", f"FAIL ({sorted(app_paths)})")
    except Exception as exc:
        print_result(9, "main.py includes jobs router", f"FAIL ({exc})")

    # 10. pipeline stages present in source
    try:
        run_src = inspect.getsource(pipeline_worker.run_pipeline.run)
        required_strings = ("extracting", "analyzing", "PARSE_ERROR", "ANALYSIS_ERROR", "finally")
        if all(token in run_src for token in required_strings):
            print_result(10, "Pipeline stage/error/finally markers present", "PASS")
            passed += 1
        else:
            print_result(10, "Pipeline stage/error/finally markers present", "FAIL")
    except Exception as exc:
        print_result(10, "Pipeline stage/error/finally markers present", f"FAIL ({exc})")

    print(f"{passed}/10 checks passed.")


if __name__ == "__main__":
    main()
