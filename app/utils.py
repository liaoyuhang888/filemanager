# -*- coding: utf-8 -*-
__author__ = 'lyh'
__time__ = '2018/1/4'
import re
import mimetypes
import os
import zipstream

_filename_ascii_strip_re = re.compile(ur'[^\u4e00-\u9fa5A-Za-z0-9_.-]')
_windows_device_files = ('CON', 'AUX', 'COM1', 'COM2', 'COM3', 'COM4', 'LPT1',
                         'LPT2', 'LPT3', 'PRN', 'NUL')

class ZipUtilities:
    zip_file = None
    def __init__(self):
        self.zip_file = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED)

    def toZip(self, file, name):
        if os.path.isfile(file):
            self.zip_file.write(file, arcname=os.path.basename(file))
        else:
            self.addFolderToZip(file, name)

    def addFolderToZip(self, folder, name):
        for file in os.listdir(folder):
            full_path = os.path.join(folder, file)
            if os.path.isfile(full_path):
                self.zip_file.write(full_path, arcname=os.path.join(name, os.path.basename(full_path)))
            elif os.path.isdir(full_path):
                self.addFolderToZip(full_path, os.path.join(name, os.path.basename(full_path)))

    def close(self):
        if self.zip_file:
            self.zip_file.close()

def _get_pathinfo(path):
    path_pattern =re.compile(r'^(.*?)[\\/]*(([^/\\]*?)(\.([^\.\\/]+?)|))[\\/\.]*$')
    results = path_pattern.search(path).groups()
    return dict(
        dirname=results[0],
        basename=results[1],
        filename=results[1] if os.path.isdir(path) else results[2],
        extension='' if os.path.isdir(path) else  results[3]
    )

def _get_mime(ext):
    if not ext:
        return ''
    try:
        mtype = mimetypes.types_map[ext]
    except KeyError:
        return ''
    return mtype

def response_stat(path):
    return dict(
        pathinfo=_get_pathinfo(path),
        mime=_get_mime(_get_pathinfo(path)['extension'])
    )

def file_size(bytesize):
    unit = (
        (1<<50, 'PB'),
        (1<<40, 'TB'),
        (1<<30, 'GB'),
        (1<<20, 'MB'),
        (1<<10, 'KB'),
        (1, 'bytes')
    )
    if bytesize == 1:
        return '1 byte'
    for factor, suffix in unit:
        if bytesize >= factor:
            break
    return '%.2f %s' % (bytesize / factor, suffix)

def secure_filename(filename):
    r"""Pass it a filename and it will return a secure version of it.  This
    filename can then safely be stored on a regular file system and passed
    to :func:`os.path.join`.  The filename returned is an ASCII only string
    for maximum portability.

    On windows systems the function also makes sure that the file is not
    named after one of the special device files.

    >>> secure_filename("My cool movie.mov")
    'My_cool_movie.mov'
    >>> secure_filename("../../../etc/passwd")
    'etc_passwd'
    >>> secure_filename(u'i contain cool \xfcml\xe4uts.txt')
    'i_contain_cool_umlauts.txt'

    The function might return an empty filename.  It's your responsibility
    to ensure that the filename is unique and that you generate random
    filename if the function returned an empty one.

    .. versionadded:: 0.5

    :param filename: the filename to secure
    """
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, ' ')

    filename = _filename_ascii_strip_re.sub('', '_'.join(
                   filename.split())).strip('._')

    # on nt a couple of special files are present in each folder.  We
    # have to ensure that the target file is not such a filename.  In
    # this case we prepend an underline
    if os.name == 'nt' and filename and \
       filename.split('.')[0].upper() in _windows_device_files:
        filename = '_' + filename

    return filename