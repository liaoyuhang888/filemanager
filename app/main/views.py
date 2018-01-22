# -*- coding: utf-8 -*-
__author__ = 'lyh'
__time__ = '2017/12/15'

from app.main import main
from flask import render_template, request, jsonify, current_app, send_file, Response, abort
from flask_login import current_user,login_required
from app.utils import response_stat, file_size, secure_filename, ZipUtilities
from paginate import Page
import os
import time
import chardet
import mimetypes

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


@main.route('/home/<path:path>', methods=['GET'])
@main.route('/home', methods=['GET'])
@login_required
def index(path=u''):
    page = request.args.get('page', 1)
    uploaded_folder = os.path.join(current_app.config['UPLOADED_FOLDER'], str(current_user.id), path)
    maxfilesizebytes = current_app.config['MAX_FILE_SIZE']
    maxfilesize = file_size(maxfilesizebytes)
    if not os.path.exists(uploaded_folder):
        os.makedirs(uploaded_folder)
    d_list = []
    f_list = []
    dirpath = '/' if not path else '{}'.format(path)
    homepath = 'home' if not path else '{}'.format(path)
    for file in os.listdir(uploaded_folder):
        filepath = os.path.join(uploaded_folder, file)
        obj = dict()
        obj['path'] = file if dirpath == '/' else u'{}/{}'.format(dirpath, file)
        obj['lastModified'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                            time.localtime(os.path.getmtime(filepath)))
        obj.update(response_stat(filepath))
        if os.path.isdir(filepath):
            obj['type'] = 'directory'
            obj['fileSize'] = file_size(os.path.getsize(filepath))
            obj['url'] = os.path.join(homepath, file).replace('\\', '/')
            d_list.append(obj)
        else:
            obj['type'] = 'file'
            obj['url'] = '/preview/{}?filename={}'.format(path, file)
            f_list.append(obj)
    pagination = Page(d_list + f_list, page=int(page), items_per_page=current_app.config['PER_PAGE'])
    return render_template('home.html',
                           path=dirpath,
                           maxfilesize=maxfilesize,
                           maxfilesizebytes=maxfilesizebytes,
                           objects=pagination)

@main.route('/manager/put/directory', methods=['PUT'])
@login_required
def new_folder():
    path = request.form.get('path')
    path = '' if path == '/' else path
    uploaded_folder = os.path.join(current_app.config['UPLOADED_FOLDER'], str(current_user.id), path)
    dirpath = u"{}/{}".format(uploaded_folder, request.form.get('dirName'))
    if os.path.exists(dirpath):
        return 'this folder folders already exists', 400
    else:
        os.mkdir(dirpath)
    file_stat = response_stat(dirpath)
    file_stat['path'] = file_stat['pathinfo']['basename'] if not path else\
        '{}/{}'.format(path, file_stat['pathinfo']['basename'])
    return jsonify(file_stat), 201

@main.route('/manager/move', methods=['POST'])
@login_required
def rename():
    path = request.form.get('path')
    path = '' if path == '/' else path
    uploaded_folder = os.path.join(current_app.config['UPLOADED_FOLDER'], str(current_user.id), path)
    oldpath = os.path.join(uploaded_folder, request.form.get('oldName'))
    newpath = os.path.join(uploaded_folder, request.form.get('newName'))
    os.rename(oldpath, newpath)
    file_stat = response_stat(newpath)
    file_stat['path'] = file_stat['pathinfo']['basename'] if not path else\
        '{}/{}'.format(path, file_stat['pathinfo']['basename'])
    return jsonify(file_stat)

@main.route('/manager/delete', methods=['DELETE'])
@login_required
def delete():
    uploaded_folder = os.path.join(current_app.config['UPLOADED_FOLDER'], str(current_user.id))
    path = request.form.get('path')
    path = u"{}/{}".format(uploaded_folder, path)
    if os.path.isdir(path): __import__('shutil').rmtree(path)
    else: os.remove(path)
    return jsonify({'status': 'ok'})

@main.route('/manager/put/file', methods=['POST'])
@login_required
def uploads():
    path = request.form.get('dirPath')
    path = '' if path == '/' else path
    uploaded_folder = os.path.join(current_app.config['UPLOADED_FOLDER'], str(current_user.id), path)
    files = request.files.getlist('files[]')
    filenames = []
    errors = []
    for file in files:
        filename = secure_filename(file.filename)
        if filename in os.listdir(uploaded_folder):
            errors.append(u'Filename {} error: Already existed'.format(filename))
            continue
        if filename:
            savepath = os.path.join(uploaded_folder, filename)
            try:
                file.save(savepath)
                file_stat = response_stat(savepath)
                file_stat['path'] = file_stat['pathinfo']['basename'] if not path else \
                    '{}/{}'.format(path, file_stat['pathinfo']['basename'])
                filenames.append(file_stat)
            except Exception, e:
                errors.append(u'File {} error: {}'.format(filename, str(e)))
        else:
            errors.append(u'File {} is incorrect'.format(filename))

    return jsonify({'errors': errors,
                    'success': filenames})

@main.route('/manager/download', methods=['POST'])
@login_required
def download():
    paths = request.form.get('path').split('///')
    zipfile = ZipUtilities()
    file_path = os.path.join(current_app.config['UPLOADED_FOLDER'], str(current_user.id), paths[0])
    if len(paths) == 1 and os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True, attachment_filename=os.path.basename(file_path))
    for path in paths:
        full_path = os.path.join(current_app.config['UPLOADED_FOLDER'], str(current_user.id), path)
        print 'full_path',full_path
        zipfile.toZip(full_path, path)
    filename = 'package.zip'
    response = Response(zipfile.zip_file, mimetype='application/zip')
    #zipfile.close()
    response.headers["Content-Disposition"] = "attachment; filename={}".format(filename)
    return response

@main.route('/preview/<path:path>', methods=['GET'])
@main.route('/preview/', methods=['GET'])
@login_required
def preview(path=u''):
    filename = request.args.get('filename')
    file_path = os.path.join(current_app.config['UPLOADED_FOLDER'], str(current_user.id), path, filename)
    mtype = mimetypes.guess_type(file_path)[0]
    if not mtype or mtype.split('/')[0].lower() not in current_app.config['ALLOWED_TYPE']:
        mtype = 'application/octet-stream'
    filetype = mtype.split('/')[0].lower()
    if filetype != 'text':
        data = 'http://{host}/uploads/{id}/{filepath}'.format(host=request.host, id=current_user.id, filepath=os.path.join(path, filename).replace('\\','/'))
    else:
        with open(file_path, 'rb') as f:
            data = f.read()
            encoding = chardet.detect(data)['encoding']
            data = data.decode(encoding)
    file_stat = response_stat(file_path)
    file_stat['path'] = file_stat['pathinfo']['basename'] if not path else \
        '{}/{}'.format(path, file_stat['pathinfo']['basename'])
    return render_template("file_preview.html",
                           filename=filename,
                           text_or_url=data,
                           filetype=filetype,
                           mtype=mtype,
                           path=path,
                           file=file_stat)