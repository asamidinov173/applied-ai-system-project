from dataclasses import dataclass, field
from datetime import time


@dataclass
class Task:
    title: str
    deadline: time
    priority: int
    duration: int
    is_done: bool = False

    def execute(self):
        pass


@dataclass
class FeedingTask(Task):
    food_type: str = ""
    portion: float = 0.0

    def execute(self):
        pass


@dataclass
class WalkTask(Task):
    route: str = ""
    distance: float = 0.0

    def execute(self):
        pass


@dataclass
class MedicationTask(Task):
    drug: str = ""
    dose: float = 0.0

    def execute(self):
        pass


@dataclass
class AppointmentTask(Task):
    vet: str = ""
    location: str = ""

    def execute(self):
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task):
        pass


@dataclass
class Owner:
    name: str
    email: str
    pet: Pet = None

    def add_pet(self, pet: Pet):
        pass


class Scheduler:
    def __init__(self, tasks: list):
        self.tasks = tasks

    def sort_by_deadline(self):
        pass

    def resolve_conflict(self):
        pass

    def generate_plan(self):
        pass