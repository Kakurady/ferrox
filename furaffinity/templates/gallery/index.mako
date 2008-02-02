<%namespace name="lib" file="/lib.mako"/>
<%inherit file="base.mako" />

<div class="basic-box xFINISHME">
    <h2>Browse Artwork</h2>

    % if c.is_mine:
    <p class="admin"> ${h.link_to('Submit Art', h.url(controller='gallery', action='submit', username=c.auth_user.username))} </p>
    % endif
    % if c.submissions:
        % for item in c.submissions:
        <div class="submission">
            <div class="submission_header">
                <div class="submission_title">${h.link_to(item['title'], h.url(controller='gallery', action='view', id=item['id'], username=item['username']))}</div>
                <div class="submission_date">Date: ${h.format_time(item['date'])}</div>
            </div>
            <div class="submission_info">
                ${item['description']}<br>
                % if item['thumbnail'] != None:
                <div class="submission_thumbnail">${h.image_tag(h.url_for(controller='gallery', action='file', filename=item['thumbnail']), item['title'])}</div>
                % endif
            </div>
        </div>
        % endfor
    % else:
    <p> There are no submissions. </p>
    % endif
</div>

<%def name="title()">Browse Artwork</%def>


