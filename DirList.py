#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Cliente do Clone do Dropbox
import os, pickle, time

class DirList(object):
    '''This class implements methods to list a specified directory file tree'''
    def __init__(self, root_dir):
        self.root_dir = root_dir
    
    def set_root(self, root_dir):
        self.root_dir = root_dir

    def item(self, path, t):
        '''This method returns a dict that contains information (path, type and level) about a file or directory
            level refers to the depth of the item in the file tree'''
        level = path.count('/') 
        mod_time = int(os.path.getmtime(self.root_dir+path))
        #subtract from level item type is file, because of the way paths are generated
        if (t == 'file'):
            level -= 1
        return path, {'level': level, 'type': t, 'time': mod_time}

    def list(self):
        '''This method returns dicts (dir_dict, file_dict) of dictionaries of the form:
            path: {
                level: INT,
                type: 'dir'/'file'
            }
        '''
        #lists start empty
        dir_list = []
        file_list = []

        #walking the directory tree with the os.walk() call
        for path, dirs, files in os.walk(self.root_dir):
            #in each iteration, 'path' is one of the subdirectories
            
            #'dirs' contains a list of directories inside. We don't need if because we are going to traverse them anyway
            #append current dir to the list
            if(path != self.root_dir):
                dir_list.append(path[len(self.root_dir):])

            #for each file in 'files', we build its corresponding item
            #the resulting list is extended into file_list
            file_list += map(lambda f: str(path[len(self.root_dir):])+'/'+f, files)
        
        dir_data = map(lambda d: self.item(d, 'dir')[1], dir_list)
        file_data = map(lambda f: self.item(f, 'file')[1], file_list)

        dir_dict = dict(zip(dir_list, dir_data))
        file_dict = dict(zip(file_list, file_data))

        return (dir_dict, file_dict)

if __name__ == "__main__":
    #Test program. This won't be run when we import this module.
    lister = DirList('.')
    (dirs, files) = lister.list()
    print 'DIRS:'
    print dirs
    print ''
    print 'FILES:'
    print files



