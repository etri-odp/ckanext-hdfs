#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ckan import plugins
from routes.mapper import SubMapper
from ckanext.hdfs import uploader

import logging
log = logging.getLogger(__name__)

class HdfsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IUploader)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IResourceController, inherit=True)

    def update_config(self, config):
        return None

    def configure(self, config):
        required_keys = ('ckan.hdfs.storage_path')
        for key in required_keys:
            if config.get(key) is None:
                raise RuntimeError('Required configuration option {0} not found.'.format(key))

    def get_resource_uploader(self, data_dict):
        return uploader.ResourceUploadHDFS(data_dict)

    def get_uploader(self, upload_to, old_filename=None):
        # We don't store misc-file in HDFS (e.g group images)
        return None

    def before_map(self, map):
        sm = SubMapper(
            map,
            controller='ckanext.hdfs.controller:UploaderController'
        )
        with sm:
            sm.connect(
                'resource_download',
                '/dataset/{id}/resource/{resource_id}/download',
                action='resource_download'
            )
            sm.connect(
                'resource_download',
                '/dataset/{id}/resource/{resource_id}/download/{filename}',
                action='resource_download'
            )
        return map

    def before_delete(self, context, resource, resources):
        for res in resources:
            if res['id'] == resource['id']:
                break
        else:
            return
        if res['url_type'] != 'upload':
            return
        res_dict = dict(res.items() + [('clear_upload', True)])
        ruploader = self.get_resource_uploader(res_dict)
        ruploader.file_remove(resource['id'])
