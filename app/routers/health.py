import time

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check(timeout: float = 0.0):
    """
    Health check endpoint to verify the API is running.
    Prints a message every second during the wait period.
    """
    try:
        start_time = time.time()
        end_time = start_time + timeout

        while time.time() < end_time:
            elapsed = time.time() - start_time
            print(f"Health check running... {elapsed:.1f}s elapsed")

            remaining = min(1.0, end_time - time.time())
            if remaining > 0:
                time.sleep(remaining)

        total_elapsed = time.time() - start_time
        print(f"Health check complete. Total time: {total_elapsed:.2f}s")

        return {"status": "ok", "elapsed_time": total_elapsed}
    except Exception as e:
        print(f"Error during health check: {str(e)}")
        return {"status": "error", "message": str(e)}
