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
        response = urllib.urlopen(request_url+'/create')
        created = json.loads(response.read())
        created = created['auth']
    except Exception as e:
        created = False
        print "Exception: '"+str(e)+"'"
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

    return authorized
    
def updateModTime(name, data):
    global user_path
    stats = os.stat(user_path+name)
    print "'%s'" % (user_path+name)

    os.utime(user_path+name, (stats.st_atime, float(data['time'])))


def download(user, name, data):
    '''Request file from server'''
    global user_path
    
    if (not auth(user)): print "User not authorized"


    #try:
    if not os.path.exists(user_path):
        os.makedirs(user_path)

    if data['type'] == 'dir':
        print 'user_path:' , user_path
        print 'u+i:', user_path+name
        os.makedirs(user_path+name)
        print "Downloaded %s: '%s'" % (data['type'], name)
    else:
        if(os.path.exists(user_path+name)):
            os.remove(user_path+name)
        url = request_url+'/download/'
        urllib.urlretrieve(url, filename=user_path+name, data=urllib.urlencode({'name':name}))
        print "Downloaded %s: '%s'" % (data['type'], name)
    #except:
    #    return "Unable to download file '%s'" % (name)
    return
    
def upload(user, name, data):
    '''Send file to server'''
    
    if (not auth(user)): print "User not authorized"

    print "Sending file: '%s'" % (name)
    content = None
    if data['type'] == 'file':
        content = open(user_path+name, 'rb')
        r = requests.post(request_url+'/upload/'+data['type'], files={name:content}, data={'time':data['time']})
        content.close() 
        return r.ok
    #else - data[type] == dir
    r = requests.post(request_url+'/upload/'+data['type'], data={'name':name, 'time':data['time']})
    return r.ok



def delete_server(user, name, data):
    '''Erase file from server'''
    if (not auth(user)): print "User not authorized"
    r = requests.post(request_url+'/delete', data={'name':name,'type':data['type']})
    return r.ok
    

def delete_local(user, name, data):
    '''Erase file from current directory'''
    if (not auth(user)): print "User not authorized"

    fname = data['name']
    if fname[0] == '/':
            fname = fname[1:]
    
    if(data['type'] == 'dir'):
        shutil.rmtree('./myDropbox/%s/%s' % (user, fname))
    else:
        os.remove('./myDropbox/%s/%s' % (user, fname))
    print "Removing %s: '%s'" % (data['type'], name)
    return True

def decide(user, changes):
    for x in changes:
        k = x[0]
        if x[1]['status'] == 'Conflict':
            x[1]['status'] = 'Download'
            #create conflict copy
            copyfile(user_path+k, user_path+k+'_conflict'+time.strftime("-%d-%m-%Y-%H-%M-%S"))

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
    #print 'local'
    #print local
    #print 'old_local'
    #print old_local
    #print 'server'
    #print server
    #print 'old_server'
    #print old_server

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
        if (item not in local) and (item in server):
            changes[item]['status'] = 'Download'
        if (item in server) and (item in local):
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
        if (item not in server) and (item in old_server):
            changes[item]['status'] = 'Delete local'
        if (item not in local) and (item in old_local):
            changes[item]['status'] = 'Delete server'
        
    #select (key, val) pairs that are of type 'file' and then transform back into a dict

    l = zip(changes.keys(), changes.values())

    files = dict(filter(lambda p: p[1]['type'] == 'file', l))
    files = map(list,zip(files.keys(), files.values()))
    files.sort(cmp=lambda x, y: cmp(x[1]['level'], y[1]['level']))

    dirs = dict(filter(lambda p: p[1]['type'] == 'dir', l))
    dirs = map(list,zip(dirs.keys(), dirs.values()))
    dirs.sort(cmp=lambda x, y: cmp(x[1]['level'], y[1]['level']))

    decide(user, dirs)
    decide(user, files)

    for k in reversed(files):
        if k[1]['status'] == 'Download': 
            updateModTime(k[0], k[1])

    for k in reversed(dirs):
        if k[1]['status'] == 'Download': 
            updateModTime(k[0], k[1])

    old_server = server
    old_local = local
    return

def load_user_data(user):
    try:
        userData_path = '.users/'+user+'.p'
        data = None
        with open(userData_path, 'rb') as f:
            data = pickle.load(f)
        return data['local'], data['server'], data['time']
    except:
        return {}, {}, 0


def save_user_data(user, time_last_save):
    global old_local, old_server
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
        
        #if user fails auth, try to create new user
        logged = auth(user) or create(user)



    #try to load old_local and old_server from files
    time_last_save = time.time()
    old_local, old_server, time_last_save = load_user_data(user) 
    update_logintimes(user, time_last_save) # update user current_login and last_login
    print "Done loading."

    user_path = './myDropbox/'+user
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
            save_user_data(user, time_last_save)
            print "Closing Client"
            sys.exit(0)

if __name__ == "__main__": 
    global old_local, old_server
    old_local = {}
    old_server = {}
    main()
