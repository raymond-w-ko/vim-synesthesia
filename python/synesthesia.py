import vim
import re
import hashlib
from clut import *

CONSOLE_COLORS = []
GUI_COLORS = {}
NUM_COLORS = 0

HILIGHTED_WORD_SETS = {}
KEYWORD_SUFFIX = " containedin=phpBracketInString,phpVarSelector,phpClExpressions,phpIdentifier "
IGNORED_FILETYPES = frozenset([
'help',
])

def generate_console_colors():
    global CONSOLE_COLORS
    global NUM_COLORS
    global IGNORED_FILETYPES

    for i in range(256):
        CONSOLE_COLORS.append(i)

    banned_colors = list(vim.eval('g:synesthesia_banned_console_colors'))
    banned_colors = map(lambda x: int(x), banned_colors)
    CONSOLE_COLORS = list(set(CONSOLE_COLORS) - set(banned_colors))
    CONSOLE_COLORS.sort()
    NUM_COLORS = len(CONSOLE_COLORS)

    ignored_filetypes = set(IGNORED_FILETYPES)
    ignored_filetypes.update(set(list(vim.eval('g:synesthesia_ignored_filetypes'))))
    IGNORED_FILETYPES = frozenset(ignored_filetypes)

def generate_gui_colors():
    global GUI_COLORS

    for i in range(0, 256):
        console_color, hex_string = CLUT[i]
        GUI_COLORS[i] = '#' + hex_string

def create_hilight_groups():
    type = 'fg'

    color_type = None
    has_gui_running = vim.eval('has("gui_running")')
    if has_gui_running == '0':
        has_gui_running = False
        color_type = 'cterm'
    elif has_gui_running == '1':
        has_gui_running = True
        color_type = 'gui'
    else:
        assert(False)

    for i in range(NUM_COLORS):
        color = CONSOLE_COLORS[i]
        if has_gui_running:
            color = GUI_COLORS[color]
        cmd = 'hi! def _synesthesia' + str(i) +  ' ' + color_type + type + '=' + str(color)
        vim.command(cmd)

def init():
    generate_console_colors()
    generate_gui_colors()
    create_hilight_groups()
    return 0

def word_to_hilight_index(word):
    digest = hashlib.sha224(word).digest()
    hash = ord(digest[0])
    return hash % NUM_COLORS

def hilight_current_buffer():
    global HILIGHTED_WORD_SETS

    b = vim.current.buffer
    if b.options['ft'] in IGNORED_FILETYPES:
        return

    # TODO: use a bloom filter to save on memory usage
    hilighted_words = None
    if b.number not in HILIGHTED_WORD_SETS:
        HILIGHTED_WORD_SETS[b.number] = set()
    hilighted_words = HILIGHTED_WORD_SETS[b.number]

    word_set = set()
    for line in b:
        words = re.finditer(r'[a-zA-Z_][a-zA-Z0-9_]*', line)
        for word in words:
            word = word.group(0)
            if len(word) > 0:
                word_set.add(word)

    for word in word_set:
        if word in hilighted_words:
            continue
        hilighted_words.add(word)
        hilight_index = str(word_to_hilight_index(word))
        cmd = 'syn keyword _synesthesia' + hilight_index + KEYWORD_SUFFIX + word
        vim.command(cmd)
