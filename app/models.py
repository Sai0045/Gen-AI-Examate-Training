from dataclasses import dataclass


@dataclass
class Record:
    vaccine: str
    due_age: str
    latest_age: str
    dose: str
    route_site: str
    protects_against: str
    id: int = 0

    def to_dict(self):
        return {
            "id": self.id,
            "vaccine": self.vaccine,
            "due_age": self.due_age,
            "latest_age": self.latest_age,
            "dose": self.dose,
            "route_site": self.route_site,
            "protects_against": self.protects_against,
        }
