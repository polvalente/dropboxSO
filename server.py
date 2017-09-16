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
app = Flask(__name__)


def server_path(s): 
    if (s[0] == '/'):
        s = s[1:]
    return './myDropboxServer/' + s

@app.route('/<user>/<psswd>/create')
def create(user, psswd):
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
    users[user] = {'password': psswd}
    pickle.dump(users, open(server_path('users.p'), 'wb'))
    res['auth'] = True
    return json.dumps(res)

@app.route('/<user>/<psswd>/auth')
def auth(user, psswd):
    '''Authorize a user''' 
    res = {'auth': False}

    try:
        users = pickle.load(open(server_path('users.p'),'rb'))
    except:
        users = {}

    if user not in users:
        print('user does not exist')
        return json.dumps(res)

    if users[user]['password'] != psswd: 
        print 'Wrong password'
        return json.dumps(res)

    res['auth'] = True
    return json.dumps(res)

def local_auth(user, psswd):
    r = auth(user, psswd)
    r = json.loads(r)
    return r['auth']

@app.route('/<user>/<psswd>/list')
def list(user, psswd):
    '''Send local directory structure to user'''
    files = []
    dirs = []
    res = {'auth':False,
            'files':files,
            'dirs': dirs}
    if (not local_auth(user, psswd)):
        return json.dumps(res)

    files, dirs = DirList(server_path(user)).list()        
    res['auth'] = True
    res['files'] = files
    res['dirs'] = dirs

    return json.dumps(res)



@app.route('/<user>/<psswd>/download/<item>', methods=['GET'])
def download(user, psswd):
    '''Return the content of a requested file'''
    res = {'auth': False}
    if (not local_auth(user, psswd)): return json.dumps{res}
    filepath = server_path(user+'/'+item)
    return send_file(filepath)


@app.route('/<user>/<psswd>/upload/<ftype>', methods=['POST'])
def upload(user, psswd):
    '''Receive a file from a client'''
    res = {'auth': False}
    if (not local_auth(user, psswd)): return json.dumps{res}
    
    if ftype == 'file':
        #file
        pass
    else:
        #dir
        pass
    raise NotImplementedError

@app.route('/<user>/<psswd>/delete', methods=['POST'])
def delete(user, psswd, item):
    '''Erase file specified by client'''
    res = {'auth': False}
    if (not local_auth(user, psswd)): return json.dumps{res}
    raise NotImplementedError

if __name__ == '__main__':
    if not os.path.exists('./myDropboxServer'):
        os.makedirs('./myDropboxServer/')
    app.run(host='127.0.0.1')
