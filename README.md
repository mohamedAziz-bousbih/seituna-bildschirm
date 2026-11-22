# Seituna Moschee – Bildschirm

Die Seite `index.html` zeigt Infos, das heutige Programm mit Gebetszeiten und das Wochenprogramm.
Die Gebetszeiten kommen von der MAWAQIT-Seite der Moschee, ohne dass jemand etwas eintippt.

## So funktioniert es

1. **Jede Nacht** startet GitHub das Skript `fetch_mawaqit.py`. Es liest die öffentliche MAWAQIT-Seite der Moschee
   und speichert den **ganzen Jahreskalender** (Adhan, Iqama, Jumu'a) als `prayer-times.json`.
2. **Der Bildschirm** liest `prayer-times.json`, alle 3 Stunden neu, und behält eine Kopie im Browser.
3. Wenn etwas ausfällt:
   - Internet weg → die gespeicherte Kopie wird benutzt (enthält das ganze Jahr).
   - Noch nie Daten bekommen → die Zeiten werden berechnet.
   - Unter den Gebetszeiten steht immer klein, woher die Zeiten gerade kommen und von wann sie sind.

## Einrichten (einmalig, ca. 15 Minuten)

1. **Neues GitHub-Repository** anlegen (öffentlich) und alle Dateien dieses Ordners hochladen,
   **auch den Ordner `.github`**. Die Seituna-Moschee ist schon eingetragen
   (`msjd-lzytwn-seituna-moschee-berlin-14059-germany`), und `prayer-times.json` mit den echten Zeiten liegt schon bei.
2. *(Nur für eine andere Moschee:)* *Settings → Secrets and variables → Actions → Variables →*
   `MAWAQIT_SLUG` = letzter Teil des MAWAQIT-Links.
3. **Erster Lauf:** *Actions → „MAWAQIT-Gebetszeiten holen“ → Run workflow.* Nach ca. 30 Sekunden ein grüner Haken;
   im Repository liegt jetzt `prayer-times.json`.
   Rot mit „Permission denied“ beim Push? Dann *Settings → Actions → General → Workflow permissions →
   Read and write permissions* einstellen und den Lauf wiederholen.
4. **Seite veröffentlichen:** *Settings → Pages → Deploy from a branch → main / (root)*.
   Die Adresse (`https://<name>.github.io/<repo>/`) im Kiosk-Browser der Stele als Startseite eintragen.
5. **Prüfen:** Unter den Gebetszeiten steht „Gebetszeiten: MAWAQIT · Stand …“ und die Zeiten stimmen mit der
   MAWAQIT-App überein.

## Wenn es einmal nicht klappt

- GitHub schickt bei einem fehlgeschlagenen Lauf eine E-Mail. Das alte `prayer-times.json` bleibt dann unverändert,
  der Bildschirm läuft mit dem Jahreskalender weiter. Nur Änderungen, die der Imam danach in MAWAQIT macht,
  kommen nicht an.
- „confData nicht gefunden“ heißt: MAWAQIT hat seine Seite umgebaut. Dann muss das Skript angepasst werden.
- Bei öffentlichen Repositories pausiert GitHub zeitgesteuerte Läufe nach 60 Tagen ohne Aktivität. Dann unter
  *Actions* den Workflow wieder aktivieren.

## Programm ändern

In `index.html` nach `const DAYS` suchen. Dort stehen die Kurse pro Tag, darunter `const INFOS` für die linke Spalte.

## Hinweis

Das ist **keine offizielle MAWAQIT-Schnittstelle**. Das Skript liest einmal pro Nacht die öffentliche Seite,
wie es auch freiwillige Tools tun. MAWAQIT kann das jederzeit ändern oder sperren.
