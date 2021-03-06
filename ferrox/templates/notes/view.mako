<%namespace name="lib" file="/lib.mako"/>
<%inherit file="base.mako" />

<p>${h.HTML.a('&laquo; Inbox', href=h.url_for(controller='notes', action='user_index', username=c.page_owner.username))}</p>
% if c.note != c.latest_note:
<p>${h.HTML.a('Latest note in this conversation', href=h.url(controller='notes', action='view', username=c.route['username'], id=c.latest_note.id))}</p>
% endif
<div class="basic-box">
    <h2>Note</h2>

    % for note in c.all_notes:
    % if note.time >= c.latest_note.time or note == c.note:
    ${lib.note_entry(note, c.page_owner)}
    % else:
    ${lib.note_collapsed_entry(note, c.page_owner)}
    % endif
    % endfor
</div>

<%def name="title()">${c.note.title}</%def>

