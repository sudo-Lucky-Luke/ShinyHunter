import argparse

from shunter.models.shiny_hunter import ShinyHunterType
from shunter.stationary import ShinyHunterStationary


def parse_hunter_type() -> ShinyHunterType:
    """Parse the command line arguments and returns the type of hunter to use."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--hunter",
        type=ShinyHunterType,
        choices=list(ShinyHunterType),
        help="Type of shiny hunter to use",
        required=True,
    )
    arguments = parser.parse_args()
    return arguments.hunter


def main():
    hunter_type = parse_hunter_type()

    if hunter_type == ShinyHunterType.stationary:
        # Passe ggf. den Fenstertitel an deinen Emulator an
        shiny_hunter = ShinyHunterStationary(window_title="Playback (Nightly)")

    elif hunter_type == ShinyHunterType.starter:
        # Lazy import, damit ImportError nur auftritt, wenn wirklich benötigt
        try:
            from shunter.starter import ShinyHunterStarter  # noqa: WPS433 (local import by design)
        except ImportError as exc:
            raise ImportError(
                "Gewählt wurde --hunter starter, aber 'shunter/starter.py' "
                "oder die Klasse 'ShinyHunterStarter' existiert nicht. "
                "Lege die Datei/Klasse an oder starte mit '--hunter stationary'."
            ) from exc
        shiny_hunter = ShinyHunterStarter(window_title="Playback (Nightly)")

    else:
        raise ValueError(f"Unknown hunter type: {hunter_type}")

    shiny_hunter.start_loop()


if __name__ == "__main__":
    main()
