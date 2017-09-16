#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Dropbox Clone Client
import os, hashlib, urllib, pickle, requests, time, sys
from getpass import getpass
from shutil import copyfile
from DirList import DirList
import json

# configs
url = 'http://127.0.0.1:5000' # servidor
path = '.' # pasta atual
sleep_time = 5 
backup_time = 15*60 # 15 minutes

request_url = ""
user = ""
psswd = ""
user_path = ""

def create(user, psswd):
    '''Create user'''
    try:
        response = urllib.urlopen(request_url+'/create')
        created = json.loads(response.read())
        created = created['auth']
    except Exception as e:
        created = False
        print "Exception: '"+str(e)+"'"
    return created

def auth(user, psswd):
    '''Verify if user is authorized'''
    authorized = False
    try:
        response = urllib.urlopen(request_url+'/auth')
        response = json.loads(response.read())
        authorized = response['auth']
    except Exception as e:
        authorized = False
        print "Exception: '"+str(e)+"'"

    if not authorized:
        print "User is not authorized"

    return authorized
    
def updateModTime(name, data):
    global user_path
    os.utime(user_path+name, (data['time']*1.0, data['time']*1.0))


def download(user, psswd, name, data):
    '''Request file from server'''
    global user_path
    
    if (not auth(user, psswd)): print "User not authorized"
    print 'name:', name
    print 'data:', data

    if data['type'] == 'file':
        print "Downloading file '"+name+"'"
    try:
        if not os.path.exists(user_path):
            os.makedirs(user_path)

        if data['type'] == 'dir':
            print 'user_path:' , user_path
            print 'u+i:', user_path+name
            os.makedirs(user_path+name)
            #os.utime(user_path+name, (data['time']*1.0, data['time']*1.0))
        else:
            url = request_url+'/download/'
            urllib.urlretrieve(url, filename=user_path+name, data=urllib.urlencode({'name':name}))
            #os.utime(user_path+name, (data['time']*1.0, data['time']*1.0))
    except:
        return "Unable to download file '"+name+"'"
    return
    
def upload(user, psswd, name, data):
    '''Send file to server'''
    
    if (not auth(user, psswd)): print "User not authorized"

    print "Sending file: '", name, "'"
    content = None
    if data['type'] == 'file':
        content = open(name, 'rb')
    r = requests.post(request_url+'/upload/'+data['type'], files[{name:content}])
    content.close() 
    return r.ok

def delete_server(user, psswd, name, data):
    '''Erase file from server'''
    
    if (not auth(user, psswd)): print "User not authorized"
    
    raise NotImplementedError

def delete_local(user, psswd, name, data):
    '''Erase file from current directory'''
    
    if (not auth(user, psswd)): print "User not authorized"
    
    raise NotImplementedError

def decide(user, psswd, changes):
    for x in changes:
        k = x[0]
        if x[1]['status'] == 'Conflict':
            x[1]['status'] = 'Download'
            #create conflict copy
            copyfile(k, k+'_conflict'+time.strftime("-%d-%m-%Y-%H-%M-%S"))

        if x[1]['status'] == 'Download': download(user, psswd, k, x[1])
        elif x[1]['status'] == 'Upload': upload(user, psswd, k, x[1])
        elif x[1]['status'] == 'Delete server': delete_server(user, psswd, k, x[1])
        elif x[1]['status'] == 'Delete local': delete_local(user, psswd, k, x[1])

def get_local_items():
    local_files, local_dirs = lister.list()
    items = local_files.copy()
    items.update(local_dirs)
    return items 

def get_server_items():
    if (not auth(user, psswd)): print "User not authorized"
    r = urllib.urlopen(request_url+'/list')
    r = r.read()
    data = json.loads(r)
    #print 'files:', data['files']
    #print 'dirs:', data['dirs']
    #print 'auth:', data['auth']

    l = data['files'].copy()
    l.update(data['dirs'])
    return l 
    

def update(user, psswd):
    '''Verify differences between server and local to decide what to do'''

    if (not auth(user, psswd)): print "User not authorized"

    #get local file list (local) and previous probe list (old_local)
    local = get_local_items() 
    #get server file list (server) and previous probe list (old_server)
    server = get_server_items()

    changes = {}

    keys = server.keys() + local.keys()
    vals = server.values() + local.values()
    
    #compare both
    #decide what to do

    #item_list['item_path'] == {'level': int, 'type':'dir'/'file'}
    for index in xrange(len(keys)):
        item = keys[index] # item == element path
        changes[item] = {'status': None, 'type': None, 'level': None, 'time': None}
        #status: what to do
        #type: dir/file
        #level: directory tree level

        changes[item]['type'] = vals[index]['type']
        changes[item]['level'] = vals[index]['level']
        changes[item]['time'] = vals[index]['time']

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
            elif (server[item]['time'] < local[item]['time']):
                changes[item]['status'] = 'Upload'
        elif (item not in server) and (item in old_server):
            changes[item]['status'] = 'Delete local'
        elif (item not in local) and (item in old_local):
            changes[item]['status'] = 'Delete server'
        
    #select (key, val) pairs that are of type 'file' and then transform back into a dict

    l = zip(changes.keys(), changes.values())

    files = dict(filter(lambda p: p[1]['type'] == 'file', l))
    files = map(list,zip(files.keys(), files.values()))
    files.sort(cmp=lambda x, y: cmp(x[1]['level'], y[1]['level']))

    dirs = dict(filter(lambda p: p[1]['type'] == 'dir', l))
    dirs = map(list,zip(dirs.keys(), dirs.values()))
    dirs.sort(cmp=lambda x, y: cmp(x[1]['level'], y[1]['level']))

    decide(user, psswd, dirs)
    decide(user, psswd, files)

    for k in reversed(files):
        if k[1]['status'] == 'Download': 
            updateModTime(k[0], k[1])

    for k in reversed(dirs):
        if k[1]['status'] == 'Download': 
            updateModTime(k[0], k[1])

    old_server = server
    old_local = local
    return

def load_user_data(user, psswd):
    raise NotImplementedError

def save_user_data(user, psswd):
    global old_local, old_server


def main():
    '''Main function'''
    global request_url, user, psswd, user_path, lister, old_local, old_server
    logged = False

    #loop for user authorization/creation
    while not logged:
        user = raw_input("Usuario: ")
        psswd = hashlib.sha512(getpass("Senha: ")).hexdigest()
        request_url = url+'/'+user+'/'+psswd
        
        #if user/psswd fails auth, try to create new user/psswd
        logged = auth(user, psswd) or create(user, psswd)


    #update_logintimes(user) # update user current_login and last_login

    #try to load old_local and old_server from files
    time_last_save = time.time()
    #old_local, old_server, time_last_save = load_user_data(user, psswd) 

    user_path = './myDropbox/'+user
    lister = DirList(user_path)
    #main loop
    while(True):
        try:
        #verifies current dir state with a periodic probe
            update(user, psswd)
            time.sleep(sleep_time)
            t = time.time()
            if (t - time_last_save) > backup_time:
                #save_user_data(user, time_last_save)
                time_last_save = t
        except KeyboardInterrupt:
            save_user_data(user, time_last_save)
            print "Closing Client"
            sys.exit(0)

if __name__ == "__main__": 
    global old_local, old_server
    old_local = {}
    old_server = {}
    main()
