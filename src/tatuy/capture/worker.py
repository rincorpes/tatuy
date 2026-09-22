from __future__ import annotations

from queue import Empty, Queue
from threading import Event, Thread
from time import monotonic, sleep
from typing import Callable

from PIL import Image

from tatuy.capture.models import (
    BaseJob,
    CaptureJob,
    CaptureResult,
    WorkerConfig,
)


class BaseWorker:
    """Base worker thread for capture tasks."""

    _thread: Thread
    _stop: Event
    _q: Queue[BaseJob]

    def start(self):
        """Start the capture worker thread."""
        if self._thread.is_alive():
            return
        self._stop.clear()
        self._thread.start()

    def stop(self):
        """Stop the capture worker thread."""
        self._stop.set()
        if self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def enqueue(self, job: BaseJob) -> bool:
        """
        Enqueue a capture job.
        """
        if self._stop.is_set():
            return False
        try:
            self._q.put_nowait(job)
            return True
        # Justification: Queue.put_nowait can raise a broad exception
        # pylint: disable=broad-exception-caught
        except Exception:
            return False
        # pylint: enable=broad-exception-caught

    def qsize(self) -> int:
        """Query the current size of the job queue."""
        return self._q.qsize()

    def wait_until_idle(self, timeout_seconds: float | None = None) -> bool:
        """
        Block until the worker queue has finished processing all queued jobs.
        """
        deadline = (
            None
            if timeout_seconds is None
            else monotonic() + max(0.0, float(timeout_seconds))
        )
        while True:
            if getattr(self._q, "unfinished_tasks", 0) <= 0:
                return True
            if deadline is not None and monotonic() >= deadline:
                return False
            sleep(0.01)

    def _run(self):
        while not self._stop.is_set():
            try:
                job = self._q.get(timeout=0.1)
                self._process_job(job)
            except Empty:
                continue

    def _process_job(self, job: BaseJob):
        """Process a single job. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _process_job()")


class CaptureWorker(BaseWorker):
    """Capture worker thread for saving screenshots asynchronously."""

    def __init__(
        self,
        worker_config: WorkerConfig | None = None,
    ):
        if worker_config is None:
            worker_config = WorkerConfig()
        self._q: Queue[CaptureJob] = Queue(maxsize=worker_config.queue_size)
        self._stop = Event()
        self._thread = Thread(
            target=self._run,
            name=worker_config.name,
            daemon=worker_config.daemon,
        )
        self._on_done = worker_config.on_done
        self._delete_temp = worker_config.delete_temp

    def set_on_done(
        self, on_done: Callable[[CaptureResult], None] | None
    ) -> None:
        """
        Replace the completion callback invoked after each processed job.
        """
        self._on_done = on_done

    def _process_job(self, job: CaptureJob) -> None:
        temporary = job.out_path.with_name(job.out_path.name + ".tmp")

        try:
            job.out_path.parent.mkdir(parents=True, exist_ok=True)

            if job.bmp_path is not None:
                with Image.open(job.bmp_path) as source:
                    image = source.convert("RGBA")
            else:
                if job.pixels is None:
                    raise ValueError("Capture job has no pixels")

                image = Image.frombytes(
                    "RGBA",
                    (job.w, job.h),
                    job.pixels,
                    "raw",
                    job.fmt,
                    job.pitch or 0,
                    1,
                )

            with image:
                if (
                    job.target_size is not None
                    and image.size != job.target_size
                ):
                    with image.resize(job.target_size) as resized:
                        resized.save(temporary, format="PNG")
                else:
                    image.save(temporary, format="PNG")

            # A final filename appears only after the PNG is complete.
            temporary.replace(job.out_path)

            result = CaptureResult(
                job_id=job.job_id,
                out_path=job.out_path,
                ok=True,
            )

        except Exception as exc:
            result = CaptureResult(
                job_id=job.job_id,
                out_path=job.out_path,
                ok=False,
                error=str(exc),
            )

        finally:
            try:
                temporary.unlink(missing_ok=True)

                if self._delete_temp and job.bmp_path is not None:
                    job.bmp_path.unlink(missing_ok=True)
            except OSError:
                pass

        try:
            if self._on_done is not None:
                self._on_done(result)
        except Exception as exc:
            print(f"Capture callback failed: {exc}")
        finally:
            self._q.task_done()
