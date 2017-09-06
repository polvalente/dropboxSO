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
        if (t == 'file'):
            level -= 1
        return {'path': path, 'level': level, 'type': t} 

    def list(self):
        '''This method returns a list of dictionaries of the form:
            {
                path:STRING,
                level: INT,
                type: 'dir'/'file'
            }'''
        dir_list = []
        file_list = []
        for path, dirs, files in os.walk(self.root_dir):
            dir_list.append(self.item(path, 'dir'))
            file_list += map(lambda f: self.item(str(path)+'/'+f, 'file'), files)
        return (dir_list, file_list)

if __name__ == "__main__":
    lister = DirList('.')
    (dirs, files) = lister.list()
    print 'DIRS:'
    print dirs
    print ''
    print 'FILES:'
    print files



