#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Dropbox Clone Client
import os, hashlib, urllib, pickle, requests, time, sys, shutil
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
user_path = ""

def create(user):
    '''Create user'''
    try:
        #request to server
        response = urllib.urlopen(request_url+'/create')
        created = json.loads(response.read())
        created = created['auth']
    except Exception as e:
        created = False
        print "Exception: '"+str(e)+"'"
    #returns True if user was created
    return created

def auth(user):
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

    #returns true if user is authorized
    return authorized
    
def updateModTime(name, data):
    global user_path
    
    #Update file modification and access times according to the downloaded files original modification and access times 
    os.utime(user_path+name, (1.0*data['time'], 1.0*data['time']))


def download(user, name, data):
    '''Request file from server'''
    global user_path
    
    if (not auth(user)): print "User not authorized"


    #if user directory doesn't exist, create ir
    if not os.path.exists(user_path):
        os.makedirs(user_path)

    #if item is a directory
    if data['type'] == 'dir':
        #Create directory
        if not os.path.exists(user_path+name):
            os.makedirs(user_path+name)
        print "Downloaded %s: '%s'" % (data['type'], name)
    else:
        #if item is a file, delete old file 
        #(workaround for a bug, should move to safe location and delete after request success)

        if(os.path.exists(user_path+name)):
            os.remove(user_path+name)
        #request for file
        url = request_url+'/download/'
        urllib.urlretrieve(url, filename=user_path+name, data=urllib.urlencode({'name':name}))
        #should check if file has been downloaded successfully
        print "Downloaded %s: '%s'" % (data['type'], name)
    return
    
def upload(user, name, data):
    '''Send file to server'''
    
    if (not auth(user)): print "User not authorized"

    print "Sending %s: '%s'" % (data['type'], name)
    content = None
    if data['type'] == 'file':
        #if we need to upload a file, open it as binary
        content = open(user_path+name, 'rb')
        #send file through the post request and also send its modification/acess time
        r = requests.post(request_url+'/upload/'+data['type'], files={name:content}, data={'time':data['time']})
        content.close() 
        return r.ok

    #else - data[type] == dir
    #for dirs, we only need to send its name and time, since it will be created locally on the server
    r = requests.post(request_url+'/upload/'+data['type'], data={'name':name, 'time':data['time']})
    return r.ok



def delete_server(user, name, data):
    '''Erase file from server'''
    if (not auth(user)): print "User not authorized"
    #request file deletion from server
    r = requests.post(request_url+'/delete', data={'name':name,'type':data['type']})
    return r.ok
    

def delete_local(user, name, data):
    '''Erase file from current directory'''
    if (not auth(user)): print "User not authorized"

    fname = name
    if fname[0] == '/':
            fname = fname[1:]

    print "Removing %s: '%s'" % (data['type'], name)
    #if item doesn't exist already, job is done
    if(not os.path.exists(user_path+'/'+fname)):
        return True
    
    if(data['type'] == 'dir'):
        #remove whole subtree if dir
        shutil.rmtree(user_path+'/'+fname)
    else:
        #remove file
        os.remove(user_path+'/'+fname)
    return True

def decide(user, changes):
    for x in changes:
        k = x[0]
        if x[1]['status'] == 'Conflict':
            #relabel item as download
            x[1]['status'] = 'Download'
            #create conflict copy
            copyfile(user_path+k, user_path+k+'_conflict'+time.strftime("-%d-%m-%Y-%H-%M-%S"))

        #if item was relabelled, it will be downloaded
        if x[1]['status'] == 'Download': download(user, k, x[1])
        elif x[1]['status'] == 'Upload': upload(user, k, x[1])
        elif x[1]['status'] == 'Delete server': delete_server(user, k, x[1])
        elif x[1]['status'] == 'Delete local': delete_local(user, k, x[1])

def get_local_items():
    local_files, local_dirs = lister.list()
    items = local_files.copy()
    items.update(local_dirs)
    return items 

def get_server_items():
    if (not auth(user)): print "User not authorized"
    r = urllib.urlopen(request_url+'/list')
    r = r.read()
    data = json.loads(r)

    l = data['files'].copy()
    l.update(data['dirs'])
    return l 
    

def update(user):
    '''Verify differences between server and local to decide what to do'''
    global old_local, old_server

    if (not auth(user)): print "User not authorized"

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
        
        changes[item]['status'] = None
        changes[item]['type'] = vals[index]['type']
        changes[item]['level'] = vals[index]['level']
        changes[item]['time'] = vals[index]['time']

        if (item in local) and (item not in server):
            changes[item]['status'] = 'Upload'
        if (item not in local) and (item in server):
            changes[item]['status'] = 'Download'
        if (item in server) and (item in local):
            #check for conflicts
            if (server[item]['time'] > local[item]['time']):
                #file has been changed in server
                if (current_login > server[item]['time']) and (local[item]['time'] > last_logout):
                    #file conflict, as described in readme
                    changes[item]['status'] = 'Conflict'
                else:
                    changes[item]['status'] = 'Download'
            elif (server[item]['time'] < local[item]['time']):
                changes[item]['status'] = 'Upload'
        if (item not in server) and (item in old_server):
            changes[item]['status'] = 'Delete local'
        if (item not in local) and (item in old_local):
            changes[item]['status'] = 'Delete server'

        if (changes[item]['status'] == 'Download' or changes[item]['status'] == 'Conflict'):
            #we need to keep the server time if we are downloading the file 
            changes[item]['time'] = server[item]['time']
        if (changes[item]['status'] == 'Upload'):
            #we need to keep the local time if we are uploading a file
            changes[item]['time'] = local[item]['time']
            
        
    #select (key, val) pairs that are of type 'file' and then transform back into a dict
    l = zip(changes.keys(), changes.values())

    #extract files from 'changes' list 'l'
    files = dict(filter(lambda p: p[1]['type'] == 'file', l))
    files = map(list,zip(files.keys(), files.values()))
    
    #sort files by level
    files.sort(cmp=lambda x, y: cmp(x[1]['level'], y[1]['level']))

    #do the same for dirs
    dirs = dict(filter(lambda p: p[1]['type'] == 'dir', l))
    dirs = map(list,zip(dirs.keys(), dirs.values()))
    dirs.sort(cmp=lambda x, y: cmp(x[1]['level'], y[1]['level']))

    #treat dirs first so downloaded directory trees are created before their content
    decide(user, dirs)
    decide(user, files)

    for k in reversed(files):
        #for each downloaded file, update modification/acess times
        if k[1]['status'] == 'Download': 
            updateModTime(k[0], k[1])

    for k in reversed(dirs):
        #for each downloaded dir, update modification/acess times
        #needs to be after file because the file updates could trigger a directory modification/acess time change
        if k[1]['status'] == 'Download': 
            updateModTime(k[0], k[1])

    old_server = server
    old_local = local
    return

def load_user_data(user):
    try:
        #try to acess a given user's metadata
        userData_path = '.users/'+user+'.p'
        data = None
        with open(userData_path, 'rb') as f:
            data = pickle.load(f)
        return data['local'], data['server'], data['time']
    except:
        #if the file open fails, it means we have no previous acess
        return {}, {}, 0


def save_user_data(user, time_last_save):
    global old_local, old_server
    #dump user metadata to file using pickle
    userData_path = '.users/'+user+'.p'
    data = {'local':old_local, 'server':old_server, 'time':time_last_save}
    with open(userData_path, 'wb') as f:
        pickle.dump(data, f)

def update_logintimes(user, t):
    global current_login, last_logout
    current_login = time.time()
    last_logout = t

def main():
    '''Main function'''
    global request_url, user, user_path, lister, old_local, old_server
    logged = False

    #loop for user authorization/creation
    while not logged:
        user = raw_input("Usuario: ")
        request_url = url+'/'+user
        user_path = './myDropbox/'+user
        
        #if user fails auth, try to create new user
        if auth(user):
            logged = True
        elif create(user):
            os.makedirs(user_path)
            logged = True



    #try to load old_local and old_server from files
    time_last_save = time.time()
    old_local, old_server, time_last_save = load_user_data(user) 
    update_logintimes(user, time_last_save) # update user current_login and last_login
    print "Done loading."

    lister = DirList(user_path)
    #main loop
    while(True):
        try:
        #verifies current dir state with a periodic probe
            update(user)
            time.sleep(sleep_time)
            t = time.time()
            if (t - time_last_save) > backup_time:
                save_user_data(user, time_last_save)
                time_last_save = t
        except KeyboardInterrupt:
            #if user tries to exit, save metadata and exit program normally
            save_user_data(user, time_last_save)
            print "Closing Client"
            sys.exit(0)

if __name__ == "__main__": 
    global old_local, old_server
    old_local = {}
    old_server = {}
    if(not os.path.exists('./myDropbox')):
        os.makedirs('./myDropbox')
    if(not os.path.exists('.users')):
        os.makedirs('.users')
    main()
