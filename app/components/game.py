import reflex as rx
from app.states.game_state import GameState
from app.states.game_api import FIGHTERS

BUTTON = "inline-flex items-center justify-center gap-2 rounded-xl border-2 border-[#202d40] bg-[#f56b58] px-5 py-3 font-extrabold text-[#202d40] shadow-[3px_3px_0_#202d40] hover:bg-[#ff806d] active:translate-y-0.5 active:shadow-none focus-visible:outline-4 focus-visible:outline-offset-4 focus-visible:outline-[#158b87] disabled:opacity-40 disabled:cursor-not-allowed motion-safe:transition-all"
INPUT = "w-full rounded-xl border-2 border-[#202d40]/30 bg-white px-4 py-3 text-[#202d40] placeholder:text-[#69717e] focus:border-[#158b87] focus:outline-2 focus:outline-[#158b87] disabled:opacity-60"
DISPLAY = "font-['Baloo_2'] font-extrabold"


# Page header: a lightweight, original handheld-game identity.
def header() -> rx.Component:
    return rx.el.header(
        rx.el.div(
            rx.el.div(
                rx.icon("swords", class_name="h-6 w-6"),
                class_name="rounded-xl border-2 border-[#202d40] bg-[#f7ce4d] p-2 -rotate-6",
            ),
            rx.el.span(
                "WILD",
                class_name="font-['Baloo_2'] text-3xl font-extrabold tracking-tight",
            ),
            rx.el.span(
                "/ CLASH",
                class_name="font-['Baloo_2'] text-3xl font-extrabold text-[#e36150]",
            ),
            class_name="flex items-center gap-2",
        ),
        rx.el.div(
            rx.icon("sparkles", class_name="h-4 w-4 text-[#168b83]"),
            "SMALL FIGHTERS. BIG ENERGY.",
            class_name="hidden sm:flex items-center gap-2 text-xs font-extrabold tracking-widest",
        ),
        class_name="flex items-center justify-between border-b-2 border-[#202d40]/15 py-5 mb-8",
    )


# Character cards: native buttons provide keyboard selection and visible focus.
def character_card(fighter: dict[str, str | int]) -> rx.Component:
    return rx.el.button(
        rx.el.div(
            rx.el.span(
                fighter["label"].to(str),
                class_name="text-[10px] font-extrabold tracking-[0.16em]",
            ),
            rx.cond(
                GameState.selected_id == fighter["id"].to(int),
                rx.el.span(
                    rx.icon("check", class_name="h-4 w-4"),
                    class_name="rounded-full bg-[#202d40] text-white p-1",
                ),
                rx.el.span(
                    class_name="w-6 h-6 rounded-full border-2 border-[#202d40]/25"
                ),
            ),
            class_name="flex items-center justify-between px-5 pt-4",
        ),
        rx.el.img(
            src=fighter["image"].to(str),
            alt=fighter["name"].to(str),
            class_name="w-full h-52 lg:h-60 object-contain p-3 group-hover:scale-105 motion-safe:transition-transform",
        ),
        rx.el.div(
            rx.el.span(
                fighter["element"].to(str),
                class_name="text-[10px] tracking-widest font-extrabold text-[#445263]",
            ),
            rx.el.h2(
                fighter["name"].to(str),
                class_name="font-['Baloo_2'] text-4xl leading-tight font-extrabold",
            ),
            rx.el.p(
                fighter["tag"].to(str), class_name="text-xs mt-1 text-[#546071]"
            ),
            class_name="px-5 pb-5 text-left",
        ),
        on_click=GameState.select_fighter(fighter["id"].to(int)),
        disabled=GameState.joining,
        aria_pressed=GameState.selected_id == fighter["id"].to(int),
        class_name=rx.cond(
            GameState.selected_id == fighter["id"].to(int),
            "group w-full rounded-2xl border-[3px] border-[#202d40] bg-[#ffe89b] text-[#202d40] shadow-[5px_5px_0_#202d40] -translate-y-1 focus-visible:outline-4 focus-visible:outline-[#158b87] active:translate-y-0 motion-safe:transition-all",
            "group w-full rounded-2xl border-2 border-[#202d40]/25 bg-[#fffdf5] text-[#202d40] hover:border-[#202d40] hover:-translate-y-1 focus-visible:outline-4 focus-visible:outline-[#158b87] active:translate-y-0 motion-safe:transition-all",
        ),
    )


# Backend URL field: the deployed service address is public configuration, not a secret.
def backend_field() -> rx.Component:
    return rx.el.div(
        rx.el.label(
            rx.icon("plug", class_name="h-4 w-4"),
            "BACKEND BASE URL",
            html_for="backend-url",
            class_name="flex items-center gap-2 text-xs font-extrabold tracking-wider mb-2",
        ),
        rx.el.input(
            id="backend-url",
            placeholder="https://api.yourgame.com",
            default_value=GameState.backend_url,
            on_change=GameState.update_url.debounce(500),
            disabled=GameState.joining,
            class_name=INPUT,
        ),
        rx.el.p(
            "Use the public HTTPS URL of your deployed FastAPI service.",
            class_name="text-xs text-[#617080] mt-2",
        ),
        class_name="w-full",
    )


# API feedback: errors stay inline, readable, and announced to assistive technology.
def error_message() -> rx.Component:
    return rx.cond(
        GameState.error != "",
        rx.el.div(
            rx.icon("circle-alert", class_name="h-5 w-5 shrink-0"),
            GameState.error,
            role="alert",
            class_name="flex items-center gap-3 rounded-xl border border-red-300 bg-red-100 text-red-800 p-4 mt-4 text-sm",
        ),
        rx.fragment(),
    )


# Room controls: local room labels never pretend to implement backend matchmaking.
def room_controls() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.div(
                rx.icon("radio-tower", class_name="h-5 w-5"),
                rx.el.h2(
                    "Next stop: the arena.",
                    class_name="font-['Baloo_2'] text-2xl font-extrabold",
                ),
                class_name="flex items-center gap-3",
            ),
            rx.el.span(
                "02 / CONNECT & PLAY",
                class_name="text-[10px] tracking-widest font-extrabold",
            ),
            class_name="flex flex-wrap items-center justify-between gap-2 mb-5",
        ),
        rx.el.div(
            backend_field(),
            rx.el.div(
                rx.el.p(
                    "YOUR FIGHTER",
                    class_name="text-[10px] font-extrabold tracking-widest text-[#617080]",
                ),
                rx.el.p(
                    GameState.selected_name,
                    class_name="font-['Baloo_2'] text-2xl font-extrabold",
                ),
                rx.el.button(
                    rx.cond(
                        GameState.joining,
                        rx.icon(
                            "loader-circle",
                            class_name="h-4 w-4 motion-safe:animate-spin",
                        ),
                        rx.icon("plus", class_name="h-4 w-4"),
                    ),
                    rx.cond(GameState.joining, "Connecting…", "Generate Room"),
                    on_click=GameState.start_room(True),
                    disabled=~GameState.ready,
                    class_name=BUTTON,
                ),
                class_name="flex flex-col gap-1",
            ),
            rx.el.div(
                "OR",
                class_name="self-center text-xs font-extrabold text-[#7b817f]",
            ),
            rx.el.div(
                rx.el.label(
                    "HAVE A ROOM CODE?",
                    html_for="room-code",
                    class_name="text-[10px] font-extrabold tracking-widest",
                ),
                rx.el.input(
                    id="room-code",
                    placeholder="WILD-XXXX",
                    default_value=GameState.room_input,
                    on_change=GameState.update_room.debounce(300),
                    disabled=GameState.joining,
                    max_length=40,
                    class_name=INPUT,
                ),
                rx.el.button(
                    "Enter Room",
                    rx.icon("arrow-right", class_name="h-4 w-4"),
                    on_click=GameState.start_room(False),
                    disabled=(~GameState.ready) | (GameState.room_input == ""),
                    class_name="flex items-center justify-center gap-2 font-extrabold text-sm py-2 hover:text-[#d44b39] disabled:opacity-40 focus-visible:outline-2 focus-visible:outline-[#158b87]",
                ),
                class_name="flex flex-col gap-2",
            ),
            class_name="grid grid-cols-1 md:grid-cols-[1.6fr_1fr_auto_1fr] gap-6 items-center",
        ),
        error_message(),
        rx.el.p(
            "Room codes label this session locally. The API pairs your fighter with an alternate opponent; it does not synchronize players by code.",
            class_name="text-xs text-[#617080] mt-5",
        ),
        class_name="mt-9 rounded-2xl border-2 border-[#202d40] bg-[#fffdf6] p-6 shadow-[5px_5px_0_#202d40]",
    )


# Selection page layout: four illustrated fighters lead into the connection controls.
def selection_page() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            header(),
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        "01 / PICK YOUR PARTNER",
                        class_name="text-xs font-extrabold tracking-[0.2em] text-[#168b83]",
                    ),
                    rx.el.h1(
                        "Tiny legends. Mighty battles.",
                        class_name="font-['Baloo_2'] text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight mt-2",
                    ),
                    rx.el.p(
                        "Pick a fighter, trust your imagination, and make your next move count.",
                        class_name="text-[#617080] mt-2 text-base",
                    ),
                ),
                rx.el.div(
                    rx.icon("zap", class_name="w-6 h-6"),
                    "YOUR WORDS.\nYOUR MOVES.",
                    class_name="hidden lg:flex items-center gap-2 rotate-6 bg-[#f7ce4d] border-2 border-[#202d40] rounded-xl px-5 py-3 text-xs font-extrabold whitespace-pre-line",
                ),
                class_name="flex items-center justify-between gap-6 mb-8",
            ),
            rx.el.div(
                rx.foreach(FIGHTERS, character_card),
                class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5",
            ),
            room_controls(),
            rx.el.footer(
                rx.el.span("BUILT FOR A LITTLE FRIENDLY CHAOS."),
                rx.el.span("4 FIGHTERS · 100 SECONDS · ENDLESS POSSIBILITIES"),
                class_name="flex flex-wrap justify-between gap-3 py-8 text-[10px] font-bold tracking-widest text-[#788078]",
            ),
            class_name="w-full max-w-7xl mx-auto px-5 sm:px-8",
        ),
        class_name="min-h-dvh bg-[#f7f3e8] text-[#202d40] font-['Nunito_Sans']",
    )


# Health bar: unknown health stays unknown; known HP is relative to max or initial HP.
def health_bar(view: rx.Var[dict[str, str]]) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(
                "HEALTH",
                class_name="text-[10px] font-extrabold tracking-widest",
            ),
            rx.el.span(view["health"], class_name="font-extrabold text-sm"),
            class_name="flex justify-between mb-1",
        ),
        rx.el.progress(
            value=view["percent"],
            max="100",
            aria_label="Fighter health",
            class_name="w-full h-3 overflow-hidden rounded-full [&::-webkit-progress-bar]:bg-[#202d40]/15 [&::-webkit-progress-value]:bg-[#168b83] [&::-moz-progress-bar]:bg-[#168b83]",
        ),
        rx.el.p(view["basis"], class_name="mt-1 text-[10px] text-[#64717e]"),
    )


# Fighter panel: backend identity and available attributes sit alongside local portrait art.
def fighter_panel(view: rx.Var[dict[str, str]], opponent: bool) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(
                rx.cond(opponent, "THE CHALLENGER", "YOUR FIGHTER"),
                class_name="text-[10px] font-extrabold tracking-[0.2em]",
            ),
            rx.el.span(f"ID {view['id']}", class_name="text-xs font-bold"),
            class_name="flex justify-between",
        ),
        rx.el.div(
            rx.el.img(
                src=view["image"],
                alt=view["name"],
                class_name="w-32 h-36 sm:w-44 sm:h-44 object-contain shrink-0",
            ),
            rx.el.div(
                rx.el.p(
                    view["element"],
                    class_name="text-[10px] font-extrabold tracking-widest text-[#536473]",
                ),
                rx.el.h2(
                    view["name"],
                    class_name="font-['Baloo_2'] text-4xl font-extrabold break-words",
                ),
                health_bar(view),
                class_name="flex-1 min-w-0",
            ),
            class_name="flex gap-4 items-center",
        ),
        rx.el.div(
            rx.foreach(
                view["stats"].split(" · "),
                lambda stat: rx.el.span(
                    stat,
                    class_name="w-fit rounded-lg bg-white/70 border border-[#202d40]/20 px-3 py-1 text-xs font-bold",
                ),
            ),
            class_name="flex flex-wrap gap-2",
        ),
        class_name=rx.cond(
            opponent,
            "relative z-10 rounded-2xl border-2 border-[#202d40] bg-[#d8efea] p-5 lg:mt-32 shadow-[5px_5px_0_#202d40]",
            "relative z-10 rounded-2xl border-2 border-[#202d40] bg-[#fff3cd] p-5 lg:mb-32 shadow-[5px_5px_0_#202d40]",
        ),
    )


# Arena: offset fighters and a diagonal dividing slash create the battle centerpiece.
def arena() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            class_name="absolute inset-0 bg-[radial-gradient(#202d4020_1px,transparent_1px)] bg-size-[12px_12px]"
        ),
        rx.el.div(
            class_name="hidden lg:block absolute top-[-20%] left-1/2 w-3 h-[145%] rotate-[32deg] bg-[#202d40]/15"
        ),
        fighter_panel(GameState.player_view, False),
        rx.el.div(
            "VS",
            class_name="z-20 justify-self-center self-center lg:absolute lg:top-1/2 lg:left-1/2 lg:-translate-x-1/2 lg:-translate-y-1/2 -rotate-12 flex h-20 w-20 items-center justify-center rounded-2xl border-[3px] border-[#202d40] bg-[#f7ce4d] font-['Baloo_2'] text-4xl font-extrabold shadow-[4px_4px_0_#202d40]",
        ),
        fighter_panel(GameState.opponent_view, True),
        class_name="relative overflow-hidden grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-20 rounded-3xl border-2 border-[#202d40]/20 bg-[#eee8d9] p-5 sm:p-8",
    )


# Combat log: raw backend results remain visible even when their structure is unfamiliar.
def combat_log() -> rx.Component:
    return rx.el.section(
        rx.el.h2(
            rx.icon("scroll-text", class_name="w-5 h-5"),
            "Battle journal",
            class_name="font-['Baloo_2'] text-xl font-extrabold flex items-center gap-2",
        ),
        rx.el.div(
            rx.foreach(
                GameState.logs,
                lambda line: rx.el.p(
                    line,
                    class_name="border-b border-[#202d40]/10 py-3 text-xs whitespace-pre-wrap break-words",
                ),
            ),
            role="log",
            class_name="max-h-56 overflow-y-auto mt-2",
        ),
        rx.el.details(
            rx.el.summary(
                "Inspect latest backend result",
                class_name="cursor-pointer font-extrabold text-xs py-3",
            ),
            rx.el.pre(
                rx.cond(
                    GameState.last_result != "",
                    GameState.last_result,
                    "No attack result yet.",
                ),
                class_name="max-h-64 overflow-auto whitespace-pre-wrap break-words rounded-lg bg-[#202d40] text-[#ecf3e9] p-4 text-xs",
            ),
            rx.el.p(
                "Only explicit player/opponent updates are merged. Other structures are shown as returned; no damage is inferred.",
                class_name="text-xs text-[#617080] mt-2",
            ),
        ),
        class_name="bg-[#fffdf6] rounded-2xl border-2 border-[#202d40]/20 p-5 min-w-0",
    )


# Attack composer: natural-language commands are sent unchanged to the real API.
def attack_composer() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.h2(
                "Make your move.",
                class_name="font-['Baloo_2'] text-3xl font-extrabold",
            ),
            rx.el.div(
                rx.icon("timer", class_name="w-5 h-5"),
                rx.el.span(
                    f"{GameState.turn_remaining}s",
                    class_name="font-['Baloo_2'] text-3xl font-extrabold",
                ),
                rx.el.span("TURN", class_name="text-[10px] font-extrabold"),
                class_name="flex items-center gap-2 bg-[#f7ce4d] border-2 border-[#202d40] rounded-xl px-3 py-1",
            ),
            class_name="flex items-center justify-between gap-2 mb-3",
        ),
        rx.el.label(
            "Describe your attack",
            html_for="attack",
            class_name="text-xs font-extrabold",
        ),
        rx.el.input(
            id="attack",
            placeholder="Dash forward and unleash a spinning strike…",
            default_value=GameState.command,
            on_change=GameState.update_command.debounce(300),
            disabled=(~GameState.active) | GameState.sending,
            max_length=2000,
            class_name=INPUT,
        ),
        rx.el.p(
            "Try “Raise a shield of roots” or “Send a wave beneath their feet.”",
            class_name="text-xs text-[#617080] mt-2 mb-4",
        ),
        rx.el.button(
            rx.cond(
                GameState.sending,
                rx.icon(
                    "loader-circle",
                    class_name="w-5 h-5 motion-safe:animate-spin",
                ),
                rx.icon("swords", class_name="w-5 h-5"),
            ),
            rx.cond(GameState.sending, "Awaiting backend…", "Send Attack"),
            on_click=GameState.send_attack,
            disabled=(~GameState.active)
            | GameState.sending
            | (GameState.command.strip() == ""),
            class_name=BUTTON,
        ),
        rx.el.p(
            "7 seconds per window. A timeout sends no attack. The match clock keeps running during requests.",
            class_name="text-xs text-[#617080] mt-4",
        ),
        error_message(),
        class_name="rounded-2xl border-2 border-[#202d40] bg-[#fffdf6] p-5 min-w-0",
    )


# Battle page layout: match status, arena, real combat feedback, and safe exit controls.
def battle_page() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            header(),
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        f"ROOM / {GameState.room_code}",
                        class_name="text-xs tracking-widest font-extrabold",
                    ),
                    rx.el.p(
                        rx.icon("circle", class_name="h-2 w-2 fill-current"),
                        rx.cond(
                            GameState.connected,
                            "API connected",
                            "Not connected",
                        ),
                        class_name="flex items-center gap-2 text-xs text-[#11746e] mt-1",
                    ),
                ),
                rx.el.div(
                    rx.icon("clock-3", class_name="h-5 w-5"),
                    rx.el.span(
                        f"{GameState.remaining}s",
                        class_name="font-['Baloo_2'] text-3xl font-extrabold",
                    ),
                    rx.el.span(
                        "MATCH CLOCK",
                        class_name="text-[10px] font-extrabold tracking-wider",
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.button(
                    rx.icon("arrow-left", class_name="h-4 w-4"),
                    "Leave Room / Choose Fighter",
                    on_click=GameState.leave_room,
                    class_name="flex items-center gap-2 text-xs font-extrabold border-2 border-[#202d40]/30 rounded-xl p-3 hover:bg-white focus-visible:outline-4 focus-visible:outline-[#158b87]",
                ),
                class_name="flex flex-wrap items-center justify-between gap-4 mb-5",
            ),
            arena(),
            rx.cond(
                GameState.outcome != "",
                rx.el.section(
                    rx.icon("flag", class_name="w-8 h-8"),
                    rx.el.h2(
                        GameState.outcome,
                        class_name="font-['Baloo_2'] text-2xl font-extrabold",
                    ),
                    rx.el.button(
                        "Choose your next fighter",
                        on_click=GameState.leave_room,
                        class_name=BUTTON,
                    ),
                    role="status",
                    class_name="flex flex-wrap items-center justify-between gap-4 bg-[#f7ce4d] border-2 border-[#202d40] p-5 rounded-xl mt-6",
                ),
                rx.fragment(),
            ),
            rx.el.div(
                combat_log(),
                attack_composer(),
                class_name="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6 pb-8",
            ),
            class_name="w-full max-w-7xl mx-auto px-5 sm:px-8",
        ),
        class_name="min-h-dvh bg-[#f7f3e8] text-[#202d40] font-['Nunito_Sans']",
    )
