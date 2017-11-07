#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Dropbox Clone Server
from flask import Flask, send_file, request, jsonify
from datetime import datetime
import cPickle as pickle
import os
import urllib
from DirList import DirList
import json
import re
import shutil
app = Flask(__name__)


def server_path(s): 
    if (s[0] == '/'):
        s = s[1:]
    return './myDropboxServer/' + s

@app.route('/<user>/create')
def create(user):
    '''Create new user'''
    res = {'auth': False}
    s = re.compile('\W')
    if(s.search(user) is not None): #user is not alphanumeric
        return json.dumps(res)
    try:
        users = pickle.load(open(server_path('users.p'),'rb'))
    except:
        f = open(server_path('users.p'),'wb')
        f.close()
        users = {}

    if user in users:
        print 'User already exists'
        return json.dumps(res)
    
    if not os.path.exists(server_path(user+'/')):
        try:
            os.makedirs(server_path(user+'/'))
        except:
            return json.dumps(res)
    
    #creating user
    users[user] = {'password': None}
    pickle.dump(users, open(server_path('users.p'), 'wb'))
    res['auth'] = True
    return json.dumps(res)

@app.route('/<user>/auth')
def auth(user):
    '''Authorize a user''' 
    res = {'auth': False}

    try:
        users = pickle.load(open(server_path('users.p'),'rb'))
    except:
        users = {}

    if user not in users:
        print('user does not exist')
        return json.dumps(res)

    res['auth'] = True
    return json.dumps(res)

def local_auth(user):
    r = auth(user)
    r = json.loads(r)
    return r['auth']

@app.route('/<user>/list')
def list(user):
    '''Send local directory structure to user'''
    files = []
    dirs = []
    res = {'auth':False,
            'files':files,
            'dirs': dirs}
    if (not local_auth(user)):
        return json.dumps(res)

    dirs, files = DirList(server_path(user)).list()        
    res['auth'] = True
    res['files'] = files
    res['dirs'] = dirs

    return json.dumps(res)



@app.route('/<user>/download/', methods=['POST'])
def download(user):
    '''Return the content of a requested file'''
    res = {'auth': False}
    if (not local_auth(user)): return json.dumps(res)

    fname = request.form['name']
    filepath = server_path(user+fname)
    return send_file(filepath)


@app.route('/<user>/upload/<ftype>', methods=['POST'])
def upload(user, ftype):
    '''Receive a file from a client'''
    res = {'auth': False}
    if (not local_auth(user)): return json.dumps(res)
    res['auth'] = True
    
    print request.form
    data = request.form
    fpath = ''
    if ftype == 'file':
        #file
        for f in request.files:
            fname = f
            if fname[0] == '/':
                fname = fname[1:]
            fpath = './myDropboxServer/%s/%s' % (user, fname)
            request.files[f].save(fpath)
    else:
        #dir
        fname = data['name']
        if fname[0] == '/':
            fname = fname[1:]
        fpath = './myDropboxServer/%s/%s' % (user, fname)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
    
    os.utime(fpath, (float(data['time'])*1.0, float(data['time'])*1.0))
    return json.dumps(res)

@app.route('/<user>/delete', methods=['POST'])
def delete(user):
    '''Erase file specified by client'''
    res = {'auth': False}
    if (not local_auth(user)): return json.dumps(res)
    res['auth'] = True
    
    data = request.form
    fname = data['name']
    if fname[0] == '/':
            fname = fname[1:]
    if(data['type'] == 'dir'):
        shutil.rmtree('./myDropboxServer/%s/%s' % (user, fname))
    else:
        os.remove('./myDropboxServer/%s/%s' % (user, fname))
    return json.dumps(res)

if __name__ == '__main__':
    if not os.path.exists('./myDropboxServer'):
        os.makedirs('./myDropboxServer/')
    app.run(host='0.0.0.0')
