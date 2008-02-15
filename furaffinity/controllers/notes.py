import logging
import formencode
import sqlalchemy
from sqlalchemy import sql

from furaffinity.lib.base import *
import furaffinity.lib.paginate as paginate
from furaffinity.model import form
from furaffinity.lib.formgen import FormGenerator
import webhelpers
log = logging.getLogger(__name__)

class NotesController(BaseController):

    def _enforce_ownership(self, note):
        """
        Causes an instant 403 if the logged-in user is neither the sender nor
        the recipient of the given note.
        """
        if note.recipient != c.auth_user and note.sender != c.auth_user:
            abort(403)

    def _note_setup(self, username, id):
        c.page_owner = model.retrieve_user(username)
        note_q = model.Session.query(model.Note)
        try:
            c.note = note_q.filter_by(id=id).one()
        except sqlalchemy.exceptions.InvalidRequestError:
            abort(404)

        if c.note.recipient != c.page_owner and c.note.sender != c.page_owner:
            abort(404)

        self._enforce_ownership(c.note)


    def user_index(self, username):
        c.page_owner = model.retrieve_user(username)
        if c.page_owner != c.auth_user:
            abort(403)

        page = request.params.get('page', 0)
        note_q = c.page_owner.recent_notes()
        c.notes_page = paginate.Page(note_q, page_nr=page, items_per_page=20)
        c.notes_nav = c.notes_page.navigator(link_var='page')
        return render('notes/index.mako')

    def view(self, username, id):
        self._note_setup(username, id)
        c.javascripts = ['notes']

        note_thread_id = c.note.original_note_id

        note_q = model.Session.query(model.Note)
        c.all_notes = note_q.filter_by(original_note_id=note_thread_id) \
            .filter(sql.or_(
                model.Note.from_user_id == c.page_owner.id,
                model.Note.to_user_id == c.page_owner.id
                )) \
            .order_by(model.Note.time.asc())

        c.latest_note = c.note.latest_note(c.page_owner)

        rendered = render('notes/view.mako')

        # Mark all notes on this thread addressed to this user as read, but do
        # it *after* the page is rendered so the user can see what *was* unread
        # TODO perf
        if c.page_owner == c.auth_user:
            unread_notes = note_q.filter_by(original_note_id=note_thread_id) \
                .filter_by(to_user_id=c.page_owner.id) \
                .filter_by(status='unread') \
                .all()
            for note in unread_notes:
                note.status = 'read'
            model.Session.commit()

        return rendered

    def ajax_expand(self, username, id):
        self._note_setup(username, id)
        return render('notes/ajax_expand.mako')

    def write(self, username):
        c.form = FormGenerator()
        return render('notes/send.mako')

    def reply(self, username, id):
        self._note_setup(username, id)
        c.reply_to_note = c.note.latest_note(c.page_owner)
        c.form = FormGenerator()
        c.form.defaults['subject'] = 'Re: ' + c.note.base_subject()
        c.form.defaults['content'] = "[quote=%s]%s[/quote]\n" % \
            (c.note.sender.username, c.note.content)

        if c.reply_to_note.recipient == c.page_owner:
            c.recipient = c.reply_to_note.sender
        else:
            c.recipient = c.reply_to_note.recipient
        c.form.defaults['reply_to_note'] = c.reply_to_note.id

        return render('notes/send.mako')

    def forward(self, username, id):
        self._note_setup(username, id)
        c.form = FormGenerator()
        c.form.defaults['subject'] = 'Fwd: ' + c.note.base_subject()
        c.form.defaults['content'] = "[quote=%s]%s[/quote]\n" % \
            (c.note.sender.username, c.note.content)

        return render('notes/send.mako')

    def write_send(self, username):
        validator = model.form.SendNoteForm()
        try:
            form_data = validator.to_python(request.params)
        except model.form.formencode.Invalid, error:
            c.form = FormGenerator(form_error=error)
            return render('notes/send.mako')

        original_note_id = None
        to_user_id = None
        if 'reply_to_note' in form_data:
            reply_to_note = form_data['reply_to_note']
            self._enforce_ownership(reply_to_note)
            original_note_id = reply_to_note.original_note_id

            if reply_to_note.recipient == c.auth_user:
                to_user_id = reply_to_note.sender.id
            elif reply_to_note.sender == c.auth_user:
                to_user_id = reply_to_note.recipient.id
        else:
            to_user_id = form_data['recipient'].id

        note = model.Note(
            from_user_id = c.auth_user.id,
            to_user_id = to_user_id,
            subject = h.escape_once(form_data['subject']),
            content = h.escape_once(form_data['content']),
            original_note_id = original_note_id,
        )
        model.Session.save(note)
        model.Session.commit()
        if note.original_note_id == None:
            note.original_note_id = note.id  # TODO perf
        model.Session.commit()
        h.redirect_to(h.url_for(controller='notes', action='view', username=c.auth_user.username, id=note.latest_note(c.auth_user).id))
