class Player:
    def __init__(self) -> None:
        self.years = 0

    def sum_years(self, action: str, years: int):
        self.years += years

    def play(self, full_history: list[list], history: list) -> str:
        pass