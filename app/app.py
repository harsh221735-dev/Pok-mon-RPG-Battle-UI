import reflex as rx
from app.components.game import selection_page, battle_page
from app.states.game_state import GameState


# Root page layout: show the illustrated fighter selection and API connection controls.
def index() -> rx.Component:
    return selection_page()


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(
            rel="preconnect",
            href="https://fonts.gstatic.com",
            cross_origin="",
        ),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&family=Nunito+Sans:wght@400;600;700;800&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(
    index,
    route="/",
    title="Wild / Clash — Choose your fighter",
    on_load=GameState.clear_match,
)
app.add_page(
    battle_page,
    route="/battle",
    title="Wild / Clash — Battle arena",
    on_load=GameState.load_battle,
)
