#!/usr/bin/env python
#Licence: GPLv2.0
#Copyright: Dave Aitel

import sys
import os.path
import os
import shutil
import urllib
try:
  import pygtk
  #tell pyGTK, if possible, that we want GTKv2
  pygtk.require("2.0")
except:
  print "You need to install pyGTK or GTKv2 or set your PYTHONPATH correctly"
  print "try: export PYTHONPATH=/usr/local/lib/python2.2/site-packages/"
  sys.exit(1)

try:
    os.statvfs
except AttributeError:
    # Win32 implementation...
    # Mac implementation...
    pass
else:
    import statvfs

  
import gtk
import gtk.glade

#now we have both gtk and gtk.glade imported
#Also, we know we are running GTKv2
def freespace(path):
    """ freespace(path) -> integer
    Return the number of bytes available to the user on the file system
    pointed to by path."""
    s = os.statvfs(path)
    return s[statvfs.F_BAVAIL] * long(s[statvfs.F_BSIZE])

def insert_row(model,parent,firstcolumn,secondcolumn):
    myiter=model.insert_after(parent,None)
    model.set_value(myiter,0,firstcolumn)
    model.set_value(myiter,1,secondcolumn)
    return myiter

class appgui:
    file_list = set()
    ok_for_copy =0
    items=0
    size_to_copy=0
    destination_folder=""
    def __init__(self):
        """
        In this init we are going to display the main serverinfo window
        """
        gladefile="pls_copy_gtk.glade"
        windowname="main"
        self.wTree=gtk.glade.XML (gladefile,windowname)
        #we only have one callback to register, but you could register
        #any number, or use a special class that 
        #automatically registers all callbacks
        dic = { "on_exit__activate":self.on_exit_clicked,"on_copy_clicked":self.on_copy_clicked,"on_exit_clicked":self.on_exit_clicked,"on_browse_clicked":self.on_browse_clicked,"on_check_clicked":self.on_check_clicked,"on_file_chooser_clicked" : self.on_file_chooser_clicked, "on_main_destroy" : (gtk.main_quit)}
        self.wTree.signal_autoconnect (dic)
    
        #self.logwindowview=self.wTree.get_widget("textview1")
        #self.logwindow=gtk.TextBuffer(None)
        #self.logwindowview.set_buffer(self.logwindow)
        
        import gobject
        #self.treeview=self.wTree.get_widget("treeview1")
        #self.treemodel=gtk.TreeStore(gobject.TYPE_STRING,
        #                             gobject.TYPE_STRING)
        #self.treeview.set_model(self.treemodel)

        #self.treeview.set_headers_visible(gtk.TRUE)
        #renderer=gtk.CellRendererText()
        #column=gtk.TreeViewColumn("Name",renderer, text=0)
        #column.set_resizable(gtk.TRUE)
        #self.treeview.append_column(column)
        #renderer=gtk.CellRendererText()
    
        #column=gtk.TreeViewColumn("Description",renderer, text=1)
        #column.set_resizable(gtk.TRUE)
        #self.treeview.append_column(column)
        self.logwindowview=self.wTree.get_widget("info_field_txt")
        self.logwindow=gtk.TextBuffer(None)
        self.logwindowview.set_buffer(self.logwindow)
        window = self.wTree.get_widget("main")
        window.show()
        #self.wTree.main.show()

        #model=self.treemodel
        #insert_row(model,None,'Empty Row', 'An Empty Row')
        #Iter=insert_row(model,None,'Cow Actions', 
        #                       'Everything you would want to do with a cow')
        #insert_row(model,Iter,'Feed Cow', 
        #          'Fills the cow with grass')
        return
#####CALLLBACKS
    
    def on_copy_clicked(self,widget):
        print "button clicked (on_copy_clicked)"
        #set_fraction
        by_count = self.wTree.get_widget("by_files_txt")
        by_size = self.wTree.get_widget("by_size_txt")
        by_count_bar =self.wTree.get_widget("byfiles")
        by_size_bar = self.wTree.get_widget("bysize")
        if (self.ok_for_copy):
            #print "kopeeshana "
            counter=0
            size=0
            for item in self.file_list:
                counter= counter+1
                size=size+os.path.getsize(item)
                gtk.mainiteration()
                by_count.set_label(str(counter)+" / "+str(self.items))
                by_count_bar.set_fraction(float(counter)/float(self.items))
                gtk.mainiteration()
                by_size.set_label(str(((size/1024)/1024))+" / "+str(((self.size_to_copy/1024)/1024))+" Mb")
                by_size_bar.set_fraction((float(size)/float(self.size_to_copy)))
                gtk.mainiteration()
                shutil.copy(item,self.destination_folder)
                #print item
        else:
            print "nekaa"
        
    def on_exit_clicked(self,widget):
        gtk.main_quit()
        
    def on_check_clicked(self,widget):
        print "button clicked (on_check_clicked)"
        filename = self.wTree.get_widget("filename").get_text()
        by_count = self.wTree.get_widget("by_files_txt")
        by_size = self.wTree.get_widget("by_size_txt")
        destination_folder = self.wTree.get_widget("destination_folder").get_text() 
        print destination_folder
        if (len(filename)>0):
            self.logwindow.insert_at_cursor("Checking file: "+filename+"\n")
            if (os.path.isfile(filename)):
                if (os.path.isdir(destination_folder)!=1):
                    self.logwindow.insert_at_cursor("Warning: There is no folder or foder is not reachable! \n")
                    return
                free_space = freespace(destination_folder)
                self.logwindow.insert_at_cursor("File exists, reading content! \n")
                in_file = open(filename, "r")
                counter=0
                exists=0
                failed=0
                size=0
                set_of_files = set()
                for line in in_file:
                    if counter==0:
                        line=line.strip()
                        if line =="[playlist]":
                            self.logwindow.insert_at_cursor("[Playlist] \n")
                        else:
                            print line
                            self.logwindow.insert_at_cursor("Warning: Wrong format, could not read playlist \n")
                            return
                    else:
                        if (line.find("file://")>0):
                            file_list=line.split("=file://")
                            pl_file = file_list[1].strip()
                            pl_file=urllib.url2pathname(pl_file)
                            #pl_file= pl_file.replace("%20"," ")
                            #pl_file= pl_file.replace("%5D","]")
                            #pl_file= pl_file.replace("%C5","\")
                            if (os.path.isfile(pl_file)):
                                self.file_list.add(pl_file)
                                size=size+os.path.getsize(pl_file)
                                exists = exists+1
                            else:
                                failed = failed+1
                                self.logwindow.insert_at_cursor("Warning: Could not reach file :"+pl_file+" \n")
                    counter = counter+1;
                if (free_space<size):
                    self.ok_for_copy=0
                    self.logwindow.insert_at_cursor("Warning: Choose different folder! Too less free disk space!! Disk space needed "+str(((size/1024)/1024))+" Mb, free disk space "+str(((free_space/1024)/1024))+" Mb \n")
                else:
                    self.ok_for_copy=1
                    by_count.set_label("0 / "+str(exists))
                    by_size.set_label("0 / "+str(((size/1024)/1024))+" Mb")
                    self.items=exists
                    self.size_to_copy=size
                    self.logwindow.insert_at_cursor("Info: Items found "+str(exists+failed)+", items ok "+str(exists)+", items failed "+str(failed)+ ", disk space needed "+str(((size/1024)/1024))+" Mb \n")
                    self.destination_folder=destination_folder
            else:
                self.logwindow.insert_at_cursor("File does not exist or is not readable! \n")
        else:
            self.logwindow.insert_at_cursor("Warning: There is no selected file! Please select playlist file!"+"\n")
            return
        
        
    def on_browse_clicked(self,widget):
        filename=""
        chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))


        response=chooser.run()
        
        if response == gtk.RESPONSE_OK:
            print chooser.get_filename(), 'selected'
            Filename = self.wTree.get_widget("destination_folder") 
            #info_field_txt=self.wTree.get_widget("info_field_txt") 
            Filename.set_text(chooser.get_filename())
            #info_field_txt.append_text("File choosed:")
            self.logwindow.insert_at_cursor("Folder choosed: "+chooser.get_filename() +"\n")
            
        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
        chooser.destroy()
        
    def on_file_chooser_clicked(self,widget):
        #window = self.wTree.get_widget("main")
        #window.hide()
        #file_chooser = self.wTree.get_widget("filechooser")
        #file_chooser.show()
        filename=""
        chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN,buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        #filter settings
        filter = gtk.FileFilter()
        filter.set_name("Playlists")
        filter.add_mime_type("audio/x-scpls")
        filter.add_pattern("*.pls")
        chooser.add_filter(filter)

        response=chooser.run()
        
        if response == gtk.RESPONSE_OK:
            print chooser.get_filename(), 'selected'
            Filename = self.wTree.get_widget("filename") 
            #info_field_txt=self.wTree.get_widget("info_field_txt") 
            Filename.set_text(chooser.get_filename())
            #info_field_txt.append_text("File choosed:")
            self.logwindow.insert_at_cursor("File choosed: "+chooser.get_filename() +"\n")
            
        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
        chooser.destroy()
        
app=appgui()
gtk.main()


