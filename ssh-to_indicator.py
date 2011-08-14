#!/usr/bin/env python
LICENSE = """
 Copyright (c) 2005 - 2010 Lyle Scott III
 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions
 are met:

 1. Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
 2. Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.
 3. Neither the name of the copyright holders nor the names of its
    contributors may be used to endorse or promote products derived from
    this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
 LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
 THE POSSIBILITY OF SUCH DAMAGE.`

 lyle@digitalfoo.net  
 http://digitalfoo.net
"""
import sys
import gtk
import appindicator
import csv
import subprocess
import shlex
import xml.dom.minidom
import pickle
import shutil
import os
import gnomeapplet
#import gobject
import pygtk
pygtk.require('2.0')

FILE_DIR = '.ssh-to_indicator'
CONFIG_FILE = 'config.xml'
CONFIG_PATH='/'.join([os.getenv('HOME'), FILE_DIR, CONFIG_FILE])

class Config:
    def __init__(self, path=CONFIG_PATH):
        if not os.path.exists(CONFIG_PATH):
            raise Exception('NO CONFIG: %s' % CONFIG_PATH)
        config = xml.dom.minidom.parse(path).getElementsByTagName('Config')[0]
        for child in config.childNodes:
            #if child.attributes is None: continue
            if child.nodeName == 'Settings':
                self._parseSettings(child)
            elif child.nodeName == 'HostDefaults':
                self._parseHostDefaults(child)
            elif child.nodeName == 'Hosts':
                self._parseHosts(child)
            elif child.nodeName in ('#text', '#comment'):
                continue
            else:
                raise Exception('Unknown <Config> element: %s' % child.nodeName)

    def _parseSettings(self, node):
        self._settings = {}
        for (k,v,) in node.attributes.items():
            self._settings[k] = str(v)
                
    def _parseHostDefaults(self, node):
        self._defaults = {}
        for (k,v,) in node.attributes.items():
            self._defaults[k] = str(v)
        
    def _parseHosts(self, node):
        self._hostinfo = {}
        for hostNode in node.childNodes:
            attrs = {}
            if hostNode.nodeName in ('#text', '#comment'):
                continue
            for (k,v,) in hostNode.attributes.items():
                attrs[k] = str(v)
            self._hostinfo[attrs['name']] = attrs
    
    def _parseSettings(self, node):
        self._settings = {}
        for (k,v,) in node.attributes.items():
            self._settings[k] = str(v) 

    def getHostinfo(self):
        return self._hostinfo
    
    def getDefaults(self, attr=None):
        if attr == None:
            return self._defaults
        return self._defaults[attr]
    
    def getSettings(self, attr=None):
        if attr == None:
            return self._settings
        return self._settings[attr]


class SSHGoToIndicator:
    def __init__(self, config):      
        self.config = Config()
        self.ind = appindicator.Indicator('SSH-To_indicator',
                                          'indicator-messages',
                                          appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_icon(self.config.getSettings('icon'))
        #self.ind.set_attention_icon('new-messages-red')
        self.ind.set_menu(self.menu_setup())
    
    def main(self):
        gtk.main()

    def menu_setup(self):
        menu = gtk.Menu()
        
        menu_item = gtk.SeparatorMenuItem()
        menu_item.show()
        menu.append(menu_item)

        for (displayname, info) in self.config.getHostinfo().items():
            port = self.config.getDefaults('port')
            sshargs = self.config.getDefaults('sshargs')
            
            # if the info isn't set by the user, substitute the default value
            info.update(dict([d for d in self.config.getDefaults().items()
                              if d[0] not in info]))
                
            menu_item = gtk.MenuItem(info['name'])
            menu_item.set_name(pickle.dumps(info))
            menu_item.connect('activate', self.connect)
            menu_item.show()
            menu.append(menu_item)

        menu_item = gtk.SeparatorMenuItem()
        menu_item.show()
        menu.append(menu_item)

        menu_item = gtk.MenuItem('About')
        menu_item.connect('activate', self.show_about)
        menu_item.show()
        menu.append(menu_item)

        menu_item = gtk.MenuItem('Quit')
        menu_item.connect('activate', self.quit)
        menu_item.show()
        menu.append(menu_item)
        
        return menu

    def connect(self, widget):    	
    	info = pickle.loads(widget.get_name())
        subcmd = 'ssh %s@%s' % (info['user'], info['host'])
        cmd = '%s %s "%s"' % (self.config.getSettings('terminal_cmd'), 
                              self.config.getSettings('wrapper_script'), 
                              subcmd)
        subprocess.Popen(shlex.split(cmd))

    def show_about(self, widget):
        dialog = gtk.AboutDialog()
        dialog.set_position(gtk.WIN_POS_CENTER)
        dialog.set_program_name("SSH-To Gnome Indicator Applet")
        dialog.set_version("0.1")
        dialog.set_copyright("(C) Lyle Scott III\n\nlyle@digitalfoo.net")
        dialog.set_website('http://digitalfoo.net')
        dialog.set_license(LICENSE)
        dialog.run()
        dialog.destroy()

    def quit(self, widget):
        sys.exit(0)


if __name__ == "__main__":
    config = Config()
    indicator = SSHGoToIndicator(config)
    indicator.main()
