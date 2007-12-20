<%inherit file="base.mako" />

<big><big>${c.submission_title}</big></big><br>
<big>by: ${c.submission_artist}</big><br>
% if (c.submission_type == 'video'):
${h.embed_flash(c.submission_file)}<br>
% elif (c.submission_type == 'image'):
${h.image_tag(c.submission_file,c.submission_title)}<br>
% elif (c.submission_type == 'audio'):
${h.link_to('Music Submission', c.submission_file)}, not yet implemented<br>
% elif (c.submission_type == 'text'):
${h.link_to('Text Submission',c.submission_file)}, not yet implemented<br>
% else:
unknown submission type: ${c.submission_type}<br>
% endif
${h.image_tag(c.submission_thumbnail,"%s Thumbnail"%c.submission_title)}<br>
Description: ${c.submission_description}<br>
Submitted at: ${h.format_time(c.submission_time)}<br><br>

${c.misc}
<%def name="title()">${c.submission_title} by ${c.submission_artist}</%def>

