#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import cgi
import datetime
import logging
import magic
import mimetypes
import pyarrow as pa

from werkzeug.datastructures import FileStorage as FlaskFileStorage
from ckan.common import config

import ckan.lib.munge as munge
import ckan.logic as logic

ALLOWED_UPLOAD_TYPES = (cgi.FieldStorage, FlaskFileStorage)
log = logging.getLogger(__name__)

_hdfs_storage_path = None

def get_hdfs_storage_path():
    '''Function to get hdfs storage path'''
    global _hdfs_storage_path
    # None means it has not been set. False means not in config.
    if _hdfs_storage_path is None:
        hdfs_storage_path = config.get('ckan.hdfs.storage_path')
        if hdfs_storage_path:
            _hdfs_storage_path = hdfs_storage_path
        else:
            log.critical('''Please specify a ckan.hdfs.storage_path in your config for your uploads''')
            _hdfs_storage_path = False
    return _hdfs_storage_path

def _get_underlying_file(wrapper):
    if isinstance(wrapper, FlaskFileStorage):
        return wrapper.stream
    return wrapper.file

class ResourceUploadHDFS(object):
    def __init__(self, resource):
        path = get_hdfs_storage_path()
        config_mimetype_guess = config.get('ckan.mimetype_guess', 'file_ext')
        if not path:
            self.hdfs_storage_path = None
            return
        self.hdfs_storage_path = os.path.join(path, 'resources')
        try:
            fs = pa.hdfs.connect()
            fs.mkdir(self.hdfs_storage_path)
        except:
            log.critical('''hdfs connection error''')
            raise

        self.filename = None
        self.mimetype = None
        url = resource.get('url')
        upload_field_storage = resource.pop('upload', None)
        self.clear = resource.pop('clear_upload', None)

        if config_mimetype_guess == 'file_ext':
            self.mimetype = mimetypes.guess_type(url)[0]

        if isinstance(upload_field_storage, ALLOWED_UPLOAD_TYPES):
            self.filesize = 0  # bytes

            self.filename = upload_field_storage.filename
            self.filename = munge.munge_filename(self.filename)
            resource['url'] = self.filename
            resource['url_type'] = 'upload'
            resource['last_modified'] = datetime.datetime.utcnow()
            self.upload_file = _get_underlying_file(upload_field_storage)
            self.upload_file.seek(0, os.SEEK_END)
            self.filesize = self.upload_file.tell()
            # go back to the beginning of the file buffer
            self.upload_file.seek(0, os.SEEK_SET)

            # check if the mimetype failed from guessing with the url
            if not self.mimetype and config_mimetype_guess == 'file_ext':
                self.mimetype = mimetypes.guess_type(self.filename)[0]

            if not self.mimetype and config_mimetype_guess == 'file_contents':
                try:
                    self.mimetype = magic.from_buffer(self.upload_file.read(),
                                                      mime=True)
                    self.upload_file.seek(0, os.SEEK_SET)
                except IOError, e:
                    # Not that important if call above fails
                    self.mimetype = None

        elif self.clear:
            resource['url_type'] = ''

    def get_directory(self, id):
        directory = os.path.join(self.hdfs_storage_path, id[0:3], id[3:6])
        return directory

    def get_path(self, id):
        directory = self.get_directory(id)
        filepath = os.path.join(directory, id[6:])
        return filepath

    def download(self, id):
        try:
            fs = pa.hdfs.connect()
        except:
            log.critical('''hdfs connection error''')
            raise
        filepath = self.get_path(id)
        with fs.open(filepath, 'rb') as read_file:
            read_file.seek(0)
            app_iter = read_file.read()
            read_file.close()
            return app_iter

    def upload(self, id, max_size=10):
        '''Actually upload the file.

        :returns: ``'file uploaded'`` if a new file was successfully uploaded
            (whether it overwrote a previously uploaded file or not),
            ``'file deleted'`` if an existing uploaded file was deleted,
            or ``None`` if nothing changed
        :rtype: ``string`` or ``None``

        '''
        if not self.hdfs_storage_path:
            return

        # Get directory and filepath on the system
        # where the file for this resource will be stored
        directory = self.get_directory(id)
        filepath = self.get_path(id)

        try:
            fs = pa.hdfs.connect()
        except:
            log.critical('''hdfs connection error''')
            raise

        # If a filename has been provided (a file is being uploaded)
        # we write it to the filepath (and overwrite it if it already
        # exists). This way the uploaded file will always be stored
        # in the same location
        if self.filename:
            try:
                fs.mkdir(directory)
            except:
                raise

            tmp_filepath = filepath + '~'
            output_file = fs.open(tmp_filepath, 'wb')

            self.upload_file.seek(0)
            current_size = 0
            while True:
                current_size = current_size + 1
                # MB chunks
                data = self.upload_file.read(2 ** 20)

                if not data:
                    break

                output_file.write(data)

                if current_size > max_size:

                    if fs.exists(tmp_filepath):
                        fs.rm(tmp_filepath)

                    raise logic.ValidationError(
                        {'upload': ['File upload too large']}
                    )

            output_file.close()
            fs.rename(tmp_filepath, filepath)
            return

        # The resource form only sets self.clear (via the input clear_upload)
        # to True when an uploaded file is not replaced by another uploaded
        # file, only if it is replaced by a link to file.
        # If the uploaded file is replaced by a link, we should remove the
        # previously uploaded file to clean up the file system.
        if self.clear:
            try:
                if fs.exists(filepath):
                    fs.rm(filepath)
            except:
                pass

    def file_remove(self, id):
        try:
            fs = pa.hdfs.connect()
        except:
            log.critical('''hdfs connection error''')
            raise
        directory = self.get_directory(id)
        filepath = self.get_path(id)
        # remove file and its directory tree in HDFS
        try:
            if fs.exists(filepath):
                fs.rm(filepath)
            if fs.exists(directory):
                fs.delete(directory)
        except:
            pass
