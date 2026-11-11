class TriageError(Exception):
    pass


class InvalidInputError(TriageError):
    pass


class ModelUnavailableError(TriageError):
    pass


class LLMServiceError(TriageError):
    pass


class OutputValidationError(TriageError):
    def __init__(self, problems: list[str]):
        super().__init__("; ".join(problems))
        self.problems = problems
