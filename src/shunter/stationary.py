import os
import time

from shunter.abstract.abstract_shiny_hunter import AbstractShinyHunter


class ShinyHunterStationary(AbstractShinyHunter):
    def __init__(self, window_title: str):
        AbstractShinyHunter.__init__(self, window_title)
        self.reference_cp = None
        self.target_cp = None

        # Wartezeit nach JEDEM einzelnen Tastendruck in der pixelgetriebenen Sequenz (Sek.)
        self.tap_gap = 2.0

    def start_loop(self):
        """Start the loop of the hunter."""
        print("[INFO] Starte ShinyHunterStationary Loop")
        self._pick_color_points_loop()
        self._find_shiny_loop()

    def _color_points_picked(self) -> bool:
        """Check if target point and reference point are picked."""
        return self.reference_cp and self.target_cp

    def _reference_color_found(self) -> bool:
        """Check if reference color is found."""
        found = self.reference_cp.color == self.picker.window_capture.get_pixel(*self.reference_cp.point)
        if found:
            print("[CHECK] Referenzfarbe erkannt.")
        return found

    def _check_shiny(self) -> bool:
        """Compare target color change."""
        current = self.picker.window_capture.get_pixel(*self.target_cp.point)
        shiny = (self.target_cp.color != current)
        print(f"[CHECK] Shiny-Check: gespeicherte Ziel-Farbe={self.target_cp.color}, "
              f"aktuelle Farbe={current} -> {'SHINY!' if shiny else 'kein Shiny'}")
        return shiny

    def _pick_color_points(self) -> None:
        """Pick target color point first and then the reference color point."""
        if not self.reference_cp:
            print("[PICK] Picking reference color and position...")
            self.reference_cp = self.picker.pick_color()
            if self.reference_cp:
                print(f"[PICK] Referenz gesetzt: point={self.reference_cp.point}, color={self.reference_cp.color}")
                return
        if not self.target_cp:
            print("[PICK] Picking target color and position...")
            self.target_cp = self.picker.pick_color()
            if self.target_cp:
                print(f"[PICK] Ziel gesetzt: point={self.target_cp.point}, color={self.target_cp.color}")

    def _pick_color_points_loop(self) -> None:
        """Loop for picking needed color points (target and reference)."""
        print_flag = True
        while not self._color_points_picked():
            if print_flag:
                current = "target" if self.reference_cp else "reference"
                print(f"[INPUT] Klicke ins Fenster, um den Farbpunkt zu wählen ({current})...")
                print_flag = False
            if self.picker.clicked:
                self._pick_color_points()
                self.picker.clicked = False
                print_flag = True
        print("[INFO] Beide Farbpunkte gewählt. Stoppe Mouse-Listener.")
        self.picker.mouse_listener.stop()

    # --- kleine Wrapper mit Logs ---
    def _press_a(self, note: str = "") -> None:
        print(f"[KEY] Drücke A {note}".rstrip())
        self.key_sim.press_continue()

    def _press_b(self, note: str = "") -> None:
        print(f"[KEY] Drücke B {note}".rstrip())
        self.key_sim.press_b()

    def _press_start(self, note: str = "") -> None:
        print(f"[KEY] Drücke START {note}".rstrip())
        self.key_sim.press_start()

    def _press_reset_combo(self) -> None:
        print("[KEY] Soft-Reset-Kombination: B + SELECT + START + A")
        self.key_sim.press_reset()

    # ===== Pixel-getriebene Helfer =====
    def _get_pixel(self, x: int, y: int):
        return self.picker.window_capture.get_pixel(x, y)

    def _drive_key_until_changes(
        self,
        label: str,
        key_func,
        pos: tuple[int, int],
        start_color: tuple[int, int, int],
        changes_needed: int,
    ) -> None:
        """
        Drückt wiederholt eine Taste (key_func) und zählt Farb-Änderungen am Pixel 'pos'.
        Eine Änderung wird gezählt, wenn current_color != last_color (Edge-Erkennung).
        """
        x, y = pos
        last_color = start_color
        changes = 0

        print(f"[SEQ] {label}: warte auf {changes_needed} Farb-Änderung(en) am Pixel {pos} "
              f"(Startfarbe={start_color})")

        while changes < changes_needed and not self.stop:
            key_func()
            time.sleep(self.tap_gap)

            current = self._get_pixel(x, y)
            changed = current != last_color

            print(f"[PIX] {pos}: vorher={last_color} -> aktuell={current} "
                  f"{'CHANGED' if changed else 'no change'}")

            if changed:
                changes += 1
                print(f"[SEQ] Änderung #{changes}/{changes_needed} erkannt.")
                # neue Referenz für die nächste Edge
                last_color = current

        print(f"[SEQ] {label}: Ziel erreicht ({changes} Änderungen).")

    def _post_reference_sequence(self) -> None:
        """
        Neue Sequenz ab Referenzpunkt:
          1) A bis Pixel (2083,1090) sich 3x ändert (Start: 194,84,59)
          2) B bis Pixel (1984,1086) sich 1x ändert (Start: 230,105,74)
          3) START bis Pixel (2549,839) sich 1x ändert (Start: 255,251,255)
          4) A bis Pixel (2549,839) sich 2x ändert (Start: 255,251,255)
        """
        # 1) A -> 3 Änderungen an (2083, 1090)
        self._drive_key_until_changes(
            label="A bis (2083,1090) 2× ändert",
            key_func=lambda: self._press_a("(Sequenz)"),
            pos=(2083, 1090),
            start_color=(194, 84, 59),
            changes_needed=2,
        )

        # 2) B -> 1 Änderung an (1984, 1086)
        self._drive_key_until_changes(
            label="B bis (1984,1086) 1× ändert",
            key_func=lambda: self._press_b("(Sequenz)"),
            pos=(1984, 1086),
            start_color=(230, 105, 74),
            changes_needed=1,
        )

        # 3) START -> 1 Änderung an (2549, 839)
        self._drive_key_until_changes(
            label="START bis (2549,839) 1× ändert",
            key_func=lambda: self._press_start("(Sequenz)"),
            pos=(2549, 839),
            start_color=(0, 0, 0),
            changes_needed=1,
        )

        # 4) A -> 2 Änderungen an (2549, 839)
        self._drive_key_until_changes(
            label="A bis (2549,839) 2× ändert",
            key_func=lambda: self._press_a("(Sequenz)"),
            pos=(2549, 839),
            start_color=(255, 251, 255),
            changes_needed=2,
        )

        print("[SEQ] Pixel-gesteuerte Zwischen-Sequenz abgeschlossen.")

    def _find_shiny_loop(self) -> None:
        """Loop for finding a shiny."""
        os.system("cls")
        print("[INFO] Starte Shiny-Suche...")
        while not self.shiny_found and not self.stop:
            # 1) Soft-Reset
            self._press_reset_combo()

            # 2) A spammen, bis Referenzfarbe erkannt ist
            press_count = 0
            while not self._reference_color_found() and not self.stop:
                press_count += 1
                self._press_a("(weiter)")
            print(f"[INFO] Referenz erreicht nach {press_count}x A.")

            if self.stop:
                break

            # 3) Neue pixelgetriebene Sequenz
            self._post_reference_sequence()

            # 4) Shiny-Check
            self.shiny_found = self._check_shiny()
            if not self.shiny_found:
                self.soft_resets += 1
                print(f"[STATUS] Kein Shiny. Soft-Resets bisher: {self.soft_resets}")
                self._display_current_status()

        if not self.stop:
            print(f"[SUCCESS] Shiny gefunden nach {self.soft_resets} Soft-Resets!")
        else:
            print("[INFO] Suche gestoppt.")
