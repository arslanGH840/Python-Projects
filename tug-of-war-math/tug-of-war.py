"""
=======================================================================
  TUG OF WAR MATH – Educational Math Game for Kids (Ages 6–12)
=======================================================================
  SETUP:   pip install pygame
  RUN:     python tug_of_war_math.py

  CONTROLS
  --------
  Mouse:    Click any answer button
  Player 1: A / S / D / F  →  Answers 1 / 2 / 3 / 4
  Player 2: J / K / L / ;  →  Answers 1 / 2 / 3 / 4  (2-player mode only)

  ESC: Return to main menu during a game
  SPACE / ENTER: Play Again (on win screen)

  HOW TO PLAY
  -----------
  • Each team takes turns answering a math question
  • Correct answer → rope flag pulls toward YOUR side
  • Wrong answer   → rope flag pulls toward OPPONENT'S side
  • 3 wrong answers in a row → rope jumps 3 steps toward opponent!
  • First team to pull the flag past their win line WINS!
=======================================================================
"""

import pygame          # Game library — install with: pip install pygame
import random          # Random numbers (for questions and AI)
import math            # Math functions (sine waves, trig)
import sys             # System exit
import struct          # Binary packing (for sound generation)

# ══════════════════════════════════════════════════════════════════════
#   STEP 1: INITIALIZE PYGAME
#   Must happen before any other pygame calls
# ══════════════════════════════════════════════════════════════════════
pygame.init()

# Try to start the audio mixer; if no audio device exists, carry on silently
SOUND_OK = False
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=1024)
    SOUND_OK = True
except Exception:
    pass

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Tug of War Math!")
clock = pygame.time.Clock()


# ══════════════════════════════════════════════════════════════════════
#   STEP 2: CONSTANTS
#   ← Change these values to customize the game without touching logic!
# ══════════════════════════════════════════════════════════════════════

SCREEN_W, SCREEN_H = 800, 600
FPS = 60

# ── Color Palette ──────────────────────────────────────────────────────
WHITE       = (255, 255, 255)
BLACK       = (  0,   0,   0)
RED         = (220,  55,  55)
DARK_RED    = (155,  20,  20)
BLUE        = ( 55, 105, 225)
DARK_BLUE   = ( 25,  55, 170)
GREEN       = ( 50, 200,  80)
DARK_GREEN  = ( 25, 140,  50)
YELLOW      = (255, 220,   0)
ORANGE      = (255, 145,   0)
PURPLE      = (150,  55, 200)
PINK        = (255, 105, 180)
CYAN        = (  0, 200, 225)
GRAY        = (155, 155, 155)
DARK_GRAY   = ( 75,  75,  75)
LIGHT_GRAY  = (210, 210, 210)
GOLD        = (255, 215,   0)

SKY_TOP     = ( 70, 150, 255)   # Sky gradient: top
SKY_BOT     = (170, 220, 255)   # Sky gradient: horizon
GROUND_COL  = ( 80, 170,  55)   # Grass
GROUND_DRK  = ( 55, 125,  35)   # Dark grass

ROPE_MID    = (155,  95,  30)   # Rope main color (brown)
ROPE_DRK    = ( 95,  55,  15)   # Rope shadow
ROPE_LIT    = (210, 155,  75)   # Rope highlight

T1_MAIN     = (220,  60,  60)   # Team 1 = Red team
T1_DRK      = (155,  25,  25)
T1_LIT      = (255, 160, 155)
T2_MAIN     = ( 55,  90, 225)   # Team 2 = Blue team
T2_DRK      = ( 25,  50, 165)
T2_LIT      = (155, 180, 255)

BTN_BASE    = (255, 205,  50)   # Answer button: normal (gold)
BTN_HOVER   = (255, 235, 100)   # Answer button: hovered
BTN_SHAD    = (165, 125,  15)   # Answer button: shadow
BTN_OK      = ( 50, 200,  80)   # Correct answer flash (green)
BTN_WRONG   = (220,  60,  60)   # Wrong answer flash (red)

TIMER_OK    = ( 50, 220,  80)   # Timer bar: plenty of time
TIMER_WARN  = (255, 200,  30)   # Timer bar: getting low
TIMER_LOW   = (220,  55,  55)   # Timer bar: almost out!

# Confetti colors for win screen
CONFETTI_COLORS = [
    (255,  50,  50), ( 50, 105, 255), ( 50, 200,  80),
    (255, 220,   0), (255, 105, 180), (  0, 200, 225),
    (150,  55, 200), (255, 145,   0),
]

# ── Gameplay Settings ──────────────────────────────────────────────────
ROPE_STEPS           = 7     # Steps to each win line (range = −7 … +7)
WRONG_STREAK_LIMIT   = 3     # Consecutive wrong answers before penalty
WRONG_STREAK_PENALTY = 3     # Steps the rope jumps on streak penalty
QUESTION_TIME        = 10.0  # Seconds per question
AI_ACCURACY          = 0.70  # Probability (0–1) the computer answers correctly
AI_DELAY             = 2.0   # Seconds the AI waits before answering
LEVEL_UP_QUESTIONS   = 5     # Questions answered before difficulty increases
FEEDBACK_DUR         = 1.6   # Seconds to show the "Correct!" / "Try again!" message
ROPE_ANIM_SPEED      = 7     # Pixels per frame the rope flag slides

# ── Screen Layout ──────────────────────────────────────────────────────
ROPE_Y     = 220     # Y center of the rope (pixels from top)
GROUND_Y   = 265     # Y of the ground level
CENTER_X   = 400     # Horizontal center of screen
P1_LINE_X  = 118     # Left win-line X (Team 1 aims for this)
P2_LINE_X  = 682     # Right win-line X (Team 2 aims for this)
# Pixels per rope step: (682-118) / 14 ≈ 40.3 px
STEP_PX    = (P2_LINE_X - P1_LINE_X) / (ROPE_STEPS * 2)

P1_CHAR_X  = 68      # Team 1 character center X
P2_CHAR_X  = 732     # Team 2 character center X

TIMER_X, TIMER_Y = 165, 375
TIMER_W, TIMER_H = 470,  20

# Answer button grid: 2 columns × 2 rows
ANS_W, ANS_H = 178, 63
_ax1 = CENTER_X - ANS_W - 8    # Column 1 left edge
_ax2 = CENTER_X + 8             # Column 2 left edge
_ay1 = 405                      # Row 1 top
_ay2 = _ay1 + ANS_H + 10       # Row 2 top (10 px gap)
ANS_RECTS = [
    pygame.Rect(_ax1, _ay1, ANS_W, ANS_H),   # Button 0 (top-left)
    pygame.Rect(_ax2, _ay1, ANS_W, ANS_H),   # Button 1 (top-right)
    pygame.Rect(_ax1, _ay2, ANS_W, ANS_H),   # Button 2 (bottom-left)
    pygame.Rect(_ax2, _ay2, ANS_W, ANS_H),   # Button 3 (bottom-right)
]

# Keyboard shortcuts for answer buttons
P1_KEYS   = [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f]
P2_KEYS   = [pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_SEMICOLON]
P1_LABELS = ['A', 'S', 'D', 'F']
P2_LABELS = ['J', 'K', 'L', ';']

# Encouraging messages shown after each answer
CORRECT_MSGS = ["Great job! ⭐", "Awesome! 🎉", "Brilliant! 💪",
                 "Correct! 🌟",  "Amazing! 🔥", "Superstar! ✨"]
WRONG_MSGS   = ["Try again! 💪", "Almost! 🤔", "Keep going! 😊",
                 "You got this!", "Don't give up!", "Next time! 👍"]
STREAK_MSGS  = ["3 wrong = BIG pull! 😱", "Penalty! Back 3 steps! 😬",
                 "Uh oh! Giant jump! 😅"]

TEAM_NAMES   = ["Team Red 🔴", "Team Blue 🔵"]
AI_NAME      = "Computer 🤖"


# ══════════════════════════════════════════════════════════════════════
#   STEP 3: FONTS
#   Comic Sans MS is loaded because it's kid-friendly and rounded.
#   If it's not installed, pygame falls back to its default font.
# ══════════════════════════════════════════════════════════════════════
_FN       = "Comic Sans MS"
FONT_HUGE = pygame.font.SysFont(_FN, 58, bold=True)
FONT_BIG  = pygame.font.SysFont(_FN, 38, bold=True)
FONT_MED  = pygame.font.SysFont(_FN, 30, bold=True)
FONT_SM   = pygame.font.SysFont(_FN, 22, bold=True)
FONT_TINY = pygame.font.SysFont(_FN, 16)


# ══════════════════════════════════════════════════════════════════════
#   STEP 4: SOUND GENERATION
#   We synthesize all sounds using math — no external audio files needed!
#   A "sound" is just a sequence of numbers (-32768 to 32767) that
#   represent air-pressure oscillations, saved as raw bytes.
# ══════════════════════════════════════════════════════════════════════
_SR = 22050   # Sample rate: 22,050 samples per second

def _buf(freq, dur, vol=0.42, wave='sine'):
    """
    Generate a single musical note as raw 16-bit mono PCM bytes.

    freq : pitch in Hz  (middle C = 261.6, A = 440)
    dur  : duration in seconds
    vol  : loudness 0.0 – 1.0
    wave : 'sine' (smooth, warm) or 'square' (buzzy retro/chiptune)
    """
    n    = int(_SR * dur)      # total number of samples
    data = bytearray(n * 2)    # 2 bytes per 16-bit sample
    for i in range(n):
        t   = i / _SR          # time in seconds for this sample
        # Simple ADSR-like envelope: quick attack, sustained middle, quick release
        env  = min(1.0, i       / max(1, _SR * 0.008))   # attack  (8 ms ramp-up)
        env *= min(1.0, (n - i) / max(1, _SR * 0.04))    # release (40 ms ramp-down)
        # Generate the waveform
        s = math.sin(2 * math.pi * freq * t)
        if wave == 'square':
            s = 1.0 if s >= 0 else -1.0    # square wave has hard transitions
        val = int(vol * 32767 * s * env)
        # Pack as little-endian signed 16-bit integer (the format pygame uses)
        struct.pack_into('<h', data, i * 2, max(-32768, min(32767, val)))
    return data


def _sound(*tones):
    """
    Concatenate several tone definitions into a single pygame Sound.
    Each tone is a tuple: (freq, dur)  or  (freq, dur, vol)  or  (freq, dur, vol, wave)
    Example: _sound((523, 0.1), (659, 0.1), (784, 0.2))
    """
    raw = bytearray()
    for t in tones:
        raw += _buf(*t)
    return pygame.mixer.Sound(buffer=bytes(raw))


def _init_sounds():
    """
    Pre-generate all sound effects at startup.
    Returns a dict of {name: pygame.mixer.Sound} or {} if audio is unavailable.
    """
    if not SOUND_OK:
        return {}
    try:
        s = {}
        # Happy ascending arpeggio for a correct answer
        s['correct'] = _sound((523,.09),(659,.09),(784,.12),(1047,.20))
        # Sad descending tones for a wrong answer
        s['wrong']   = _sound((330,.12),(247,.22))
        # Victory fanfare for winning
        s['win']     = _sound((523,.10),(523,.10),(523,.10),(659,.22),
                               (523,.12),(659,.15),(784,.48))
        # Low descending tones for the streak penalty
        s['penalty'] = _sound((220,.14),(196,.14),(165,.24))
        # Short blip for timer warning
        s['tick']    = _sound((880,.07,.20))

        # Background music: short chiptune loop (square wave = retro game feel)
        # Kept short (≈2.5 s) so it generates fast at startup
        bg = [
            (262,.20),(330,.20),(392,.20),(523,.20),
            (440,.20),(392,.20),(330,.20),(294,.20),
            (262,.40),(392,.20),(523,.40),(392,.20),
            (330,.20),(294,.20),(262,.40),
        ]
        s['music'] = _sound(*[(f, d, .14, 'square') for f, d in bg])
        return s
    except Exception:
        return {}   # silently continue if sound fails


# Pre-generate sounds once at startup (this may take ~1-2 seconds)
print("Loading sounds...")
SOUNDS = _init_sounds()
print("Ready! Starting game...")


def play(name):
    """Play a named sound effect. Silent if unavailable."""
    try:   SOUNDS[name].play()
    except Exception: pass


def play_music():
    """Start looping the background music track."""
    try:   SOUNDS['music'].play(-1)   # -1 = loop forever
    except Exception: pass


def stop_music():
    """Stop the background music."""
    try:   SOUNDS['music'].stop()
    except Exception: pass


# ══════════════════════════════════════════════════════════════════════
#   STEP 5: QUESTION GENERATOR
#   Creates age-appropriate math problems with 4 multiple-choice answers.
# ══════════════════════════════════════════════════════════════════════
def generate_question(level):
    """
    Create a math question for the given difficulty level.

    Level 1 : 1-digit + 1-digit addition            e.g.  3 + 7 = ?
    Level 2 : 2-digit + or - 1-digit                e.g. 24 - 5 = ?
    Level 3 : 2-digit × 1-digit multiplication      e.g. 13 × 4 = ?

    Returns a tuple: (question_string, correct_answer_int, [4 choice ints])
    The correct answer is placed at a random position in the choices list.
    """
    if level == 1:
        a, b   = random.randint(1, 9), random.randint(1, 9)
        answer = a + b
        q      = f"{a}  +  {b}  =  ?"

    elif level == 2:
        a  = random.randint(11, 99)
        b  = random.randint(2,  9)
        op = random.choice(['+', '-'])
        if op == '-':
            a = max(a, b + 2)          # ensure the result is always positive
        answer = a + b if op == '+' else a - b
        q      = f"{a}  {op}  {b}  =  ?"

    else:   # level 3
        a      = random.randint(11, 19)   # smaller range makes it still solvable
        b      = random.randint(2,  9)
        answer = a * b
        q      = f"{a}  ×  {b}  =  ?"

    # Build 3 wrong-but-plausible "distractor" answers
    wrong = set()
    while len(wrong) < 3:
        delta = random.choice([-5, -3, -2, -1, 1, 2, 3, 5, -8, 8, -10, 10])
        d = answer + delta
        if d != answer and d > 0:
            wrong.add(d)

    choices = list(wrong) + [answer]
    random.shuffle(choices)            # put correct answer at random position
    return q, answer, choices


# ══════════════════════════════════════════════════════════════════════
#   STEP 6: CONFETTI PARTICLE
#   Simple falling rectangles for the win-screen celebration.
# ══════════════════════════════════════════════════════════════════════
class Particle:
    """One piece of confetti that falls from the top of the screen."""

    def __init__(self, scatter=False):
        """
        scatter=True  : spawn at a random Y (fills screen immediately on win)
        scatter=False : spawn above the top edge (falls in naturally)
        """
        self._spawn(scatter)

    def _spawn(self, scatter=False):
        self.x   = random.randint(0, SCREEN_W)
        self.y   = random.randint(0, SCREEN_H) if scatter else random.randint(-70, -5)
        self.vx  = random.uniform(-2.2, 2.2)    # horizontal drift
        self.vy  = random.uniform(2.8,  6.5)    # fall speed
        self.col = random.choice(CONFETTI_COLORS)
        self.w   = random.randint(8, 20)         # confetti piece width
        self.h   = random.randint(4, 10)         # confetti piece height

    def update(self):
        """Move the particle down each frame, with slight horizontal drift."""
        self.x += self.vx + random.uniform(-0.15, 0.15)
        self.y += self.vy
        if self.y > SCREEN_H + 20:
            self._spawn()   # respawn above screen when it falls off the bottom

    def draw(self, surf):
        """Draw as a small colored rectangle."""
        pygame.draw.rect(surf, self.col,
                         (int(self.x) - self.w // 2,
                          int(self.y) - self.h // 2,
                          self.w, self.h))


# ══════════════════════════════════════════════════════════════════════
#   STEP 7: PRE-RENDER BACKGROUND SKY
#   Drawing a gradient from scratch each frame is slow; do it once here.
# ══════════════════════════════════════════════════════════════════════
_sky_h    = GROUND_Y + 25
_sky_surf = pygame.Surface((SCREEN_W, _sky_h))
for _i in range(_sky_h):
    _t = _i / _sky_h
    # Linear interpolation between SKY_TOP and SKY_BOT colors
    _c = tuple(int(SKY_TOP[k] * (1 - _t) + SKY_BOT[k] * _t) for k in range(3))
    pygame.draw.line(_sky_surf, _c, (0, _i), (SCREEN_W, _i))


# ══════════════════════════════════════════════════════════════════════
#   STEP 8: DRAWING UTILITIES
#   Small helper functions used throughout the game.
# ══════════════════════════════════════════════════════════════════════
def rnd_rect(surf, color, rect, r=14):
    """
    Draw a filled rectangle with rounded corners.
    rect can be a pygame.Rect or a plain (x, y, w, h) tuple.
    r = corner radius in pixels.
    """
    if isinstance(rect, pygame.Rect):
        x, y, w, h = rect.x, rect.y, rect.w, rect.h
    else:
        x, y, w, h = rect
    r = min(r, w // 2, h // 2)
    # Fill the cross-shaped interior first
    pygame.draw.rect(surf, color, (x + r, y,     w - 2 * r, h))
    pygame.draw.rect(surf, color, (x,     y + r, w,         h - 2 * r))
    # Then draw a circle at each corner to round it
    for cx, cy in [(x+r, y+r), (x+w-r, y+r), (x+r, y+h-r), (x+w-r, y+h-r)]:
        pygame.draw.circle(surf, color, (cx, cy), r)


def txt(surf, text, font, color, cx, cy, shadow=True):
    """
    Render text centered at pixel position (cx, cy).
    shadow=True adds a dark drop-shadow 2px down-right for readability.
    """
    if shadow:
        ss = font.render(text, True, (0, 0, 0))
        surf.blit(ss, ss.get_rect(center=(cx + 2, cy + 2)))
    ts = font.render(text, True, color)
    surf.blit(ts, ts.get_rect(center=(cx, cy)))


def draw_btn(surf, rect, label, font, col, hcol, shad, mouse, active=True):
    """
    Draw a 3D-looking rounded button with shadow, body, and highlight strip.
    Returns True if the mouse is hovering over it (useful for click detection).
    active=False grays out the button (e.g. when it's not your turn).
    """
    r   = pygame.Rect(rect)
    hov = active and r.collidepoint(mouse)
    fc  = hcol if hov else col
    if not active:
        fc = LIGHT_GRAY

    rnd_rect(surf, shad if active else DARK_GRAY, (r.x+3, r.y+5, r.w, r.h), 16)  # shadow
    rnd_rect(surf, fc, r, 16)                                                       # body
    hi = tuple(min(255, c + 55) for c in fc)
    rnd_rect(surf, hi, (r.x+5, r.y+3, r.w-10, r.h//3), 10)                        # highlight
    txt(surf, label, font, BLACK if active else DARK_GRAY, r.centerx, r.centery)
    return hov


# ══════════════════════════════════════════════════════════════════════
#   STEP 9: CHARACTER DRAWING
#   Cartoon characters drawn with basic pygame shapes (circles, lines, etc.)
#   Each character has 3 emotional states: normal, cheering, and sad.
# ══════════════════════════════════════════════════════════════════════
def draw_char(surf, cx, feet_y, team, state='normal'):
    """
    Draw a cute cartoon character at the given position.

    cx     : horizontal center of the character (pixels)
    feet_y : Y position of the character's feet (they grow upward from here)
    team   : 0 = Red team (faces right) | 1 = Blue team (faces left)
    state  : 'normal' | 'cheering' (arms up, happy face) | 'sad' (arms down, frown)
    """
    # Choose color scheme based on team
    mc  = T1_MAIN if team == 0 else T2_MAIN   # main color
    dc  = T1_DRK  if team == 0 else T2_DRK    # dark accent (hair, outline)
    lc  = T1_LIT  if team == 0 else T2_LIT    # light accent (skin, shirt shine)
    fd  = 1 if team == 0 else -1              # facing direction (+1=right, -1=left)

    # Apply jump offset for the 'jumping' state (unused currently, easy to add)
    fy  = feet_y - (18 if state == 'jumping' else 0)

    # ── Feet ──────────────────────────────────────────────
    pygame.draw.ellipse(surf, dc, (cx-20, fy-4, 18, 8))    # left foot
    pygame.draw.ellipse(surf, dc, (cx+2,  fy-4, 18, 8))    # right foot

    # ── Legs (two thick lines) ─────────────────────────────
    pygame.draw.line(surf, dc, (cx-10, fy-4),  (cx-12, fy-26), 7)
    pygame.draw.line(surf, dc, (cx+10, fy-4),  (cx+12, fy-26), 7)

    # ── Body (oval torso + shirt highlight) ───────────────
    pygame.draw.ellipse(surf, mc, (cx-17, fy-70, 34, 46))
    pygame.draw.ellipse(surf, lc, (cx-11, fy-66, 20, 24))  # shirt shine spot

    # ── Arms ──────────────────────────────────────────────
    ah = fy - 65    # arm attachment height (≈ where rope is held)
    if state == 'cheering':
        # Both arms raised up high — victory pose!
        pygame.draw.line(surf, dc, (cx-14, ah), (cx-32, ah-28), 7)
        pygame.draw.line(surf, dc, (cx+14, ah), (cx+32, ah-28), 7)
    elif state == 'sad':
        # Both arms drooping down — losing pose
        pygame.draw.line(surf, dc, (cx-14, ah), (cx-26, ah+22), 7)
        pygame.draw.line(surf, dc, (cx+14, ah), (cx+26, ah+22), 7)
    else:
        # Normal: one arm forward gripping rope, one arm pulling back
        pygame.draw.line(surf, dc, (cx - fd*14, ah),
                                   (cx - fd*30, ah-8),  7)   # back arm
        pygame.draw.line(surf, dc, (cx + fd*14, ah),
                                   (cx + fd*36, ah-4),  7)   # forward arm (gripping rope)

    # ── Head ──────────────────────────────────────────────
    hy = fy - 90    # head center Y
    pygame.draw.circle(surf, lc, (cx, hy), 22)       # face (skin)
    pygame.draw.circle(surf, mc, (cx, hy), 22, 3)    # colored outline

    # ── Hair (three bumps at the top) ─────────────────────
    for hbx, hbr in [(-7, 10), (0, 11), (7, 10)]:
        pygame.draw.circle(surf, dc, (cx + hbx, hy - 18), hbr)

    # ── Face ──────────────────────────────────────────────
    ey  = hy - 4    # eye level (slightly above head center)
    eox = 7         # eye offset from center
    el  = (cx - eox, ey)   # left eye center
    er  = (cx + eox, ey)   # right eye center

    if state == 'cheering':
        # Closed happy arc eyes (like  ^^ )
        pygame.draw.arc(surf, BLACK, (el[0]-5, el[1]-3, 10, 8), 0, math.pi, 3)
        pygame.draw.arc(surf, BLACK, (er[0]-5, er[1]-3, 10, 8), 0, math.pi, 3)
        # Big wide smile
        pygame.draw.arc(surf, BLACK, (cx-11, ey+5, 22, 13), math.pi, 2*math.pi, 3)
        # Rosy cheeks
        pygame.draw.circle(surf, PINK, (cx-13, ey+7), 5)
        pygame.draw.circle(surf, PINK, (cx+13, ey+7), 5)

    elif state == 'sad':
        # Open eyes (circles)
        pygame.draw.circle(surf, BLACK, el, 4)
        pygame.draw.circle(surf, BLACK, er, 4)
        pygame.draw.circle(surf, WHITE, (el[0]+1, el[1]-1), 1)   # eye glint
        # Frown (upside-down smile arc)
        pygame.draw.arc(surf, BLACK, (cx-10, ey+8, 20, 12), 0, math.pi, 3)
        # Tear drop
        pygame.draw.circle(surf, CYAN, (cx - eox + 3, ey + 14), 3)

    else:   # normal / pulling face
        pygame.draw.circle(surf, BLACK, el, 4)
        pygame.draw.circle(surf, BLACK, er, 4)
        pygame.draw.circle(surf, WHITE, (el[0]+1, el[1]-1), 1)   # left glint
        pygame.draw.circle(surf, WHITE, (er[0]+1, er[1]-1), 1)   # right glint
        # Small neutral smile
        pygame.draw.arc(surf, BLACK, (cx-8, ey+5, 16, 10), math.pi, 2*math.pi, 2)


# ══════════════════════════════════════════════════════════════════════
#   STEP 10: SCENE DRAWING (background, ground, rope, flag)
# ══════════════════════════════════════════════════════════════════════
def draw_scene(surf, flag_x):
    """
    Draw the play area: sky, clouds, ground, win-line posts, rope, and flag.
    flag_x : current ANIMATED X position (pixels) of the center rope flag.
    """
    # Sky gradient (pre-rendered surface, just blit it)
    surf.blit(_sky_surf, (0, 0))

    # ── Clouds ────────────────────────────────────────────
    # Each cloud is 3 overlapping circles
    for cx, cy, r in [(140, 55, 36), (295, 38, 28), (560, 68, 38), (710, 44, 30)]:
        pygame.draw.circle(surf, WHITE, (cx, cy), r)
        pygame.draw.circle(surf, WHITE, (cx - r//2, cy+6), r - 8)
        pygame.draw.circle(surf, WHITE, (cx + r//2, cy+6), r - 8)

    # ── Ground ────────────────────────────────────────────
    gy = GROUND_Y + 12
    pygame.draw.rect(surf, GROUND_COL,  (0, gy, SCREEN_W, SCREEN_H - gy))
    pygame.draw.rect(surf, (100, 200, 65), (0, gy, SCREEN_W, 8))   # bright grass strip

    # ── Win-Line Posts (with team-colored pennant flags) ──
    for lx, team in [(P1_LINE_X, 0), (P2_LINE_X, 1)]:
        c = T1_MAIN if team == 0 else T2_MAIN
        # Wooden post
        pygame.draw.rect(surf, DARK_GRAY, (lx-3, GROUND_Y-82, 6, 96))
        # Triangular pennant
        fp = [(lx+3, GROUND_Y-82), (lx+30, GROUND_Y-70), (lx+3, GROUND_Y-58)]
        pygame.draw.polygon(surf, c, fp)
        pygame.draw.polygon(surf, BLACK, fp, 2)
        wl = FONT_TINY.render("WIN!", True, WHITE)
        surf.blit(wl, wl.get_rect(center=(lx+15, GROUND_Y-70)))
        # Dashed ground line showing the boundary
        for dy in range(gy, gy+20, 6):
            pygame.draw.line(surf, DARK_GRAY, (lx, dy), (lx, dy+3), 2)

    # ── Rope ──────────────────────────────────────────────
    rl = 82     # rope left  (near Team 1 hands)
    rr = 718    # rope right (near Team 2 hands)
    ry = ROPE_Y
    pygame.draw.line(surf, ROPE_DRK, (rl, ry+4), (rr, ry+4), 20)   # shadow
    pygame.draw.line(surf, ROPE_MID, (rl, ry),   (rr, ry),   18)   # body
    pygame.draw.line(surf, ROPE_LIT, (rl, ry-5), (rr, ry-5),  4)   # highlight
    # Twisted rope texture: diagonal stripes every 22 pixels
    for sx in range(rl, rr, 22):
        pygame.draw.line(surf, ROPE_DRK, (sx, ry-7), (sx+11, ry+6), 3)

    # ── Center Flag ───────────────────────────────────────
    fx = int(flag_x)
    pygame.draw.line(surf, DARK_GRAY, (fx, ROPE_Y-52), (fx, ROPE_Y+8), 4)   # pole
    fp = [(fx+2, ROPE_Y-52), (fx+28, ROPE_Y-39), (fx+2, ROPE_Y-26)]         # pennant
    pygame.draw.polygon(surf, RED,   fp)
    pygame.draw.polygon(surf, BLACK, fp, 2)


# ══════════════════════════════════════════════════════════════════════
#   STEP 11: HUD (Heads-Up Display — the top info bar)
# ══════════════════════════════════════════════════════════════════════
def draw_hud(surf, gs):
    """
    Draw the top status bar showing team names, current turn, level,
    and streak warning indicators.
    gs : the active GameState object
    """
    pygame.draw.rect(surf, (20, 20, 55), (0, 0, SCREEN_W, 38))   # dark banner

    t2name = AI_NAME if gs.mode == 'ai' else TEAM_NAMES[1]

    # Team name labels
    txt(surf, TEAM_NAMES[0], FONT_SM, T1_LIT, 140, 19, shadow=False)
    txt(surf, t2name,         FONT_SM, T2_LIT, 660, 19, shadow=False)

    # Streak warning (shown when a team has consecutive wrong answers)
    for ti, lx in [(0, 140), (1, 660)]:
        if gs.streak[ti] > 0:
            sc = ORANGE if gs.streak[ti] < WRONG_STREAK_LIMIT else RED
            wl = FONT_TINY.render(f"⚠ {gs.streak[ti]} wrong!", True, sc)
            surf.blit(wl, wl.get_rect(center=(lx, 31)))

    # Center: difficulty level + whose turn it is
    ll = FONT_TINY.render(f"Level {gs.level}", True, LIGHT_GRAY)
    surf.blit(ll, ll.get_rect(center=(CENTER_X, 10)))
    turn_name = TEAM_NAMES[0] if gs.turn == 0 else t2name
    turn_col  = T1_LIT        if gs.turn == 0 else T2_LIT
    tl = FONT_SM.render(f"{turn_name}'s turn!", True, turn_col)
    surf.blit(tl, tl.get_rect(center=(CENTER_X, 26)))


# ══════════════════════════════════════════════════════════════════════
#   STEP 12: QUESTION PANEL (question text, timer bar, answer buttons)
# ══════════════════════════════════════════════════════════════════════
def draw_question_panel(surf, gs, mouse):
    """
    Draw the question panel: math problem text, countdown timer bar,
    four answer buttons, and any active feedback message.
    gs    : active GameState
    mouse : current mouse position tuple (x, y) for button hover detection
    """
    # ── Question text background ───────────────────────────
    rnd_rect(surf, (20, 20, 60), (88, 308, 624, 56), 18)
    txt(surf, gs.question, FONT_BIG, YELLOW, CENTER_X, 336)

    # ── Timer bar ─────────────────────────────────────────
    ratio   = max(0.0, gs.time_left / QUESTION_TIME)
    bar_w   = int(TIMER_W * ratio)
    bar_col = TIMER_OK if ratio > 0.5 else (TIMER_WARN if ratio > 0.25 else TIMER_LOW)
    rnd_rect(surf, DARK_GRAY, (TIMER_X, TIMER_Y, TIMER_W, TIMER_H), 8)   # background
    if bar_w > 0:
        rnd_rect(surf, bar_col, (TIMER_X, TIMER_Y, bar_w, TIMER_H), 8)   # filled portion
    tl = FONT_TINY.render(f"{gs.time_left:.1f}s", True, WHITE)
    surf.blit(tl, (TIMER_X + TIMER_W + 8, TIMER_Y + 2))

    # ── Answer Buttons ────────────────────────────────────
    labels = P1_LABELS if gs.turn == 0 else P2_LABELS
    for i, rect in enumerate(ANS_RECTS):

        if gs.state == 'feedback':
            # Show which answer was correct and which was wrong
            if i == gs.flash_idx:
                col = BTN_OK if gs.flash_ok else BTN_WRONG
            elif gs.choices[i] == gs.answer:
                col = BTN_OK        # always reveal correct answer in green
            else:
                col = LIGHT_GRAY    # gray out unchosen wrong answers
            # Draw colored (not interactive) button during feedback
            rnd_rect(surf, BTN_SHAD, (rect.x+3, rect.y+5, rect.w, rect.h), 16)
            rnd_rect(surf, col, rect, 16)
            hi = tuple(min(255, c + 40) for c in col)
            rnd_rect(surf, hi, (rect.x+5, rect.y+3, rect.w-10, rect.h//3), 10)
            txt(surf, str(gs.choices[i]), FONT_MED, BLACK, rect.centerx, rect.centery)
        else:
            # Normal interactive button (highlights on hover)
            draw_btn(surf, rect, str(gs.choices[i]), FONT_MED,
                     BTN_BASE, BTN_HOVER, BTN_SHAD, mouse, active=True)

        # Keyboard shortcut hint in top-left corner of each button
        kl = FONT_TINY.render(f"[{labels[i]}]", True, DARK_GRAY)
        surf.blit(kl, (rect.x + 5, rect.y + 4))

    # ── Feedback message (e.g. "Great job! ⭐") ───────────
    if gs.feedback and gs.state == 'feedback':
        # Fade out as fb_timer approaches 0
        alpha = max(0, min(255, int(255 * gs.fb_timer / FEEDBACK_DUR)))
        msg = FONT_MED.render(gs.feedback, True, GOLD)
        msg.set_alpha(alpha)
        surf.blit(msg, msg.get_rect(center=(CENTER_X, 558)))

    # ── Keyboard hint at the very bottom ──────────────────
    hint = "Click buttons  ·  P1: A/S/D/F  ·  P2: J/K/L/;"
    hs = FONT_TINY.render(hint, True, GRAY)
    surf.blit(hs, hs.get_rect(center=(CENTER_X, 589)))


# ══════════════════════════════════════════════════════════════════════
#   STEP 13: GAME STATE CLASS
#   Holds ALL mutable state for one match and implements the game logic.
# ══════════════════════════════════════════════════════════════════════
class GameState:
    """
    Manages everything about the current match.

    Key concepts:
    - rope_pos  : integer from −ROPE_STEPS to +ROPE_STEPS
                  Negative = flag closer to Team 1's win line (left)
                  Positive = flag closer to Team 2's win line (right)
    - flag_x    : ANIMATED pixel X position of the rope flag
                  (smoothly follows rope_pos)
    - turn      : 0 = Team 1's turn, 1 = Team 2's turn
    - state     : 'answering' (waiting for input) | 'feedback' (showing result)
    - streak[]  : [Team1_wrong_streak, Team2_wrong_streak]
    """

    def __init__(self, mode):
        """
        mode : 'ai' (vs Computer AI) | 'pvp' (two local players)
        """
        self.mode = mode

        # Rope / Flag
        self.rope_pos  = 0                    # logical position −7 … +7
        self.flag_x    = float(CENTER_X)      # animated pixel X
        self._target_x = float(CENTER_X)      # where flag is heading

        # Teams & turns
        self.streak    = [0, 0]               # consecutive wrong answers per team
        self.turn      = 0                    # 0 = Team 1, 1 = Team 2
        self.q_count   = 0                    # total questions answered so far
        self.level     = 1                    # difficulty 1–3

        # Current question
        self.question  = ""
        self.answer    = 0
        self.choices   = []

        # State machine
        self.state     = 'answering'

        # Countdown timer
        self.time_left = QUESTION_TIME

        # AI countdown until it "thinks" of an answer
        self.ai_timer  = AI_DELAY

        # Feedback display
        self.feedback  = ""
        self.fb_timer  = 0.0
        self.flash_idx = -1      # which button index to color (−1 = none)
        self.flash_ok  = False   # True = green (correct), False = red (wrong)

        # Character animation states (one per team)
        self.char_state = ['normal', 'normal']

        # Generate the very first question
        self._new_question()

    # ────────────────────────────────────────────────────────
    # Private helpers
    # ────────────────────────────────────────────────────────

    def _pos_to_x(self, pos):
        """Convert a logical rope_pos integer to a pixel X coordinate."""
        return CENTER_X + pos * STEP_PX

    def _new_question(self):
        """Prepare a fresh question and reset per-question state."""
        # Level increases every LEVEL_UP_QUESTIONS questions, max 3
        self.level     = 1 + min(2, self.q_count // LEVEL_UP_QUESTIONS)
        self.question, self.answer, self.choices = generate_question(self.level)
        self.time_left  = QUESTION_TIME
        self.ai_timer   = AI_DELAY
        self.flash_idx  = -1
        self.state      = 'answering'
        self.char_state = ['normal', 'normal']

    def _apply_answer(self, team, correct):
        """
        Update rope position, wrong streak, and feedback after a team answers.

        team    : 0 or 1 (who answered)
        correct : True if they got it right
        """
        other = 1 - team   # the other team's index

        if correct:
            # Correct: pull flag toward THIS team's side
            # Team 0 is on the LEFT, so they pull the flag LEFT (negative direction)
            delta = -1 if team == 0 else +1
            self.streak[team] = 0
            self.char_state[team]  = 'cheering'
            self.char_state[other] = 'sad'
            self.feedback = random.choice(CORRECT_MSGS)
            play('correct')
        else:
            # Wrong: flag moves AWAY from this team (toward opponent)
            delta = +1 if team == 0 else -1
            self.streak[team] += 1
            self.char_state[team]  = 'sad'
            self.char_state[other] = 'cheering'
            self.feedback = random.choice(WRONG_MSGS)
            play('wrong')

            # Check for streak penalty (3 wrong in a row)
            if self.streak[team] >= WRONG_STREAK_LIMIT:
                delta *= WRONG_STREAK_PENALTY   # triple the punishment!
                self.streak[team] = 0
                self.feedback = random.choice(STREAK_MSGS)
                play('penalty')

        # Clamp rope position to valid range (−ROPE_STEPS … +ROPE_STEPS)
        self.rope_pos  = max(-ROPE_STEPS, min(ROPE_STEPS, self.rope_pos + delta))
        self._target_x = self._pos_to_x(self.rope_pos)

        # Enter feedback state: freeze input, show result message
        self.state    = 'feedback'
        self.fb_timer = FEEDBACK_DUR
        self.q_count += 1

    # ────────────────────────────────────────────────────────
    # Public interface (called from game_screen)
    # ────────────────────────────────────────────────────────

    def answer_idx(self, idx):
        """
        Called when the current player selects answer button at index idx (0–3).
        Does nothing if not currently in 'answering' state.
        """
        if self.state != 'answering':
            return
        correct = (self.choices[idx] == self.answer)
        self.flash_idx = idx
        self.flash_ok  = correct
        self._apply_answer(self.turn, correct)

    def update(self, dt):
        """
        Advance the game by dt seconds (called every frame).
        Returns: 'playing' | 'team1_win' | 'team2_win'
        """
        # ── Animate flag sliding to target position ────────────
        dx = self._target_x - self.flag_x
        if abs(dx) > 0.5:
            self.flag_x += math.copysign(min(abs(dx), ROPE_ANIM_SPEED), dx)
        else:
            self.flag_x = self._target_x

        # ── Answering state (waiting for player input) ─────────
        if self.state == 'answering':
            self.time_left -= dt

            # Play a tick sound in the last 3 seconds (once per second)
            if 0 < self.time_left <= 3.0:
                if int(self.time_left + dt) > int(self.time_left):
                    play('tick')

            # Time's up → counts as a wrong answer
            if self.time_left <= 0:
                self.time_left = 0.0
                self.flash_idx = -1
                self._apply_answer(self.turn, False)
                return 'playing'

            # AI thinking (only in 'ai' mode during Team 2's turn)
            if self.mode == 'ai' and self.turn == 1:
                self.ai_timer -= dt
                if self.ai_timer <= 0:
                    # AI randomly decides to answer correctly or not
                    if random.random() < AI_ACCURACY:
                        idx = self.choices.index(self.answer)     # pick correct
                    else:
                        bad = [i for i, c in enumerate(self.choices)
                               if c != self.answer]
                        idx = random.choice(bad)                  # pick wrong
                    self.flash_idx = idx
                    self.flash_ok  = (self.choices[idx] == self.answer)
                    self._apply_answer(1, self.choices[idx] == self.answer)

        # ── Feedback state (briefly showing result) ────────────
        elif self.state == 'feedback':
            self.fb_timer -= dt
            if self.fb_timer <= 0:
                # Check for win AFTER feedback so the animation plays out
                if self.rope_pos <= -ROPE_STEPS:
                    return 'team1_win'
                if self.rope_pos >= ROPE_STEPS:
                    return 'team2_win'
                # No winner yet → switch turns and ask new question
                self.turn = 1 - self.turn
                self._new_question()

        return 'playing'


# ══════════════════════════════════════════════════════════════════════
#   STEP 14: START SCREEN
# ══════════════════════════════════════════════════════════════════════
def start_screen():
    """
    Display the animated title screen.
    Returns 'ai' or 'pvp' depending on which mode the player chooses.
    """
    btn_ai   = pygame.Rect(CENTER_X - 215, 368, 200, 68)
    btn_pvp  = pygame.Rect(CENTER_X +  15, 368, 200, 68)
    btn_quit = pygame.Rect(CENTER_X -  75, 455, 150, 50)
    bob = 0.0   # angle for the bobbing title animation

    play_music()

    while True:
        dt    = clock.tick(FPS) / 1000.0
        bob  += dt * 2.2
        mouse = pygame.mouse.get_pos()

        # ── Handle events ──────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_ai.collidepoint(mouse):
                    stop_music(); return 'ai'
                if btn_pvp.collidepoint(mouse):
                    stop_music(); return 'pvp'
                if btn_quit.collidepoint(mouse):
                    pygame.quit(); sys.exit()

        # ── Draw ──────────────────────────────────────────
        screen.blit(_sky_surf, (0, 0))
        gy = GROUND_Y + 12
        pygame.draw.rect(screen, GROUND_COL, (0, gy, SCREEN_W, SCREEN_H - gy))
        pygame.draw.rect(screen, (100, 200, 65), (0, gy, SCREEN_W, 8))

        # Clouds
        for cx, cy, r in [(140, 55, 36), (295, 38, 28), (560, 68, 38), (710, 44, 30)]:
            pygame.draw.circle(screen, WHITE, (cx, cy), r)
            pygame.draw.circle(screen, WHITE, (cx-r//2, cy+6), r-8)
            pygame.draw.circle(screen, WHITE, (cx+r//2, cy+6), r-8)

        # Characters (both cheering on the title screen)
        draw_char(screen, 155, GROUND_Y+12, 0, 'cheering')
        draw_char(screen, 645, GROUND_Y+12, 1, 'cheering')

        # Decorative rope across the middle
        pygame.draw.line(screen, ROPE_DRK, (205, 215), (595, 215), 20)
        pygame.draw.line(screen, ROPE_MID, (205, 215), (595, 215), 16)
        pygame.draw.line(screen, ROPE_LIT, (205, 215), (595, 210),  4)
        for sx in range(205, 595, 22):
            pygame.draw.line(screen, ROPE_DRK, (sx, 208), (sx+11, 221), 3)

        # Bobbing title text
        by = int(math.sin(bob) * 9)
        txt(screen, "Tug of War",  FONT_HUGE, GOLD,   CENTER_X, 140 + by)
        txt(screen, "MATH!",       FONT_HUGE, ORANGE, CENTER_X, 200 + by)

        # Subtitle instructions
        txt(screen, "Answer math questions to pull the rope!", FONT_SM, WHITE,
            CENTER_X, 265)
        txt(screen, "First team past the WIN line wins! 🎉", FONT_SM,
            LIGHT_GRAY, CENTER_X, 292)

        # Mode selection buttons
        draw_btn(screen, btn_ai,   "vs Computer 🤖", FONT_SM,
                 T2_MAIN, T2_LIT, T2_DRK, mouse)
        draw_btn(screen, btn_pvp,  "2 Players 👥",   FONT_SM,
                 T1_MAIN, T1_LIT, T1_DRK, mouse)
        draw_btn(screen, btn_quit, "Quit",            FONT_SM,
                 GRAY, LIGHT_GRAY, DARK_GRAY, mouse)

        txt(screen, "P1: A/S/D/F keys  ·  P2: J/K/L/; keys  ·  or click!",
            FONT_TINY, GRAY, CENTER_X, 525, shadow=False)

        pygame.display.flip()


# ══════════════════════════════════════════════════════════════════════
#   STEP 15: GAME SCREEN
# ══════════════════════════════════════════════════════════════════════
def game_screen(mode):
    """
    Run one complete match from start to finish.
    mode    : 'ai' | 'pvp'
    Returns : 0 (Team 1 wins) | 1 (Team 2 wins) | -1 (ESC → back to menu)
    """
    gs = GameState(mode)
    play_music()

    while True:
        dt    = clock.tick(FPS) / 1000.0
        mouse = pygame.mouse.get_pos()

        # ── Handle events ──────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                # ESC → abandon match and go back to menu
                if event.key == pygame.K_ESCAPE:
                    stop_music(); return -1

                # Player 1 keyboard (always active on P1's turn)
                if gs.state == 'answering' and gs.turn == 0:
                    for i, k in enumerate(P1_KEYS):
                        if event.key == k:
                            gs.answer_idx(i)
                            break

                # Player 2 keyboard (pvp mode only, P2's turn)
                if gs.state == 'answering' and gs.turn == 1 and mode == 'pvp':
                    for i, k in enumerate(P2_KEYS):
                        if event.key == k:
                            gs.answer_idx(i)
                            break

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if gs.state == 'answering':
                    # Ignore mouse clicks during AI's turn (AI answers itself)
                    if not (mode == 'ai' and gs.turn == 1):
                        for i, rect in enumerate(ANS_RECTS):
                            if rect.collidepoint(mouse):
                                gs.answer_idx(i)
                                break

        # ── Update game logic ──────────────────────────────
        result = gs.update(dt)

        # ── Draw everything ────────────────────────────────
        draw_scene(screen, gs.flag_x)
        draw_char(screen, P1_CHAR_X, GROUND_Y + 12, 0, gs.char_state[0])
        draw_char(screen, P2_CHAR_X, GROUND_Y + 12, 1, gs.char_state[1])
        draw_hud(screen, gs)
        draw_question_panel(screen, gs, mouse)

        pygame.display.flip()

        # ── Check win condition ────────────────────────────
        if result == 'team1_win':
            stop_music(); return 0
        if result == 'team2_win':
            stop_music(); return 1


# ══════════════════════════════════════════════════════════════════════
#   STEP 16: WIN SCREEN
# ══════════════════════════════════════════════════════════════════════
def win_screen(winner, mode):
    """
    Celebrate the winning team with confetti and a big winner banner.
    winner  : 0 (Team 1 wins) | 1 (Team 2 wins)
    mode    : 'ai' | 'pvp'
    Returns : 'again' (replay same mode) | 'menu' (go to start screen)
    """
    # Create 150 confetti pieces: half already on screen, half above it
    particles = ([Particle(scatter=True)  for _ in range(75)] +
                 [Particle(scatter=False) for _ in range(75)])

    t2name    = AI_NAME if mode == 'ai' else TEAM_NAMES[1]
    win_name  = TEAM_NAMES[0] if winner == 0 else t2name
    win_color = T1_LIT        if winner == 0 else T2_LIT

    btn_again = pygame.Rect(CENTER_X - 215, 452, 200, 65)
    btn_menu  = pygame.Rect(CENTER_X +  15, 452, 200, 65)
    bob = 0.0

    play('win')
    play_music()

    while True:
        dt    = clock.tick(FPS) / 1000.0
        bob  += dt * 2.5
        mouse = pygame.mouse.get_pos()

        # ── Handle events ──────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    stop_music(); return 'menu'
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    stop_music(); return 'again'
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_again.collidepoint(mouse):
                    stop_music(); return 'again'
                if btn_menu.collidepoint(mouse):
                    stop_music(); return 'menu'

        # ── Draw ──────────────────────────────────────────
        screen.fill((15, 15, 45))   # deep dark background

        # Confetti rain
        for p in particles:
            p.update()
            p.draw(screen)

        # Winner banner panel (3 nested rounded rects for a glowing effect)
        rnd_rect(screen, (30, 30, 80),  (132, 132, 536, 294), 30)
        rnd_rect(screen, win_color,     (136, 136, 528, 286), 28)
        rnd_rect(screen, (22, 22, 68),  (146, 146, 508, 266), 24)

        by = int(math.sin(bob) * 10)
        txt(screen, "🎉  WINNER!  🎉", FONT_BIG,  GOLD,  CENTER_X, 220 + by)
        txt(screen, win_name,           FONT_HUGE, WHITE, CENTER_X, 290 + by)
        txt(screen, "Amazing math skills!",    FONT_SM, YELLOW, CENTER_X, 368)

        draw_btn(screen, btn_again, "Play Again 🔁", FONT_SM,
                 GREEN, (100, 255, 130), DARK_GREEN, mouse)
        draw_btn(screen, btn_menu,  "Main Menu 🏠",  FONT_SM,
                 ORANGE, (255, 195, 80), DARK_RED,   mouse)

        txt(screen, "SPACE or ENTER to play again",
            FONT_TINY, LIGHT_GRAY, CENTER_X, 535, shadow=False)

        pygame.display.flip()


# ══════════════════════════════════════════════════════════════════════
#   STEP 17: MAIN ENTRY POINT
#   Orchestrates the screen flow: Start → Game → Win → (repeat)
# ══════════════════════════════════════════════════════════════════════
def main():
    """
    The main game loop.
    Navigates between the three screens: start, game, and win.
    The player can ESC during a game to return to the start menu.
    """
    mode = start_screen()   # returns 'ai' or 'pvp'

    while True:
        winner = game_screen(mode)   # returns 0, 1, or −1 (back to menu)

        if winner == -1:
            # Player pressed ESC mid-game — go back to mode select
            mode = start_screen()
        else:
            # Show the win celebration screen
            outcome = win_screen(winner, mode)
            if outcome == 'again':
                pass   # same mode, play again immediately
            else:
                mode = start_screen()   # show mode select again


if __name__ == "__main__":
    main()
