# coding: utf-8

import os
import re
import cStringIO
import StringIO

import leancloud
from leancloud import rest
from leancloud.mine_type import mine_types


__author__ = 'asaka <lan@leancloud.rocks>'


class File(object):
    def __init__(self, name, data=None, type_=None):
        self._name = name
        self.id = None
        self._url = None
        self._acl = None
        self.current_user = None  # TODO
        self._metadata = {
            'owner': 'unknown'
        }
        if self.current_user and self.current_user is not None:
            self._metadata['owner'] = self.current_user.id

        pattern = re.compile('\.([^.]*)$')
        extension = pattern.findall(name)
        if extension:
            extension = extension[0].lower()
        else:
            extension = None

        if type_:
            self._guessed_type = type_
        else:
            self._guessed_type = mine_types.get(extension, 'text/plain')

        if data is None:
            # self._source = cStringIO.StringIO()
            self._source = None
        elif isinstance(data, (cStringIO.OutputType, StringIO.StringIO)):
            self._source = data
        elif isinstance(data, file):
            data.seek(0, os.SEEK_SET)
            self._source = cStringIO.StringIO(data.read())
        elif isinstance(data, buffer):
            self._source = cStringIO.StringIO(data)
        else:
            raise TypeError('data must be a StringIO / buffer / file instance')

        if self._source:
            self._source.seek(0, os.SEEK_END)
            self._metadata['size'] = self._source.tell()
            self._source.seek(0, os.SEEK_SET)

    @classmethod
    def create_with_url(cls, name, url, meta_data=None, type_=None):
        f = File(name, None, type_)
        if meta_data:
            f._metadata.update(meta_data)

        f._url = url
        f._metadata['__source'] = 'external'
        return f

    @classmethod
    def create_without_data(cls, object_id):
        f = File('')
        f.id = object_id
        return f

    def get_acl(self):
        return self._acl

    def set_acl(self, acl):
        if not isinstance(acl, leancloud.ACL):
            raise TypeError('acl must be a leancloud.ACL instance')
        self._acl = acl

    @property
    def name(self):
        return self._name

    @property
    def url(self):
        return self._url

    @property
    def size(self):
        return self._metadata['size']

    @property
    def owner_id(self):
        return self._metadata['owner']

    @property
    def metadata(self):
        return self._metadata

    def get_thumbnail_url(self, width, height, quality=100, scale_to_fit=True, fmt='png'):
        if not self._url:
            raise ValueError('invalid url')

        if width < 0 or height < 0:
            raise ValueError('invalid height or width params')

        if quality > 100 or quality <= 0:
            raise ValueError('quality must between 0 and 100')

        mode = 2 if scale_to_fit else 1

        return self.url + '?imageView/{}/w/{}/h{}/q{}/format/{}'.format(mode, width, height, quality, fmt)

    def destroy(self):
        if not self.id:
            return False
        response = rest.delete('/files/{}'.format(self.id))
        return response  # TODO: check result

    def save(self):
        pass