from dataclasses import dataclass
from enum import Enum
from collections.abc import Callable
from threading import Lock
from uuid import uuid4


class ProgressState(Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


@dataclass
class JobProgress:
    state: ProgressState
    value: int


class Progress:
    def __init__(self) -> None:
        self.progress_map: dict[str, JobProgress] = {}
        self.lock = Lock()
        self.progress_value = 0
        self.job_id = str(uuid4())

    def add_job(self) -> str:
        """
        Add a new job with a unique job id.

        Args: None

        Returns: str(job_id)
        """
        with self.lock:
            job_id = str(uuid4())
            self.progress_map[job_id] = JobProgress(state=ProgressState.PENDING, value=self.progress_value)
        return job_id

    def start_job(self, job_id: str) -> None:
        self.progress_map[job_id] = JobProgress(
            state=ProgressState.PENDING, value=self.progress_value
        )

    def remove_job(self, job_id: str) -> None:
        self.progress_map.pop(job_id, None)

    def get_progress(self, job_id: str) -> tuple[int, str] | None:
        job_progress = self.progress_map.get(job_id)
        if job_progress:
            return job_progress.value, job_progress.state.value
        else:
            return None

    def __call__(self, job_id: str, value: int, state: ProgressState) -> None:
        with self.lock:
            if job_id in self.progress_map:
                self.progress_map[job_id].state = state
                self.progress_map[job_id].value = value
            else:
                self.progress_map[job_id] = JobProgress(state=state, value=value)
        

progress_instance = Progress()
