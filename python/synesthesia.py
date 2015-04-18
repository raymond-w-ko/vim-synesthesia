import vim
import re
import hashlib

NUM_COLORS = 256
HILIGHTED_WORDS = set()

def create_hilight_groups():
    for i in range(NUM_COLORS):
        type = 'fg'
        color_type = 'cterm'
        cmd = 'hi! def _synethesia' + str(i) +  ' ' + color_type + type + '=' + str(i)
        vim.command(cmd)

def init():
    create_hilight_groups()
    return 1

def word_to_color_index(word):
    digest = hashlib.md5(word).digest()
    hash = ord(digest[-2]) * 16 + ord(digest[-1])
    return hash % NUM_COLORS

def hilight_current_buffer():
    b = vim.current.buffer
    word_set = set()
    for line in b:
        words = re.split(r'\W+', line)
        for word in words:
            if len(word) > 0:
                word_set.add(word)

    for word in word_set:
        if word in HILIGHTED_WORDS:
            continue
        HILIGHTED_WORDS.add(word)
        index = str(word_to_color_index(word))
        cmd = 'syn keyword _synethesia' + index + " " + word
        vim.command(cmd)
