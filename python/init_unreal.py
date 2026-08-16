# init_unreal.py
# Copy to <YourProject>/Content/Python/init_unreal.py (or merge with an
# existing init) so the TA Journey menu appears when the editor starts.
#
# The python/ folder from this repo must sit next to this file, or be on
# Unreal's Python path.

try:
    import register_ta_menu
    register_ta_menu.register()
except Exception as exc:
    print("[TA Journey] menu registration failed:", exc)
