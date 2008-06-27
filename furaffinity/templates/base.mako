<%namespace name="lib" file="/lib.mako"/>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <title>${self.title()} -- Fur Affinity [dot] net</title>
    <link rel="shortcut icon" type="image/png" href="/images/icons/pawprint.png"/>
    ${self.css_links()}
    ${self.javascript_includes()}
</head>
<body>
<p id="skip-to-content"><a href="#content">Skip to content</a></p>
<div id="header">
    <div id="user">
        % if c.auth_user.id == 0:
        <p>
            Welcome to FurAffinity! Please log in or
            ${h.link_to('register', h.url(controller='index', action='register'))}.
        </p>
        <p>(${h.link_to("Lost your password?", h.url(controller='index', action='lost_password'))})</p>
        ${c.empty_form.start(h.url(controller='index', action='login_check'), method='post')}
        <dl class="standard-form">
            <dt>Username</dt>
            <dd>${c.empty_form.text_field('username')}</dd>
            <dt>Password</dt>
            <dd>${c.empty_form.password_field('password')}</dd>
        </dl>
        ${c.empty_form.submit('Login')}
        ${c.empty_form.end()}
        % else:
        ${c.empty_form.start(h.url(controller='index', action='logout'), method='post')}
        <p>Welcome back, ${lib.user_link(c.auth_user)}!  ${c.empty_form.submit('Log out')}</p>
        ${c.empty_form.end()}
        <ul class="inline">
            <li>${h.link_to("Profile", h.url(controller='user', action='view', username=c.auth_user.username))}</li>
            <li>${h.link_to("Journal", h.url(controller='journal', action='index', username=c.auth_user.username))}</li>
            <li>${h.link_to("Gallery", h.url(controller='gallery', action='index', username=c.auth_user.username))}</li>
        </ul>
        <ul class="inline">
            <li>${h.link_to('Control Panel', h.url(controller='user_settings', action='index', username=c.auth_user.username))}</li>
            <li>${h.link_to("Submit Art", h.url(controller='gallery', action='submit', username=c.auth_user.username))}</li>
        </ul>
        % if c.auth_user.can('administrate'):
        <p id="superpowers">${h.link_to("Activate Superpowers", h.url(controller='admin', action='auth'), class_='admin')}</p>
        % endif
        <ul id="messages">
        <% note_count = c.auth_user.unread_note_count() %>
            <li${' class="new"' if note_count else ''}> ${h.link_to("%s%d new note%s" % (h.image_tag('/images/icons/internet-mail.png', ''), note_count, 's' if note_count != 1 else ''), h.url(controller='notes', action='user_index', username=c.auth_user.username))} </li>
            <li class="new FINISHME"> ${h.link_to(h.image_tag('/images/icons/internet-group-chat.png', '') + "5 new feedback", "")} </li>
            <li class="FINISHME"> ${h.link_to(h.image_tag('/images/icons/internet-news-reader.png', '') + "No new watches", "")} </li>
        </ul>
        % endif
    </div>
    <h1 id="logo">${h.link_to(h.image_tag('/images/banner.jpg', 'FurAffinity'), h.url(controller='index', action='index'))}</h1>
</div>
<div id="navigation">
    <div class="basic-box" id="site-nav">
        <h2>Site</h2>
        <ul>
            <li>${h.link_to("Home", h.url(controller='index', action='index'))}</li>
            <li>${h.link_to("Browse", h.url(controller='gallery', action='index'))}</li>
            <li>${h.link_to("News", h.url(controller='news'))}</li>
            <li>${h.link_to("Staff", h.url(controller='staff'))}</li>
        </ul>
    </div>
    <div class="basic-box" id="community-nav">
        <h2>Community</h2>
        <ul>
            <li>${h.link_to("Forums", 'http://www.furaffinityforums.net')}</li>
            <li>${h.link_to("Chat", 'http://www.wikiffinity.net/index.php?title=IRC_Chat')}</li>
            <li>${h.link_to("Support", 'http://www.wikiffinity.net/')}</li>
        </ul>
    </div>
    <div class="basic-box" id="search">
        <h2>Search gallery</h2>
        ${c.empty_form.start(h.url(controller='search', action='do'), method='post')}
        <p>
            ${c.empty_form.text_field('query_main')}<br>
            ${c.empty_form.check_box('search_title', checked=True)} Title
            ${c.empty_form.check_box('search_description', checked=True)} Description
            ${c.empty_form.hidden_field('search_for', value='submissions')}
            ${c.empty_form.hidden_field('query_author', value='')}
            ${c.empty_form.hidden_field('query_tags', value='')}
            ${c.empty_form.submit('Search')}
        </p>
        ${c.empty_form.end()}
    </div>
</div>
<ul id="ads">
    <li>${h.image_tag('/images/ad1.gif', 'Ad 1')}</li>
    <li>${h.image_tag('/images/ad2.gif', 'Ad 2')}</li>
</ul>

% if c.error_msgs:
<ul id="error">
    asdfsadf
    % for error in c.error_msgs:
    <li>${error}</li>
    % endfor
</ul>
% endif

<div id="content">
    ${next.body()}
</div>

<div id="footer">
    <div id="shameless-whoring">
        <img src="http://static.furaffinity.net/images/donate.gif" alt="Screw the ads and donate!"/>
    </div>
    <ul class="inline">
        <li><a href="/.ferrox/design/docs/tos">Terms of Service</a></li>
        <li><a href="/.ferrox/design/docs/sa">Submission Agreement</a></li>
        <li><a href="/.ferrox/design/docs/aup">Acceptable Upload Policy</a></li>
    </ul>
    <p> No portions of furaffinity.net may be used without expressed, written permission. </p>
    <p> All artwork is copyrighted to the respective owner.  All rights reserved unless otherwise specified. </p>
    <div id="stats">
<%
    total_time = c.time_elapsed()
    sql_time = c.query_log.time_elapsed()
    sql_percent = sql_time / total_time * 100
%>
        <div id="python-bar" style="width: ${100 - sql_percent}%;">&nbsp;</div>
        <p> Page generated in ${"%.4f" % total_time}s; ${"%.1f" % sql_percent}% SQL, ${len(c.query_log.queries)} quer${'y' if len(c.query_log.queries) == 1 else 'ies'} </p>
    </div>
    % if c.auth_user.can('debug'):
    <table id="query-log">
    <tr>
        <th>Time</th>
        <th>Query</th>
    </tr>
    % for query, time in sorted(c.query_log.queries, key=lambda x: x[1], reverse=True):
    <tr>
        <td>${"%.6f" % time}</td>
        <td>${query}</td>
    </tr>
    % endfor
    </table>
    % endif
</div>
</body>
</html>

<%def name="css_links()">
    <link rel="stylesheet" type="text/css" href="${h.url_for(controller='stylesheets', action='index', sheet='gallery')}"/>
    <link rel="stylesheet" type="text/css" href="${h.url_for(controller='stylesheets', action='index', sheet='reset')}"/>
    <link rel="stylesheet" type="text/css" href="${h.url_for(controller='stylesheets', action='index', sheet='common')}"/>
    <link rel="stylesheet" type="text/css" href="${h.url_for(controller='stylesheets', action='index', sheet=c.auth_user.preference('style_sheet'), color=c.auth_user.preference('style_color'))}"/>
</%def>

<%def name="javascript_includes()">
    % for script in c.javascripts:
    ${h.javascript_include_tag("%s.js" % script)}
    % endfor
</%def>
