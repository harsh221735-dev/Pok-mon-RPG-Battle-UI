import reflex as rx
import asyncio
import json
import logging
import math
import secrets
import time
from app.states.game_api import (
    FIGHTERS,
    base_url,
    post_json,
    document,
    normalize,
    record,
    health,
    merge_record,
    fighter_view,
)


# Match state: shared across both pages, with canonical JSON strings for lossless records.
class GameState(rx.State):
    backend_url: str = ""
    selected_id: int = 0
    opponent_id: int = 2
    room_input: str = ""
    room_code: str = ""
    command: str = ""
    error: str = ""
    joining: bool = False
    sending: bool = False
    connected: bool = False
    active: bool = False
    player_data: str = "{}"
    opponent_data: str = "{}"
    last_result: str = ""
    logs: list[str] = []
    remaining: int = 100
    turn_remaining: int = 7
    outcome: str = ""
    initial_player_hp: float = 0.0
    initial_opponent_hp: float = 0.0
    _generation: int = 0
    _timer_generation: int = -1
    _deadline: float = 0.0
    _turn_deadline: float = 0.0

    # Room controls: require a fighter and a syntactically valid backend URL.
    @rx.var
    def ready(self) -> bool:
        try:
            base_url(self.backend_url)
            return self.selected_id in (1, 2, 3, 4) and not self.joining
        except ValueError:
            return False

    @rx.var
    def selected_name(self) -> str:
        return (
            FIGHTERS[self.selected_id - 1]["name"]
            if self.selected_id
            else "Choose your fighter"
        )

    @rx.var
    def player_view(self) -> dict[str, str]:
        return fighter_view(
            self.player_data, self.selected_id or 1, self.initial_player_hp
        )

    @rx.var
    def opponent_view(self) -> dict[str, str]:
        return fighter_view(
            self.opponent_data, self.opponent_id, self.initial_opponent_hp
        )

    # Backend URL field: keep the user's public service URL between matches.
    @rx.event
    def update_url(self, value: str):
        self.backend_url = value.strip().rstrip("/")
        self.error = ""

    @rx.event
    def select_fighter(self, fighter_id: int):
        if not self.joining:
            self.selected_id = fighter_id
            self.error = ""

    @rx.event
    def update_room(self, value: str):
        self.room_input = value.strip().upper()

    @rx.event
    def update_command(self, value: str):
        self.command = value

    # Room controls: generate or accept a local label before the real character request.
    @rx.event
    def start_room(self, generate: bool):
        if self.joining:
            return
        try:
            self.backend_url = base_url(self.backend_url)
        except ValueError as e:
            self.error = str(e)
            return
        if not self.selected_id:
            self.error = "Choose a fighter first."
            return
        if not generate and not self.room_input.strip():
            self.error = "Enter a room code first."
            return
        self.room_code = (
            f"WILD-{secrets.token_hex(2).upper()}"
            if generate
            else self.room_input.strip()
        )
        self.opponent_id = self.selected_id % 4 + 1
        self.joining = True
        self.error = ""
        self._generation += 1
        return GameState.connect_room

    # API helper integration: network I/O runs outside the state lock.
    @rx.event(background=True)
    async def connect_room(self):
        async with self:
            generation = self._generation
            url, selected, opponent = (
                self.backend_url,
                self.selected_id,
                self.opponent_id,
            )
        try:
            data = await asyncio.to_thread(
                post_json,
                url,
                "/charachter",
                {"id": selected, "opponent_id": opponent},
            )
            if (
                data.get("status") != "success"
                or "player" not in data
                or "opponent" not in data
            ):
                raise ValueError(
                    "Unexpected response: expected success with player and opponent records."
                )
            player, enemy = record(data["player"]), record(data["opponent"])
            if player["id"] != selected or enemy["id"] == selected:
                raise ValueError(
                    "The backend returned mismatched or duplicate fighter IDs."
                )
            player_json, enemy_json = document(player), document(enemy)
        except Exception as e:
            logging.exception(f"Error: {e}")
            async with self:
                if generation == self._generation:
                    self.error = (
                        str(e)
                        if isinstance(e, ValueError)
                        else "Unable to prepare the match. Please retry."
                    )
                    self.joining = False
            return
        async with self:
            if generation != self._generation:
                return
            self.player_data, self.opponent_data = player_json, enemy_json
            self.initial_player_hp = health(player) or 0.0
            self.initial_opponent_hp = health(enemy) or 0.0
            self.connected = True
            self.joining = False
            self.active = True
            self.outcome = ""
            self.command = ""
            self.last_result = ""
            self.logs = ["Connected to FastAPI. Fighters ready."]
            self.remaining, self.turn_remaining = 100, 7
            self._deadline = time.monotonic() + 100
            self._turn_deadline = time.monotonic() + 7
            self._check_health()
        yield rx.redirect("/battle")

    # Timers: a generation token prevents old requests or loops affecting a new match.
    @rx.event
    def load_battle(self):
        if not self.connected:
            return rx.redirect("/")
        if self.active:
            return GameState.tick

    @rx.event(background=True)
    async def tick(self):
        async with self:
            generation = self._generation
            if self._timer_generation == generation or not self.active:
                return
            self._timer_generation = generation
        while True:
            await asyncio.sleep(0.2)
            async with self:
                if generation != self._generation or not self.active:
                    return
                now = time.monotonic()
                self.remaining = max(0, math.ceil(self._deadline - now))
                self.turn_remaining = max(
                    0, math.ceil(self._turn_deadline - now)
                )
                if not self.remaining:
                    self.active = False
                    self.outcome = (
                        "Time’s up! No winner was declared by the backend."
                    )
                    self.logs = [*self.logs, "Match clock expired."][-50:]
                    return
                if not self.turn_remaining:
                    self.logs = [
                        *self.logs,
                        "Turn timed out — no attack was sent. A new 7-second window begins.",
                    ][-50:]
                    self._turn_deadline = now + 7
                    self.turn_remaining = 7

    # Outcome detection: only recognized health values can establish a knockout.
    def _check_health(self):
        player_hp = health(json.loads(self.player_data))
        enemy_hp = health(json.loads(self.opponent_data))
        player_out = player_hp is not None and player_hp <= 0
        enemy_out = enemy_hp is not None and enemy_hp <= 0
        if player_out or enemy_out:
            self.active = False
            self.outcome = (
                "Double knockout!"
                if player_out and enemy_out
                else (
                    "Victory! Opponent HP reached zero."
                    if enemy_out
                    else "Defeated — your fighter’s HP reached zero."
                )
            )

    # Attack composer: preserve the command on failure and prevent duplicate submissions.
    @rx.event
    def send_attack(self):
        if self.sending or not self.active:
            return
        if not self.command.strip():
            self.error = "Describe an attack before sending."
            return
        self.sending = True
        self.error = ""
        return GameState.request_attack

    @rx.event(background=True)
    async def request_attack(self):
        async with self:
            generation = self._generation
            url, command = self.backend_url, self.command.strip()
            player, enemy = self.player_data, self.opponent_data
        try:
            data = await asyncio.to_thread(
                post_json,
                url,
                "/give_attack",
                {"attack": command, "attacker": player, "opponent_str": enemy},
            )
            if "result" not in data:
                raise ValueError(
                    "Unexpected response: the result field is missing."
                )
            result = normalize(data["result"])
            if not isinstance(result, (dict, list)):
                raise ValueError(
                    "Unexpected result: expected a JSON object or list of changes."
                )
            formatted = document(result)
            p, o = json.loads(player), json.loads(enemy)
            if isinstance(result, dict):
                if isinstance(result.get("player"), dict):
                    p = merge_record(p, result["player"])
                if isinstance(result.get("opponent"), dict):
                    o = merge_record(o, result["opponent"])
            updated_player, updated_enemy = document(p), document(o)
        except Exception as e:
            logging.exception(f"Error: {e}")
            async with self:
                if generation == self._generation:
                    self.error = (
                        str(e)
                        if isinstance(e, ValueError)
                        else "Attack failed. Your command is saved; please retry."
                    )
                    self.sending = False
            return
        async with self:
            if generation != self._generation:
                return
            self.sending = False
            self.last_result = formatted
            self.logs = [*self.logs, f"YOU → {command}", f"API → {formatted}"][
                -50:
            ]
            if not self.active or time.monotonic() >= self._deadline:
                self.logs = [
                    *self.logs,
                    "Response arrived after match end; recorded without changing the finished match.",
                ][-50:]
                return
            self.player_data, self.opponent_data = updated_player, updated_enemy
            self.command = ""
            self.turn_remaining = 7
            self._turn_deadline = time.monotonic() + 7
            self._check_health()

    # Leaving invalidates in-flight work while retaining the backend URL and selection.
    @rx.event
    def clear_match(self):
        self._generation += 1
        self.active = False
        self.connected = False
        self.joining = False
        self.sending = False
        self.room_code = ""
        self.player_data = "{}"
        self.opponent_data = "{}"
        self.last_result = ""
        self.logs = []
        self.command = ""
        self.error = ""
        self.outcome = ""

    @rx.event
    def leave_room(self):
        self.clear_match()
        return rx.redirect("/")
