import time
import logging
import uuid
from fastapi import Request

logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)


async def add_process_time_header(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start_time = time.time()
    logging.info(
        f"Request {request_id} started",
    )
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logging.info(
            f"Request {request_id} completed with code {response.status_code}: time {process_time}",
        )
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as e:
        logging.error(
            f"Request {request_id} failed: {e}",
        )
        raise e
    finally:
        process_time = time.time() - start_time
        logging.info(
            f"Request {request_id} completed: time {process_time}",
        )
