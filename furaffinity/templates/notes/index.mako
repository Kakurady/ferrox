<%namespace name="lib" file="/lib.mako"/>
<%inherit file="base.mako" />

<ul class="mini-linkbar">
    <li>${h.link_to("%s Write" % h.image_tag('/images/icons/mail-message-new-32.png', ''), h.url(controller='notes', action='write', username=c.route['username']))}</li>
</ul>

<div class="basic-box">
    <h2>Inbox</h2>

    <table class="bare-table">
    <col class="status-icon"/>
    <col class="time"/>
    <col class="user"/>
    <col class="subject"/>
    % for note in c.notes_page:
    <tr>
        % if note.status == 'unread':
        <td> ${h.image_tag('/images/icons/mail-unread.png', 'Unread')} </td>
        % else:
        <td> </td>
        % endif
        <td> ${h.format_time(note.time)} </td>
        <td> ${lib.user_link(note.sender)} </td>
        <td> ${h.link_to(note.subject, h.url(controller='notes', action='view', username=c.page_owner.username, id=note.id))} </td>
    </tr>
    % endfor
    </table>

    <p> ${c.notes_nav} </p>
</div>

<%def name="title()">Inbox</%def>

