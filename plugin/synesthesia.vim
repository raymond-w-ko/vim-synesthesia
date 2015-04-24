if exists("g:loaded_synesthesia") || v:version < 700 || &cp
  finish
  let g:loaded_synesthesia = 1
endif

if !exists('g:synesthesia_banned_console_colors')
  let g:synesthesia_banned_console_colors = []
endif

" load python code into synesthesia module
let s:python_dir = fnamemodify(expand("<sfile>"), ':p:h:h') . '/python'
let s:python_file = s:python_dir . 'synesthesia.py'
python << EOF
sys.path.append(vim.eval("s:python_dir"))
import synesthesia
synesthesia.init()
EOF

autocmd BufReadPost * python synesthesia.hilight_current_buffer()
autocmd BufWritePost * python synesthesia.hilight_current_buffer()
autocmd CursorHold * python synesthesia.hilight_current_buffer()
