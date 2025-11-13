# Dual-Night-Abyss-Fishing (DNAF)

Automated basic fishing helper for a game. Use at your own responsibility — running automation may violate game rules and can result in account penalties or bans.

## Contents
- DNAF.py
- area folders: `sewers/`, `purgatorio/`, `island/` (each must contain reference images)

## Required images (inside the chosen area folder) They should be already uploaded
- start.png
- fish.png
- topBar.png
- topFishingBar.png
- bottomFishingBar.png
- got_a_fish.png

## Requirements
- Python 3.8+
- Windows (script uses Win32 input)
- Packages:
  - numpy
  - mss
  - opencv-python
  - pyautogui
  - pynput
  - pydirectinput

Install dependencies:
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install numpy mss opencv-python pyautogui pynput pydirectinput
```

## Configure area
Open `DNAF.py` and set the `area` variable to the folder that matches your game UI. Edit these lines and leave only the desired area uncommented, for example:
```python
area = "sewers"
# area = "purgatorio"
# area = "island"
```
Make sure the chosen folder exists in the project root and contains the required images listed above.

## Run
From the project root in a PowerShell / Command Prompt with the virtualenv active:
```powershell
python DNAF.py
```
Give the script focus to the game window.

## Notes & warnings
- Use this script at your own risk. Automation may violate the game's terms of service and can lead to bans or penalties.
- Test carefully (use small runs / debug copies of images) before extended use.
- Suggestions and improvements are welcome — open an issue or send a patch.
