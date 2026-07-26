import shutil

PAUSE_SHORT = 2

term_width = shutil.get_terminal_size().columns
WIDTH = min(term_width, 80)
CENTER_MARGIN = max((term_width - WIDTH) // 2, 0)
MARGIN = 2
CONTENT_WIDTH = WIDTH - (MARGIN * 2)

# WIDTH is the target UI width inside the terminal bounds.
# CENTER_MARGIN is the left padding used to center the UI horizontally.
# MARGIN is the inset padding inside the centered UI body.
# CONTENT_WIDTH is the width available for wrapped body text and labels.

# ===== TWO-COLUMN CONSTANTS =====

TC_WIDTH = WIDTH//2
TC_CONTENT_WIDTH = TC_WIDTH - (MARGIN*2)
TC_CENTER_MARGIN = 0