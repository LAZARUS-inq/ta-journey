# register_ta_menu.py
# Adds a "TA Journey" menu to the UE5 Level Editor.
# Run once per editor session, or copy python/init_unreal.py to
# <Project>/Content/Python/init_unreal.py so it loads on startup.
#
# Author: LAZARUS-inq

import os
import unreal

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

MENU_OWNER = "TAJourney"
MENU_NAME = "LevelEditor.MainMenu.TAJourney"

TOOLS = (
    ("TextureChecker", "Texture Checker", "texture_checker.py"),
    ("MaterialAudit", "Material Audit", "material_audit.py"),
    ("MeshValidator", "Mesh Validator", "mesh_validator.py"),
    ("DependencyChecker", "Asset Dependency Checker", "asset_dependency_checker.py"),
)


def _python_command(filename):
    path = os.path.join(SCRIPT_DIR, filename)
    return f"import runpy; runpy.run_path({path!r}, run_name='__main__')"


def register():
    menus = unreal.ToolMenus.get()
    main_menu = menus.find_menu("LevelEditor.MainMenu")
    if main_menu is None:
        unreal.log_warning("[TA Journey] LevelEditor.MainMenu not found — open a level editor first.")
        return False

    ta_menu = main_menu.add_sub_menu(
        MENU_OWNER,
        "TAJourneySection",
        "TAJourney",
        "TA Journey",
        "Technical Artist pipeline tools",
    )

    for entry_name, label, filename in TOOLS:
        entry = unreal.ToolMenuEntry(
            name=entry_name,
            type=unreal.MultiBlockType.MENU_ENTRY,
        )
        entry.set_label(label)
        entry.set_tool_tip(f"Run {filename} (report-only defaults)")
        entry.set_string_command(
            unreal.ToolMenuStringCommandType.PYTHON,
            "",
            _python_command(filename),
        )
        ta_menu.add_menu_entry("TAJourneyTools", entry)

    menus.refresh_all_widgets()
    unreal.log("[TA Journey] Menu registered: Level Editor → TA Journey")
    return True


if __name__ == "__main__":
    register()
