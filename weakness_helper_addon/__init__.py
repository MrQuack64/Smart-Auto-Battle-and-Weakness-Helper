import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

from aqt import mw
from aqt.utils import showWarning
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)


ADDON_DIR = Path(__file__).parent
NAME_CACHE = ADDON_DIR / "pokemon_names_cache.json"
POKEMON_LIST_URL = "https://pokeapi.co/api/v2/pokemon?limit=2000"
POKEMON_URL = "https://pokeapi.co/api/v2/pokemon/{name}"

TYPE_CHART = {
    "normal": {"weak": ["fighting"], "resist": [], "immune": ["ghost"]},
    "fire": {"weak": ["water", "ground", "rock"], "resist": ["fire", "grass", "ice", "bug", "steel", "fairy"], "immune": []},
    "water": {"weak": ["electric", "grass"], "resist": ["fire", "water", "ice", "steel"], "immune": []},
    "electric": {"weak": ["ground"], "resist": ["electric", "flying", "steel"], "immune": []},
    "grass": {"weak": ["fire", "ice", "poison", "flying", "bug"], "resist": ["water", "electric", "grass", "ground"], "immune": []},
    "ice": {"weak": ["fire", "fighting", "rock", "steel"], "resist": ["ice"], "immune": []},
    "fighting": {"weak": ["flying", "psychic", "fairy"], "resist": ["bug", "rock", "dark"], "immune": []},
    "poison": {"weak": ["ground", "psychic"], "resist": ["grass", "fighting", "poison", "bug", "fairy"], "immune": []},
    "ground": {"weak": ["water", "grass", "ice"], "resist": ["poison", "rock"], "immune": ["electric"]},
    "flying": {"weak": ["electric", "ice", "rock"], "resist": ["grass", "fighting", "bug"], "immune": ["ground"]},
    "psychic": {"weak": ["bug", "ghost", "dark"], "resist": ["fighting", "psychic"], "immune": []},
    "bug": {"weak": ["fire", "flying", "rock"], "resist": ["grass", "fighting", "ground"], "immune": []},
    "rock": {"weak": ["water", "grass", "fighting", "ground", "steel"], "resist": ["normal", "fire", "poison", "flying"], "immune": []},
    "ghost": {"weak": ["ghost", "dark"], "resist": ["poison", "bug"], "immune": ["normal", "fighting"]},
    "dragon": {"weak": ["ice", "dragon", "fairy"], "resist": ["fire", "water", "electric", "grass"], "immune": []},
    "dark": {"weak": ["fighting", "bug", "fairy"], "resist": ["ghost", "dark"], "immune": ["psychic"]},
    "steel": {"weak": ["fire", "fighting", "ground"], "resist": ["normal", "grass", "ice", "flying", "psychic", "bug", "rock", "dragon", "steel", "fairy"], "immune": ["poison"]},
    "fairy": {"weak": ["poison", "steel"], "resist": ["fighting", "bug", "dark"], "immune": ["dragon"]},
}


def title_case(name):
    return " ".join(part.capitalize() for part in name.replace("-", " ").split())


def fetch_json(url):
    request = Request(url, headers={"User-Agent": "AnkimonWeaknessHelper/0.2"})
    with urlopen(request, timeout=8) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_pokemon_names():
    payload = fetch_json(POKEMON_LIST_URL)
    names = sorted(entry["name"] for entry in payload.get("results", []) if "name" in entry)
    if names:
        with NAME_CACHE.open("w", encoding="utf-8") as handle:
            json.dump(names, handle)
    return names


def fetch_pokemon(name):
    clean_name = name.strip().lower().replace(" ", "-")
    payload = fetch_json(POKEMON_URL.format(name=quote(clean_name)))
    types = [
        item["type"]["name"]
        for item in sorted(payload["types"], key=lambda entry: entry["slot"])
    ]
    return payload["name"], types


def calculate_weaknesses(defender_types):
    multipliers = {type_name: 1 for type_name in TYPE_CHART}
    for defender_type in defender_types:
        chart = TYPE_CHART[defender_type]
        for attack_type in chart["weak"]:
            multipliers[attack_type] *= 2
        for attack_type in chart["resist"]:
            multipliers[attack_type] *= 0.5
        for attack_type in chart["immune"]:
            multipliers[attack_type] = 0

    return sorted(
        ((type_name, value) for type_name, value in multipliers.items() if value > 1),
        key=lambda item: (-item[1], item[0]),
    )


class WeaknessDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ankimon Weakness")
        self.setFixedWidth(360)
        self.names = self.load_cached_names()

        root = QVBoxLayout(self)
        root.setSpacing(6)

        row = QHBoxLayout()
        row.addWidget(QLabel("Name:"))
        self.input = QLineEdit()
        self.input.setPlaceholderText("charizard")
        self.input.textChanged.connect(self.update_suggestions)
        self.input.returnPressed.connect(self.lookup_current_text)
        row.addWidget(self.input, 1)
        root.addLayout(row)

        self.suggestions = QListWidget()
        self.suggestions.setMaximumHeight(92)
        self.suggestions.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.suggestions.itemClicked.connect(self.lookup_item)
        root.addWidget(self.suggestions)

        self.button = QPushButton("Find weakness")
        self.button.clicked.connect(self.lookup_current_text)
        root.addWidget(self.button)

        self.result = QLabel("Weakness: type 3+ letters or a full Pokemon name")
        self.result.setWordWrap(True)
        self.result.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        root.addWidget(self.result)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        self.status.setStyleSheet("color: #6b7280; font-size: 11px;")
        root.addWidget(self.status)

        if not self.names:
            self.load_names_in_background()

    def load_cached_names(self):
        if not NAME_CACHE.exists():
            return []
        try:
            with NAME_CACHE.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, list):
                return sorted(str(name) for name in data)
        except Exception:
            return []
        return []

    def load_names_in_background(self):
        self.status.setText("Loading suggestions...")

        def on_done(future):
            try:
                self.names = future.result()
                self.status.setText("Suggestions ready.")
                self.update_suggestions()
            except Exception:
                self.status.setText("Suggestions failed. Full-name search still works.")

        mw.taskman.run_in_background(fetch_pokemon_names, on_done)

    def update_suggestions(self):
        query = self.input.text().strip().lower()
        self.suggestions.clear()
        if len(query) < 3:
            return

        matches = [name for name in self.names if query in name.replace("-", " ")]
        for name in matches[:12]:
            item = QListWidgetItem(title_case(name))
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.suggestions.addItem(item)

    def lookup_item(self, item):
        name = item.data(Qt.ItemDataRole.UserRole)
        self.input.setText(title_case(name))
        self.lookup_pokemon(name)

    def lookup_current_text(self):
        name = self.input.text().strip()
        if not name:
            return
        self.lookup_pokemon(name)

    def lookup_pokemon(self, name):
        self.button.setEnabled(False)
        self.result.setText("Weakness: checking...")
        self.status.setText("")

        def task():
            return fetch_pokemon(name)

        def on_done(future):
            self.button.setEnabled(True)
            try:
                pokemon_name, types = future.result()
                self.render_result(pokemon_name, types)
            except Exception:
                self.result.setText("Weakness: not found")
                self.status.setText("Try clicking a suggestion after typing 3+ letters.")

        mw.taskman.run_in_background(task, on_done)

    def render_result(self, pokemon_name, types):
        weaknesses = calculate_weaknesses(types)
        type_text = "/".join(title_case(type_name) for type_name in types)
        if weaknesses:
            weak_text = ", ".join(
                f"{title_case(type_name)} {int(multiplier)}x"
                for type_name, multiplier in weaknesses
            )
        else:
            weak_text = "No super-effective weaknesses"
        self.result.setText(f"{title_case(pokemon_name)} ({type_text})\nWeakness: {weak_text}")


_dialog = None


def open_weakness_helper():
    global _dialog
    if mw is None:
        showWarning("Anki main window is not ready yet.")
        return
    if _dialog is None:
        _dialog = WeaknessDialog(mw)
    _dialog.show()
    _dialog.raise_()
    _dialog.activateWindow()
    _dialog.input.setFocus()


action = QAction("Ankimon Weakness Helper", mw)
action.triggered.connect(open_weakness_helper)
mw.form.menuTools.addAction(action)
