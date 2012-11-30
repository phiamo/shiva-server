# -*- coding: utf-8 -*-
from shiva.exceptions import PathDoesNotExistError, PathIsNotDirectoryError

from flask import url_for
import os


class Directory(object):
    """Represents a directory in filesystem.
    """

    def __init__(self, path):
        if not os.path.exists(path):
            raise PathDoesNotExistError(path)
        if not os.path.isdir(path):
            raise PathIsNotDirectoryError(path)

        self.path = path
        self.dirs = []
        self.files = []

        for directory in self.listdir():
            if os.path.isdir(path):
                self.dirs.append(Directory(path))
            elif os.path.isfile(path):
                _file = File(path)
                if _file.is_media():
                    self.files.append(_file)

        print '%s:' % self.path
        print self.dirs
        print self.paths

    def listdir(self):
        return os.path.listdir(self.path)


class File(object):
    """
    """

    def __init__(self, path):
        if not os.path.exists(path):
            raise PathDoesNotExistError(path)
        if not os.path.isfile(path):
            raise PathIsNotFileError(path)

        self.path = path
        last_dot = path.rfind('.') + 1
        self.extension = path[last_dot:].lower()

    def is_media(self):
        raise NotImplementedError


class Audio(File):
    """
    """

    pass


class Video(File):
    """
    """

    pass


class MediaDir(object):
    """This object allows for media configuration. By instantiating a MediaDir
    class you can tell Shiva where to look for the media files and how to serve
    those files. It's possible to configure the system to look for files on a
    directory and serve those files through a different server.

    MediaDir(root='/srv/http', dirs=('/music', '/songs),
             url='http://localhost:8080/')

    Given that configuration Shiva will scan the directories /srv/http/music
    and /srv/http/songs for media files, but they will be served through
    http://localhost:8080/music/ and http://localhost:8080/songs/

    If just a dir is provided Shiva will serve it through the same instance.
    This is *NOT* recommended, but is useful for developing.

    MediaDir('/home/fatmike/music')
    """

    def __init__(self, root='/', dirs=tuple(), url=None):
        """If you provide just 1 argument it will be assumed as a path to
    serve. Like:

    MediaDir('/home/fatmike/music')

    However, you can't just provide the dirs argument, you have to define
    several MediaDirs.
    You can also provide just the dirs argument and they will be served too
    through the same server as Shiva.

    MediaDir(dirs=('/srv/http/music', '/opt/music'))  # WRONG

    # Right:
    MediaDir('/srv/http/music')
    MediaDir('/opt/music')

    If the dirs share the same root you can define them both at once:

    MediaDir(root='/srv/http', dirs=('/music', '/songs'))
        """

        if type(root) in (str, unicode):
            # MediaDir('/path/to/dir')
            if not dirs and not url:
                dirs = (root,)
                root = '/'

            # MediaDir('/path/to/dir', dirs='sub/path')
            if type(dirs) != tuple:
                raise TypeError("The 'dirs' attribute has to be a tuple.")

            # MediaDir(root='/', url='http://localhost')
            if root == '/' and not dirs and url:
                raise TypeError('Please define at least one directory ' +
                                "different from '/'.")
        else:
            raise TypeError("The 'root' attribute has to be a string.")

        if url and type(url) not in (str, unicode):
            raise TypeError('URL has to be a string.')

        if url:
            if not root:
                raise TypeError('You need to supply a root directory for ' +
                                'this url.')

        if type(root) in (str, unicode) and root != '/':
            root = self.root_slashes(root)

        if type(dirs) == tuple:
            dirs = tuple((self.dirs_slashes(d) for d in dirs))

        if type(url) in (str, unicode) and not url.endswith('/'):
            url += '/'

        self.root = root
        self.dirs = dirs
        self.url = url

    def root_slashes(self, path):
        """Removes the trailing slash, and makes sure the path begins with a
        slash.
        """

        path = path.rstrip('/')
        if not path.startswith('/'):
            path = '/%s' % path

        return path

    def dirs_slashes(self, path):
        """Removes the first slash, if exists, and makes sure the path has a
        trailing slash.
        """

        path = path.lstrip('/')
        if not path.endswith('/'):
            path += '/'

        return path

    def get_dirs(self):
        """Returns a tuple containing directories to look for multimedia files.
        """

        dirs = []

        if self.root:
            if self.dirs:
                for music_dir in self.dirs:
                    # dirs.append(os.path.join(self.root, music_dir))
                    dirs.append('/%s' % '/'.join(p.strip('/') \
                                for p in (self.root, music_dir)).lstrip('/'))
            else:
                dirs.append(self.root)
        else:
            if self.dirs:
                for music_dir in self.dirs:
                    dirs.append(music_dir)

        return dirs

    def get_song_url(self, song):
        """
        """

        url = None
        for mdir in self.get_dirs():
            if song.path.startswith(mdir):
                if self.url:
                    # Remove trailing slash to avoid double-slashed URL.
                    url = song.path.replace(self.root, self.url.rstrip('/'))
                else:
                    url = url_for('stream', song_pk=song.pk)

        return url

    def allowed_to_stream(self, song):
        """
        """

        for mdir in self.get_dirs():
            if song.path.startswith(mdir):
                return True

        return False