#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Cliente do Clone do Dropbox
import os, hashlib, urllib, pickle, requests, time
from getpass import getpass
from shutil import copyfile

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
    
def download(user, psswd, name, data):
    '''Request file from server'''
    
    if (auth(user, psswd) != 'True'): print "User not authorized"

    if data['type'] == 'file':
        print "Downloading file '"+name+"'"
    try:
        userpath = './myDropbox/'+user+'/'
        if not os.path.exists(userpath):
            os.makedirs(userpath)

        if data['type'] == 'dir':
            os.makedirs(userpath+item)
        else:
            url = request_url+'/'+urllib.quote_plus(name)
            urllib.urlretrieve(url, filename=userpath+item)
    except:
        return "Unable to download file '"+name+"'"
    return
    
def upload(user, psswd, name, data):
    '''Send file to server'''
    
    if (auth(user, psswd) != 'True'): print "User not authorized"

    print "Sending file: '", name, "'"
    content = open(name, 'rb')
    r = requests.post(request_url, files[{name:content}])
    content.close() 
    return r.ok

def delete_server(user, psswd, name, data):
    '''Erase file from server'''
    
    if (auth(user, psswd) != 'True'): print "User not authorized"
    
    raise NotImplementedError

def delete_local(user, psswd, name, data):
    '''Erase file from current directory'''
    
    if (auth(user, psswd) != 'True'): print "User not authorized"
    
    raise NotImplementedError

def decide(user, psswd, changes):
    for k in changes:
        if changes[k]['status'] == 'Conflict':
            changes[k]['status'] = 'Download'
            #create conflict copy
            copyfile(k, k+'_conflict'+time.strftime("-%d-%m-%Y-%H-%M-%S"))

        if changes[k]['status'] == 'Download': download(user, psswd, k, changes[k])
        elif changes[k]['status'] == 'Upload': upload(user, psswd, k, changes[k])
        elif changes[k]['status'] == 'Delete server': delete_server(user, psswd, k, changes[k])
        elif changes[k]['status'] == 'Delete local': delete_local(user, psswd, k, changes[k])

def update(user, psswd, server, local):
    '''Verify differences between server and local to decide what to do'''

    if (auth(user, psswd) != 'True'): print "User not authorized"

    #get local file list (local) and previous probe list (old_local)
    local, old_local = get_local_files() 
    #get server file list (server) and previous probe list (old_server)
    server, old_server = get_server_files()

    changes = {}

    elements = server.keys() + local.keys()
    element_data = server.values() + local.values()
    
    #compare both
    #decide what to do

    #item_list['item_path'] == {'level': int, 'type':'dir'/'file'}
    for index in xrange(len(files)):
        item = files[index] # item == element path
        changes[item] = {'status': None, 'type': None, 'level': None}
        #status: what to do
        #type: dir/file
        #level: directory tree level

        changes[item]['type'] = vals[index]['type']

        if (item in local) and (item not in server):
            changes[item]['status'] = 'Upload'
        elif (item not in local) and (item in server):
            changes[item]['status'] = 'Download'
        elif (item in server) and (item in local):
            #check for conflicts
            if (server[item]['time'] > local[item]['time']):
                #file has been changed in server
                if (current_login > server[item]['time']) and (local[item]['time'] > last_logout):
                    #file conflict
                    changes[item]['status'] = 'Conflict'
                else:
                    changes[item]['status'] = 'Download'
        elif (item not in server) and (item in old_server):
            changes[item]['status'] = 'Delete local'
        elif (item not in local) and (item in old_local):
            changes[item]['status'] = 'Delete server'
        
    

    #do things
    dirs, files = split_file_list(changes)
    decide(user, psswd, dirs)
    decide(user, psswd, files)

    old_server = server
    old_local = local
    return


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

    update_logintimes(user) # update user current_login and last_login

    #main loop
    while(True):
        #verifies current dir state with a periodic probe
        update(user, psswd)
        time.sleep(sleep_time)



if __name__ == "__main__": 
    old_local = {}
    old_server = {}
    main()
