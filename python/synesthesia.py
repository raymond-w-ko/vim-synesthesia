import vim
import re
import hashlib

CONSOLE_COLORS = []
NUM_COLORS = 0

HILIGHTED_WORD_SETS = {}
KEYWORD_SUFFIX = " containedin=phpBracketInString,phpVarSelector,phpClExpressions,phpIdentifier "
IGNORED_FILETYPES = frozenset(['help', 'text', 'diff'])

def generate_console_colors():
    global CONSOLE_COLORS
    global NUM_COLORS

    for i in range(257):
        CONSOLE_COLORS.append(i)

    banned_colors = list(vim.eval('g:synesthesia_banned_console_colors'))
    banned_colors = map(lambda x: int(x), banned_colors)
    CONSOLE_COLORS = list(set(CONSOLE_COLORS) - set(banned_colors))
    CONSOLE_COLORS.sort()
    NUM_COLORS = len(CONSOLE_COLORS)

def create_hilight_groups():
    for i in range(NUM_COLORS):
        type = 'fg'
        color_type = 'cterm'
        color = CONSOLE_COLORS[i]
        cmd = 'hi! def _synesthesia' + str(i) +  ' ' + color_type + type + '=' + str(color)
        vim.command(cmd)

def init():
    generate_console_colors()
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
