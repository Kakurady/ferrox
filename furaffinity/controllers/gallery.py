from __future__ import with_statement

import logging

from furaffinity.lib.base import *
from furaffinity.lib import filestore, tagging
from pylons.decorators.secure import *

from furaffinity.lib.thumbnailer import Thumbnailer

from chardet.universaldetector import UniversalDetector
import codecs
import os
import md5
import sqlalchemy.exceptions
from tempfile import TemporaryFile
from sqlalchemy import or_,and_,not_
from sqlalchemy.orm import eagerload

import re

search_enabled = True
try:
    import xapian
except ImportError:
    search_enabled = False

log = logging.getLogger(__name__)

fullfile_size = 1280
thumbnail_size = 120
halfview_size = 300


def get_submission(id):
    try:
        id = int(id)
    except ValueError:
        c.error_text = 'Submission ID must be a number.'
        c.error_title = 'Not Found'
        abort ( 404 )
        
    submission = None
    try:
        submission = model.Session.query(model.Submission).options(eagerload('tags')).filter(model.Submission.id==id).one()
        c.tags = tagging.make_tags_into_string(submission.tags)
    except sqlalchemy.exceptions.InvalidRequestError:
        c.error_text = 'Requested submission was not found.'
        c.error_title = 'Not Found'
        abort ( 404 )
        
    return submission


class GalleryController(BaseController):

    def index(self):
        '''
        submission_q = model.Session.query(model.Submission)
        #submission_q = submission_q.options(eagerload('user_submission'))
        #submission_q = submission_q.options(eagerload('user_submission.user'))
        submission_q = submission_q.options(eagerload('tags'))

        tags = []
        tags = ['asdf','zxcv']
        
        if len(tags):
            eval_query = 'or_('
            first = True
            for tag_text in tags:
                if first:
                    first = False
                else:
                    eval_query += ', '
                    
                if tag_text[0] == '-':
                    #tag = tagging.get_by_text(tag_text[1:])
                    negate = True
                else:
                    #tag = tagging.get_by_text(tag_text)
                    negate = False
                    
                    eval_query += "model.Tag.text == '%s'"%tag_text
            eval_query += ')'
            # there has to be a better way to construct this
            submission_q = submission_q.filter(eval(eval_query)).group_by(model.Submission.id).having(count(model.Submission.id) == 2)


        model.Session.bind.echo = True
        submissions = submission_q.all()
        model.Session.bind.echo = False
        
        if submissions:
            c.submissions = []
            for item in submissions:
                tn_ind = item.get_derived_index(['thumb'])
                if ( tn_ind != None ):
                    thumbnail = filestore.get_submission_file(item.derived_submission[tn_ind].metadata)
                else:
                    thumbnail = None
                #template_item = h.to_dict ( item )
                #template_item.update({'thumbnail':thumbnail,'username':item.primary_artist()})
                #c.submissions.append ( template_item )
                print item.id
        else:
            c.submissions = None
            
        c.submissions = None
        return render('/gallery/index.mako')
        '''
        return ''
        
    def user_index(self, username=None):
        c.page_owner = None
        if ( username != None ):
            user_q = model.Session.query(model.User)
            try:
                c.page_owner = user_q.filter_by(username = username).one()
            except sqlalchemy.exceptions.InvalidRequestError:
                c.error_text = "User %s not found." % h.escape_once(username)
                c.error_title = 'User not found'
                return render('/error.mako')
        
        submission_q = model.Session.query(model.UserSubmission)
        submission_q = submission_q.filter(model.UserSubmission.status != 'deleted')
        submission_q = submission_q.filter_by(user_id = c.page_owner.id)
        submission_q = submission_q.options(eagerload('user'))
        submission_q = submission_q.options(eagerload('submission'))
        submission_q = submission_q.options(eagerload('submission.tags'))
        submission_q = submission_q.filter(model.UserSubmission.status != 'deleted')
        submission_q = submission_q.filter(model.UserSubmission.user_id == c.page_owner.id)
        
        submissions = submission_q.all()
        if submissions:
            c.submissions = []
            for item in submissions:
                tn_ind = item.submission.get_derived_index(['thumb'])
                if ( tn_ind != None ):
                    thumbnail = filestore.get_submission_file(item.submission.derived_submission[tn_ind].metadata)
                else:
                    thumbnail = None
                template_item = dict (
                    id = item.submission.id,
                    title = item.submission.title,
                    date = item.submission.time,
                    description = item.submission.description_parsed,
                    thumbnail = thumbnail,
                    username = item.user.display_name
                )
                c.submissions.append ( template_item )
        else:
            c.submissions = None
            
        c.is_mine = ( c.page_owner != None ) and (c.auth_user != None) and (c.page_owner.id == c.auth_user.id)
        return render('/gallery/user_index.mako')
        
    @check_perm('submit_art')
    def submit(self):
        c.edit = False
        c.prefill['title'] = ''
        c.prefill['description'] = ''
        c.prefill['tags'] = ''
        return render('/gallery/submit.mako')

    @check_perms(['submit_art','administrate'])
    def edit(self, id=None):
        submission = get_submission(id)
        self.is_my_submission(submission, True)
        c.submission = submission
        c.edit = True
        c.prefill['title'] = submission.title
        c.prefill['description'] = submission.description
        c.prefill['tags'] = tagging.make_tags_into_string(submission.tags)
        return render('/gallery/submit.mako')

    @check_perms(['submit_art','administrate'])
    def delete(self, id=None):
        submission = get_submission(id)
        self.is_my_submission(submission, True)
        c.text = "Are you sure you want to delete the submission titled \" %s \"?"%submission.title
        c.url = h.url(action="delete_commit",id=id)
        c.fields = {}
        return render('/confirm.mako')
    
    @check_perms(['submit_art','administrate'])
    def edit_commit(self, id=None):
        # -- validate form input --
        validator = model.form.SubmitForm();
        submission_data = None
        try:
            submission_data = validator.to_python(request.params);
        except model.form.formencode.Invalid, error:
            c.edit = True
            c.prefill = request.params
            c.input_errors = "There were input errors: %s %s" % (error, c.prefill)
            return render('/gallery/submit.mako')
            
        # -- get image from database, make sure user has permission --
        submission = get_submission(id)
        self.is_my_submission(submission,True)
        
        # -- get relevant information from submission_data --
        submission_data = self.set_up_submission_data(submission_data, submission)
        
        # -- store image in mogile or wherever, if it's been changed --
        if ( submission_data['fullfile'] != None ):
            submission.metadata.count_dec()
            submission_data['fullfile']['metadata'] = filestore.store( submission_data['fullfile']['hash'], submission_data['fullfile']['mimetype'], submission_data['fullfile']['content'] )
            submission_data['fullfile']['metadata'].height = submission_data['fullfile']['height']
            submission_data['fullfile']['metadata'].width = submission_data['fullfile']['width']
                
        # -- store thumbnail in mogile or wherever --
        if ( submission_data['thumbfile'] != None ):
            tn_ind = submission.get_derived_index(['thumb'])
            if ( submission.get_derived_index(['thumb']) != None ):
                submission.derived_submission[0].metadata.count_dec()
            submission_data['thumbfile']['metadata'] = filestore.store ( submission_data['thumbfile']['hash'], submission_data['thumbfile']['mimetype'], submission_data['thumbfile']['content'] )
            submission_data['thumbfile']['metadata'].height = submission_data['thumbfile']['height']
            submission_data['thumbfile']['metadata'].width = submission_data['thumbfile']['width']
            
        # -- store halfview in mogile or wherever --
        if ( submission_data['halffile'] != None ):
            tn_ind = submission.get_derived_index(['halfview'])
            if ( submission.get_derived_index(['halfview']) != None ):
                submission.derived_submission[0].metadata.count_dec()
            submission_data['halffile']['metadata'] = filestore.store ( submission_data['halffile']['hash'], submission_data['halffile']['mimetype'], submission_data['halffile']['content'] )
            submission_data['halffile']['metadata'].height = submission_data['halffile']['height']
            submission_data['halffile']['metadata'].width = submission_data['halffile']['width']
            
        # -- put submission in database --
        if ( submission.title != submission_data['title'] or submission.description != submission_data['description'] ):
            if ( submission.editlog == None ):
                submission.editlog = model.EditLog(c.auth_user)
            editlog_entry = model.EditLogEntry(c.auth_user,'no reasons yet',submission.title,submission.description,submission.description_parsed)
            submission.editlog.update(editlog_entry)
            submission.title = submission_data['title']
            submission.description = submission_data['description']
            submission.description_parsed = submission_data['description'] # waiting for bbcode parser
        submission.type = submission_data['type']
        submission.status = 'normal'
        if ( submission_data['fullfile'] != None ):
            submission_data['fullfile']['metadata'].count_inc()
            submission.metadata = submission_data['fullfile']['metadata']

        tn_ind = submission.get_derived_index(['thumb'])
        if ( submission_data['thumbfile'] != None ):
            submission_data['thumbfile']['metadata'].count_inc()
            if ( tn_ind == None ):
                derived_submission = model.DerivedSubmission(derivetype = 'thumb')
                derived_submission.metadata = submission_data['thumbfile']['metadata']
                submission.derived_submission.append(derived_submission)
            else:
                submission.derived_submission[tn_ind].metadata.count_dec()
                submission.derived_submission[tn_ind].metadata = submission_data['thumbfile']['metadata']
            
        hv_ind = submission.get_derived_index(['halfview'])
        if ( submission_data['halffile'] != None ):
            submission_data['halffile']['metadata'].count_inc()
            if ( hv_ind == None ):
                derived_submission = model.DerivedSubmission(derivetype = 'halfview')
                derived_submission.metadata = submission_data['halffile']['metadata']
                submission.derived_submission.append(derived_submission)
            else:
                submission.derived_submission[hv_ind].metadata.count_dec()
                submission.derived_submission[hv_ind].metadata = submission_data['halffile']['metadata']

        # Tag shuffle
        for tag_object in submission.tags:
            if not (tag_object.text in submission_data['tags']):
                submission.tags.remove(tag_object)
                #model.Session.delete(submission_tag_object)
            else:
                submission_data['tags'].remove(tag_object.text)
                
        for tag in submission_data['tags']:
            tag_object = tagging.get_by_text(tag, True)
            submission.tags.append(tag_object)
        model.Session.save(submission)
            
        model.Session.commit()

        if search_enabled:
            xapian_database = xapian.WritableDatabase('submission.xapian', xapian.DB_OPEN)
            xapian_document = submission_data_to_xapian(submission)
            xapian_database.replace_document("I%d"%submission.id,xapian_document)

        h.redirect_to(h.url_for(controller='gallery', action='view', id = submission.id))
        
        
    @check_perms(['submit_art','administrate'])
    def delete_commit(self, id=None):
        # -- validate form input --
        validator = model.form.DeleteForm();
        delete_form_data = None
        try:
            delete_form_data = validator.to_python(request.params);
        except model.form.formencode.Invalid, error:
            return "There were input errors: %s" % (error)
        
        submission = get_submission(id)
        self.is_my_submission(submission,True)
        
        if (delete_form_data['confirm'] != None):
            # -- update submission in database --
            submission.status = 'deleted'
            submission.user_submission[0].status = 'deleted'
            model.Session.commit()
            
            if search_enabled:
                xapian_database = WritableDatabase('submission.xapian',DB_OPEN)
                xapian_database.delete_document("I%d"%submission.id);
            h.redirect_to(h.url_for(controller='gallery', action='index', username = submission.user_submission[0].user.username, id=None))
        else:
            h.redirect_to(h.url_for(controller='gallery', action='view', id = submission.id))

    @check_perm('submit_art')
    def submit_upload(self):
        validator = model.form.SubmitForm();
        submission_data = None
        error = None
        try:
            submission_data = validator.to_python(request.params);
        except model.form.formencode.Invalid, error:
            pass
        
        if ( error != None or submission_data['fullfile'] == None ):
            if ( error == None ):
                error = 'No file supplied.'
            c.edit = False
            c.prefill = request.params
            c.input_errors = "There were input errors: %s %s" % (error, c.prefill)
            return render('/gallery/submit.mako')
        
        
        # -- fill out submission_data --
        submission_data = self.set_up_submission_data(submission_data,None)
                                
        # -- store image in mogile or wherever --
        submission_data['fullfile']['metadata'] = filestore.store( submission_data['fullfile']['hash'], submission_data['fullfile']['mimetype'], submission_data['fullfile']['content'] )
        submission_data['fullfile']['metadata'].height = submission_data['fullfile']['height']
        submission_data['fullfile']['metadata'].width = submission_data['fullfile']['width']
                
        # -- store thumbnail in mogile or wherever --
        if ( submission_data['thumbfile'] ):
            submission_data['thumbfile']['metadata'] = filestore.store ( submission_data['thumbfile']['hash'], submission_data['thumbfile']['mimetype'], submission_data['thumbfile']['content'] )
            submission_data['thumbfile']['metadata'].height = submission_data['thumbfile']['height']
            submission_data['thumbfile']['metadata'].width = submission_data['thumbfile']['width']
        else:
            # FIXME: Default thumbnail?
            pass
            
        # -- store halfview in mogile or wherever --
        if ( submission_data['halffile'] ):
            submission_data['halffile']['metadata'] = filestore.store ( submission_data['halffile']['hash'], submission_data['halffile']['mimetype'], submission_data['halffile']['content'] )
            submission_data['halffile']['metadata'].height = submission_data['halffile']['height']
            submission_data['halffile']['metadata'].width = submission_data['halffile']['width']
            
        submission = model.Submission(
            title = submission_data['title'],
            description = submission_data['description'],
            description_parsed = submission_data['description'], # FIXME: waiting for bbcode parser
            type = submission_data['type'],
            discussion_id = 0,
            status = 'normal'
        )
        model.Session.save(submission)
        submission_data['fullfile']['metadata'].count_inc()
        submission.metadata = submission_data['fullfile']['metadata']
        for tag in submission_data['tags']:
            tag_object = tagging.get_by_text(tag, True)
            submission.tags.append(tag_object)
        model.Session.save(submission)
        user_submission = model.UserSubmission(
            user_id = session['user_id'],
            relationship = 'artist',
            status = 'primary'
        )
        submission.user_submission.append(user_submission)
        model.Session.save(submission)
        if ( submission_data['thumbfile'] != None ):
            thumbfile_derived_submission = model.DerivedSubmission(derivetype = 'thumb')
            submission_data['thumbfile']['metadata'].count_inc()
            thumbfile_derived_submission.metadata = submission_data['thumbfile']['metadata']
            submission.derived_submission.append(thumbfile_derived_submission)
            model.Session.save(submission)
        if ( submission_data['halffile'] != None ):
            thumbfile_derived_submission = model.DerivedSubmission(derivetype = 'halfview')
            submission_data['halffile']['metadata'].count_inc()
            thumbfile_derived_submission.metadata = submission_data['halffile']['metadata']
            submission.derived_submission.append(thumbfile_derived_submission)
            model.Session.save(submission)

        model.Session.commit()
        
        # update xapian
        if search_enabled:
            xapian_database = xapian.WritableDatabase('submission.xapian', xapian.DB_OPEN)
            xapian_document = self.submission_data_to_xapian(submission)
            xapian_database.add_document(xapian_document)
        
        h.redirect_to(h.url_for(controller='gallery', action='view', id = submission.id))
            
    def view(self,id=None):
        submission = get_submission(id)
        filename=filestore.get_submission_file(submission.metadata)
        
        c.submission_thumbnail = submission.get_derived_index(['thumb'])
        if ( c.submission_thumbnail != None ):
            tn_filename=filestore.get_submission_file(submission.derived_submission[c.submission_thumbnail].metadata)
            c.submission_thumbnail = h.url_for(controller='gallery', action='file', filename=tn_filename, id=None)
        else:
            # supply default thumbnail for type here
            c.submission_thumbnail = ''
        c.submission_halfview = submission.get_derived_index(['halfview'])
        if ( c.submission_halfview != None ):
            hv_filename=filestore.get_submission_file(submission.derived_submission[c.submission_halfview].metadata)
            c.submission_halfview = h.url_for(controller='gallery', action='file', filename=hv_filename, id=None)
        else:
            # supply default thumbnail for type here
            c.submission_thumbnail = ''
        c.submission_file = h.url_for(controller='gallery', action='file', filename=filename, id=None)
        c.submission = submission
        
        if ( submission.type == 'text' ):
            filedata = filestore.dump(filestore.get_submission_file(submission.metadata))
            c.submission_content = filedata[0]
        
        return render('/gallery/view.mako');
        
    def file(self,filename=None):
        filename = os.path.basename(filename)
        try:
            filedata = filestore.dump(filename)
        except filestore.ImageManagerExceptionFileNotFound:
            c.error_text = 'Requested file was not found.'
            c.error_title = 'Not Found'
            abort ( 404 )
            
        response.headers['Content-Type'] = filedata[1].mimetype
        response.headers['Content-Length'] = len(filedata[0])
        return filedata[0]
        
    def hash(self,s):
        m = md5.new()
        m.update(s)
        return m.hexdigest()

    def get_submission_type(self,mime_type):
        (major, minor) = mime_type.split('/')
        if ( major == 'image' ):
            try:
                ['png','gif','jpeg'].index(minor)
            except ValueError:
                return 'unknown'
            else:
                return 'image'
        elif ( major == 'application' and minor == 'x-shockwave-flash' ):
            return 'video'
        elif ( major == 'audio' and minor == 'mpeg' ):
            return 'audio'
        elif ( major == 'text' ):
            return 'text'
            try:
                ['plain','html'].index(minor)
            except ValueError:
                return 'unknown'
            else:
                return 'text'
        else:
            return 'unknown'

        
    def is_my_submission(self,submission,abort=False):
        if ( not c.auth_user or (not c.auth_user.can('administrate') and (c.auth_user.id != journal_entry.user_id)) ):
            if (abort):
                c.error_text = 'You cannot edit this submission.'
                c.error_title = 'Forbidden'
                abort ( 403 )
            else:
                return False
        return True

    def set_up_submission_data(self,submission_data,submission):
        # Is there a new image uploaded?
        if ( submission_data['fullfile'] != None ):
            # Yes, find out what type of submission we're dealing with...
            submission_data['fullfile']['mimetype'] = h.get_mime_type(submission_data['fullfile'])
            submission_type = self.get_submission_type(submission_data['fullfile']['mimetype'])
            if ( submission_type == 'unknown' ):
                abort(403)
        else:
            # No, grab it out of current submission.
            submission_type = submission.type
            
        # If it's not an image, there are no dimensions
        if ( submission_type != 'image' ):
            submission_data['fullfile']['height'] = 0
            submission_data['fullfile']['width'] = 0
        
        # Do we have a thumbnail?
        if ( submission_data['thumbfile'] != None ):
            # Yes we do.
            
            # Is it an image?
            submission_data['thumbfile']['mimetype'] = h.get_mime_type(submission_data['thumbfile'])
            if ( self.get_submission_type(submission_data['thumbfile']['mimetype']) == 'image' ):
                # Yes it is
                with Thumbnailer() as t:
                    t.parse(submission_data['thumbfile']['content'],submission_data['thumbfile']['mimetype'])
                    
                    # Is it too big?
                    toobig = t.generate(thumbnail_size)
                    if ( toobig != None ):
                        # Yes it is.
                        submission_data['thumbfile'].update(toobig)
                        toobig.clear()
                    else:
                        # No it isn't
                        submission_data['thumbfile']['width'] = t.width
                        submission_data['thumbfile']['height'] = t.height
            else:
                # No, it isn't. So we may as well not have one.
                submission_data['thumbfile'].clear()
                submission_data['thumbfile'] = None
        

        # Do we have a half view?
        if ( submission_data['halffile'] != None ):
            # Yes we do.

            # Do we care?
            if ( submission_type == 'image' ):
                # Yes we do
                # Is it an image?
                submission_data['halffile']['mimetype'] = h.get_mime_type(submission_data['halffile'])
                if ( self.get_submission_type(submission_data['halffile']['mimetype']) == 'image' ):
                    # Yes it is
                    with Thumbnailer() as t:
                        t.parse(submission_data['halffile']['content'],submission_data['halffile']['mimetype'])
                        
                        # Is it too big?
                        toobig = t.generate(halfview_size)
                        if ( toobig != None ):
                            # Yes it is.
                            submission_data['halffile'].update(toobig)
                            toobig.clear()
                        else:
                            # No it isn't
                            submission_data['halffile']['width'] = t.width
                            submission_data['halffile']['height'] = t.height
                else:
                    # No, it isn't. So we may as well not have one.
                    submission_data['halffile'].clear()
                    submission_data['halffile'] = None
            else:
                # No we don't
                submission_data['halffile'].clear()
                submission_data['halffile'] = None
                
        # Do any required image processing on the main image now. If it's an image.
        
        # Do we even need to generate new thumbnail/halfview?
        if ( submission_data['fullfile'] != None ):
            if ( submission_type == 'image' ):
                with Thumbnailer() as t:
                    t.parse(submission_data['fullfile']['content'],submission_data['fullfile']['mimetype'])
                    submission_data['fullfile']['width'] = t.width
                    submission_data['fullfile']['height'] = t.height
                    
                    # Do we need to make a thumbnail?
                    if ( submission_data['thumbfile'] == None ):
                        # Yes we do
                        
                        # Can we derive one from the submission?
                        if ( submission_type == 'image' ):
                            # Yes, we can.
                            submission_data['thumbfile'] = t.generate(thumbnail_size)
                            submission_data['thumbfile']['mimetype'] = submission_data['fullfile']['mimetype']
                            
                    # Do we need to make a half view image?
                    if ( submission_type == 'image' and submission_data['halffile'] == None ):
                        submission_data['halffile'] = t.generate(halfview_size)
                        submission_data['halffile']['mimetype'] = submission_data['fullfile']['mimetype']
                        
                    # Is the submission itself too big?
                    toobig = t.generate(fullfile_size)
                    if ( toobig != None ):
                        # Yes it is
                        submission_data['fullfile'].update(toobig)
                        toobig.clear()
            elif ( submission_type == 'text' ):
                if ( submission_data['fullfile']['mimetype'] == 'text/plain' or submission_data['fullfile']['mimetype'] == 'text/html' ):
                    detector = UniversalDetector()
                    detector.feed(submission_data['fullfile']['content'])
                    detector.close()
                    decoded = codecs.getdecoder(detector.result['encoding'])(submission_data['fullfile']['content'],'replace')[0]
                    submission_data['fullfile']['content'] = codecs.getencoder('utf_8')(h.escape_once(decoded),'replace')[0]
                    
                    
            submission_data['fullfile']['hash'] = self.hash(submission_data['fullfile']['content'])
        
        if ( submission_data['halffile'] != None ):
            submission_data['halffile']['hash'] = self.hash(submission_data['halffile']['content'])
        if ( submission_data['thumbfile'] != None ):
            submission_data['thumbfile']['hash'] = self.hash(submission_data['thumbfile']['content'])
                        
        submission_data['type'] = submission_type
        
        submission_data['tags'] = tagging.get_tags_from_string(submission_data['tags'])

        return submission_data
    
    def submission_data_to_xapian(self, submission):
        xapian_document = xapian.Document()
        xapian_document.add_term("I%d"%submission.id)
        xapian_document.add_value(0,"I%d"%submission.id)
        xapian_document.add_term("A%s"%submission.user_submission[0].user.id)
        
        # tags
        for tag in submission.tags:
            xapian_document.add_term("G%s"%tag.text)
            
        # title
        words = []
        rmex = re.compile(r'[^a-z0-9]')
        for word in submission.title.lower().split(' '):
            words.append(rmex.sub('',word))
        words = set(words)
        for word in words:
            xapian_document.add_term("T%s"%word)
            
        # description
        words = []
        # FIX ME: needs bbcode parser. should be plain text representation.
        for word in submission.description.lower().split(' '):
            words.append(rmex.sub('',word))
        words = set(words)
        for word in words:
            xapian_document.add_term("P%s"%word)
        
        return xapian_document
