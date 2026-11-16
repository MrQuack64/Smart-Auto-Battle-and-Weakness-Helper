# Omar's Ankimon additions — install on another PC

Everything here was added to Ankimon on top of **Ankimon 2.5-E** (AnkiWeb code 1908235722):

1. **Smart Auto Battle** — Battle settings → *Move Selection* = `2 – Smart Auto Battle`. Always uses the strongest move against the current enemy and, at each new wild encounter, sends out the best team member from the Cycle Team rotation.
2. **Team level balancing** — Battle settings → *Team Level Gap* (default 5, 0 = off). With Smart Auto Battle on, only team members within that many levels of the lowest-level member are sent out, so the team levels up together.
3. **GIFs in the Ankimon battle window** — GUI settings → *Ankimon Window Sprites as GIF*. Animated sprites are raised so they don't overlap the weakness bar or the message box.
4. **Weakness bars in the battle window** — red "WEAK: …" plaques above each Pokémon's info box (part of the battle-window file, no setting needed).
5. **Ankimon Weakness Helper** — a separate small add-on: a lookup window that shows any Pokémon's type weaknesses.

## Change log

- **v1** — Smart Auto Battle (Move Selection 0/1/2 replaces "Allow Choosing Moves"; old setting migrates automatically). GIF sprites and weakness bars in the battle window.
- **v2** — Code-review fixes: switched-in Pokémon gets its own held item; no auto-switch while the active Pokémon has fainted (double faint); battle state is never reused across two Pokémon of the same species; never falls back to Explosion/self-KO moves when another move exists; Move Selection and Team Level Gap appear in both settings windows, and the old "Allow Choosing Moves" toggle stays in sync. New **Team Level Gap** setting (level balancing).
- **v3** — GIF sprites raised in the battle window (wild Pokémon +16 px, yours +18 px).

## What's in this folder

| Path | What it is |
|---|---|
| `ankimon_patch_2.5-E/` | Changed Ankimon files, in the same folder layout as the Ankimon add-on folder: `battle_loop.py`, `config.json`, `functions/encounter_functions.py`, `functions/smart_move_selection.py` (new), `functions/smart_team_switch.py` (new), `pyobj/settings.py`, `pyobj/settings_window.py`, `pyobj/test_window.py`, `ankimon_items_web/settings_schema.py`, `lang/setting_name.json`, `lang/setting_description.json`. |
| `Ankimon_Weakness_Helper.ankiaddon` | The Weakness Helper add-on. Double-click to install. |

## Instructions for Claude (on the new PC)

Follow these steps on the user's computer. Ask before overwriting anything.

1. **Find the Anki add-ons folder.**
   - Windows: `%APPDATA%\Anki2\addons21` (e.g. `C:\Users\<name>\AppData\Roaming\Anki2\addons21`)
   - macOS: `~/Library/Application Support/Anki2/addons21`
   - Linux: `~/.local/share/Anki2/addons21`
2. **Check Ankimon is installed** as the folder `1908235722`, and read its `manifest.json` `"version"`.
   - If Ankimon is missing, tell the user to install it in Anki first (Tools → Add-ons → Get Add-ons → code `1908235722`), then restart Anki and continue.
3. **Make sure Anki is closed** before changing files.
4. **Back up** each file in `1908235722/` that the patch will replace, into `1908235722/user_files/omar_patch_backup/` (same sub-folders).
5. **If the version is `2.5-E`:** copy everything inside `ankimon_patch_2.5-E/` into `1908235722/`, keeping the sub-folders (`functions/`, `pyobj/`, `lang/`, `ankimon_items_web/`), overwriting the existing files. Two files are brand new: `functions/smart_move_selection.py` and `functions/smart_team_switch.py`.
6. **If the version is NOT `2.5-E`:** do not copy the files over blindly — that could undo Ankimon updates. Instead merge the changes: for each patched file, compare it with the installed one and apply only Omar's additions (Move Selection / Smart Auto Battle, Team Level Gap, Ankimon Window GIF setting with the raised GIF positions `_GIF_LIFT = {"enemy": 40, "main": 40}`, and the weakness bars in `pyobj/test_window.py`). The clean, reviewable version of the Smart Auto Battle + level balancing changes is on the `smart-auto-battle` branch of `github.com/MrQuack64/Smart-Auto-Battle-and-Weakness-Helper` (pull request #1075 on `h0tp-ftw/ankimon`). If Ankimon already contains *Move Selection* in its Battle settings, the feature has been merged officially and no patch is needed.
7. **Install the Weakness Helper:** copy `__init__.py` and `manifest.json` from `Ankimon_Weakness_Helper.ankiaddon` (it's a zip) into a new folder `addons21/ankimon_weakness_helper/`, or have the user double-click the `.ankiaddon` file with Anki open.
8. **Restart Anki**, then in Ankimon's settings set *Move Selection* to `2 – Smart Auto Battle`, check *Team Level Gap* (default 5), and turn on *Ankimon Window Sprites as GIF* if wanted.
9. Never touch `1908235722/user_files/` except for the backup folder — it holds the user's save.

## Undo

Copy the files from `1908235722/user_files/omar_patch_backup/` back into `1908235722/` and restart Anki. Delete `addons21/ankimon_weakness_helper/` to remove the Weakness Helper.

## Note about Ankimon updates

Until these changes are merged into official Ankimon, an Ankimon update from AnkiWeb will replace the patched files and the additions will disappear. If that happens, run these steps again (step 6 if the version changed).
