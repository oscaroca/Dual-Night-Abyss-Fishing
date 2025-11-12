# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# .\.venv\Scripts\activate
import numpy as np
import mss
import cv2
import pyautogui
from pynput.keyboard import Key, Controller
import time
import threading
import ctypes
import ctypes
import time
import pydirectinput
import os

# Constants
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

def press_space(duration=0.05):
    # Define constants
    INPUT_KEYBOARD = 1
    KEYEVENTF_KEYUP = 0x0002
    VK_SPACE = 0x20

    # Press
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(VK_SPACE, 0, 0, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(INPUT_KEYBOARD), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    time.sleep(duration)

    # Release
    ii_.ki = KeyBdInput(VK_SPACE, 0, KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(INPUT_KEYBOARD), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    print("Pressed SPACE (SendInput)")

BAR_TOP_COLOUR = np.array([0, 193, 73, 255])
BAR_BOTTOM_COLOUR = np.array([1, 101, 33, 255])
BAR_COLUMN = 20
FISH_COLOUR = np.array([151, 96, 2, 255])
FISH_COLUMN = 20
EXC_COLOUR1 = np.array([0, 186, 247, 255])
EXC_COLOUR2 = np.array([0, 249, 251, 255])


# def press_space():
#     """Pulse the spacebar asynchronously."""
#     def do_press():
#         keyboard.press(Key.space)
#         time.sleep(0.1)
#         keyboard.release(Key.space)
#         print("Pressed SPACE")
#     threading.Thread(target=do_press, daemon=True).start()

def holdSpace(holdTime):
    keyboard.press(Key.space)
    time.sleep(holdTime)
    keyboard.release(Key.space)
    return

def holdW(key, holdTime):
    keyboard.press(key)
    time.sleep(holdTime)
    keyboard.release(key)
    return

def _as_gray(img):
    """Return a single-channel uint8 image for matchTemplate."""
    if img is None:
        return None
    # already single-channel
    if img.ndim == 2:
        return img
    # BGRA from mss
    if img.shape[2] == 4:
        return cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
    # BGR
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def findTopBar(screen, barTop):
    topBarY = -1
    s = _as_gray(screen)
    t = _as_gray(barTop)
    if s is None or t is None:
        return -1
    res = cv2.matchTemplate(s, t, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val > 0.80:
        topBarY = max_loc[1]
    return topBarY

def findBottomBar(screen, barBottom):
    bottomBarY = -1
    s = _as_gray(screen)
    t = _as_gray(barBottom)
    if s is None or t is None:
        return -1
    res = cv2.matchTemplate(s, t, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val > 0.80:
        bottomBarY = max_loc[1]
    return bottomBarY

def findFish(screen, fish):
    fishY = -1
    s = _as_gray(screen)
    t = _as_gray(fish)
    if s is None or t is None:
        return -1
    res = cv2.matchTemplate(s, t, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val > 0.70:  # 0.8
        fishY = max_loc[1]
    return fishY

def gotAFish(screen, gotAFishImage):
    s = _as_gray(screen)
    t = _as_gray(gotAFishImage)
    if s is None or t is None:
        return False
    res = cv2.matchTemplate(s, t, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val > 0.90:
        return True
    return False
    

#Program start delay
startDelay = 3
for i in range(startDelay, 0, -1):
    print(f"Starting in {i}...")
    time.sleep(1)
print("Program started.")
# Create keyboard controller
keyboard = Controller()

# area = "sewers"
area = "purgatorio"
# area = "island"

state = "waiting"

# Load reference images
startStateImage = cv2.imread(os.path.join(area, "start.png"), cv2.IMREAD_GRAYSCALE)
if startStateImage is None:
    raise FileNotFoundError(f"Could not load {os.path.join(area,'start.png')}")

fishImage = cv2.imread(os.path.join(area, "fish.png"), cv2.IMREAD_GRAYSCALE)
topBarImage = cv2.imread(os.path.join(area, "topBar.png"), cv2.IMREAD_GRAYSCALE)
topFishingBarImage = cv2.imread(os.path.join(area, "topFishingBar.png"), cv2.IMREAD_GRAYSCALE)
bottomFishingBarImage = cv2.imread(os.path.join(area, "bottomFishingBar.png"), cv2.IMREAD_GRAYSCALE)

if fishImage is None:
    raise FileNotFoundError(f"Could not load {os.path.join(area,'fish.png')}")
if topBarImage is None:
    raise FileNotFoundError(f"Could not load {os.path.join(area,'topbar.png')}")
if topFishingBarImage is None:
    raise FileNotFoundError(f"Could not load {os.path.join(area,'topbar.png')}")
if bottomFishingBarImage is None:
    raise FileNotFoundError(f"Could not load {os.path.join(area,'bottombar.png')}")

gotAFishImage = cv2.imread(os.path.join(area, "got_a_fish.png"), cv2.IMREAD_GRAYSCALE)
if gotAFishImage is None:
    raise FileNotFoundError(f"Could not load {os.path.join(area,'got_a_fish.png')}")

saved_debug = False
prev_bar_length = 150
prev_topBarY = None
prev_bottomBarY = None

# add periodic dump settings
dump_interval = 5.0   # seconds between exported annotated images
last_dump = 0.0

# check for "got a fish" every N seconds
got_check_interval = 5.0
last_got_check = 0.0


with mss.mss() as sct:
    monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
    # pyautogui.press('space')  # initial focus
    # time.sleep(1)
    # pyautogui.press('space')  # initial focus
    # time.sleep(5)
    # press_space(2)
    # time.sleep(2)
    # pydirectinput.press('space')
    # print("tried direct input")

  
    # remove or replace the above test with your normal loop when ready

    while True:
        while state == "waiting":
            screen = np.array(sct.grab(monitor))
            newScreen = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)

            res = cv2.matchTemplate(newScreen, startStateImage, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
         
            if max_val > 0.95:
                print("Fishing can start!")
                press_space()
                state = "fishing"
                time.sleep(3)

        while state == "fishing":
            screen = np.array(sct.grab(monitor))
            newScreen = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)

            res = cv2.matchTemplate(newScreen, startStateImage, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            if max_val > 0.95:
                print("Fish found!!")
                press_space()
                state = "minigame"
                time.sleep(0.5)


        while state == "minigame":
            screen = np.array(sct.grab(monitor))
            newScreen = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
            print("Minigame started")
            fishRegion = {}
        
            foundUI = False

            while foundUI == False:

                #Detect when fishing
                res = cv2.matchTemplate(newScreen,topBarImage,cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                print("Matching : ", max_val)
                if(max_val > 0.58):
                    print("Fishing started!")
                    foundUI = True
                    # save the full screen and the best matching patch once for visual verification
                    if not saved_debug and False:
                        saved_debug = True
                        # newScreen is grayscale; save the whole screen
                        try:
                            cv2.imwrite(r"c:\Users\oscaroca\Desktop\DNAF\sewers\debug_fullscreen.png", newScreen)
                            # extract the matched patch (use template size)
                            th, tw = topBarImage.shape[:2]
                            mx, my = max_loc
                            matched_patch = newScreen[my:my+th, mx:mx+tw].copy()
                            cv2.imwrite(r"c:\Users\oscaroca\Desktop\DNAF\sewers\debug_matched_patch.png", matched_patch)
                            print("Saved debug_fullscreen.png and debug_matched_patch.png in sewers\\")
                        except Exception as e:
                            print("Failed to save debug images:", e)
                    smallRegion = {"top": monitor['top'] + max_loc[1], "left": monitor['left'] + max_loc[0], "width": 30, "height": 450}

            barY = 0
            fishY = 0
            prevdy = 0
            prevBarY = 550

            fishing = True

            #GET BAR LENGTH

            # Grab the data
            screen = np.array(sct.grab(smallRegion))

            #Find top and bottom bars (robust handling when one/both aren't found)
            topBarY = findTopBar(screen, topFishingBarImage)
            bottomBarY = findBottomBar(screen, bottomFishingBarImage)
            # print("TopBar", topBarY, "BottomBar", bottomBarY)

            # small region height for safe clamping
            small_h = screen.shape[0] if hasattr(screen, "shape") else 0

            # If both bars missing: use previous positions if available, otherwise center fallback
            if topBarY == -1 and bottomBarY == -1:
                print("Both bars missing during length calc")
                if prev_topBarY is not None and prev_bottomBarY is not None:
                    topBarY = prev_topBarY
                    bottomBarY = prev_bottomBarY
                else:
                    center = small_h // 2
                    half = prev_bar_length // 2
                    topBarY = max(0, center - half)
                    bottomBarY = min(max(1, small_h - 1), center + half)

            # If only top missing, estimate it above bottom by previous length
            elif topBarY == -1:
                print("Top bar missing during length calc")
                topBarY = max(0, bottomBarY - prev_bar_length)

            # If only bottom missing, estimate it below top by previous length
            elif bottomBarY == -1:
                print("Bottom bar missing during length calc")
                bottomBarY = min(max(1, small_h - 1), topBarY + prev_bar_length)

            # Compute bar length and keep a running previous value for fallbacks
            barLength = bottomBarY - topBarY
            if barLength <= 0:
                barLength = prev_bar_length
            else:
                prev_bar_length = barLength

            prev_topBarY = topBarY
            prev_bottomBarY = bottomBarY

            # --- debug: save annotated images once for visual verification ---
            if not saved_debug and False:
                try:
                    # grab small region (BGRA) and convert for annotation
                    small_region = np.array(sct.grab(smallRegion))              # BGRA
                    small_gray = cv2.cvtColor(small_region, cv2.COLOR_BGRA2GRAY)
                    small_color = cv2.cvtColor(small_gray, cv2.COLOR_GRAY2BGR)

                    # prepare full-screen image for context (newScreen is grayscale full screen)
                    full_gray = newScreen.copy()
                    full_color = cv2.cvtColor(full_gray, cv2.COLOR_GRAY2BGR)

                    # draw smallRegion rectangle on the full screen (blue)
                    sr_tl = (int(smallRegion["left"]), int(smallRegion["top"]))
                    sr_br = (int(smallRegion["left"] + smallRegion["width"]), int(smallRegion["top"] + smallRegion["height"]))
                    cv2.rectangle(full_color, sr_tl, sr_br, (255, 0, 0), 2)  # blue

                    # annotate top fishing bar on both images (green)
                    if topBarY != -1:
                        th = topFishingBarImage.shape[0]
                        # coordinates in small_region
                        top_tl_small = (0, int(topBarY))
                        top_br_small = (small_color.shape[1] - 1, int(topBarY + th))
                        cv2.rectangle(small_color, top_tl_small, top_br_small, (0, 255, 0), 2)  # green
                        # coordinates in full screen
                        top_tl_full = (sr_tl[0], sr_tl[1] + int(topBarY))
                        top_br_full = (sr_br[0], sr_tl[1] + int(topBarY + th))
                        cv2.rectangle(full_color, top_tl_full, top_br_full, (0, 255, 0), 2)  # green

                    # annotate bottom fishing bar on both images (green)
                    if bottomBarY != -1:
                        bh = bottomFishingBarImage.shape[0]
                        bottom_tl_small = (0, int(bottomBarY))
                        bottom_br_small = (small_color.shape[1] - 1, int(bottomBarY + bh))
                        cv2.rectangle(small_color, bottom_tl_small, bottom_br_small, (0, 255, 0), 2)  # green
                        bottom_tl_full = (sr_tl[0], sr_tl[1] + int(bottomBarY))
                        bottom_br_full = (sr_br[0], sr_tl[1] + int(bottomBarY + bh))
                        cv2.rectangle(full_color, bottom_tl_full, bottom_br_full, (0, 255, 0), 2)  # green

                    # locate fish in the small region and annotate (yellow)
                    res_fish = cv2.matchTemplate(small_gray, fishImage, cv2.TM_CCOEFF_NORMED)
                    _, max_val_fish, _, max_loc_fish = cv2.minMaxLoc(res_fish)
                    if max_val_fish > 0.80:
                        fh, fw = fishImage.shape[:2]
                        fx, fy = max_loc_fish
                        # small region rectangle (yellow)
                        cv2.rectangle(small_color, (fx, fy), (fx + fw, fy + fh), (0, 255, 255), 2)
                        # full-screen rectangle for fish
                        fish_tl_full = (sr_tl[0] + int(fx), sr_tl[1] + int(fy))
                        fish_br_full = (sr_tl[0] + int(fx + fw), sr_tl[1] + int(fy + fh))
                        cv2.rectangle(full_color, fish_tl_full, fish_br_full, (0, 255, 255), 2)

                    # save both images for inspection
                    cv2.imwrite(r"c:\Users\oscaroca\Desktop\DNAF\sewers\debug_fullscreen_with_region.png", full_color)
                    cv2.imwrite(r"c:\Users\oscaroca\Desktop\DNAF\sewers\debug_smallregion_annotated.png", small_color)
                    print("Saved debug_fullscreen_with_region.png and debug_smallregion_annotated.png in sewers\\")
                    saved_debug = True
                except Exception as e:
                    print("Failed to save debug images:", e)
            # --- end debug ---
 
            centrePerc = 0.50

            barLength = bottomBarY - topBarY
            barAddition = int(centrePerc*barLength)

            while fishing == True:

                # Grab the data
                screen = np.array(sct.grab(smallRegion))

                #Find top and bottom bars (robust handling when one/both aren't found)
                topBarY = findTopBar(screen, topFishingBarImage)
                bottomBarY = findBottomBar(screen, bottomFishingBarImage)
                # print("TopBar", topBarY, "BottomBar", bottomBarY)

                # small region height for safe clamping
                small_h = screen.shape[0] if hasattr(screen, "shape") else 0

                # If both bars missing: use previous positions if available, otherwise center fallback
                if topBarY == -1 and bottomBarY == -1:
                    if prev_topBarY is not None and prev_bottomBarY is not None:
                        topBarY = prev_topBarY
                        bottomBarY = prev_bottomBarY
                    else:
                        center = small_h // 2
                        half = prev_bar_length // 2
                        topBarY = max(0, center - half)
                        bottomBarY = min(max(1, small_h - 1), center + half)

                # If only top missing, estimate it above bottom by previous length
                elif topBarY == -1:
                    topBarY = max(0, bottomBarY - prev_bar_length)

                # If only bottom missing, estimate it below top by previous length
                elif bottomBarY == -1:
                    bottomBarY = min(max(1, small_h - 1), topBarY + prev_bar_length)

                # Compute bar length and keep a running previous value for fallbacks
                barLength = bottomBarY - topBarY
                if barLength <= 0:
                    barLength = prev_bar_length
                else:
                    prev_bar_length = barLength

                prev_topBarY = topBarY
                prev_bottomBarY = bottomBarY

                #Find fish
                fishY = findFish(screen,    fishImage)
                # if fishY == -1:
                    # print("Fish Not found...\n")
                    # fishing = False

                barY = topBarY + barAddition        #'Centre' of the bar

                # --- export annotated full-screen every dump_interval seconds ---
                now = time.time()
                if now - last_dump >= dump_interval and False:
                    last_dump = now
                    try:
                        # grab current full screen BGRA and convert to grayscale/color for drawing
                        full_bgra = np.array(sct.grab(monitor))
                        full_gray = cv2.cvtColor(full_bgra, cv2.COLOR_BGRA2GRAY)
                        full_color = cv2.cvtColor(full_gray, cv2.COLOR_GRAY2BGR)

                        # draw smallRegion rectangle (blue) if available
                        if smallRegion["top"] is not None and smallRegion["left"] is not None:
                            sr_tl = (int(smallRegion["left"]), int(smallRegion["top"]))
                            sr_br = (int(smallRegion["left"] + smallRegion["width"]), int(smallRegion["top"] + smallRegion["height"]))
                            cv2.rectangle(full_color, sr_tl, sr_br, (255, 0, 0), 2)  # blue

                        # draw top fishing bar (green) if available
                        if topBarY != -1:
                            th = topFishingBarImage.shape[0]
                            top_tl_full = (sr_tl[0], sr_tl[1] + int(topBarY))
                            top_br_full = (sr_br[0], sr_tl[1] + int(topBarY + th))
                            cv2.rectangle(full_color, top_tl_full, top_br_full, (0, 255, 0), 2)

                        # draw bottom fishing bar (green) if available
                        if bottomBarY != -1:
                            bh = bottomFishingBarImage.shape[0]
                            bottom_tl_full = (sr_tl[0], sr_tl[1] + int(bottomBarY))
                            bottom_br_full = (sr_br[0], sr_tl[1] + int(bottomBarY + bh))
                            cv2.rectangle(full_color, bottom_tl_full, bottom_br_full, (0, 255, 0), 2)

                        # attempt to locate fish in the small region to get full coordinates
                        small_gray = _as_gray(screen)
                        res_fish = cv2.matchTemplate(small_gray, fishImage, cv2.TM_CCOEFF_NORMED)
                        _, max_val_fish, _, max_loc_fish = cv2.minMaxLoc(res_fish)
                        if max_val_fish > 0.80:
                            fh, fw = fishImage.shape[:2]
                            fx, fy = max_loc_fish
                            # fish rectangle in full-screen coords (yellow)
                            fish_tl_full = (sr_tl[0] + int(fx), sr_tl[1] + int(fy))
                            fish_br_full = (sr_tl[0] + int(fx + fw), sr_tl[1] + int(fy + fh))
                            cv2.rectangle(full_color, fish_tl_full, fish_br_full, (0, 255, 255), 2)

                        # save file with timestamp
                        fname = rf"c:\Users\oscaroca\Desktop\DNAF\sewers\debug_minigame_{int(now)}.png"
                        cv2.imwrite(fname, full_color)
                        print("Saved debug image:", fname)
                    except Exception as e:
                        print("Failed to save periodic debug image:", e)
                # --- end export ---

                # Control loop: hold SPACE to move the bar up, release to let it fall.
                # Goal: keep the fish vertically between topBarY and bottomBarY.
                # Use a simple dead-zone PD-like control to decide whether to press/release.

                # fish center (fallback to middle of bar if fish not detected)
                fh = fishImage.shape[0] if fishImage is not None else 0
                print("FishY:", fh, fishY)
                if fishY == -1:
                    target_y = topBarY + (bottomBarY - topBarY) // 2
                    fish_center = target_y
                else:
                    fish_center = fishY + fh // 2

                bar_center = barY
                error = bar_center - fish_center   # positive => bar is below fish (need to move up)

                # controller params
                dead_zone = 4          # pixels: small gap where we do nothing
                # hold/release state (persist between iterations)
                if "space_pressed" not in locals():
                    space_pressed = False

                # Decide action
                if error > dead_zone:
                    print("Bar is too low -> pressing space to move up")
                    # bar is too low -> press space to move up
                    # print("Pressing space to move bar up")
                    if not space_pressed:
                        keyboard.press(Key.space)
                        space_pressed = True
                elif error < -dead_zone:
                    print("Bar is too high -> releasing space to let it fall")
                    # bar is too high -> release space to fall
                    # print("Releasing space to let bar fall")
                    if space_pressed:
                        keyboard.release(Key.space)
                        space_pressed = False
                else:
                    print("Within dead zone; releasing space")
                    # within dead zone -> stop pressing to avoid oscillation
                    # print("Within dead zone; releasing space")
                    if space_pressed:
                        keyboard.release(Key.space)
                        space_pressed = False

                # update previous values used elsewhere
                prevdy = error
                prevBarY = bar_center
                 

                if cv2.waitKey(25) & 0xFF == ord("q"):
                    cv2.destroyAllWindows()
                    break
            # # ensure space released when leaving the fishing loop
            # if 'space_pressed' in locals() and space_pressed:
            #     try:
            #         keyboard.release(Key.space)
            #     except Exception:F
            #         pass

                # --- periodic "got a fish" check every got_check_interval seconds ---
                now = time.time()
                if now - last_got_check >= got_check_interval:
                    print("Performing periodic 'got a fish' check...")
                    last_got_check = now
                    try:
                        full_screen = np.array(sct.grab(monitor))
                        if gotAFish(full_screen, gotAFishImage):
                            print("Detected GOT A FISH -> returning to waiting state")
                            # press space to collect / close the UI
                            try:
                                press_space()
                            except Exception:
                                # fallback to pynput if SendInput fails
                                try:
                                    keyboard.press(Key.space); time.sleep(0.05); keyboard.release(Key.space)
                                except Exception:
                                    pass
                            # switch state and exit minigame/fishing loops
                            state = "waiting"
                            fishing = False
                            # ensure any held space is released
                            if 'space_pressed' in locals() and space_pressed:
                                try:
                                    keyboard.release(Key.space)
                                except Exception:
                                    pass
                            break
                    except Exception as e:
                        print("Error during gotAFish check:", e)




print("Program ended.")