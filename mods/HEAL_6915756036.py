# test_mod_loading.py
#
# PURPOSE: This has ZERO dependency on bascenev1 or any game API.
# Its only job is to prove whether BombSquad is loading .py files from
# your mods folder at all.
#
# HOW TO USE
# ----------
# 1. Put this file in the EXACT same folder as your working boxing-glove
#    mod (same folder, same install method, nothing different).
# 2. Launch the game.
# 3. Check the in-game log / console.
#
# EXPECTED RESULT
# ----------------
# If mods ARE loading correctly, you will see this line somewhere in
# the log, immediately at startup:
#
#     >>> TEST_MOD_LOADING: this file was executed <<<
#
# If you do NOT see that line, the problem is 100% about placement,
# permissions, "Enable Custom Modules" setting, or how mods get
# imported on your platform -- not about mod code itself.

print(">>> TEST_MOD_LOADING: this file was executed <<<")

try:
    import babase
    print(">>> TEST_MOD_LOADING: babase import OK <<<")
except Exception as e:
    print(f">>> TEST_MOD_LOADING: babase import FAILED: {e} <<<")

try:
    import bascenev1
    print(">>> TEST_MOD_LOADING: bascenev1 import OK <<<")
except Exception as e:
    print(f">>> TEST_MOD_LOADING: bascenev1 import FAILED: {e} <<<")
