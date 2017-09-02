#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Cliente do Clone do Dropbox
import os, hashlib, urllib, pickle, requests
from time import sleep
from getpass import getpass

# configs
url = 'http://127.0.0.1:5000' # servidor
path = '.' # pasta atual
sleep_time = 5

request_url = ""
user = ""
psswd = ""

def create(user, psswd):
    '''Create user'''
    try:
        created = eval(urllib.urlopen(request_url+'/create').read())
    except:
        created = False
        print "Exception: '"+str(Exception)+"'"
    return created

def auth(user, psswd):
    '''Verify if user is authorized'''
    authorized = False
    try:
        authorized = eval(urllib.urlopen(request_url+'/auth').read())
    except:
        authorized = False
        print "Exception: '"+str(Exception)+"'"

    if not authorized:
        print "User is not authorized"

    return authorized
    
def download(user, psswd, item):
    '''Request file from server'''
    
    if (auth(user, psswd) != 'True'): print "User not authorized"
    
    raise NotImplementedError

def upload(user, psswd, item):
    '''Send file to server'''
    
    if (auth(user, psswd) != 'True'): print "User not authorized"
    
    raise NotImplementedError

def delete_server(user, psswd, item):
    '''Erase file from server'''
    
    if (auth(user, psswd) != 'True'): print "User not authorized"
    
    raise NotImplementedError

def delete_local(user, psswd, item):
    '''Erase file from current directory'''
    
    if (auth(user, psswd) != 'True'): print "User not authorized"
    
    raise NotImplementedError

def update(user, psswd, server, local):
    '''Verify differences between server and local to decide what to do'''

    if (auth(user, psswd) != 'True'): print "User not authorized"

    raise NotImplementedError

def main():
    '''Main function'''
    global request_url, user, psswd
    logged = False

    #loop for user authorization/creation
    while not logged:
        user = raw_input("Usuario: ")
        psswd = hashlib.sha512(getpass("Senha: ")).hexdigest()
        
        #if user/psswd fails auth, try to create new user/psswd
        logged = auth(user, psswd) or create(user, psswd)

    request_url = url+'/'+user+'/'+psswd

    #main loop
    while(True):
        #verifies current dir state with a periodic probe
        update(user, psswd)
        sleep(sleep_time)



if __name__ == "__main__": 
    old_local = {}
    old_server = {}
    main()
