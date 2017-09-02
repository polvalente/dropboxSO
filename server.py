#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Servidor do Clone do Dropbox
from flask import Flask, send_file, request
from datetime import datetime
import cPickle as pickle
import os
import urllib
app = Flask(__name__)


def server_path(s): 
    if (s[0] == '/'):
        s = s[1:]
    return './myDropboxServer/' + s

@app.route('/<user>/<psswd>/create')
def create(user, psswd):
    '''Create new user'''
    try:
        users = pickle.load(open(server_path('users.p'),'rb'))
    except:
        f = open(server_path('users.p'),'wb')
        f.close()
        users = {}

    if user in users:
        print 'User already exists'
        return 'False'
    
    if not os.path.exists(server_path(user+'/')):
        try:
            os.makedirs(server_path(user+'/'))
        except:
            return 'False'
    
    #creating user
    users[user] = {'password': psswd}
    pickle.dump(users, open(server_path('users.p'), 'wb'))
    return 'True'

@app.route('/<user>/<psswd>/auth')
def auth(user, psswd):
    '''Authorize a user''' 

    try:
        users = pickle.load(open(server_path('users.p'),'rb'))
    except:
        users = {}

    if user not in users:
        print('user doesnt exist')
        return 'False'

    if users[user]['password'] != psswd: 
        print 'Wrong password'
        return 'False'

    return 'True'

@app.route('/<user>/<psswd>/list')
def get_list(user, psswd):
    '''Função que retorna um objeto JSON que descreve a lista de arquivos do servidor'''
    if (auth(user, psswd) != 'True'): return "User not authorized"
    raise NotImplementedError

@app.route('/<user>/<psswd>/download', methods=['POST'])
def download(user, psswd):
    '''Essa função retorna o conteúdo do arquivo pedido em um objeto JSON'''
    if (auth(user, psswd) != 'True'): return "User not authorized"
    raise NotImplementedError

@app.route('/<user>/<psswd>/upload', methods=['POST'])
def upload(user, psswd):
    '''Essa função recebe um novo arquivo do cliente como um objeto JSON'''
    if (auth(user, psswd) != 'True'): return "User not authorized"
    raise NotImplementedError

@app.route('/<user>/<psswd>/delete', methods=['POST'])
def delete(user, psswd, item):
    '''Essa função apaga o arquivo especificado pelo cliente através de um objeto JSON'''
    if (auth(user, psswd) != 'True'): return "User not authorized"
    raise NotImplementedError

if __name__ == '__main__':
    if not os.path.exists('./myDropboxServer'):
        os.makedirs('./myDropboxServer/')
    app.run(host='127.0.0.1')
