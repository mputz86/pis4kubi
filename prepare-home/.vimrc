set nocompatible                " make Vim behave in a more useful way, less vi compatible
filetype off                    " required!

let s:vimconfig='.vim'
let &rtp=&rtp.',~/'.s:vimconfig.'/bundle/vundle/'

call plug#begin('~/.vim/plugged')

Plug 'scrooloose/nerdtree'

Plug 'tpope/vim-surround'
Plug 'derekwyatt/vim-fswitch'
Plug 'BufOnly.vim'
Plug 'christoomey/vim-tmux-navigator'

call plug#end()

let g:editcommand_prompt = ']'       " default is '$'

filetype plugin indent on           " required!

" UI Stuff {
    syntax enable
    if has('gui_running')
      set guitablabel=%t            " only display the filename not the path
      set guioptions-=m             " remove [m]enubar
      set guioptions-=T             " remove [T]oolbar
      set cursorline                " highlight the screen line of the cursor
    else
    endif
    if has('statusline')
      set laststatus=2                         " always show statusline
      set statusline=%<%f\                     " Filename
      set statusline+=%w%h%m%r                 " Options
      set statusline+=\ [%{&ff}/%Y]            " filetype
      set statusline+=%=%-14.(%l,%c%V%)\ %p%%  " Right aligned file nav info
    endif
    if has('cmdline_info')
      set ruler                     " show the cursor position all the time
      set rulerformat=%30(%=\:b%n%y%m%r%w\ %l,%c%V\ %P%) " a ruler on steroids
      set showcmd                   " show (partial) command in the last line of the screen
    endif
" }
" basic settings {
    set backupdir=~/.vim/tmp
    set rnu                         " relative line numbers
    set wildignore+=*.o,*.obj,*.o.d,.git,*.a,*.s,tags
    set nofoldenable                " disable folding
    set showmode                    " always show what mode we're currently editing in
    set nowrap                      " don't wrap lines
    set tabstop=2                   " a tab is 2 spaces by default
    set softtabstop=2               " when hitting <BS>, pretend like a tab is removed, even if spaces
    set expandtab                   " expand tabs default
    set shiftwidth=2                " number of spaces to use for autoindenting
    set shiftround                  " use multiple of shiftwidth when indenting with '<' and '>'
    set backspace=indent,eol,start  " allow backspacing over everything in insert mode
    set autoindent                  " always set autoindenting on
    set copyindent                  " copy the previous indentation on autoindenting
    set ignorecase                  " ignore case when searching
    set smartcase                   " ignore case if all lowercase, otherwise case-sensitive
    set smarttab                    " insert tabs on the start of a line according to shiftwidth
    set scrolloff=3                 " keep off the edges of the screen when scrolling
    set virtualedit=block           " allow virtual editing in Visual block mode.
    set winminheight=0              " windows can be 0 line high
    set hlsearch                    " highlight search terms
    set incsearch                   " show search matches as you type
    set completeopt=longest,menuone,preview
    set wildmode=longest:full       " bash like filename completion
    set wildmenu                    " show possible completions for filenames
    set hidden
    set noswapfile                  " disable swapfiles
    set history=1000                " keep 1000 lines of command line history
    set smartindent                 " do smart autoindenting when starting a new line
    set vb                          " visual beep
    set autoread                    " reload file if permissions change due to BufWritePost below
    set autowrite                   " write file to disk on :make, :!, :first, :next
    set gcr=n:blinkon0              " turn of blinking cursor in normal mode
    set synmaxcol=800               " Don't try to highlight lines longer than 800 characters.
    set listchars=eol:$,tab:>-,trail:~,extends:>,precedes:<
" }
" general utilities {
    let mapleader="\<Space>"
    " quick way to escape from insert mode
    inoremap jj <ESC>
    " use :w!! to write to a file using sudo
    cnoremap w!! %!sudo tee > /dev/null %
    nnoremap<leader>l :set list!<CR>
    " Yank from the cursor to the end of the line, to be consistent with C and D.
    nnoremap Y y$
    " if pasted over visual selection, do not copy visual selection to unnamed
    " register
    xnoremap <leader>p "_dP
    " leave the cursor at the point where it was before editing started
    nnoremap . .`[
    noremap <F7> :call OpenInTerminal()<CR><CR>
    " Go to newer/older text state
    nnoremap <S-F11> g-
    nnoremap <S-F12> g+
    " Wrapped lines goes down/up to next row, rather than next line in file.
    nnoremap j gj
    nnoremap k gk
    execute 'nnoremap ,rc :vsplit ~/'.s:vimconfig.'/_vimrc_universal<CR>'
    nnoremap ,bc :e ~/.bashrc <CR>
    " move lines up and down
    nnoremap <M-Down> mz:m+<CR>`z==
    nnoremap <M-Up> mz:m-2<CR>`z==
    inoremap <M-Down> <Esc>:m+<CR>==gi
    inoremap <M-Up> <Esc>:m-2<CR>==gi
    vnoremap <M-Down> :m'>+<CR>gv=`<my`>mzgv`yo`z
    vnoremap <M-Up> :m'<-2<CR>gv=`>my`<mzgv`yo`z
    "
    " trailing whitespaces {
        " highlight end of line whitespace as Error
        hi link ExtraWhitespace Error
        augroup whitespaces " {
          autocmd!
          autocmd BufNewFile,BufRead,InsertLeave * match ExtraWhitespace /\s\+$/
          " except the line I am typing on
          autocmd InsertEnter * match ExtraWhitespace /\s\+\%#\@<!$/
          nnoremap <leader>c :call ClearWhitespaces()<CR>
        augroup END " }
    " }
    " directories and files {
        noremap ,cd :call SetWorkingDirToCurrentDir()<CR>
        " climb up one directory level
        noremap <leader>u :cd ..<CR>:pwd<CR>
        " Some helpers to edit mode (http://vimcasts.org/e/14)
        cnoremap %% <C-R>=expand('%:h').'/'<cr>
        noremap <leader>ew :e %%
        noremap <leader>es :sp %%
        noremap <leader>ev :vsp %%
        noremap <leader>et :tabe %%
        " prompt for opening files in the same dir as the current buffer's file.
        if has("unix")
          let g:os_specific_delimiter="/"
        else
          let g:os_specific_delimiter="\\"
        endif
        noremap ,e :e <C-R>=expand("%:p:h") . g:os_specific_delimiter <CR>
    " }
    " search and substitution {
        " use normal regexes in search
        nnoremap / /\v
        vnoremap / /\v
        " search for the keyword under the cursor in the current directory using the 'grep' command
        nnoremap <F8> :grep <C-R><C-W> *<CR>
        " search for visually highlighted text
        vnoremap // y/<C-R>"<CR>
        " Prepare a :substitute command using the current word or the selected text:
        vnoremap <F6> y:%s/\<<C-r>"\>//gc<Left><Left><Left>
        nnoremap <F6> y:%s/\<<C-r>=expand("<cword>")<CR>\>//gc<Left><Left><Left>
    " }
    " movement {
        " jump back and forth between the last 2 files
        inoremap <C-Tab> <Esc>:e#<CR>
        noremap <C-Tab> :e#<CR>
        inoremap <C-S-Tab> <Esc> :bp<CR>
        noremap <C-S-Tab> :bp<CR>
        " jump to next/previous quickfix
        nnoremap <F4> :cn<CR>
        inoremap <F4> <Esc>:cn<CR>a
        nnoremap <S-F4> :cp<CR>
        inoremap <S-F4> <Esc>:cp<CR>a
    " }
    " hippie occurrence {
        " highlight current word with <F12> and on mouse click
        nnoremap <LeftRelease> :let @/='\<<C-R>=expand("<cword>")<CR>\>'<CR>:set hls<CR>
        inoremap <LeftRelease> <Esc>:let @/='\<<C-R>=expand("<cword>")<CR>\>'<CR>:set hls<CR>li
        noremap <F12> :let @/='\<<C-R>=expand("<cword>")<CR>\>'<CR>:set hls<CR>
        inoremap <F12> <Esc>:let @/='\<<C-R>=expand("<cword>")<CR>\>'<CR>:set hls<CR>li
    " }
    " window handling {
        set splitbelow splitright " Create split windows in more intuitive places
        " [v]ertical or [h]orizontal split then hop to new buffer
        nnoremap <Leader>v :vsp<CR>^W^W<CR>
        nnoremap <Leader>h :split<CR>^W^W<CR>
        nnoremap <silent> ;; :call SwitchWindowKeepCurrentDir()<CR>
        vnoremap <silent> ;; :call SwitchWindowKeepCurrentDir()<CR>
        "Make current window the only one
        nnoremap <Leader>o :only<CR>
    " }
" }
" nerdtree {
    noremap <leader>d :execute 'NERDTreeToggle ' . getcwd()<CR><C-W>b
    noremap <leader>f :execute 'NERDTreeFind'<CR>
    let NERDTreeShowHidden=0  " display hidden files by default
    let NERDTreeChDirMode=2   " change dir to root of tree
" }
" Relative numbering {
    function! NumberToggle()
      if(&relativenumber == 1)
        set nornu
        set number
      else
        set rnu
      endif
    endfunc
    " Toggle between normal and relative numbering.
    nnoremap <leader>n :call NumberToggle()<CR>
" }
