
'''
Created on Sep 6, 2014

@author: Mukundan
'''

'''
        frameWidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        paddingRight = self._clearButton.sizeHint().width() + frameWidth + 1
        stylesheet = "QLineEdit {{ padding-right:{0}px; }}".format(paddingRight)
        self.setStyleSheet(stylesheet)
'''


'''
from kmxGeneral import kmxINIConfigReadWrite
from kmxGeneral import kmxTools
from kmxPyQt import kmxQtCommonTools


        self.cfg = kmxINIConfigReadWrite.INIConfig("config.ini")
        self.iconPath = self.cfg.getOption('UserInterface', 'IconPath')
        self.icons = core.icons.iconSetup()
        self.infoStyle = kmxTools.infoStyle()
        self.infoStyle.errorLevel = 2
        self.infoStyle.infoLevel = 0

        self.tls = kmxTools.Tools(self.infoStyle)
        self.qtTools = kmxQtCommonTools.CommonTools(self.win, self.iconPath)


        or

        self.qtTools = kmxQtCommonTools.CommonTools(self)
        self.ttls = kmxTools.Tools()


'''

from time import strftime
import inspect
import os
import pickle
import random
import shutil
import sys
import re
numbers = re.compile('\d+')
import socket
import getpass
import logging as log
import uuid
from uuid import getnode as get_mac
import traceback
import subprocess

#Include below point in your main and errors will be displayed.
#sys.excepthook = kmxTools.errorHandler

def errorHandler(etype, value, tb):
    """
    Global function to catch unhandled exceptions.
    
    @param etype exception type
    @param value exception value
    @param tb traceback object
    """    
    
    info = ''
    try:
        info = traceback.format_exc()
        print(info)
    except:
        print ('Traceback formatter failed! Custom formatted exception info')
        print('--------')
        print('')
        info = traceback.format_exception(etype, value, tb)
        disp = ''
        for eachLine in info:
            disp += eachLine
        print(disp)
        info = disp
        print('--------')
    try:
        f = open('error.log', "w")
        f.write(str(info))
        f.close()
    except IOError:
        pass    
    
class Tools(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.randomSeed = 50
        self.rand = random.Random(self.randomSeed)
        
    def shellExecute(self, command):
        #This will chock and execute
        subprocess.call(command)              
    
    def raiseError(self, msg='CustomError'):
        raise Exception(msg)
    
    def encrypt(self, text, cryptoKey=4132):
        cipher=''
        for each in text:
            c = (ord(each)+int(cryptoKey)) % 126
            if c < 32: c+=31
            cipher += chr(c)
        return cipher
    
    def decrypt(self, text, cryptoKey=4132):
        plaintext=''
        for each in text:
            p = (ord(each)-int(cryptoKey)) % 126    
            if p < 32: p+=95
            plaintext += chr(p)
        return plaintext   
    
    def getUUID(self):
        return str(uuid.getnode())       
    
    def errorInfoOld(self):
        TrackStack = sys.exc_info()[2]
        ErrorReport = []
        while TrackStack:
            FileName = TrackStack.tb_frame.f_code.co_filename
            FunctionName = TrackStack.tb_frame.f_code.co_name
            ErrorLine =TrackStack.tb_lineno
            TrackStack = TrackStack.tb_next
            ErrorReport.append([FileName,FunctionName,ErrorLine])
        ErrorReport.append([sys.exc_info()[0],sys.exc_info()[1],0])

        ErrorInfo=''
        for eachErrorLevel in ErrorReport:
            ErrorInfo+= '\nFile: "' + str(eachErrorLevel[0]) + '", line ' + str(eachErrorLevel[2]) + ', in ' + str(eachErrorLevel[1])

        print(ErrorInfo)
        return None        

    def errorInfo(self):
        info = traceback.format_exc()
        print(info)        

    def printObjInfos(self, obj):
        lst = self.getObjInfos(obj)
        for each in lst:
            print('{0} - {1}'.format(each[0],each[1]))

    def getObjInfos(self, obj):
        infos = []
        members = inspect.getmembers(obj)
        for eachMember in members:
            obj = eachMember[1]
            mem = eachMember[0]
            tp = 'Obj'
            if inspect.isfunction(obj) or inspect.ismethod(obj):
                tp = 'Fn'
            elif inspect.isbuiltin(obj):
                tp = 'Fn-BuiltIn'
            elif inspect.isclass(obj):
                tp = 'Class'
            elif inspect.ismodule(obj):
                tp = 'Module'
            elif inspect.iscode(obj):
                tp = 'Code'
            elif (type(obj) is type(1) or
                type(obj) is type('') or
                type(obj) is type([]) or
                type(obj) is type(()) or
                type(obj) is type({})
              ):
                tp = 'Variable'
            elif type(obj) is type(None):
                tp = 'Obj'
            else:
                tp = 'Obj'
        
            infos.append([mem,tp,eachMember[1]])
        return infos

    def getRandom(self, stop, start=0):
        return self.rand.randrange(start, stop)

    def getSystemName(self):
        return str(socket.gethostname())

    def getCurrentPath(self):
        return os.path.abspath(os.curdir)
    
    def getCurrentUser(self):
        return getpass.getuser()

    def getRelativeFolder(self, folderName):
        return os.path.join(self.getCurrentPath(), folderName)

    def getDateTime(self, format="%Y-%m-%d %H:%M:%S"):
        """
        "%Y-%m-%d %H:%M:%S"
        Directive Meaning Notes
        %a Locale's abbreviated weekday name.
        %A Locale's full weekday name.
        %b Locale's abbreviated month name.
        %B Locale's full month name.
        %c Locale's appropriate date and time representation.
        %d Day of the month as a decimal number [01,31].
        %H Hour (24-hour clock) as a decimal number [00,23].
        %I Hour (12-hour clock) as a decimal number [01,12].
        %j Day of the year as a decimal number [001,366].
        %m Month as a decimal number [01,12].
        %M Minute as a decimal number [00,59].
        %p Locale's equivalent of either AM or PM. (1)
        %S Second as a decimal number [00,61]. (2)
        %U Week number of the year (Sunday as the first day of the week) as a decimal number [00,53]. All days in a new year preceding the first Sunday are considered to be in week 0. (3)
        %w Weekday as a decimal number [0(Sunday),6].
        %W Week number of the year (Monday as the first day of the week) as a decimal number [00,53]. All days in a new year preceding the first Monday are considered to be in week 0. (3)
        %x Locale's appropriate date representation.
        %X Locale's appropriate time representation.
        %y Year without century as a decimal number [00,99].
        %Y Year with century as a decimal number.
        %Z Time zone name (no characters if no time zone exists).
        %% A literal "%" character.
        """
        return strftime(format)

    def fileContent(self, fileName):
        f = open(fileName, "r")
        content = str(f.read())
        f.close()
        return content

    def writeFileContent(self, fileName, data):
        f = open(fileName, 'w')
        f.write(str(data))
        f.close()

    def cleanFolder(folder):
        folder = os.path.abspath(folder)
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))        

    def copyFile(self, src, dst):
        shutil.copy(src, dst)

    def copyFolderSpl(self, src, dst):
        src = os.path.abspath(src)
        dst = os.path.abspath(dst)
        shutil.copytree(src, dst)

    def copyFolder(self, source_folder, destination_folder, latest_overwrite=1, forced_overwrite=0, verbose=1):
        for root, dirs, files in os.walk(source_folder):
            for item in files:
                src_path = os.path.join(root, item)
                dst_path = os.path.join(destination_folder, src_path.replace(source_folder, ""))
                if os.path.exists(dst_path):
                    if (not forced_overwrite and not latest_overwrite):
                        if(verbose):
                            print("Already exist, Skipping...\n" + src_path + " to " + dst_path)
                    if (not forced_overwrite and latest_overwrite):
                        if os.stat(src_path).st_mtime > os.stat(dst_path).st_mtime:
                            if(verbose):
                                print("Overwriting latest...\n" + src_path + " to " + dst_path)
                            shutil.copy2(src_path, dst_path)
                    if (forced_overwrite):
                        if(verbose):
                            print("Overwriting...\n" + src_path + " to " + dst_path)
                        shutil.copy2(src_path, dst_path)
                else:
                    if(verbose):
                        print("Copying...\n" + src_path + " to " + dst_path)
                    shutil.copy2(src_path, dst_path)
            for item in dirs:
                src_path = os.path.join(root, item)
                dst_path = os.path.join(destination_folder, src_path.replace(source_folder, ""))
                if not os.path.exists(dst_path):
                    if(verbose):
                        print("Creating folder...\n" + dst_path)
                    os.mkdir(dst_path)
        if(verbose):
            print("Copy process completed!")

    def _buildCallerPath(self, parentOnly=0):
        stack = inspect.stack()
        path = ""
        for eachStack in stack:
            if("self" in eachStack[0].f_locals.keys()):
                the_class = eachStack[0].f_locals["self"].__class__.__name__
                the_method = eachStack[0].f_code.co_name
                if(the_class != "basic"):
                    if(parentOnly):
                        path = "{}.{}()->".format(the_class, the_method)
                    else:
                        path += "{}.{}()->".format(the_class, the_method)
        return path

    def makeEmptyFile(self, fileName):
        self.makePathForFile(fileName)
        self.writeFileContent(fileName, '')

    def makePathForFile(self, file):
        base = os.path.dirname(file)
        self.makePath(base)

    def makePath(self, path):
        print(path)
        if(not os.path.exists(path) and path != ''):
            os.makedirs(path)
        else:
            log.error("Unable to read (OR) Path exists " + path)

    def isPathOK(self, path):
        return os.path.exists(path) and path != '' and path is not None

    def isPathFile(self, path):
        return os.path.isfile(path) and path != '' and path is not None

    def pickleSaveObject(self, obj, file=""):
        if(obj is None):
            log.error("Pass me valid object to save" + obj)
        className = obj.__class__.__name__
        if(file is None or file == ""):
            file = className + ".txt"
        base = os.path.dirname(file)
        if(not os.path.exists(base) and base != ''):
            os.makedirs(base)
        f = open(file, "wb")
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
        f.close()
        print("Saved!" + className + "-" + file)

    def pickleLoadObject(self, file):
        x = None
        if(file is None or file == ""):
            log.error("Pass me file name to read and pass the object")
        if(os.path.exists(file)):
            try:
                f = open(file, "rb")
                x = pickle.load(f)
                f.close()
                log.info ("File read and obj returned " + file + " obj: " + x.__class__.__name__)
            except:
                log.error ("Error loading the pickle. Passing default!")
        else:
            log.error ("Error! File doesn't exist " + file)
        return x

    def smart_bool(self, s):
        if s is True or s is False:
            return s
        s = str(s).strip().lower()
        return not s in ['false', 'f', 'n', '0', '']
