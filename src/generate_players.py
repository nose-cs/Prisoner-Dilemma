import random
from typing import List

from src.players import Player

names = [
    "Ana", "Carlos", "David", "Elena", "Fernando",
    "Gabriela", "Hugo", "Inés", "Javier", "Karen",
    "Luis", "María", "Natalia", "Óscar", "Paula",
    "Quintín", "Rosa", "Sergio", "Tatiana", "Ulises",
    "Valentina", "Walter", "Ximena", "Yolanda", "Zoe",
    "Adrián", "Beatriz", "Carmen", "Diego", "Eva",
    "Francisco", "Gloria", "Héctor", "Isabel", "Juan",
    "Laura", "Miguel", "Nora", "Óliver", "Patricia",
    "Ramón", "Sofía", "Tomás", "Verónica", "William",
    "Alejandro", "Bianca", "César", "Daniela", "Emilio",
    "Florencia", "Gustavo", "Helena", "Ignacio", "Julia",
    "Kevin", "Lorena", "Manuel", "Nadia", "Omar",
    "Pilar", "Raúl", "Sara", "Tobías", "Valeria",
    "Xavier", "Yasmin", "Zacarías", "Amelia", "Bruno",
    "Camila", "Dante", "Elsa", "Felipe", "Gisela",
    "Hannah", "Iván", "Jazmín", "Kai", "Luna",
    "Mariano", "Nuria", "Oriol", "Penélope", "Quirino",
    "Rocío", "Samuel", "Teresa", "Uriel", "Violeta",
    "Waldo", "Xenia", "Yago", "Zara", "Alberto",
    "Berta", "Ciro", "Diana", "Eduardo", "Flavia",
    "Gonzalo", "Hilda", "Iker", "Jacinta", "Kenia",
    "Leandro", "Mónica", "Néstor", "Olga", "Pablo"
]


def assign_names(players: List[Player]) -> List[Player]:
    available_names = names.copy()

    for i, player in enumerate(players):
        if available_names:
            name = random.choice(available_names)
            player.assign_name(name)
            available_names.remove(name)
        else:
            player.assign_name(f"Player {i}")

    return players
