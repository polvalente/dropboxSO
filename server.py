#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Servidor do Clone do Dropbox
from flask import Flask, send_file, request
from datetime import datetime
import cPickle as pickle
import os
import urllib
app = Flask(__name__)

@app.route('/<user>/<psswd>/create')
def create(user, psswd):
    '''Create new user'''
    try:
        users = pickle.load(open('./myDroboxServer/users.p','rb'))
    except:
        users = {}

    if user in users:
        #usuario ja existe
        return 'False'
    
    try:
        os.makedirs('./myDropboxServer/'+user+'/')
    except:
        return 'False'
    
    #criando o usuario
    users[user] = {'password': psswd}
    pickle.dump(user, open('./myDroboxServer/user.p', 'rb'))
    return 'True'

@app.route('/<user>/<psswd>/auth')
def auth(user, psswd):
    '''Authorize a user''' 

    try:
        users = pickle.load(open('./myDroboxServer/users.p','rb'))
    except:
        users = {}

    if user not in users:
        #usuario nao existe
        return 'False'

    if users[user]['password'] != psswd: 
        #usuario existe, mas a senha está errada
        return 'False'

    #Se chegou aqui, o usuario existe e está autorizado 
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
    app.run(host='127.0.0.1')
