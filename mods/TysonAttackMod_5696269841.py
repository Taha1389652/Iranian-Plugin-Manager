# ba_meta require api 9
import babase
import bascenev1 as bs
import re
import logging

logging.disable(logging.CRITICAL)

_orig_pushcall = babase.pushcall

def _safe_pushcall(call, from_other_thread: bool = False, suppress_other_thread_warning: bool = False, other_thread_use_fg_context: bool = False, raw: bool = False) -> None:
    try:
        if from_other_thread and babase.in_logic_thread():
            from_other_thread = False
        _orig_pushcall(call, from_other_thread=from_other_thread, suppress_other_thread_warning=True, other_thread_use_fg_context=other_thread_use_fg_context, raw=raw)
    except TypeError:
        try:
            if from_other_thread and babase.in_logic_thread():
                _orig_pushcall(call)
            else:
                _orig_pushcall(call, from_other_thread=from_other_thread)
        except Exception:
            pass
    except Exception:
        pass

babase.pushcall = _safe_pushcall

_original_chatmessage = bs.chatmessage
_attack_mode_enabled = False

def _custom_chatmessage(message: str | babase.Lstr, clients: list[int] | None = None, sender_override: str | None = None) -> None:
    global _attack_mode_enabled
    try:
        if isinstance(message, str):
            msg_clean = message.strip()
            
            if msg_clean == "اتک مود روشن":
                _attack_mode_enabled = True
                babase.screenmessage(" اتک مود روشن شد!", color=(0.0, 1.0, 0.0))
                bs.getsound('dingSmallHigh').play()
                return
                
            elif msg_clean == "اتک مود خاموش":
                _attack_mode_enabled = False
                babase.screenmessage(" اتک مود خاموش شد!", color=(1.0, 0.2, 0.2))
                bs.getsound('shieldDown').play()
                return

            if _attack_mode_enabled:
                match_cu = re.match(r'^(%?)cu\s+(\d+)$', msg_clean)
                if match_cu:
                    prefix = match_cu.group(1)
                    target_id = match_cu.group(2)
                    
                    _original_chatmessage(message, clients, sender_override)
                    
                    def _send_fr():
                        try:
                            _original_chatmessage(f"{prefix}fr {target_id}")
                        except Exception:
                            pass
                        
                    def _send_hug():
                        try:
                            _original_chatmessage(f"{prefix}hug {target_id}")
                        except Exception:
                            pass
                    
                    babase.apptimer(0.08, _send_fr)
                    babase.apptimer(0.16, _send_hug)
                    return

                match_fr = re.match(r'^(%?)fr\s+(\d+)$', msg_clean)
                if match_fr:
                    prefix = match_fr.group(1)
                    target_id = match_fr.group(2)
                    
                    _original_chatmessage(message, clients, sender_override)
                    
                    def _send_hug_only():
                        try:
                            _original_chatmessage(f"{prefix}hug {target_id}")
                        except Exception:
                            pass
                    
                    babase.apptimer(0.08, _send_hug_only)
                    return
    except Exception:
        pass

    try:
        _original_chatmessage(message, clients, sender_override)
    except Exception:
        pass


# ba_meta export babase.Plugin
class BSLifeAttackMod(babase.Plugin):
    def on_app_running(self) -> None:
        try:
            logging.getLogger().setLevel(logging.CRITICAL + 1)
            bs.chatmessage = _custom_chatmessage
        except Exception:
            pass
