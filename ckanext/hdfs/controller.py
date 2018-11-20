#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import mimetypes

import ckan.lib.helpers as h

from ckan import logic, model
from ckan.common import _, request, c, response
from ckan.lib import base, uploader
from pylons import c
from ckan.common import config

log = logging.getLogger(__name__)
abort = base.abort

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
get_action = logic.get_action

class UploaderController(base.BaseController):
    def resource_download(self, id, resource_id, filename=None):
        """
        Provides a direct download by either redirecting the user to the url
        stored or downloading an uploaded file directly.
        """
        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'auth_user_obj': c.userobj}
        try:
            rsc = get_action('resource_show')(context, {'id': resource_id})
            get_action('package_show')(context, {'id': id})
        except (NotFound, NotAuthorized):
            abort(404, _('Resource not found'))
        if rsc.get('url_type') == 'upload':
            upload = uploader.get_resource_uploader(rsc)
            app_iter = upload.download(rsc['id'])
            content_type, content_enc = mimetypes.guess_type(rsc.get('url', ''))
            if content_type:
                response.headers['Content-Type'] = content_type
            return app_iter
        elif 'url' not in rsc:
            abort(404, _('No download is available'))
        h.redirect_to(rsc['url'])
