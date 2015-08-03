import vim
import re
import hashlib
from clut import *

CONSOLE_COLORS = []
GUI_COLORS = {}
NUM_COLORS = 0

HILIGHTED_WORD_SETS = {}
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

    override_colors = vim.eval('g:synesthesia_gui_color_table')

    for i in range(0, 256):
        console_color, hex_string = CLUT[i]
        console_color = str(int(console_color, 10))
        if console_color in override_colors:
            hex_string = override_colors[console_color]
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

A     =  3141515926
B     =  2718281828
PRIME = 22801763489

def djb2a(word):
    hash = 5381;
    for c in word:
        # faster version of (hash * 33 ^ c) using bitshifting
        hash = ((hash << 5) + hash) ^ ord(c)
        # cast to uint32, is there a better way to do this Python?
        hash = 0xFFFFFFFF & hash
    return hash

def word_to_hilight_index(word):
    hash = djb2a(word)
    # universal hash hash(x) = ((ax + b) mod p) mod m
    return ((hash * A + B) % PRIME) % NUM_COLORS

def get_word_regexp(ft):
    if ft == 'clojure':
        return r'[a-zA-Z_\-][a-zA-Z0-9_\-\>/\.]*'
    else:
        return r'[a-zA-Z_][a-zA-Z0-9_]*'

def get_syn_suffix(ft):
    if ft == 'php':
        return "containedin=phpBracketInString,phpVarSelector,phpClExpressions,phpIdentifier"
    else:
        return ''

def hilight_current_buffer():
    global HILIGHTED_WORD_SETS

    b = vim.current.buffer
    ft = b.options['ft']
    if ft in IGNORED_FILETYPES:
        return

    # TODO: use a bloom filter to save on memory usage
    hilighted_words = None
    if b.number not in HILIGHTED_WORD_SETS:
        HILIGHTED_WORD_SETS[b.number] = set()
    hilighted_words = HILIGHTED_WORD_SETS[b.number]

    word_set = set()
    for line in b:
        words = re.finditer(get_word_regexp(ft), line)
        for word in words:
            word = word.group(0)
            if len(word) > 0:
                word_set.add(word)

    for word in word_set:
        if word in hilighted_words:
            continue
        hilighted_words.add(word)
        hilight_index = str(word_to_hilight_index(word))
        cmd = 'syn keyword _synesthesia' + hilight_index + ' ' + get_syn_suffix(ft) + ' ' + word
        vim.command(cmd)

def clear_hilighted_words():
    global HILIGHTED_WORD_SETS

    b = vim.current.buffer
    if b.number in HILIGHTED_WORD_SETS:
        HILIGHTED_WORD_SETS[b.number].clear()
