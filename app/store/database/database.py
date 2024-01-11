from dataclasses import dataclass, field
from typing import List

from app.admin.models import Admin
from app.quiz.models import Question, Theme


@dataclass
class Database:
    admins: List[Admin] = field(default_factory=list)
    themes: List[Theme] = field(default_factory=list)
    questions: List[Question] = field(default_factory=list)

    @property
    def next_admin_id(self) -> int:
        return len(self.admins) + 1

    @property
    def next_theme_id(self) -> int:
        return len(self.themes) + 1

    @property
    def next_question_id(self) -> int:
        return len(self.questions) + 1

    def clear(self):
        self.admins = []
        self.themes = []
        self.questions = []
