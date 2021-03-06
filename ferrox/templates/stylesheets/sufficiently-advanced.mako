body { background: ${c.colors['background']}; color: ${c.colors['text']}; font-family: Verdana, Helvetica, sans-serif; font-size: 11px; }

p { margin: 0.5em 0.25em; line-height: 1.33; }

a:link, a:visited { font-weight: bold; text-decoration: none; }
a:link { color: ${c.colors['link']}; }
a:visited { color: ${c.colors['link_visited']}; }
a:focus { color: ${c.colors['link_active']}; outline: 1px dotted ${c.colors['border']}; }
a:hover { color: ${c.colors['link_hover']}; }

#header { position: relative; min-height: 140px; }

#user { position: absolute; top: 0em; right: 0em; bottom: 0em; padding: 0.25em; text-align: right; }
#user input { vertical-align: middle; }
#user #messages { position: absolute; right: 0; bottom: 0; padding: 0.25em; }
#user #messages li { margin: 0; text-align: left; }
#user #messages li a { font-weight: normal; }
#user #messages li a img { margin-right: 3px; vertical-align: middle; }
#user #messages li.new a { font-weight: bold; font-size: 1.2em; }
#user #superpowers { margin: 0.5em 0; }

#logo { display: inline-block; }

#navigation { background: ${c.colors['border']}; padding: 1px 0; }
#navigation:after { display: block; clear: left; height: 0; visibility: hidden; content: 'vee was here'; }
#navigation ul { margin: 0; }
#navigation ul li { display: inline-block; background: ${c.colors['background']}; margin: 0 0.25em; }
#navigation ul li a { display: block; padding: 0.25em 1em; }
#navigation ul li a:hover { background: white; }
/* have to undo basic-box formatting that duality uses */
#site-nav,
#community-nav { margin: 0; float: left; vertical-align: middle; }
#search { margin: 0; float: right; vertical-align: middle; }
#site-nav h2,
#community-nav h2,
#search h2 { display: inline-block; margin-left: 3em; vertical-align: middle; font-size: 1em; font-weight: bold; color: ${c.colors['background']}; border-bottom: none; }
/* the rest is regular ol styling */
#site-nav ul,
#community-nav ul,
#search form { display: inline-block; vertical-align: middle; }
#search p { margin: 0; }
#search { margin-right: 1.5em; }
#search input[type='submit'] { display: none; }
#search input[type='text'] { height: 100%; padding: 0.17em 0.25em; font-size: 1em; font-family: inherit; border: 0; background: #d4dce8; }
#search input[type='text']:hover,
#search input[type='text']:focus { background: white; }

#ads { position: absolute; bottom: 0; right: 0; margin: 0.17em; }

#content { position: relative; margin: 0.75em; }

#footer { text-align: center; font-size: 0.8em; padding: 0.5em; border-top: 0.25em double ${c.colors['border']}; }

#shameless-whoring { position: absolute; left: 0.5em; }

#stats { position: relative; font-family: monospace; background: #d4e8e3; color: black; border: 1px solid black; margin: 0 33%; }
#stats #python-bar { position: absolute; width: 0; height: 100%; background: #e8e8d4; border-right: 1px dotted #c0c0c0; }
#stats p { position: relative; /* z-index context */ }

/******* FRONT PAGE *******/

#left-column { float: left; width: 66.6%; }
#right-column { float: right; width: 33.3%; }
#content:after { display: block; clear: both; visibility: hidden; height: 0; content: 'vee was here'; }

.right-tabs { float: right; }
.right-tabs + .right-tabs { margin-right: 2em; }




/*** pair of objects that float left and right ***/
.lr-left { float: left; width: 50%; }
.lr-right { float: right; width: 50%; }


/*** forms ***/

input[type='button'],
input[type='submit'],
input[type='reset'],
input[type='checkbox'],
input[type='radio'] { cursor: pointer; }



/*** widgets ***/

.basic-box { margin: 0.5em; }
.basic-box h2 { font-size: 2em; letter-spacing: 0.125em; color: ${c.colors['header']}; border-bottom: 1px solid ${c.colors['border_strong']}; }

/* journal/news entry */
.entry { padding: 0.5em; }
.entry + .entry { border-top: 1px solid ${c.colors['border']}; }
.entry .header { background: ${c.colors['background_alt']}; padding: 0.25em; }
.entry .header .title { float: left; font-size: 1.67em; font-weight: bold; color: ${c.colors['header2']}; }
.entry .header .avatar { float: right; }
.entry .header .avatar img { max-height: 50px; width: 50px; }
.entry .header .author { clear: left; }
.entry .header:after { content: 'vee was here'; display: block; height: 0; visibility: hidden; clear: both; }
.entry ul.inline.admin { display: block; float: right; }
.entry .content { padding: 0.5em; }

.entry.collapsed { padding: 0 0.5em; }
.entry.collapsed .header { padding: 0; }
.entry.collapsed .header .title { float: none; font-size: 1.33em; }
.entry.collapsed .header .title a { display: block; padding: 0.25em; }

.entry.comment .header { position: relative; min-height: 100px; }
.entry.comment .header .avatar { position: absolute; top: 0; left: 0; height: 100px; width: 100px; text-align: center; line-height: 100px; }
.entry.comment .header .avatar img { vertical-align: middle; }
.entry.comment .header .title,
.entry.comment .header .author,
.entry.comment .header .date { margin-left: 100px; }
.entry.comment .header .micro-linkbar { position: absolute; bottom: 0; left: 100px; right: 0; }

/* thumbnail grid tweaks*/
ul.thumbnail-grid { margin: 0 auto; clear: both; }
ul.thumbnail-grid li { float: none; display: inline-block; padding: 1em; }

/* standard tables */
table.bare-table tbody tr:hover { background: ${c.colors['background_hover']}; }

/* sub-link-bar */
.mini-linkbar { display: table /* shrinkwrap */; margin: 0.25em auto; }
.mini-linkbar li { display: table-cell; vertical-align: middle; border: 1px solid ${c.colors['border']}; border-left-style: dotted; border-right-width: 0; border-left-style: dotted; background: ${c.colors['background_alt']}; }
.mini-linkbar li:first-child { border-left-style: solid; }
.mini-linkbar li:last-child { border-right-width: 1px; }
.mini-linkbar li a { display: block; text-align: center; padding: 0.5em; }
.mini-linkbar li img { margin: 0 auto; vertical-align: text-bottom; }
.mini-linkbar li:hover { background: ${c.colors['background_hover']}; }
.mini-linkbar li.admin:before,
.mini-linkbar li.admin:after { content: none; }
.mini-linkbar li.admin { margin: -1px; border: 1px dotted #e87400; }
.mini-linkbar li.not-link { padding: 0.5em; background: transparent; border-top-color: transparent; border-bottom-color: transparent; }
.mini-linkbar li.not-link a { display: inline; padding: 0; }
.mini-linkbar li.not-link + li,
.mini-linkbar li + li.not-link { border-left-style: solid; }
.mini-linkbar li.not-link:first-child { border-left-width: 0; }
.mini-linkbar li.not-link:last-child { border-right-width: 0; }

/* basic-box linkbar, all in a row */
.micro-linkbar { background: ${c.colors['background_alt']}; border-top: 1px dotted ${c.colors['border']}; }
.micro-linkbar li { display: inline-block; margin: 0 0.5em; }
.micro-linkbar li a { display: block; padding: 0.25em 0.5em; vertical-align: middle; }
.micro-linkbar li img { vertical-align: middle; }
.micro-linkbar li:hover { background: ${c.colors['background_hover']}; }

