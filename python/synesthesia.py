import vim
import re
import hashlib

NUM_COLORS = 256
HILIGHTED_WORD_SETS = {}

def create_hilight_groups():
    for i in range(NUM_COLORS):
        type = 'fg'
        color_type = 'cterm'
        cmd = 'hi! def _synethesia' + str(i) +  ' ' + color_type + type + '=' + str(i)
        vim.command(cmd)

def init():
    create_hilight_groups()
    return 1

def word_to_hilight_index(word):
    digest = hashlib.md5(word).digest()
    hash = ord(digest[-2]) * 16 + ord(digest[-1])
    return hash % NUM_COLORS

def hilight_current_buffer():
    global HILIGHTED_WORD_SETS

    b = vim.current.buffer

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
        cmd = 'syn keyword _synethesia' + hilight_index + " " + word
        vim.command(cmd)