
CaveCleanup = ["stone", "flint", "Crystalshardblue", "TurabadaArm"]

TreeLag = ["Stick", "ArrowShaftWooden"]

RedwoodBox = ["MushroomRedHalfRipe", "MushroomCaveLargeHalfRipe", "GourdCanteen", "MushroomCaveSmallFullRipe", "MushroomBrownHalfRipe", "MushroomCaveSmallHalfRipe"]

BoulderCleanup = ['Stone', 'sandstone', 'flint']

turabadaCleanup = ['Stone', 'flint']

spriggullCleanup = ['spriggulldrumstickbone', 'spriggullfeatherred', 'spriggullfeatherblue', 'spriggullfletchingred', 'spriggullfletchingblue', 'spikefancy']

items = ["arrow", "woodcutwedge", "KaKarimataArrow", "SmallBoneSpike", "RustyAxe", "RustyChisel", "RustyGreataxe", "RustyGreatsword", "RustyHammer", "RustyPickaxe", "RustyPitchfork", "RustyShield", "RustyShortsword", "RustySpade", "stick", "stone", "flint", "spriggulldrumstickbone", "SpriggullDrumstickFullRipe", "SpriggullDrumstickHalfRipe", "spriggullfeatherred", "spriggullfeatherblue", "spriggullfletchingred", "spriggullfletchingblue", "AppleCoreRipe", "AppleCoreUnripe", "ArrowShaftWooden", "TurabadaArm", "HebiosHandleKunai", "Kunai", "Salt", "SandstoneStone"]


from .logger import CaveLevelAlertLogger
import os
import threading
import time

from server.core.data_store import CONSOLE_TOKEN_FILE
from tavern_shared.ws_console_client import WsConsoleClient
from .settings import * 


'''
AVAILABLE settings:
"cleanup_delay": 300,
"tree_cleanup": True,
"cave_cleanup": True,
"redwood_box": True,
"spriggull_cleanup": True,
"lag_items_cleanup": True,


'''





logger = CaveLevelAlertLogger()
_stop_event = threading.Event()

global _ws_client
_ws_client = WsConsoleClient()
    


register_town_cleanup_settings_window()


def on_shutdown():
    global _ws_client
    _stop_event.set()
    
    if _ws_client is not None:
        _ws_client.disconnect()
        _ws_client = None
    logger._log("town_cleanup Logger shutting down.")


def on_line(line):
    return  # Ignore incoming lines; this addon does not process them.
        

def on_disc(reason=""):
    global _ws_client
    if reason:
        logger._log(f"[town_cleanup] disconnected from console: {reason}")
       
       
        if _ws_client is not None: #ignore 
            _ws_client.disconnect() #ignore
            _ws_client = None
            threading.Thread(target=startup, daemon=True).start()   
    else:
        logger._log("[town_cleanup] disconnected from console.")
        _stop_event.clear()
        
        if _ws_client is not None:
            _ws_client.disconnect()
            _ws_client = None

            threading.Thread(target=startup, daemon=True).start()


def _wait_for_token(check_every=1.0):
    while not _stop_event.is_set():
        try:
            if os.path.isfile(CONSOLE_TOKEN_FILE):
                token = open(CONSOLE_TOKEN_FILE, "r").read().strip()
                if token:
                    return token
        except Exception:
            pass
        time.sleep(check_every)
    return ""
def startup():
    global _ws_client

    token = _wait_for_token()
    if not token:
        logger._log("[town_cleanup] startup canceled before token became available.")
        return

    logger._log(f"Console token: {token}")
    logger._new_line()
    logger._log("[town_cleanup] attempting to subscribe to PlayerJoined and PlayerLeft events.")

    if _ws_client is None:
        _ws_client = WsConsoleClient()
    
    while not _stop_event.is_set():
        client = _ws_client
        if client is None:
            logger._log("[town_cleanup] websocket client unavailable; stopping startup loop.")
            return
        logger._log("[town_cleanup] attempting to connect to console...")
        try:
            success, msg = client.connect("127.0.0.1", token,on_line=on_line, on_disc=on_disc)
        except Exception as e:
            logger._log(f"[town_cleanup] connect RAISED: {type(e).__name__}: {e}")
            time.sleep(2.0)
            continue
        logger._log(f"[town_cleanup] connect attempt result: {success}, message: {msg}")
        if not success:
            logger._log(f"[town_cleanup] console not ready yet ({msg}); retrying in 2s...")
            time.sleep(2.0)
            continue
        if success:
            logger._log(f"[town_cleanup] connected to console: {msg}")

            logger._new_line()
            settings = load_settings()
            delay = settings.get("cleanup_delay", 300)
            logger._log(f"[town_cleanup] cleanup delay: {delay} seconds")
            items_to_cleanup = []
            if settings.get("tree_cleanup", True):
                items_to_cleanup.extend(TreeLag)
                logger._log(f"[town_cleanup] tree cleanup enabled; items: {TreeLag}")
            if settings.get("cave_cleanup", True):
                items_to_cleanup.extend(CaveCleanup)
                items_to_cleanup.extend(BoulderCleanup)
                items_to_cleanup.extend(turabadaCleanup)
                logger._log(f"[town_cleanup] cave cleanup enabled; items: {CaveCleanup}")
            if settings.get("redwood_box", True):
                items_to_cleanup.extend(RedwoodBox)
                logger._log(f"[town_cleanup] redwood box cleanup enabled; items: {RedwoodBox}")
            if settings.get("spriggull_cleanup", True):
                items_to_cleanup.extend(spriggullCleanup)
                logger._log(f"[town_cleanup] spriggull cleanup enabled; items: {spriggullCleanup}")

            if settings.get("lag_items_cleanup", True):
                items_to_cleanup.extend(items)
                logger._log(f"[town_cleanup] lag items cleanup enabled; items: {items}")
            while not _stop_event.is_set():

                time.sleep(delay)
                for item in items_to_cleanup:
                    client.send(f"wacky destroy-free {item}")
                    logger._log(f"[town_cleanup] removed item: {item}")


        logger._log(f"[town_cleanup] console not ready yet ({msg}); retrying in 2s...")
        time.sleep(2.0)


threading.Thread(target=startup, daemon=True).start()
