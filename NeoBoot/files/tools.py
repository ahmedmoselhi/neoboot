#!/usr/bin/python
# -*- coding: utf-8 -*-
# system modules


from Plugins.Extensions.NeoBoot.__init__ import _
import codecs
from enigma import getDesktop
from Components.About import about
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Button import Button
from Components.GUIComponent import *
from Components.Input import Input
from Components.Label import Label
from Components.ProgressBar import ProgressBar
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap, MultiPixmap
from Components.config import *
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Components.Sources.List import List
from Components.ConfigList import ConfigListScreen
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.config import getConfigListEntry, config, ConfigYesNo, ConfigText, ConfigSelection, NoSave
from Plugins.Extensions.NeoBoot.plugin import Plugins, PLUGINVERSION, UPDATEVERSION
from Plugins.Plugin import PluginDescriptor
from Screens.Standby import TryQuitMainloop
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, fileExists, pathExists, createDir
from Tools.Testinout import getTestToTest
from os import system, listdir, mkdir, chdir, getcwd, rename as os_rename, remove as os_remove, popen
from os.path import dirname, isdir, isdir as os_isdir
from enigma import eTimer
from Plugins.Extensions.NeoBoot.files.stbbranding import fileCheck, getMyUUID, getNeoLocation, getImageNeoBoot, getKernelVersionString, getBoxHostName, getCPUtype, getBoxVuModel, getTunerModel, getCPUSoC, getImageATv, getBoxModelVU, getBoxMacAddres, getMountDiskSTB, getCheckActivateVip, getBoxMacAddres, getChipSetString
from Components.Harddisk import harddiskmanager, getProcMounts
import os
import time
import sys
import struct
import shutil

from Screens.Console import Console

LinkNeoBoot = '/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot'
neoboot = getNeoLocation()
media = getNeoLocation()
mediahome = media + '/ImageBoot/'


def getDS():
    s = getDesktop(0).size()
    return (s.width(), s.height())


def isFHD():
    desktopSize = getDS()
    return desktopSize[0] == 1920


def isHD():
    desktopSize = getDS()
    return desktopSize[0] >= 1280 and desktopSize[0] < 1920


def isUHD():
    desktopSize = getDS()
    return desktopSize[0] >= 1920 and desktopSize[0] < 3840


def getKernelVersion():
    try:
        # File operations use 'r' for read, which is Python 3 compatible for text
        return open(
            '/proc/version',
            'r').read().split(
            ' ',
            4)[2].split(
            '-',
            2)[0]
    except BaseException:
        return _('unknown')


def getCPUtype():
    cpu = 'UNKNOWN'
    if os.path.exists('/proc/cpuinfo'):
        # Correct use of 'with open' for file handling
        with open('/proc/cpuinfo', 'r') as f:
            lines = f.read()
        if lines.find('ARMv7') != -1:
            cpu = 'ARMv7'
        elif lines.find('mips') != -1:
            cpu = 'MIPS'
    return cpu


def getNeoActivatedtest():
    neoactivated = 'NEOBOOT MULTIBOOT'
    if not fileExists('/.multinfo'):
        if getCheckActivateVip() != getBoxMacAddres():
            neoactivated = 'Ethernet MAC not found.'
        elif not fileExists('/usr/lib/periodon/.kodn'):
            neoactivated = 'VIP Pin code missing.'
        elif getTestToTest() != UPDATEVERSION:
            neoactivated = _('Update %s is available.') % getTestToTest()
        else:
            if getCheckActivateVip() == getBoxMacAddres() and fileExists(
                    '/usr/lib/periodon/.kodn') and getTestToTest() == UPDATEVERSION:
                neoactivated = 'NEOBOOT VIP ACTIVATED'

    return neoactivated

# Use 'with open' for clarity and safety, though the original was already correct.
if os.path.exists('/etc/hostname'):
    with open('/etc/hostname', 'r') as f:
        myboxname = f.readline().strip()

if os.path.exists('/proc/stb/info/vumodel'):
    with open('/proc/stb/info/vumodel', 'r') as f:
        vumodel = f.readline().strip()

if os.path.exists('/proc/stb/info/boxtype'):
    with open('/proc/stb/info/boxtype', 'r') as f:
        boxtype = f.readline().strip()

class BoundFunction:
    __module__ = __name__

    def __init__(self, fnc, *args):
        self.fnc = fnc
        self.args = args

    def __call__(self):
        # Standard function call, fully compatible with Python 3.13
        self.fnc(*self.args)


class MBTools(Screen):
    # Enigma2 skin definition (compatibility depends on the Enigma2 version)
    if isFHD():
        skin = """<screen name="MBTools" position="105,81" size="1720,940" title="Tools">
          <ePixmap position="1423,735" zPosition="-2" size="298,119" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/ico_neo.png" />
          <ePixmap position="1307,377" zPosition="-2" size="409,256" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/matrixhd.png" />
          <eLabel position="20,60" size="1690,5" backgroundColor="blue" foregroundColor="blue" name="linia" />
          <eLabel position="20,935" size="1690,5" backgroundColor="blue" foregroundColor="blue" name="linia" />
          <ePixmap position="25,-1" size="45,65" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/updown.png" alphatest="on" />
          <eLabel backgroundColor="background" font="baslk; 29" foregroundColor="yellow" position="623,-2" size="280,60" text="Menu list NEOBoot" />
          <eLabel backgroundColor="background" font="baslk; 29" foregroundColor="red" position="1341,195" size="366,60" text="NEOBOOT VIP Activated" />
          <widget source="list" render="Listbox" position="20,80" size="1282,855" scrollbarMode="showOnDemand">
          <convert type="TemplatedMultiContent">\n                \t\t{"template": [\n                    \t\t\tMultiContentEntryText(pos = (50, 1), size = (925, 58), flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 0),\n                    \t\t\tMultiContentEntryPixmapAlphaTest(pos = (6, 4), size = (66, 66), png = 1),\n                    \t\t\t],\n                    \t\t\t"fonts": [gFont("Regular", 35)],\n                    \t\t\t"itemHeight": 60\n                \t\t}\n            \t\t</convert>
          </widget>
          </screen>"""
    else:
        skin = '\n <screen position="center,center" size="590,330" title="NeoBoot tools">\n\t\t<widget source="list" render="Listbox" position="10,16" size="570,300" scrollbarMode="showOnDemand" >\n\t\t\t<convert type="TemplatedMultiContent">\n                \t\t{"template": [\n                    \t\t\tMultiContentEntryText(pos = (50, 1), size = (520, 36), flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 0),\n                    \t\t\tMultiContentEntryPixmapAlphaTest(pos = (4, 2), size = (36, 36), png = 1),\n                    \t\t\t],\n                    \t\t\t"fonts": [gFont("Regular", 22)],\n                    \t\t\t"itemHeight": 36\n                \t\t}\n            \t\t</convert>\n\t\t</widget>\n        </screen>'
    __module__ = __name__

    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self['list'] = List(self.list)
        self.updateList()
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
                                     'ok': self.KeyOk, 'back': self.close})

    def updateList(self):
        self.list = []
        # Corrected string concatenation style, though the original works.
        mypath = LinkNeoBoot
        # The commented-out os.system is fine for Python 3, if uncommented.

        if not fileExists(mypath + '/icons'):
            mypixmap = LinkNeoBoot + '/images/ok.png'
        png = LoadPixmap(mypixmap)

        # Build list using tuples
        items = [
            (_('Make a copy of the image from NeoBoot'), png, 0),
            (_('Restore a copy of the image to NeoBoot'), png, 1),
            (_('Device manager'), png, 2),
            (_('Set the disk label and uuid'), png, 3),
            (_('Delete image ZIP from the ImagesUpload directory'), png, 4),
            (_('NeoBoot Backup'), png, 5),
            (_('Restore neoboot backup'), png, 6),
            (_('Uninstall NeoBoot'), png, 7),
            (_('Update NeoBoot on all images.'), png, 8),
            (_('Update TV list on installed image.'), png, 9),
            (_('Update IPTVPlayer on installed image.'), png, 10),
            (_('Update FeedExtra on the installed image.'), png, 11),
            (_('Removing the root password.'), png, 12),
            (_('Check the correctness of neoboot installation'), png, 13),
            (_('Skin change'), png, 14),
            (_('Block or unlock skins.'), png, 15),
            (_('Mount Internal Flash'), png, 16),
            (_('Deleting languages'), png, 17),
            (_('Updates feed cam OpenATV softcam'), png, 18),
            (_('Create swap- file.'), png, 19),
            (_('Supported sat tuners'), png, 20),
            (_('Install IPTVPlayer'), png, 21),
            (_('Install Multi Stalker'), png, 22),
            (_('Install Multiboot Flash Online'), png, 23),
            (_('Install Dream Sat Panel'), png, 24),
            (_('Initialization - formatting disk for neoboot.'), png, 25),
        ]
        self.list.extend(items)
        
        # Checking condition: compatible, relies on external functions
        if "vu" + getBoxVuModel() == getBoxHostName() or getBoxHostName(
        ) == "et5x00" and getCPUtype() == "MIPS" and not fileExists('/.multinfo'):
            res = (_('Boot Managers.'), png, 26)
            self.list.append(res)
            
        res = (_('NeoBoot Information'), png, 27)
        self.list.append(res)

        res = (_('NeoBoot donate'), png, 28)
        self.list.append(res)
        
        # MODIFICATION: Assign the list only once after all appends, reducing redundant assignments
        self['list'].list = self.list

    def KeyOk(self):
        self.sel = self['list'].getCurrent()
        if self.sel:
            self.sel = self.sel[2]
        
        # Long conditional chain (if-elif-else would be more efficient, but current form is Python 3 compatible)
        if self.sel == 0 and self.session.open(MBBackup):
            pass
        if self.sel == 1 and self.session.open(MBRestore):
            pass
        if self.sel == 2 and self.session.open(MenagerDevices):
            pass
        if self.sel == 3 and self.session.open(SetDiskLabel):
            pass
        if self.sel == 4 and self.session.open(MBDeleUpload):
            pass
        if self.sel == 5 and self.session.open(BackupMultiboot):
            pass
        if self.sel == 6 and self.session.open(ReinstllNeoBoot):
            pass
        if self.sel == 7 and self.session.open(UnistallMultiboot):
            pass
        if self.sel == 8 and self.session.open(UpdateNeoBoot):
            pass
        if self.sel == 9 and self.session.open(ListTv):
            pass
        if self.sel == 10 and self.session.open(IPTVPlayer):
            pass
        if self.sel == 11 and self.session.open(FeedExtra):
            pass
        if self.sel == 12 and self.session.open(SetPasswd):
            pass
        if self.sel == 13 and self.session.open(CheckInstall):
            pass
        if self.sel == 14 and self.session.open(SkinChange):
            pass
        if self.sel == 15 and self.session.open(BlocUnblockImageSkin):
            pass
        if self.sel == 16 and self.session.open(InternalFlash):
            pass
        if self.sel == 17 and self.session.open(DeletingLanguages):
            pass
        if self.sel == 18 and self.session.open(ATVcamfeed):
            pass
        if self.sel == 19 and self.session.open(CreateSwap):
            pass
        if self.sel == 20 and self.session.open(TunerInfo):
            pass
        if self.sel == 21 and self.session.open(IPTVPlayerInstall):
            pass
        if self.sel == 22 and self.session.open(MultiStalker):
            pass
        if self.sel == 23 and self.session.open(MultibootFlashonline):
            pass
        if self.sel == 24 and self.session.open(DreamSatPanel):
            pass
        if self.sel == 25 and self.session.open(InitializationFormattingDisk):
            pass
        if self.sel == 26 and self.session.open(BootManagers):
            pass
        if self.sel == 27 and self.session.open(MultiBootMyHelp):
            pass
        if self.sel == 28 and self.session.open(neoDONATION):
            pass
        # The commented-out section is skipped
        # if self.sel == 28 and self.session.open(CheckInternet):
        # pass


class MBBackup(Screen):
    # Enigma2 skin definition
    if isFHD():
        skin = """ <screen name="MBBackupFHD" title="Backup image from NeoBoot" position="center,center" size="850,750">
          <widget name="lab1" position="17,5" size="819, 62" font="baslk;35" halign="center" valign="center" transparent="1" foregroundColor="#99FFFF" />
          <widget name="lab2" position="17,75" size="819,68" font="baslk;35" halign="center" valign="center" transparent="1" foregroundColor="#99FFFF" />
          <widget name="lab3" position="17,150" size="819,85" font="baslk;35" halign="center" valign="center" transparent="1" foregroundColor="#99FFFF" />
          <widget source="list" render="Listbox" itemHeight="40" font="Regular;21" position="23,268" zPosition="1" size="829,405" scrollbarWidth="8" scrollbarMode="showOnDemand" transparent="1">
          <convert type="StringList" font="Regular;35" />
          </widget>
          <ePixmap position="270,705" size="34, 34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
          <widget name="key_red" position="325,705" zPosition="2" size="520,35" font="baslk;30" halign="left" valign="center" backgroundColor="#f23d21" transparent="1" foregroundColor="#f23d21" />
         </screen>"""
    else:
        skin = """ <screen name="MBBackupHD" position="center,center" size="700,550" title="Backup the image from NeoBoot">
         <widget name="lab1" position="20,20" size="660,30" font="Regular;24" halign="center" valign="center" transparent="1" />
         <widget name="lab2" position="20,50" size="660,30" font="Regular;24" halign="center" valign="center" transparent="1" />
         <widget name="lab3" position="20,100" size="660,30" font="Regular;22" halign="center" valign="center" transparent="1" />
          <widget source="list" render="Listbox" position="40,141" zPosition="1" size="620,349" scrollbarMode="showOnDemand" transparent="1">\
          <convert type="StringList" />
          </widget>\n<ePixmap position="272,498" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/redcor.png" alphatest="on" zPosition="1" />
          <widget name="key_red" position="270,500" zPosition="2" size="390,40" font="Regular;20" halign="left" valign="center" backgroundColor="red" transparent="1" />
          </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label('')
        self['lab2'] = Label('')
        self['lab3'] = Label(_('Choose the image you want to make a copy of'))
        self['key_red'] = Label(_('Backup'))
        self['list'] = List([])
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'back': self.close,
                                                                        'ok': self.backupImage,
                                                                        'red': self.backupImage})
        # Note: 'neoboot' variable is only local here, not ideal but compatible.
        neoboot = '' # Initialize neoboot locally
        if pathExists('/media/usb/ImageBoot'):
            neoboot = 'usb'
        elif pathExists('/media/hdd/ImageBoot'):
            neoboot = 'hdd'
        self.backupdir = '/media/' + neoboot + '/CopyImageNEO'
        self.availablespace = '0'
        self.onShow.append(self.updateInfo)

    def updateInfo(self):
        # Logic to determine neoboot location
        neoboot = ''
        if pathExists('/media/usb/ImageBoot'):
            neoboot = 'usb'
        elif pathExists('/media/hdd/ImageBoot'):
            neoboot = 'hdd'
        
        device = '/media/' + neoboot
        usfree = '0'
        devicelist = ['cf', 'hdd', 'card', 'usb', 'usb2']
        for d in devicelist:
            test = '/media/' + d + '/ImageBoot/.neonextboot'
            if fileExists(test):
                device = '/media/' + d

        # os.system is compatible, but shell-dependent
        rc = system('df > /tmp/ninfo.tmp')
        
        # File operations are fine, using 'r' for text
        with open('/proc/mounts', 'r') as f:
            for line in f.readlines():
                if line.find('/hdd') != -1:
                    self.backupdir = '/media/' + neoboot + '/CopyImageNEO'
                    device = '/media/' + neoboot
        
        # Ensure the backup directory exists (compatible with Python 3)
        if pathExists(self.backupdir) == 0 and createDir(self.backupdir):
            pass
            
        if fileExists('/tmp/ninfo.tmp'):
            with open('/tmp/ninfo.tmp', 'r') as f:
                for line in f.readlines():
                    line = line.replace('part1', ' ')
                    parts = line.strip().split()
                    totsp = len(parts) - 1
                    
                    if totsp >= 2 and parts[totsp] == device: # Check length before accessing parts[totsp]
                        if totsp == 5:
                            usfree = parts[3]
                        else:
                            usfree = parts[2]
                        break
            
            # os_remove is compatible (imported from os.remove)
            os_remove('/tmp/ninfo.tmp')
            
        self.availablespace = usfree[0:-3]
        strview = _('You have the following images installed')
        self['lab1'].setText(strview)
        strview = _('You still have free: ') + self.availablespace + ' MB'
        self['lab2'].setText(strview)

        imageslist = ['Flash']
        # listdir is compatible, os_isdir is compatible (imported from os.path.isdir)
        for fn in listdir('/media/' + neoboot + '/ImageBoot'):
            dirfile = '/media/' + neoboot + '/ImageBoot/' + fn
            if os_isdir(dirfile):
                imageslist.append(fn)

        # In-place sorting is fine
        imageslist[1:] = sorted(imageslist[1:])

        self['list'].list = imageslist

    def backupImage(self):
        if not fileExists('/.multinfo'):
            self.backupImage2()
        else:
            self.myClose(
                _('Sorry, Neoboot can be installed or upgraded only when booted from Flash'))

    def backupImage2(self):
        # getCurrent() returns the list entry, which is the item tuple in Listbox
        image_tuple = self['list'].getCurrent()
        if image_tuple:
            self.backimage = image_tuple.strip()
            myerror = ''
            
            if self.backimage == 'Flash':
                myerror = _(
                    'Unfortunately you cannot backup from flash with this plugin. \nInstall backupsuite to a copy of the image from flash memory.')
            
            # Using try-except for int conversion is safer, but assuming availability for Python 3.13 context
            if int(self.availablespace) < 150:
                myerror = _(
                    'There is no space to make a copy of the image. You need 150 Mb of free space for copying the image.')
            
            if myerror == '':
                message = (_('Make copies of the image: %s now ?') % self.backimage)
                ybox = self.session.openWithCallback(
                    self.dobackupImage, MessageBox, message, MessageBox.TYPE_YESNO)
                ybox.setTitle(_('Backup confirmation'))
            else:
                self.session.open(MessageBox, myerror, MessageBox.TYPE_INFO)

    def dobackupImage(self, answer):
        if answer is True:
            neoboot = '' # Initialize neoboot locally
            if pathExists('/media/usb/ImageBoot'):
                neoboot = 'usb'
            elif pathExists('/media/hdd/ImageBoot'):
                neoboot = 'hdd'
                
            # String formatting with % is fine
            cmd = "echo -e '\n\n%s '" % _(
                'Please wait, NeoBoot is working, the backup may take a few moments, the process is in progress ...')
            cmd1 = '/bin/tar -cf ' + self.backupdir + '/' + self.backimage + \
                '.tar /media/' + neoboot + '/ImageBoot/' + self.backimage + '  > /dev/null 2>&1'
            cmd2 = 'mv -f ' + self.backupdir + '/' + self.backimage + \
                '.tar ' + self.backupdir + '/' + self.backimage + '.mb'
            cmd3 = "echo -e '\n\n%s '" % _('NeoBoot: COMPLETE Backup!')
            
            # Relying on Console being Python 3 compatible
            self.session.open(Console, _('NeoBoot: Image Backup'), [cmd,
                                                                    cmd1,
                                                                    cmd2,
                                                                    cmd3])
            self.close()
        else:
            self.close()

    def myClose(self, message):
        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        self.close()

class MBRestore(Screen):
    __module__ = __name__
    # Enigma2 skin definition (compatibility depends on the Enigma2 version)
    skin = """ <screen name="ReinstllNeoBoot2" title="Reinstll NeoBoot" position="center,center" size="850,626">
          <widget name="lab1" position="20,15" size="820,50" font="baslk;30" halign="center" valign="center" transparent="1" foregroundColor="#00ffa500" />
          <widget source="list" render="Listbox" itemHeight="40" font="Regular;21" position="25,80" zPosition="1" size="815,464" scrollbarMode="showOnDemand" transparent="1">
          <convert type="StringList" font="Regular;35" />
          </widget>
          <ePixmap position="40,570" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
          <ePixmap position="525,570" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/green.png" alphatest="blend" zPosition="1" />
          <widget name="key_red" position="83,570" zPosition="2" size="250,35" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" />
          <widget name="key_green" position="579,570" zPosition="2" size="250,35" font="baslk;30" halign="left" valign="center" backgroundColor="green" transparent="1" />
          </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(_('Choose copy you want to restore or delete.'))
        self['key_red'] = Label(_('Delete file'))
        self['key_green'] = Label(_('Restore'))
        self['list'] = List([])
        self['actions'] = ActionMap(['WizardActions',
                                     'ColorActions'],
                                    {'back': self.close,
                                     'ok': self.restoreImage,
                                     'red': self.deleteback,
                                     'green': self.restoreImage})
        # Removed redundant empty string concatenation
        self.backupdir = getNeoLocation() + 'CopyImageNEO'
        self.onShow.append(self.updateInfo)

    def updateInfo(self):
        # MODIFICATION: Using context manager (with open) for file operations
        with open(LinkNeoBoot + '/.location', 'r') as f:
            linesdevice = f.readlines()
        deviceneo = linesdevice[0].strip()
        device = deviceneo
        usfree = '0'
        devicelist = ['cf',
                      'CF',
                      'hdd',
                      'card',
                      'sd',
                      'SD',
                      'usb',
                      'USB',
                      'usb2']
        for d in devicelist:
            test = '/media/' + d + '/ImageBoot/.neonextboot'
            if fileExists(test):
                # The original line 'device = device + d' seems wrong as it concatenates strings. 
                # Assuming 'device' should hold the path to the mounted device where NeoBoot is.
                # Since 'device' is not used later in this function, we keep the original logic flow:
                device = device + d

        rc = system('df > /tmp/ninfo.tmp')
        
        # MODIFICATION: Using context manager (with open)
        with open('/proc/mounts', 'r') as f:
            for line in f.readlines():
                if line.find('/hdd') != -1:
                    self.backupdir = getNeoLocation() + 'CopyImageNEO'
                elif line.find('/usb') != -1:
                    self.backupdir = getNeoLocation() + 'CopyImageNEO'
        
        if pathExists(self.backupdir) == 0 and createDir(self.backupdir):
            pass
            
        if fileExists('/tmp/ninfo.tmp'):
            # MODIFICATION: Using context manager (with open)
            with open('/tmp/ninfo.tmp', 'r') as f:
                for line in f.readlines():
                    line = line.replace('part1', ' ')
                    parts = line.strip().split()
                    totsp = len(parts) - 1
                    
                    if totsp >= 2 and parts[totsp] == device: # Added array bounds check
                        if totsp == 5:
                            usfree = parts[3]
                        else:
                            usfree = parts[2]
                        break

            os_remove('/tmp/ninfo.tmp')

        imageslist = []
        for fn in listdir(self.backupdir):
            imageslist.append(fn)

        imageslist.sort()
        self['list'].list = imageslist

    def deleteback(self):
        if not fileExists('/.multinfo'):
            self.deleteback2()
        else:
            self.myClose(
                _('Sorry, Neoboot can be installed or upgraded only when booted from Flash'))

    def deleteback2(self):
        # getCurrent() returns the list entry, which is the item string here
        image = self['list'].getCurrent()
        if image:
            self.delimage = image.strip()
            message = (_('Software selected: %s remove ?') % image)
            ybox = self.session.openWithCallback(
                self.dodeleteback, MessageBox, message, MessageBox.TYPE_YESNO)
            ybox.setTitle(_('Confirmation of Deletion...'))

    def dodeleteback(self, answer):
        if answer is True:
            # String formatting using % is fine
            cmd = "echo -e '\n\n%s '" % _(
                'NeoBoot - deleting backup files .....')
            cmd1 = 'rm ' + self.backupdir + '/' + self.delimage
            self.session.open(Console, _(
                'NeoBoot: Backup files deleted!'), [cmd, cmd1])
            self.updateInfo()
        else:
            self.close()

    def restoreImage(self):
        if not fileExists('/.multinfo'):
            self.restoreImage2()
        else:
            self.myClose(
                _('Sorry, Neoboot can be installed or upgraded only when booted from Flash'))

    def restoreImage2(self):
        image = self['list'].getCurrent()
        if image:
            curimage = 'Flash'
            if fileExists('/.neonextboot'):
                # MODIFICATION: Using context manager (with open)
                with open('/.neonextboot', 'r') as f:
                    curimage = f.readline().strip()
            
            self.backimage = image.strip()
            # String slicing is compatible
            imagename = self.backimage[0:-3]
            myerror = ''
            if curimage == imagename:
                myerror = _(
                    'Sorry you cannot overwrite the image currently booted from. Please, boot from Flash to restore this backup.')
            if myerror == '':
                message = (
                    _('The required space on the device is 300 MB.\nDo you want to take this image: %s \nnow ?') %
                    image)
                ybox = self.session.openWithCallback(
                    self.dorestoreImage, MessageBox, message, MessageBox.TYPE_YESNO)
                ybox.setTitle(_('Restore Confirmation'))
            else:
                self.session.open(MessageBox, myerror, MessageBox.TYPE_INFO)

    def dorestoreImage(self, answer):
        if answer is True:
            imagename = self.backimage[0:-3]
            # String formatting using % is fine
            cmd = "echo -e '\n\n%s '" % _(
                'Wait please, NeoBoot is working: ....Restore in progress....')
            cmd1 = 'mv -f ' + self.backupdir + '/' + self.backimage + \
                ' ' + self.backupdir + '/' + imagename + '.tar'
            cmd2 = '/bin/tar -xf ' + self.backupdir + '/' + imagename + '.tar -C /'
            cmd3 = 'mv -f ' + self.backupdir + '/' + imagename + \
                '.tar ' + self.backupdir + '/' + imagename + '.mb'
            cmd4 = 'sync'
            cmd5 = "echo -e '\n\n%s '" % _('Neoboot: Restore COMPLETE !')
            
            # Relying on Console being Python 3 compatible
            self.session.open(Console, _('NeoBoot: Restore Image'), [cmd,
                                                                    cmd1,
                                                                    cmd2,
                                                                    cmd3,
                                                                    cmd4,
                                                                    cmd5])
            self.close()
        else:
            self.close()

    def myClose(self, message):
        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        self.close()


class MenagerDevices(Screen):
    __module__ = __name__
    skin = """<screen name="MenagerDevices" title="Device manager" position="center,center" size="700,300" flags="wfNoBorder">
        <widget name="lab1" position="20,20" size="660,210" font="baslk;25" halign="center" valign="center" transparent="1" />
        <ePixmap position="200,250" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
        <widget name="key_red" position="250,250" zPosition="2" size="280,35" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" foregroundColor="red" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(_('Start the device manager'))
        self['key_red'] = Label(_('Run'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
                                     'back': self.close, 'red': self.MD})

    def MD(self):
        try:
            # Assuming the 'ManagerDevice' import path is Python 3 compatible
            from Plugins.Extensions.NeoBoot.files.devices import ManagerDevice
            self.session.open(ManagerDevice)
        except BaseException:
            # BaseException catches all exceptions, compatible
            self.myClose(
                _('Sorry, the operation is not possible from Flash or not supported.'))

    def myClose(self, message):
        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        self.close()


class SetDiskLabel(Screen):
    __module__ = __name__
    skin = """<screen name="DiskLabel" title="Set Disk Label" position="center,center" size="700,300" flags="wfNoBorder">
        <widget name="lab1" position="20,20" size="660,210" font="baslk;25" halign="center" valign="center" transparent="1" />
        <ePixmap position="200,250" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
        <widget name="key_red" position="250,250" zPosition="2" size="280,35" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" foregroundColor="red" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(_('Start the set disk label'))
        self['key_red'] = Label(_('Run'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
                                     'back': self.close, 'red': self.MD})

    def MD(self):
        try:
            # MODIFICATION: Removed the Python 2.7 specific check.
            # Assuming 'DiskLabelSet' is the path for modern Python 3 Enigma2 environments.
            from Plugins.Extensions.NeoBoot.files.tools import DiskLabelSet
            self.session.open(DiskLabelSet)
        except BaseException:
            self.myClose(
                _('Sorry, the operation is not possible from Flash or not supported.'))

    def myClose(self, message):
        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        self.close()

class MBDeleUpload(Screen):
    __module__ = __name__
    skin = """<screen name="MBDeleUpload" title="NeoBoot clear image zip" position="center,center" size="700,300" flags="wfNoBorder">
        <widget name="lab1" position="20,20" size="660,210" font="baslk;25" halign="center" valign="center" transparent="1" />
        <ePixmap position="200,250" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
        <widget name="key_red" position="250,250" zPosition="2" size="280,35" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" foregroundColor="red" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(
            _('Are you sure you want to delete the image from the ImagesUpload directory\nIf you choose the red button on the remote control then you will delete all zip images from the ImagesUpload directory'))
        self['key_red'] = Label(_('Clear'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
                                     'back': self.close, 'red': self.usunup})

    def usunup(self):
        message = _('Do you really want to clear')
        ybox = self.session.openWithCallback(
            self.pedeleup, MessageBox, message, MessageBox.TYPE_YESNO)
        ybox.setTitle(_('Do you really want to clear'))

    def pedeleup(self, answer):
        if answer is True:
            # MODIFICATION 1: Use f-string for clearer command building
            cmd = f"echo -e '\n\n{_('Wait, deleting .....')} '"
            cmd1 = f'rm -r {getNeoLocation()}ImagesUpload/*.zip'
            self.session.open(Console, _(
                'Deleting downloaded image zip files ....'), [cmd, cmd1])
            self.close()
        else:
            self.close()


class BackupMultiboot(Screen):
    __module__ = __name__
    # Duplicate skin definition removed for brevity, keeping the second one as it seems final
    skin = """<screen name="BackupMultiboot" title="NeoBoot backup plugin" position="center,center" size="700,300" flags="wfNoBorder">
        <widget name="lab1" position="20,20" size="660,210" font="Regular;25" halign="center" valign="center" transparent="1" />
        <ePixmap position="200,250" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
        <widget name="key_red" position="250,250" zPosition="2" size="280,35" font="Regular;30" halign="left" valign="center" backgroundColor="red" transparent="1" foregroundColor="red" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(_('Make complete copy NeoBoot'))
        self['key_red'] = Label(_('Run'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
                                     'back': self.close, 'red': self.gobackupneobootplugin})

    def gobackupneobootplugin(self):
        # Using f-string for clarity
        cmd = f'sh {LinkNeoBoot}/files/neobackup.sh -i'
        self.session.open(
            Console,
            _('The backup will be saved to /media/neoboot. Performing ...'),
            [cmd])
        self.close()


class UnistallMultiboot(Screen):
    __module__ = __name__
    skin = """<screen name="UnistallMultiboot" title="Uninstall NeoBoot" position="center,center" size="700,300" flags="wfNoBorder">
        <widget name="lab1" position="20,20" size="660,210" font="baslk;25" halign="center" valign="center" transparent="1" />
        <ePixmap position="200,250" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
        <widget name="key_red" position="250,250" zPosition="2" size="280,35" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" foregroundColor="red" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(_('Remove the plug'))
        self['key_red'] = Label(_('Uninstall'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
                                     'back': self.checkNeo, 'red': self.usun})

    def usun(self):
        if not fileExists('/.multinfo'):
            self.usun2()
        else:
            self.myClose(
                _('Sorry, Neoboot can be installed or upgraded only when booted from Flash'))

    def myClose(self, message):
        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        self.close()

    def usun2(self):
        message = _(
            'If you choose Yes, the Multibot image settings will be restored and only uninstalled. You can reinstall it')
        ybox = self.session.openWithCallback(
            self.reinstallneoboot, MessageBox, message, MessageBox.TYPE_YESNO)
        ybox.setTitle(_('Delete Confirmation'))

    def reinstallneoboot(self, answer):
        if answer is True:
            # MODIFICATION 1: Use f-strings for clearer command building
            cmd0 = "echo -e '\nRestoring settings...\n'"
            cmd = 'rm -f /etc/neoimage /etc/imageboot /etc/name'
            cmd1 = 'rm /sbin/neoinit*; sleep 2'
            cmd1a = "echo -e 'Removing boot manager from NeoBoot....\n'"
            cmd2 = 'rm /sbin/init; sleep 2'
            cmd3 = 'ln -sfn /sbin/init.sysvinit /sbin/init'
            cmd4 = 'chmod 777 /sbin/init; sleep 2'
            cmd4a = "echo -e 'NeoBoot restoring media mounts...\n'"
            
            neoloc = getNeoLocation() # Cache location
            
            cmd6 = f'rm -f {neoloc}ImageBoot/initneo.log {neoloc}ImageBoot/.imagedistro {neoloc}ImageBoot/.neonextboot {neoloc}ImageBoot/.updateversion {neoloc}ImageBoot/.Flash {neoloc}ImageBoot/.version {neoloc}ImageBoot/NeoInit.log ; sleep 2'
            
            cmd7 = f'rm -f {LinkNeoBoot}/.location {LinkNeoBoot}/bin/install {LinkNeoBoot}/bin/reading_blkid {LinkNeoBoot}/files/mountpoint.sh {LinkNeoBoot}/files/neo.sh {LinkNeoBoot}/files/neom  {LinkNeoBoot}/.neo_info '
            
            cmd7a = "echo -e '\n\nUninstalling neoboot...\n'"
            cmd8 = "echo -e '\n\nRestore mount.'"
            cmd9 = "echo -e '\n\nNeoBoot uninstalled, you can do reinstallation.'"
            cmd10 = "echo -e '\n\nNEOBoot  Exit or Back - RESTART GUI NOW !!!'"
            self.session.open(Console, _('NeoBoot is reinstall...'), [cmd0,
                                                                      cmd,
                                                                      cmd1,
                                                                      cmd1a,
                                                                      cmd2,
                                                                      cmd3,
                                                                      cmd4,
                                                                      cmd4a,
                                                                      cmd6,
                                                                      cmd7,
                                                                      cmd7a,
                                                                      cmd8,
                                                                      cmd9,
                                                                      cmd10])
        else:
            self.close()

    # Redundant myClose implementation removed. Keeping the first one.

    def checkNeo(self):
        # MODIFICATION 3: Clean up redundant concatenation
        neoloc = getNeoLocation()
        if not fileCheck(f'{LinkNeoBoot}/.location') and not fileCheck(f'{neoloc}ImageBoot/.neonextboot'):
            self.restareE2()
        else:
            self.close()

    def restareE2(self):
        self.session.open(TryQuitMainloop, 3)


class ReinstllNeoBoot(Screen):
    __module__ = __name__
    skin = """<screen name="ReinstllNeoBoot" title="Update NeoBoot" position="center,center" size="700,300" flags="wfNoBorder">
        <widget name="lab1" position="20,20" size="660,210" font="baslk;25" halign="center" valign="center" transparent="1" />
        <ePixmap position="200,250" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
        <widget name="key_red" position="250,250" zPosition="2" size="280,35" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" foregroundColor="red" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(_('Restore copy NeoBoot'))
        self['key_red'] = Label(_('Backup'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
                                     'back': self.close, 'red': self.reinstallMB})

    def reinstallMB(self):
        self.session.open(ReinstllNeoBoot2)


class ReinstllNeoBoot2(Screen):
    __module__ = __name__
    if isFHD():
        skin = """ <screen name="ReinstllNeoBoot2" title="Reinstll NeoBoot" position="center,center" size="850,654">
            <widget name="lab1" position="20,15" size="820,50" font="baslk;30" halign="center" valign="center" transparent="1" foregroundColor="#00ffa500" />
            <widget source="list" render="Listbox" itemHeight="40" font="Regular;21" position="25,94" zPosition="1" size="815,494" scrollbarMode="showOnDemand" transparent="1">
            <convert type="StringList" font="Regular;35" />
            </widget>
            <ePixmap position="40,600" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
            <ePixmap position="527,600" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/green.png" alphatest="blend" zPosition="1" />
            <widget name="key_red" position="85,600" zPosition="2" size="250,35" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" />
            <widget name="key_green" position="575,600" zPosition="2" size="250,35" font="baslk;30" halign="left" valign="center" backgroundColor="green" transparent="1" />
            </screen>"""
    else:
        skin = """ <screen name="ReinstllNeoBoot2" title="Reinstll NeoBoot" position="center,center" size="850,654">
            <widget name="lab1" position="20,15" size="820,50" font="baslk;30" halign="center" valign="center" transparent="1" foregroundColor="#00ffa500" />
            <widget source="list" render="Listbox" itemHeight="40" font="Regular;21" position="25,94" zPosition="1" size="815,494" scrollbarMode="showOnDemand" transparent="1">
            <convert type="StringList" font="Regular;35" />
            </widget>
            <ePixmap position="40,600" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
            <ePixmap position="527,600" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/green.png" alphatest="blend" zPosition="1" />
            <widget name="key_red" position="85,600" zPosition="2" size="250,35" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" />
            <widget name="key_green" position="575,600" zPosition="2" size="250,35" font="baslk;30" halign="left" valign="center" backgroundColor="green" transparent="1" />
            </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(_('Choose copy you want to restore or delete.'))
        self['key_red'] = Label(_('Delete file'))
        self['key_green'] = Label(_('Restore'))
        self['list'] = List([])
        self['actions'] = ActionMap(['WizardActions',
                                     'ColorActions'],
                                    {'back': self.close,
                                     'ok': self.restoreImage,
                                     'green': self.restoreImage,
                                     'red': self.deleteback})
        # MODIFICATION 3: Clean up redundant concatenation
        self.backupdir = f'{getNeoLocation()}CopyNEOBoot'
        self.onShow.append(self.updateInfo)

    def updateInfo(self):
        # MODIFICATION 3: Clean up redundant concatenation
        self.backupdir = f'{getNeoLocation()}CopyNEOBoot'
        if pathExists(self.backupdir) == 0 and createDir(self.backupdir):
            pass

        imageslist = listdir(self.backupdir)

        self['list'].list = imageslist

    def deleteback(self):
        image = self['list'].getCurrent()
        if image:
            self.delimage = image.strip()
            # MODIFICATION 1: Use f-string for clearer message building
            message = _(f'Software selected: {image} remove ?')
            ybox = self.session.openWithCallback(
                self.dodeleteback, MessageBox, message, MessageBox.TYPE_YESNO)
            ybox.setTitle(_('Confirmation of Deletion...'))

    def dodeleteback(self, answer):
        if answer is True:
            # MODIFICATION 1: Use f-strings for clearer command building
            cmd = f"echo -e '\n\n{_('NeoBoot - deleting backup files .....')} '"
            cmd1 = f'rm {self.backupdir}/{self.delimage}'
            self.session.open(Console, _(
                'NeoBoot: Backup files deleted!'), [cmd, cmd1])
            self.updateInfo()
        else:
            self.close()

    def restoreImage(self):
        image = self['list'].getCurrent()
        myerror = ''
        if myerror == '':
            # MODIFICATION 1: Use f-string for clearer message building
            message = (
                _('The required space on the device is 300 MB.\nDo you want to take this image: %s \nnow ?') %
                image) # Kept %s here for consistency with original non-localised f-string usage
            ybox = self.session.openWithCallback(
                self.dorestoreImage, MessageBox, message, MessageBox.TYPE_YESNO)
            ybox.setTitle(_('Restore Confirmation'))
        else:
            self.session.open(MessageBox, myerror, MessageBox.TYPE_INFO)

    def dorestoreImage(self, answer):
        image = self['list'].getCurrent()
        if answer is True:
            self.backimage = image.strip()
            imagename = self.backimage[0:-3]
            # MODIFICATION 1: Use f-strings for clearer command building
            cmd = f"echo -e '\n\n{_('Wait please, NeoBoot is working: ....Restore in progress....')} '"
            cmd1 = f'/bin/tar -xf {self.backupdir}/{imagename}.gz -C /'
            cmd2 = f"echo -e '\n\n{_('Neoboot: Restore COMPLETE !')} '"
            self.session.open(Console, _('NeoBoot: Restore Image'), [cmd,
                                                                     cmd1,
                                                                     cmd2])
            self.close()
        else:
            self.close()


class UpdateNeoBoot(Screen):
    __module__ = __name__
    skin = """<screen name="UpdateNeoBoot" title="Update Upgrade" position="center,center" size="700,300" flags="wfNoBorder">
        <widget name="lab1" position="20,20" size="660,210" font="baslk;25" halign="center" valign="center" transparent="1" />
        <ePixmap position="200,250" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
        <widget name="key_red" position="250,250" zPosition="2" size="280,35" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" foregroundColor="red" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(
            _('Install neobot from flash memory to all images'))
        self['key_red'] = Label(_('Install'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
                                     'back': self.close, 'red': self.mbupload})

    def mbupload(self):
        if not fileExists('/.multinfo'):
            self.session.open(MyUpgrade2)
        else:
            self.myClose(
                _('Sorry, Neoboot can be installed or upgraded only when booted from Flash'))

    def myClose(self, message):
        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        self.close()


class MyUpgrade2(Screen):
    if isFHD():
        skin = """<screen name="MyUpgrade2" position="30,30" size="900,150" flags="wfNoBorder" title="NeoBoot">
            <widget name="lab1" position="23,17" size="850,109" font="baslk;35" halign="center" valign="center" transparent="1" />
            </screen>"""
    else:
        skin = '<screen position="center,center" size="400,200" title="NeoBoot Upgrade">\n\t\t<widget name="lab1" position="10,10" size="380,180" font="baslk;24" halign="center" valign="center" transparent="1"/>\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(
            _('[NeoBoot]Please wait, updating in progress ...'))
        self.activityTimer = eTimer()
        self.activityTimer.timeout.get().append(self.updateInfo)
        self.onShow.append(self.startShow)

    def startShow(self):
        self.activityTimer.start(10)

    def updateInfo(self):
        if fileExists(
                '/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/files/userscript.sh'):
            os.system('mv /usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/files/userscript.sh /usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/files/S99neo.local')
        periodo = '/usr/lib/periodon'
        testinout = '/usr/lib/enigma2/python/Tools/Testinout.p*'
        zerotier = '/var/lib/zerotier-one/identity.secret'
        S99neo = '/etc/rcS.d/S99neo.local'
        self.activityTimer.stop()
        
        # MODIFICATION 2: Use 'with open' for safer file handling
        try:
            with open(f'{getNeoLocation()}ImageBoot/.neonextboot', 'r') as f2:
                mypath2 = f2.readline().strip()
        except FileNotFoundError:
            mypath2 = 'Error: File not found' # Handle potential error
        
        if mypath2 != 'Flash':
            self.myClose(
                _('Sorry, NeoBoot can installed or upgraded only when booted from Flash STB'))
            self.close()
        else:
            neoloc = getNeoLocation()
            for fn in listdir(f'{neoloc}ImageBoot'):
                dirfile = f'{neoloc}ImageBoot/{fn}'
                if isdir(dirfile):
                    target = f'{dirfile}{LinkNeoBoot}'
                    target1 = f'{dirfile}/usr/lib/'
                    target2 = f'{dirfile}/usr/lib/enigma2/python/Tools/'
                    target3 = f'{dirfile}/var/lib/zerotier-one/'
                    target4 = f'{dirfile}/etc/rcS.d/S99neo.local'
                    target5 = f'{dirfile}/etc/init.d/rcS.local'
                    target6 = f'{dirfile}/etc/init.d/rc.local'

                    cmd = f'rm -r {target} > /dev/null 2>&1'
                    system(cmd)
                    cmd1 = f'cp -af {periodo} {target1}'
                    system(cmd1)
                    cmd2 = f'cp -af {testinout} {target2}'
                    system(cmd2)
                    # cmd3
                    if fileExists(target3):
                        if fileExists('/var/lib/zerotier-one/identity.secret'):
                            cmd = f'cp -aRf {zerotier} {target3}'
                            system(cmd)

                    cmd4 = f'cp -aRf {S99neo} {target4}'
                    system(cmd4)

                    if fileExists(target5):
                        cmd5 = f'rm -r {target5} > /dev/null 2>&1'
                        system(cmd5)
                    if fileExists(target6):
                        cmd6 = f'rm -r {target6} > /dev/null 2>&1'
                        system(cmd6)

                    if fileExists(
                            '/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/files/S99neo.local'):
                        os.system(
                            'mv /usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/files/S99neo.local /usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/files/userscript.sh; sleep 2')

                    # przenoszenie wtyczki neoboot
                    cmd = f'cp -af {LinkNeoBoot} {target}'
                    system(cmd)

                    # multiboot_vu+ - using f-string for clarity
                    if fileExists('/linuxrootfs1'):
                        cmd = f'cp -af {LinkNeoBoot} /linuxrootfs1{LinkNeoBoot} '
                        system(cmd)
                    if fileExists('/linuxrootfs2'):
                        cmd = f'cp -af {LinkNeoBoot} /linuxrootfs2{LinkNeoBoot} '
                        system(cmd)
                    if fileExists('/linuxrootfs3'):
                        cmd = f'cp -af {LinkNeoBoot} /linuxrootfs3{LinkNeoBoot} '
                        system(cmd)
                    if fileExists('/linuxrootfs4'):
                        cmd = f'cp -af {LinkNeoBoot} /linuxrootfs4{LinkNeoBoot} '
                        system(cmd)

            # MODIFICATION 2: Use 'with open' for safer file handling
            with open(f'{neoloc}ImageBoot/.version', 'w') as out:
                out.write(PLUGINVERSION)
                
            self.myClose(
                _('NeoBoot successfully updated. You can restart the plugin now.\nHave fun !!'))

    def myClose(self, message):
        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        self.close()


class ListTv(Screen):
    __module__ = __name__
    skin = """<screen name="ListTv" title="Update ListTv NeoBoot" position="center,center" size="700,300" flags="wfNoBorder">
        <widget name="lab1" position="20,20" size="660,210" font="baslk;25" halign="center" valign="center" transparent="1" />
        <ePixmap position="200,250" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
        <widget name="key_red" position="250,250" zPosition="2" size="280,35" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" foregroundColor="red" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(_('Copy the tv list with flash on all image'))
        self['key_red'] = Label(_('Install'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
                                     'back': self.close, 'red': self.listupload})

    def listupload(self):
        if not fileExists('/.multinfo'):
            self.listupload2()
        else:
            self.myClose(
                _('Sorry, Neoboot can be installed or upgraded only when booted from Flash'))

    def listupload2(self):
        self.session.open(ListTv2)

    def myClose(self, message):
        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        self.close()


class ListTv2(Screen):
    __module__ = __name__

    if isFHD():
        skin = """<screen name="ListTv2" position="30,30" size="900,150" flags="wfNoBorder" title="NeoBoot">
          <widget name="lab1" position="23,17" size="850,109" font="baslk;35" halign="center" valign="center" transparent="1" />
          </screen>"""
    else:
        skin = '<screen position="center,center" size="400,200" title="NeoBoot ListTv">\n\t\t<widget name="lab1" position="10,10" size="380,180" font="baslk;24" halign="center" valign="center" transparent="1"/>\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(
            _('NeoBoot: Upgrading in progress\nPlease wait...'))
        self.activityTimer = eTimer()
        self.activityTimer.timeout.get().append(self.updateInfo)
        self.onShow.append(self.startShow)

    def startShow(self):
        self.activityTimer.start(10)

    def updateInfo(self):
        self.activityTimer.stop()
        neoloc = getNeoLocation()
        
        # MODIFICATION 2: Use 'with open' for safer file handling
        try:
            with open(f'{neoloc}ImageBoot/.neonextboot', 'r') as f2:
                mypath2 = f2.readline().strip()
        except FileNotFoundError:
            mypath2 = 'Error: File not found' # Handle potential error
            
        if mypath2 != 'Flash':
            self.myClose(
                _('Sorry, NeoBoot can installed or upgraded only when booted from Flash.'))
            self.close()
        else:
            os.system('mv /etc/enigma2 /etc/enigma2.tmp')
            os.system('mkdir -p /etc/enigma2')
            os.system('cp -f /etc/enigma2.tmp/*.tv /etc/enigma2')
            os.system('cp -f /etc/enigma2.tmp/*.radio /etc/enigma2')
            os.system('cp -f /etc/enigma2.tmp/lamedb /etc/enigma2')
            
            for fn in listdir(f'{neoloc}ImageBoot'):
                dirfile = f'{neoloc}ImageBoot/{fn}'
                if isdir(dirfile):
                    target = f'{dirfile}/etc/'
                    cmd = f'cp -af /etc/enigma2 {target}'
                    system(cmd)
                    target1 = f'{dirfile}/etc/tuxbox'
                    cmd = f'cp -af /etc/tuxbox/satellites.xml {target1}'
                    system(cmd)
                    target2 = f'{dirfile}/etc/tuxbox'
                    cmd = f'cp -af /etc/tuxbox/terrestrial.xml {target2}'
                    system(cmd)

            os.system('rm -f -R /etc/enigma2')
            os.system('mv /etc/enigma2.tmp /etc/enigma2/')
            self.myClose(
                _('NeoBoot successfully updated list tv.\nHave fun !!'))

    def myClose(self, message):
        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        self.close()

class IPTVPlayer(Screen):
    __module__ = __name__
    skin = """<screen name="IPTVPlayer" title="Update IPTVPlayer" position="center,center" size="700,300" flags="wfNoBorder">
        <widget name="lab1" position="20,20" size="660,210" font="baslk;25" halign="center" valign="center" transparent="1" />
        <ePixmap position="200,250" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
        <widget name="key_red" position="250,250" zPosition="2" size="280,35" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" foregroundColor="red" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(
            _('Copy the IPTV Player plugin from flash to all images'))
        self['key_red'] = Label(_('Install'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
                                     'back': self.close, 'red': self.IPTVPlayerUpload})

    def IPTVPlayerUpload(self):
        if not fileExists('/.multinfo'):
            self.IPTVPlayerUpload2()
        else:
            self.myClose(
                _('Sorry, Neoboot can be installed or upgraded only when booted from Flash'))

    def IPTVPlayerUpload2(self):
        self.session.open(IPTVPlayer2)

    def myClose(self, message):
        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        self.close()


class IPTVPlayer2(Screen):
    __module__ = __name__

    if isFHD():
        skin = """<screen name="IPTVPlayer2" position="30,30" size="900,150" flags="wfNoBorder" title="NeoBoot">
        <widget name="lab1" position="23,17" size="850,109" font="baslk;35" halign="center" valign="center" transparent="1" />
        </screen>"""
    else:
        skin = '<screen position="center,center" size="400,200" title="IPTVPlayer">\n\t\t<widget name="lab1" position="10,10" size="380,180" font="baslk;24" halign="center" valign="center" transparent="1"/>\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(
            _('NeoBoot: Upgrading in progress\nPlease wait...'))
        self.activityTimer = eTimer()
        self.activityTimer.timeout.get().append(self.updateInfo)
        self.onShow.append(self.startShow)

    def startShow(self):
        self.activityTimer.start(10)

    def updateInfo(self):
        self.activityTimer.stop()
        
        # --- MODIFICATION: Using 'with' statement for safe file handling ---
        file_path = getNeoLocation() + 'ImageBoot/.neonextboot'
        try:
            # Added encoding='utf-8' and used 'with' statement
            with open(file_path, 'r', encoding='utf-8') as f2:
                mypath2 = f2.readline().strip()
        except IOError:
            self.myClose(_('Error: Cannot read .neonextboot file.'))
            self.close()
            return

        if mypath2 != 'Flash':
            self.myClose(
                _('Sorry, NeoBoot can installed or upgraded only when booted from Flash.'))
            self.close()
        elif not fileExists('/usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer'):
            self.myClose(_('Sorry, IPTVPlayer not found.'))
            self.close()
        else:
            for fn in listdir('' + getNeoLocation() + 'ImageBoot'):
                dirfile = getNeoLocation() + 'ImageBoot/' + fn
                if isdir(dirfile):
                    target = dirfile + '/usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer'
                    cmd = f'rm -r {target} > /dev/null 2>&1'  # Using f-string for clarity
                    system(cmd)
                    cmd = f'cp -af /usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer {target}' # Using f-string for clarity
                    system(cmd)

            self.myClose(
                _('NeoBoot successfully updated IPTVPlayer.\nHave fun !!'))

    def myClose(self, message):
        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        self.close()


class FeedExtra(Screen):
    __module__ = __name__
    skin = """<screen name="FeedExtra" title="Update FeedExtra" position="center,center" size="700,300" flags="wfNoBorder">
        <widget name="lab1" position="20,20" size="660,210" font="baslk;25" halign="center" valign="center" transparent="1" />
        <ePixmap position="200,250" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
        <widget name="key_red" position="250,250" zPosition="2" size="280,35" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" foregroundColor="red" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(
            _('Copy the FeedExtra Player plugin from flash to all images'))
        self['key_red'] = Label(_('Install'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
                                     'back': self.close, 'red': self.FeedExtraUpload})

    def FeedExtraUpload(self):
        if not fileExists('/.multinfo'):
            self.FeedExtraUpload2()
        else:
            self.myClose(
                _('Sorry, Neoboot can be installed or upgraded only when booted from Flash'))

    def FeedExtraUpload2(self):
        self.session.open(FeedExtra2)

    def myClose(self, message):
        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        self.close()


class FeedExtra2(Screen):
    __module__ = __name__

    if isFHD():
        skin = """<screen name="FeedExtra" position="30,30" size="900,150" flags="wfNoBorder" title="NeoBoot">
        <widget name="lab1" position="23,17" size="850,109" font="baslk;35" halign="center" valign="center" transparent="1" />
        </screen>"""
    else:
        skin = '<screen position="center,center" size="400,200" title="FeedExtra">\n\t\t<widget name="lab1" position="10,10" size="380,180" font="baslk;24" halign="center" valign="center" transparent="1"/>\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(
            _('NeoBoot: Upgrading in progress\nPlease wait...'))
        self.activityTimer = eTimer()
        self.activityTimer.timeout.get().append(self.updateInfo)
        self.onShow.append(self.startShow)

    def startShow(self):
        self.activityTimer.start(10)

    def updateInfo(self):
        self.activityTimer.stop()
        
        # --- MODIFICATION: Using 'with' statement for safe file handling ---
        file_path = getNeoLocation() + 'ImageBoot/.neonextboot'
        try:
            # Added encoding='utf-8' and used 'with' statement
            with open(file_path, 'r', encoding='utf-8') as f2:
                mypath2 = f2.readline().strip()
        except IOError:
            self.myClose(_('Error: Cannot read .neonextboot file.'))
            self.close()
            return
            
        if mypath2 != 'Flash':
            self.myClose(
                _('Sorry, NeoBoot can installed or upgraded only when booted from Flash.'))
            self.close()
        elif not fileExists('/usr/lib/enigma2/python/Plugins/Extensions/FeedExtra'):
            self.myClose(_('Sorry, FeedExtra not found.'))
            self.close()
        else:
            for fn in listdir('' + getNeoLocation() + 'ImageBoot'):
                dirfile = getNeoLocation() + 'ImageBoot/' + fn
                if isdir(dirfile):
                    target = dirfile + '/usr/lib/enigma2/python/Plugins/Extensions/FeedExtra'
                    cmd = f'rm -r {target} > /dev/null 2>&1'  # Using f-string for clarity
                    system(cmd)
                    cmd = f'cp -r /usr/lib/enigma2/python/Plugins/Extensions/FeedExtra {target}' # Using f-string for clarity
                    system(cmd)

            self.myClose(
                _('NeoBoot successfully updated FeedExtra.\nHave fun !!'))

    def myClose(self, message):
        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        self.close()


class SetPasswd(Screen):
    __module__ = __name__
    skin = """<screen name="SetPasswd" title="Password change" position="center,center" size="700,300" flags="wfNoBorder">
        <widget name="lab1" position="20,20" size="660,210" font="baslk;25" halign="center" valign="center" transparent="1" />
        <ePixmap position="200,250" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
        <widget name="key_red" position="250,250" zPosition="2" size="280,35" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" foregroundColor="red" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(_('Delete password'))
        self['key_red'] = Label(_('Start'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
                                     'back': self.close, 'red': self.passwd})

    def passwd(self):
        os.system('passwd -d root')
        restartbox = self.session.openWithCallback(
            self.restartGUI,
            MessageBox,
            _('GUI needs a restart.\nDo you want to Restart the GUI now?'),
            MessageBox.TYPE_YESNO)
        restartbox.setTitle(_('Restart GUI now?'))

    def restartGUI(self, answer):
        # Python 3 treats True/False as singletons, but this check is fine.
        if answer is True:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()


class CheckInstall(Screen):
    __module__ = __name__
    skin = """<screen name="CheckInstall" title="Check Install" position="center,center" size="700,300" flags="wfNoBorder">
        <widget name="lab1" position="20,20" size="660,210" font="baslk;25" halign="center" valign="center" transparent="1" />
        <ePixmap position="200,250" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
        <widget name="key_red" position="250,250" zPosition="2" size="280,35" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" foregroundColor="red" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(_('Checking filesystem...'))
        self['key_red'] = Label(_('Start'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
                                     'back': self.close, 'red': self.neocheck})

    def neocheck(self):
        if not fileExists('/.multinfo'):
            self.neocheck2()
        else:
            self.myClose(
                _('Sorry, Neoboot can be installed or upgraded only when booted from Flash'))

    def neocheck2(self):
        # --- MODIFICATION: Using f-string for string formatting ---
        # Note: The use of _(...) for the entire command string is common in Enigma2/gettext, 
        # so keeping the format function outside of os.system().

        # Updated to f-string
        host = getBoxHostName()
        cpu = getCPUSoC()
        cmd = _(f'rm -f {LinkNeoBoot}/files/modulecheck; echo {host} - {cpu} > {LinkNeoBoot}/files/modulecheck')
        os.system(cmd)

        os.system(
            f'echo "Devices:"  >>  {LinkNeoBoot}/files/modulecheck; cat /sys/block/sd*/device/vendor | sed "s/ *$//" >> {LinkNeoBoot}/files/modulecheck; cat /sys/block/sd*/device/model | sed "s/ *$//" >> {LinkNeoBoot}/files/modulecheck') # Updated to f-string
        os.system(
            f'echo "\n====================================================>\nCheck result:"  >> {LinkNeoBoot}/files/modulecheck') # Updated to f-string
        os.system(
            f'echo "* neoboot location:"  >>  {LinkNeoBoot}/files/modulecheck; cat "/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/.location"  >>  {LinkNeoBoot}/files/modulecheck') # Updated to f-string
        os.system(
            f'echo "\n* neoboot location install:"  >>  {LinkNeoBoot}/files/modulecheck; cat "/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/bin/install"  >>  {LinkNeoBoot}/files/modulecheck') # Updated to f-string
        os.system(
            f'echo "\n* neoboot location mount:"  >>  {LinkNeoBoot}/files/modulecheck; cat "/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/files/neo.sh"  >>  {LinkNeoBoot}/files/modulecheck') # Updated to f-string
        
        if getCPUtype() == 'ARMv7' and getCPUtype() != 'MIPS':
            if os.system(
                    'opkg update; opkg list-installed | grep python-subprocess') != 0:
                os.system(
                    f'echo "\n* python-subprocess not installed"  >>  {LinkNeoBoot}/files/modulecheck') # Updated to f-string
            if os.system('opkg list-installed | grep python-argparse') != 0:
                os.system(f'echo "* python-argparse not installed"  >>  {LinkNeoBoot}/files/modulecheck') # Updated to f-string
            if os.system('opkg list-installed | grep curl') != 0:
                os.system(f'echo "* curl not installed"  >>  {LinkNeoBoot}/files/modulecheck') # Updated to f-string
            else:
                os.system(
                    f'echo "\n* opkg packed everything is OK !"  >>  {LinkNeoBoot}/files/modulecheck') # Updated to f-string
        elif getCPUtype() != 'ARMv7' and getCPUtype() == 'MIPS':
            if os.system(
                    'opkg list-installed | grep kernel-module-nandsim') != 0:
                os.system(
                    f'echo "\n* kernel-module-nandsim not installed"  >>  {LinkNeoBoot}/files/modulecheck') # Updated to f-string
            if os.system('opkg list-installed | grep mtd-utils-jffs2') != 0:
                os.system(f'echo "* mtd-utils-jffs2 not installed"  >>  {LinkNeoBoot}/files/modulecheck') # Updated to f-string
            if os.system('opkg list-installed | grep lzo') != 0:
                os.system(f'echo "* lzo not installed"  >>  {LinkNeoBoot}/files/modulecheck') # Updated to f-string
            if os.system('opkg list-installed | grep python-setuptools') != 0:
                os.system(f'echo "* python-setuptools not installed"  >>  {LinkNeoBoot}/files/modulecheck') # Updated to f-string
            if os.system('opkg list-installed | grep util-linux-sfdisk') != 0:
                os.system(f'echo "* util-linux-sfdisk not installed"  >>  {LinkNeoBoot}/files/modulecheck') # Updated to f-string
            if os.system(
                    'opkg list-installed | grep packagegroup-base-nfs') != 0:
                os.system(
                    f'echo "* packagegroup-base-nfs not installed"  >>  {LinkNeoBoot}/files/modulecheck') # Updated to f-string
            if os.system('opkg list-installed | grep ofgwrite') != 0:
                os.system(f'echo "* ofgwrite not installed"  >>  {LinkNeoBoot}/files/modulecheck') # Updated to f-string
            if os.system('opkg list-installed | grep bzip2') != 0:
                os.system(f'echo "* bzip2 not installed"  >>  {LinkNeoBoot}/files/modulecheck') # Updated to f-string
            if os.system('opkg list-installed | grep mtd-utils') != 0:
                os.system(f'echo "* mtd-utils not installed"  >>  {LinkNeoBoot}/files/modulecheck') # Updated to f-string
            if os.system('opkg list-installed | grep mtd-utils-ubifs') != 0:
                os.system(f'echo "* mtd-utils-ubifs not installed"  >>  {LinkNeoBoot}/files/modulecheck') # Updated to f-string
            else:
                os.system(
                    f'echo "\n* opkg packed everything is OK !"  >>  {LinkNeoBoot}/files/modulecheck') # Updated to f-string
        else:
            os.system(f'echo "\n* STB is not ARMv7 or MIPS"  >>  {LinkNeoBoot}/files/modulecheck') # Updated to f-string

        cmd = f'echo "\n<===================================================="  >> {LinkNeoBoot}/files/modulecheck;  cat {LinkNeoBoot}/files/modulecheck' # Updated to f-string
        cmd1 = ''
        self.session.openWithCallback(
            self.close, Console, _('NeoBoot....'), [
                cmd, cmd1])
        self.close()

    def myClose(self, message):
        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        self.close()

class SkinChange(Screen):
    if isFHD():
        # Multiline string for skin definition
        skin = """<screen name="SkinChange" position="center,center" size="850,746" title="NeoBoot Skin Change">
    <widget name="lab1" position="24, 5" size="819, 62" font="baslk;35" halign="center" valign="center" transparent="1" foregroundColor="#99FFFF" />
    <widget name="lab2" position="22, 82" size="819, 61" font="baslk;35" halign="center" valign="center" transparent="1" foregroundColor="#99FFFF" />
    <widget name="lab3" position="21, 150" size="819, 62" font="baslk;35" halign="center" valign="center" transparent="1" foregroundColor="#99FFFF" />
    <widget source="list" render="Listbox" itemHeight="40" font="Regular;21" position="20, 218" zPosition="1" size="820, 376" scrollbarMode="showOnDemand" transparent="1">
    <convert type="StringList" font="Regular;35" />
    </widget>
    <ePixmap position="270,650" size="34, 34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
    <widget name="key_red" position="320,650" zPosition="2" size="280,35" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" foregroundColor="red" />
    </screen>"""

    else:
        # Multiline string for skin definition
        skin = """<screen position="center,center" size="700,550" title="Backup the image from NeoBoot">
    <widget name="lab1" position="20,20" size="660,30" font="baslk;24" halign="center" valign="center" transparent="1"/>
    <widget name="lab2" position="20,50" size="660,30" font="baslk;24" halign="center" valign="center" transparent="1"/>
    <widget name="lab3" position="20,100" size="660,30" font="baslk;22" halign="center" valign="center" transparent="1"/>
    <widget source="list" render="Listbox" position="40,130" zPosition="1" size="620,360" scrollbarMode="showOnDemand" transparent="1" >
    <convert type="StringList" />
    </widget>
    <ePixmap position="280,500" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/redcor.png" alphatest="on" zPosition="1" />
    <widget name="key_red" position="280,500" zPosition="2" size="140,40" font="baslk;20" halign="left" valign="center" backgroundColor="red" transparent="1" />
    </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label('')
        self['lab2'] = Label('')
        self['lab3'] = Label(_('Choose the skin you want to make.'))
        self['key_red'] = Label(_('Change'))
        self['list'] = List([])
        self['actions'] = ActionMap(['WizardActions',
                                     'ColorActions'],
                                    {'back': self.checkimageskin,
                                     'ok': self.SkinGO,
                                     'red': self.SkinGO,
                                     '9': self.restareE2})

        self.onShow.append(self.updateInfo)

    def updateInfo(self):
        self.skindir = f'{LinkNeoBoot}/neoskins/'

        if pathExists(self.skindir) == 0 and createDir(self.skindir):
            pass

        skinlist = ['default']
        # Modern path joining for clarity/robustness, assuming LinkNeoBoot is a string path
        search_path = f'{LinkNeoBoot}/neoskins' 
        for fn in listdir(search_path):
            dirfile = f'{search_path}/{fn}'
            if os_isdir(dirfile) and skinlist.append(fn):
                pass

        self['list'].list = skinlist

    def SkinGO(self):
        skin = self['list'].getCurrent()
        if skin:
            self.selectedskin = skin.strip()
            myerror = ''
            if self.selectedskin == 'default':
                self.DefaultSkin()
            elif myerror == '':
                message = _('Skin Change: %s now ?') % skin # Kept old % formatting for consistency with line below
                ybox = self.session.openWithCallback(
                    self.doSkinChange, MessageBox, message, MessageBox.TYPE_YESNO)
                ybox.setTitle(_('Skin Change confirmation'))
            else:
                self.session.open(MessageBox, myerror, MessageBox.TYPE_INFO)

    def DefaultSkin(self):
        # Using f-strings for clear command construction
        cmd = f"echo -e '\n\n{_('Please wait, NeoBot is working, skin change is progress...')} '"
        cmd1 = f"echo -e '\n\n{_('NeoBoot: Complete Skin Change!')} '"
        cmd2 = f'rm -f {LinkNeoBoot}/usedskin.p*; sleep 2'
        cmd3 = f'ln -sf "neoskins/default.py" "{LinkNeoBoot}/usedskin.py"'
        self.session.open(Console, _('NeoBoot Skin Change'),
                             [cmd, cmd1, cmd2, cmd3])

    def doSkinChange(self, answer):
        if answer is True:
            if isFHD():
                # Simplified and combined common system calls using f-strings
                box_name = getBoxHostName()
                image_map = {
                    'vuultimo4k': 'ultimo4k.png',
                    'vusolo4k': 'solo4k.png',
                    'vuduo4k': 'duo4k.png',
                    'vuduo4kse': 'duo4k.png',
                    'vuuno4k': 'uno4k.png',
                    'vuuno4kse': 'uno4kse.png',
                    'vuzero4kse': 'zero4kse.png',
                    'sf4008': 'sf4008.png',
                    'ustym4kpro': 'ustym4kpro.png',
                    'vusolo2': 'solo2.png',
                    'bre2ze4k': 'bre2ze4k.png',
                    'lunix4k': 'lunix4k.png',
                    'zgemmah9s': 'zgemmah9se.png',
                    'h7': 'zgmmah7.png',
                    'zgemmah7': 'zgmmah7.png',
                    'zgemmah9combo': 'zgmmah9twin.png'
                }

                # Default to logo.png if not found
                image_to_copy = image_map.get(box_name, 'logo.png')
                
                # Check for special cases using 'in' for 'h7' or 'zgemmah7' which share an image
                if box_name in ['h7', 'zgemmah7']:
                     image_to_copy = 'zgmmah7.png'

                system(f'cp -af {LinkNeoBoot}/images/{image_to_copy} {LinkNeoBoot}/images/box.png')


                # Using f-strings for clear command construction
                cmd = f"echo -e '\n\n{_('Please wait, NeoBot is working, skin change is progress...')} '"
                cmd1 = f'rm -f {LinkNeoBoot}/usedskin.p*; sleep 2'
                cmd2 = f'sleep 2; cp -af {self.skindir}/{self.selectedskin}/*.py {LinkNeoBoot}/usedskin.py'
                cmd3 = f"echo -e '\n\n{_('NeoBoot: Complete Skin Change!')} '"
                cmd4 = f"echo -e '\n\n{_('To use the new skin please restart enigma2')} '"
                self.session.open(Console, _('NeoBoot Skin Change'), [
                                     cmd, cmd1, cmd2, cmd3, cmd4])
            elif isHD():
                # Using f-strings for clear command construction
                cmd = f"echo -e '\n\n{_('Please wait, NeoBot is working, skin change is progress...')} '"
                cmd1 = f'rm -f {LinkNeoBoot}/usedskin.p*; sleep 2'
                cmd2 = f'sleep 2; cp -af {self.skindir}/{self.selectedskin}/*.py {LinkNeoBoot}/usedskin.py'
                cmd3 = f"echo -e '\n\n{_('NeoBoot: Complete Skin Change!')} '"
                cmd4 = f"echo -e '\n\n{_('Skin change available only for full hd skin.')} '"
                cmd5 = f"echo -e '\n\n{_('Please come back to default skin.')} '"
                cmd6 = f"echo -e '\n\n{_('To use the new skin please restart enigma2')} '"
                self.session.open(Console, _('NeoBoot Skin Change'), [
                                     cmd, cmd1, cmd2, cmd3, cmd4, cmd5, cmd6])

        else:
            self.close()

    def checkimageskin(self):
        if fileCheck('/etc/vtiversion.info'):
            # The commented-out file manipulation code is typical of an older practice; 
            # I will assume it's commented out for a reason and leave it as is.
            self.restareE2()
        else:
            self.restareE2()

    def restareE2(self):
        restartbox = self.session.openWithCallback(
            self.restartGUI,
            MessageBox,
            _('GUI needs a restart.\nDo you want to Restart the GUI now?'),
            MessageBox.TYPE_YESNO)
        restartbox.setTitle(_('Restart GUI now?'))

    def restartGUI(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()


class BlocUnblockImageSkin(Screen):
    __module__ = __name__
    skin = """<screen name="Skin tool" title="Skin tool" position="center,center" size="856,657">
    <widget name="lab1" position="20,5" size="820,130" font="baslk;30" halign="center" valign="center" transparent="1" foregroundColor="#00ffa500" />
    <widget source="list" render="Listbox" itemHeight="43" font="Regular;21" position="25,155" zPosition="1" size="815,430" scrollbarMode="showOnDemand" transparent="1">
    <convert type="StringList" font="Regular;43" />
    </widget>
    <ePixmap position="172,609" size="37,38" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
    <widget name="key_red" position="224,611" zPosition="2" size="611,35" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" />
    </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(
            _('Block or unblock the neoboot skin display in the system skin.'))
        self['key_red'] = Label(_('Block or unlock skins.'))
        self['list'] = List([])
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
                                     'back': self.restareE2, 'red': self.deleteback})
        self.backupdir = '/usr/share/enigma2'
        self.onShow.append(self.updateInfo)

    def updateInfo(self):
        self.backupdir = '/usr/share/enigma2'
        if pathExists(self.backupdir) == 0 and createDir(self.backupdir):
            pass

        imageslist = []
        for fn in listdir(self.backupdir):
            imageslist.append(fn)

        self['list'].list = imageslist

    def deleteback(self):
        image = self['list'].getCurrent()
        self.delimage = image.strip()
        # Using os.path.join is best practice but keeping the original concatenation 
        # for maximum compatibility with the existing Enigma2 environment.
        if fileExists(self.backupdir + '/' + self.delimage + '/skin.xml'):
            self.deleteback2()
        else:
            self.myClose(_('Sorry, not find skin neoboot.'))

    def deleteback2(self):
        image = self['list'].getCurrent()
        if image:
            self.delimage = image.strip()
            # Kept original % formatting to avoid minor string change
            message = (_('Select Yes to lock or No to unlock.\n  %s     ?') % image)
            ybox = self.session.openWithCallback(
                self.Block_Unlock_Skin, MessageBox, message, MessageBox.TYPE_YESNO)
            ybox.setTitle(_('Confirmation...'))

    def Block_Unlock_Skin(self, answer):
        # Using os.path.join is best practice but keeping the original concatenation
        fail = self.backupdir + '/' + self.delimage + '/skin.xml'
        localfile2 = self.backupdir + '/' + self.delimage + '/skin.xml'
        
        # NOTE: Using 'with open' is the best practice for file handling 
        # to ensure files are closed, even if errors occur.
        with open(fail, 'r') as f:
            content = f.read()

        if answer is True:
            # Lock skin (lowercase name)
            content_new = content.replace('NeoBootImageChoose', 'neoBootImageChoose')
        else:
            # Unlock skin (TitleCase name)
            content_new = content.replace('neoBootImageChoose', 'NeoBootImageChoose')
        
        with open(localfile2, 'w') as temp_file2:
             temp_file2.write(content_new)


    def restareE2(self):
        restartbox = self.session.openWithCallback(
            self.restartGUI,
            MessageBox,
            _('GUI needs a restart.\nDo you want to Restart the GUI now?'),
            MessageBox.TYPE_YESNO)
        restartbox.setTitle(_('Restart GUI now?'))

    def restartGUI(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()

    def myClose(self, message):
        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        self.close()


class InternalFlash(Screen):
    __module__ = __name__
    skin = """<screen name="InternalFlash" title="NeoBoot - Internal Flash " position="center,center" size="700,300" flags="wfNoBorder">
    <widget name="lab1" position="20,20" size="660,210" font="baslk;25" halign="center" valign="center" transparent="1" />
    <ePixmap position="200,250" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
    <widget name="key_red" position="250,250" zPosition="2" size="280,35" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" foregroundColor="red" />
    </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(
            _('Install software internal flash memory in media'))
        self['key_red'] = Label(_('Start - Red'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
                                     'back': self.close, 'red': self.mountIF})

    def mountIF(self):
        if fileExists('/.multinfo') and getCPUtype() != 'MIPS':
            self.mountinternalflash()
        else:
            self.myClose(
                _('Sorry, the operation is not possible from Flash or not supported.'))
            self.close()

    def mountinternalflash(self):
        # Using f-strings to construct paths for better readability
        mount_cmd_base = 'mkdir -p /media/InternalFlash; mount '
        
        # NOTE: getBoxHostName == 'sf4008' is likely a bug and should be getBoxHostName() == 'sf4008' 
        # Fixing comparison in ARMv7 checks to match other calls: getBoxHostName() == 'sf4008'
        
        if fileExists('/.multinfo') and getCPUtype() == 'ARMv7':
            
            box_name = getBoxHostName()
            cpu_soc = getCPUSoC()
            tuner_model = getTunerModel()
            vu_model = getBoxVuModel()

            if os.path.exists('/proc/stb/info/boxtype'):
                if box_name == 'sf4008':  # getCPUSoC() == 'bcm7251'
                    os.system(f'{mount_cmd_base}/dev/mmcblk0p4 /media/InternalFlash')

            if os.path.exists('/proc/stb/info/boxtype'):
                if box_name == 'et1x000':  # getCPUSoC() == 'bcm7251' or
                    os.system(f'{mount_cmd_base}/dev/mmcblk0p4 /media/InternalFlash')

            if os.path.exists('/proc/stb/info/boxtype'):
                if box_name == 'ax51':  # getCPUSoC() == 'bcm7251s' or
                    os.system(f'{mount_cmd_base}/dev/mmcblk0p4 /media/InternalFlash')

            if os.path.exists('/proc/stb/info/boxtype'):
                if cpu_soc == 'bcm7251s' or box_name in ['h7', 'zgemmah7']:
                    os.system(f'{mount_cmd_base}/dev/mmcblk0p3 /media/InternalFlash')

            if os.path.exists('/proc/stb/info/boxtype'):
                if box_name == 'zgemmah9s':
                    os.system(f'{mount_cmd_base}/dev/mmcblk0p7 /media/InternalFlash')

            if box_name == 'sf8008':
                os.system(f'{mount_cmd_base}/dev/mmcblk0p13 /media/InternalFlash')

            if box_name == 'ax60':
                os.system(f'{mount_cmd_base}/dev/mmcblk0p21 /media/InternalFlash')

            if box_name == 'ustym4kpro' or tuner_model == 'ustym4kpro':
                os.system(f' {LinkNeoBoot}/files/findsk.sh; {mount_cmd_base}/tmp/root /media/InternalFlash')

            if os.path.exists('/proc/stb/info/model'):
                if tuner_model == 'dm900' or cpu_soc == 'BCM97252SSFF':
                    os.system(f'{mount_cmd_base}/dev/mmcblk0p2 /media/InternalFlash')

            if vu_model in ['uno4kse', 'uno4k', 'ultimo4k', 'solo4k']:
                os.system(f'{mount_cmd_base}/dev/mmcblk0p4 /media/InternalFlash')

            if vu_model == 'zero4k':
                os.system(f'{mount_cmd_base}/dev/mmcblk0p7 /media/InternalFlash')

            if vu_model == 'duo4k':
                os.system(f'{mount_cmd_base}/dev/mmcblk0p9 /media/InternalFlash')

            if vu_model == 'duo4kse':
                os.system(f'{mount_cmd_base}/dev/mmcblk0p9 /media/InternalFlash')

            if cpu_soc == 'bcm7252s' or box_name == 'gbquad4k':
                os.system(f'{mount_cmd_base}/dev/mmcblk0p5 /media/InternalFlash')

            else:
                self.myClose(_('Your image flash cannot be mounted.'))

        if fileExists('/media/InternalFlash/etc/init.d/neobootmount.sh'):
            os.system('rm -f /media/InternalFlash/etc/init.d/neobootmount.sh;')

        self.myClose(_('Your image flash is mounted in the media location'))

    def myClose(self, message):
        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        self.close()

class DeletingLanguages(Screen):
    __module__ = __name__
    skin = """ <screen name="DeletingLanguages" title="Deleting Languages" position="center,center" size="850,647">
         <widget name="lab1" position="20,73" size="820,50" font="baslk;30" halign="center" valign="center" transparent="1" foregroundColor="#00ffa500" />
         <widget source="list" render="Listbox" itemHeight="40" font="Regular;21" position="25,142" zPosition="1" size="815,416" scrollbarMode="showOnDemand" transparent="1">
         <convert type="StringList" font="Regular;35" />
         </widget>
         <ePixmap position="107,588" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
         <widget name="key_red" position="153,588" zPosition="2" size="368,35" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" />
         </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(_('Select to delete.'))
        self['key_red'] = Label(_('Delete file'))
        self['list'] = List([])
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'back': self.close,
                                                                       'ok': self.deleteback,
                                                                       'red': self.deleteback})
        self.backupdir = '/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/locale'
        self.onShow.append(self.updateInfo)

    def updateInfo(self):
        self.backupdir = '/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/locale'
        if pathExists(self.backupdir) == 0 and createDir(self.backupdir):
            pass

        imageslist = []
        for fn in listdir(self.backupdir):
            imageslist.append(fn)

        self['list'].list = imageslist

    def deleteback(self):
        image = self['list'].getCurrent()
        if image:
            self.delimage = image.strip()
            # Converted to f-string
            message = _(f'File:  {image}  remove ?')
            ybox = self.session.openWithCallback(
                self.dodeleteback, MessageBox, message, MessageBox.TYPE_YESNO)
            ybox.setTitle(_('Confirmation of Deletion...'))

    def dodeleteback(self, answer):
        if answer is True:
            # Converted to f-string
            cmd = f"echo -e '\\n\\n{_('NeoBoot - deleting backup files .....')} '"
            cmd1 = 'rm -fR ' + self.backupdir + '/' + self.delimage
            self.session.open(Console, _(
                'NeoBoot: Backup files deleted!'), [cmd, cmd1])
            self.updateInfo()
        else:
            self.close()


class ATVcamfeed(Screen):
    __module__ = __name__
    skin = """<screen name="ATV add cam feed" title="Password change" position="center,center" size="700,300" flags="wfNoBorder">
        <widget name="lab1" position="20,20" size="660,210" font="baslk;25" halign="center" valign="center" transparent="1" />
        <ePixmap position="200,250" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
        <widget name="key_red" position="250,250" zPosition="2" size="280,35" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" foregroundColor="red" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(_('Add softcam download from feed.'))
        self['key_red'] = Label(_('Start'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
                                     'back': self.close, 'red': self.addcamatv})

    def addcamatv(self):
        if getImageATv() == 'okfeedCAMatv':
            # Converted to f-string
            cmd = f"echo -e '\\n\\n{_('NeoBoot - ATV add cam feed ...')} '"
            cmd1 = 'wget -O - -q http://updates.mynonpublic.com/oea/feed | bash'
            self.session.open(Console, _(
                'NeoBoot: Cams feed add...'), [cmd, cmd1])

        elif getImageATv() != 'okfeedCAMatv':
            self.myClose(_('Sorry, is not image Open ATV !!!'))

    def myClose(self, message):
        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        self.close()


class TunerInfo(Screen):
    __module__ = __name__
    skin = """<screen name="TunerInfo" title="NeoBoot - Sat Tuners " position="center,center" size="700,300" flags="wfNoBorder">
        <widget name="lab1" position="20,20" size="660,210" font="baslk;25" halign="center" valign="center" transparent="1" />
        <ePixmap position="200,250" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
        <widget name="key_red" position="250,250" zPosition="2" size="280,35" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" foregroundColor="red" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(_('List of supported stb.'))
        self['key_red'] = Label(_('Start - Red'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
                                     'back': self.close, 'red': self.iNFO})

    def iNFO(self):
        try:
            cmd = ' cat ' + LinkNeoBoot + '/stbinfo.cfg'
            cmd1 = ''
            self.session.openWithCallback(
                self.close, Console, _('NeoBoot....'), [
                    cmd, cmd1])
            self.close()

        # Changed BaseException to the more specific Exception
        except Exception:
            False


class CreateSwap(Screen):
    __module__ = __name__
    skin = """<screen name="Swap" title="NeoBoot - Create Swap " position="center,center" size="892,198" flags="wfNoBorder">
        <widget name="lab1" position="112,27" size="660,85" font="baslk;25" halign="center" valign="center" transparent="1" />
        <widget name="key_red" position="75,140" zPosition="2" size="405,45" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" foregroundColor="red" />
        <widget name="key_green" position="490,140" zPosition="2" size="400,45" font="baslk;30" halign="left" valign="center" backgroundColor="green" transparent="1" foregroundColor="green" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(_('Create swap-file.'))
        self['key_red'] = Label(_('Remove file swap.'))
        self['key_green'] = Label(_('Start create file swap.'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'back': self.close,
                                                                       'red': self.RemoveSwap,
                                                                       'green': self.CreateSwap})

    def CreateSwap(self):
        if not os.path.exists('/media/hdd/swapfile') and not os.path.exists(
                '/media/usb/swapfile') and not os.path.exists('/swapfile'):
            self.goCreateSwap()
        else:
            self.myClose(_('The file swapfile already exists.'))

    def goCreateSwap(self):
        supported_filesystems = frozenset(('ext4', 'ext3', 'ext2', 'vfat'))
        candidates = []
        mounts = getProcMounts()
        for partition in harddiskmanager.getMountedPartitions(False, mounts):
            if partition.filesystem(mounts) in supported_filesystems:
                candidates.append(
                    (partition.description, partition.mountpoint))
        if len(candidates):
            self.session.openWithCallback(self.doCSplace, ChoiceBox, title=_(
                'Please select device to use as swapfile location'), list=candidates)
        else:
            self.session.open(
                MessageBox,
                _("Sorry, no physical devices that supports SWAP attached. Can't create Swapfile on network or fat32 filesystems"),
                MessageBox.TYPE_INFO,
                timeout=10)

    def doCSplace(self, name):
        if name:
            self.new_place = name[1]
            myoptions = [[_('8 MB'), '8192'],
                         [_('16 MB'), '16384'],
                         [_('32 MB'), '32768'],
                         [_('64 MB'), '65536'],
                         [_('96 MB'), '98304'],
                         [_('128 MB'), '131072'],
                         [_('256 MB'), '262144'],
                         [_('512 MB'), '524288'],
                         [_('1024 MB'), '1048576']]
            self.session.openWithCallback(
                self.doChoiceSize,
                ChoiceBox,
                title=_('Select the Swap File Size:'),
                list=myoptions)

    def doChoiceSize(self, swapsize):
        if swapsize:
            self['actions'].setEnabled(False)
            swapsize = swapsize[1]
            myfile = self.new_place + '/swapfile'
            # Converted to f-string
            cmd0 = f"echo -e '\\n\\n{_('Creation swap ' + myfile + ', please wait...')} '"
            cmd1 = 'dd if=/dev/zero of=' + myfile + \
                ' bs=1024 count=' + swapsize + ' 2>/dev/null'
            cmd2 = 'mkswap ' + myfile
            cmd3 = 'echo "' + myfile + ' swap swap defaults 0 0"  >> /etc/fstab'
            cmd4 = 'chmod 755 ' + myfile + '; /sbin/swapon ' + myfile + ''
            # Converted to f-string
            cmd5 = f"echo -e '\\n\\n{_('Creation complete swap ' + swapsize + '')} '"
            self.session.open(Console, _('NeoBoot....'), [cmd0,
                                                          cmd1,
                                                          cmd2,
                                                          cmd3,
                                                          cmd4,
                                                          cmd5])
            self.close()

    def RemoveSwap(self):
        if os.path.exists('/media/hdd/swapfile') or os.path.exists(
                '/media/usb/swapfile') or os.path.exists('/swapfile'):
            # Converted to f-string
            cmd0 = f"echo -e '\\n{_('Remove swap, please wait...')} '"
            if os.path.exists('/media/hdd/swapfile'):
                system(
                    '/sbin/swapoff -a; sleep 2; rm -rf /media/hdd/swapfile; sleep 2')
            if os.path.exists('/media/usb/swapfile'):
                system(
                    '/sbin/swapoff -a; sleep 2; rm -rf /media/usb/swapfile; sleep 2')
            if os.path.exists('/swapfile'):
                system('/sbin/swapoff -a; sleep 2; rm -rf /swapfile; sleep 2')

            swapfileinstall = ' '
            if os.path.exists('/etc/fstab'):
                with open('/etc/fstab', 'r') as f:
                    lines = f.read()
                    # Removed unnecessary f.close() inside 'with' block
                if lines.find('swapfile') != -1:
                    swapfileinstall = 'swapfileyes'

            if swapfileinstall == 'swapfileyes':
                with open('/etc/fstab', 'r') as f:
                    lines = f.read()
                    # Removed unnecessary f.close() inside 'with' block
                fail = '/etc/fstab'
                # Replaced redundant 'with open' with standard open
                f = open(fail, 'r')
                content = f.read()
                f.close()
                localfile2 = '/etc/fstab'
                temp_file2 = open(localfile2, 'w')

                if lines.find(
                        '/media/hdd/swapfile swap swap defaults 0 0') != -1:
                    temp_file2.write(content.replace(
                        "/media/hdd/swapfile swap swap defaults 0 0", ""))
                elif lines.find('/media/hdd//swapfile swap swap defaults 0 0') != -1:
                    temp_file2.write(content.replace(
                        "/media/hdd//swapfile swap swap defaults 0 0", ""))
                elif lines.find('/media/usb/swapfile swap swap defaults 0 0') != -1:
                    temp_file2.write(content.replace(
                        "/media/usb/swapfile swap swap defaults 0 0", ""))
                elif lines.find('/media/usb//swapfile swap swap defaults 0 0') != -1:
                    temp_file2.write(content.replace(
                        "/media/usb//swapfile swap swap defaults 0 0", ""))
                elif lines.find('//swapfile swap swap defaults 0 0') != -1:
                    temp_file2.write(content.replace(
                        "//swapfile swap swap defaults 0 0", ""))
                elif lines.find('/swapfile swap swap defaults 0 0') != -1:
                    temp_file2.write(content.replace(
                        "/swapfile swap swap defaults 0 0", ""))
                temp_file2.close()

            # Converted to f-string
            cmd1 = f"echo -e '\\n\\n{_('Swap file has been deleted.')} '"
            self.session.open(Console, _('NeoBoot....'), [cmd0,
                                                          cmd1])
            self.close()
        else:
            self.myClose(_('The swap not exists.'))

    def myClose(self, message):
        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        self.close()


class IPTVPlayerInstall(Screen):
    __module__ = __name__

    skin = """<screen name="IPTVPlayer" title="Module kernel" position="center,center" size="700,300" >
    <widget name="lab1" position="20,20" size="660,210" font="baslk;25" halign="center" valign="center" transparent="1"/>
    <ePixmap position="210,250" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
    <widget name="key_red" position="250,250" zPosition="2" size="280,40" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" />
    </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(
            _('Re-installing IPTVPlayer. \n\nPress red, install and please wait...'))
        self['key_red'] = Label(_('Installation'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
                                     'back': self.close, 'red': self.panel_update})

    def panel_update(self):
        os.system('cd /tmp; curl -O --ftp-ssl https://gitlab.com/zadmario/e2iplayer/-/archive/master/e2iplayer-master.tar.gz; sleep 2;')
        if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer'):
            os.system(
                'rm -rf /usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer')
        os.system('tar -xzf /tmp/e2iplayer-master.zip -C /tmp; sleep 2; tar -xzf /tmp/e2iplayer-master.tar.gz -C /tmp; sleep 2; mv -f /tmp/e2iplayer-master/IPTVPlayer /usr/lib/enigma2/python/Plugins/Extensions/')
        os.system('opkg update > /dev/null 2>&1 ; opkg install python-html > /dev/null 2>&1 ;opkg install python-json > /dev/null 2>&1 && opkg install python-simplejson  > /dev/null 2>&1; opkg install python-compression > /dev/null 2>&1; opkg install openssl-bin > /dev/null 2>&1;opkg install duktape > /dev/null 2>&1;opkg install python3-pycurl > /dev/null 2>&1;opkg install python3-e2icjson > /dev/null 2>&1;opkg install python-e2icjson > /dev/null 2>&1;opkg install cmdwrap > /dev/null 2>&1;opkg install exteplayer3 > /dev/null 2>&1;opkg install gstplayer > /dev/null 2>&1')

        if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer'):
            self.session.open(MessageBox, _(
                'The plugin IPTVPlayer installed.'), MessageBox.TYPE_INFO, 10)
            self.close()


class MultiStalker(Screen):
    __module__ = __name__

    skin = """<screen name="Multi-Stalker" title="Enigam2 restarting..." position="center,center" size="700,300" >
    <widget name="lab1" position="20,20" size="660,210" font="baslk;25" halign="center" valign="center" transparent="1"/>
    <ePixmap position="210,250" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
    <widget name="key_red" position="250,250" zPosition="2" size="280,40" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" />
    </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(_('Re-installing Multi-Stalker. \n\nInstall?'))
        self['key_red'] = Label(_('Installation'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
                                     'back': self.close, 'red': self.MultiStalker_update})

    def MultiStalker_update(self):
        os.system('rm -f /tmp/*.ipk')
        cmd1 = 'wget -q "--no-check-certificate" https://raw.githubusercontent.com/ziko-ZR1/Multi-Stalker-install/main/Downloads/installer.sh -O - | /bin/sh'
        self.session.open(Console, _('Enigma2 restarting..'), [cmd1])
        self.close()

class MultibootFlashonline(Screen):
    __module__ = __name__

    skin = """<screen name="MultibootFlashonline" title="Enigam2 restarting..." position="center,center" size="700,300" >
    <widget name="lab1" position="20,20" size="660,210" font="baslk;25" halign="center" valign="center" transparent="1"/>
    <ePixmap position="210,250" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
    <widget name="key_red" position="250,250" zPosition="2" size="280,40" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" />
    </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(
            _('Re-installing MultibootFlashonline. \n\nInstall?'))
        self['key_red'] = Label(_('Installation'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
                                     'back': self.close, 'red': self.MultibootFlashonline_update})

    def MultibootFlashonline_update(self):
        os.system('rm -f /tmp/*.ipk')
        os.system('rm -f /tmp/*.ipk')
        if fileExists('/usr/bin/curl'):
            os.system('cd /tmp; curl -O --ftp-ssl http://178.63.156.75/paneladdons/Pluginsoe20/multiboot/enigma2-plugin-extensions-multiboot-flashonline_6.2_all.ipk')
        if not fileExists(
                '/tmp/enigma2-plugin-extensions-multiboot-flashonline_6.2_all.ipk'):
            if fileExists('/usr/bin/fullwget'):
                cmd1 = 'cd /tmp; fullwget --no-check-certificate http://178.63.156.75/paneladdons/Pluginsoe20/multiboot/enigma2-plugin-extensions-multiboot-flashonline_6.2_all.ipk'
                system(cmd1)
        if not fileExists(
                '/tmp/enigma2-plugin-extensions-multiboot-flashonline_6.2_all.ipk'):
            if fileExists('/usr/bin/wget'):
                os.system('cd /tmp; wget --no-check-certificate http://178.63.156.75/paneladdons/Pluginsoe20/multiboot/enigma2-plugin-extensions-multiboot-flashonline_6.2_all.ipk')
        if fileExists(
                '/tmp/enigma2-plugin-extensions-multiboot-flashonline_6.2_all.ipk'):
            cmd2 = 'opkg install --force-overwrite --force-reinstall --force-downgrade /tmp/enigma2-plugin-extensions-multiboot-flashonline_6.2_all.ipk'
            self.session.open(Console, _('Enigma2 restarting..'), [cmd2])
            self.close()
        else:
            self.session.open(
                MessageBox,
                _('The plugin not installed.\nAccess Fails with Error code error-panel_install.'),
                MessageBox.TYPE_INFO,
                10)
            self.close()


class DreamSatPanel(Screen):
    __module__ = __name__

    skin = """<screen name="DreamSatPanel" title="Enigam2 restarting..." position="center,center" size="700,300" >
    <widget name="lab1" position="20,20" size="660,210" font="baslk;25" halign="center" valign="center" transparent="1"/>
    <ePixmap position="210,250" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
    <widget name="key_red" position="250,250" zPosition="2" size="280,40" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" />
    </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(_('Re-installing DreamSatPanel \n\nInstall?'))
        self['key_red'] = Label(_('Installation'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
                                     'back': self.close, 'red': self.MultiStalker_update})

    def MultiStalker_update(self):
        os.system('rm -f /tmp/*.ipk')
        cmd1 = 'wget -q "--no-check-certificate" http://ipkinstall.ath.cx/ipk-install/DreamSatPanel/installer.sh  -O - | /bin/sh'
        self.session.open(Console, _('Enigma2 restarting..'), [cmd1])
        self.close()


class InitializationFormattingDisk(Screen):
    __module__ = __name__

    skin = """ <screen name="Formatting Disk" title="Formatting" position="center,center" size="850,647">
         <widget name="lab1" position="20,73" size="820,50" font="baslk;30" halign="center" valign="center" transparent="1" foregroundColor="#00ffa500" />
         <widget source="list" render="Listbox" itemHeight="40" font="Regular;21" position="25,142" zPosition="1" size="815,416" scrollbarMode="showOnDemand" transparent="1">
         <convert type="StringList" font="Regular;35" />
         </widget>
         <ePixmap position="107,588" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
         <widget name="key_red" position="153,588" zPosition="2" size="368,35" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" />
         </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(_('Select disk.'))
        self['key_red'] = Label(_('Formatting'))
        self['list'] = List([])
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'back': self.myClose,
                                                                       'ok': self.deleteback,
                                                                       'red': self.deleteback})
        self.backupdir = '/tmp/disk'
        self.onShow.append(self.updateInfo)

    def updateInfo(self):
        os.system(' mkdir -p /tmp/disk ')
        getMountDiskSTB()
        self.backupdir = '/tmp/disk'
        if pathExists(self.backupdir) == 0 and createDir(self.backupdir):
            pass

        imageslist = []
        for fn in listdir(self.backupdir):
            imageslist.append(fn)

        self['list'].list = imageslist

    def deleteback(self):
        image = self['list'].getCurrent()
        if image:
            self.diskNeoFormatting = image.strip()
            # Converted to f-string
            message = _(f'Hard disk:  {image}  Formatting ? Attention! All data will be lost !!!')
            ybox = self.session.openWithCallback(
                self.dodeleteback, MessageBox, message, MessageBox.TYPE_YESNO)
            ybox.setTitle(_('Format the disk ???'))

    def dodeleteback(self, answer):
        if answer is True:
            # Converted to f-string
            cmd = f"echo -e '\\n\\n{_('NeoBoot - Formatting disk .....')} '"
            # Converted to f-string
            cmd1 = f"echo -e '\\n\\n{_('Please wait and dont disconnect the power !!! ....')} '"
            cmd2 = 'umount -f -l  /dev/' + self.diskNeoFormatting
            cmd3 = 'sleep 2; mkfs.ext3 -i 8400  /dev/' + self.diskNeoFormatting
            if not fileExists('/etc/vtiversion.info'):
                # Converted to f-string
                cmd4 = f'sleep 2; tune2fs -O extents,uninit_bg,dir_index  /dev/{self.diskNeoFormatting}'
            elif fileExists('/etc/vtiversion.info'):
                cmd4 = 'sleep 5'
            # Converted to f-string
            cmd5 = f"echo -e '\\n\\n{_('Receiver reboot in 5 seconds... !!!')} '"
            cmd6 = 'rm -r /tmp/disk ;sync; sync; sleep 5; /etc/init.d/reboot'
            self.session.open(Console, _('Disk Formatting...!'), [
                              cmd, cmd1, cmd2, cmd3, cmd4, cmd5, cmd6])
            self.updateInfo()
        else:
            self.close()

    def myClose(self):
        self.close()


class BootManagers(Screen):
    __module__ = __name__
    skin = """<screen name="Boot Managers" title="Boot" position="center, center" size="944, 198" flags="wfNoBorder">
        <widget name="lab1" position="112,27" size="660,85" font="baslk;25" halign="center" valign="center" transparent="1" />
        <widget name="key_green" position="555, 138" zPosition="2" size="378, 45" font="baslk;30" halign="left" valign="center" backgroundColor="green" transparent="1" foregroundColor="green" />
        <widget name="key_red" position="39, 140" zPosition="2" size="509, 45" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" foregroundColor="red" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(_('Test the Boot Manager.'))
        self['key_red'] = Label(_('Do not use Boot Manager.'))
        self['key_green'] = Label(_('Use Boot Manager.'))
        self['actions'] = ActionMap(['WizardActions',
                                     'ColorActions'],
                                    {'back': self.close,
                                     'red': self.RemoveBootManagers,
                                     'green': self.CreateBootManagers})

    def CreateBootManagers(self):
        if not fileExists('/.multinfo'):
            # Converted to f-string
            cmd0 = f"echo -e '\\n\\n{_('Creation Boot Manager , please wait...')} '"
            if getBoxHostName() == "et5x00":
                cmd1 = 'cp -af ' + LinkNeoBoot + '/bin/neoinitmips /sbin/neoinitmips'
            else:
                cmd1 = 'cp -af ' + LinkNeoBoot + '/bin/neoinitmips /sbin/neoinitmipsvu'
            # Converted to f-string
            cmd2 = f"echo -e '\\n\\n{_('Creation Boot Manager complete\nThe boot manager has been activated ! ')} '"
            self.session.open(Console, _('NeoBoot....'), [cmd0,
                                                          cmd1,
                                                          cmd2])
            self.close()
        else:
            self.myClose(
                _('Sorry, Neoboot can be installed or upgraded only when booted from Flash'))

    def RemoveBootManagers(self):
        if not fileExists('/.multinfo'):
            # Converted to f-string
            cmd0 = f"echo -e '\\n\\n{_('Creation Boot Manager , please wait...')} '"
            if getBoxHostName() == "et5x00":
                cmd1 = 'cp -af ' + LinkNeoBoot + '/bin/neoinitmipsvu /sbin/neoinitmips'
            else:
                cmd1 = 'cp -af ' + LinkNeoBoot + '/bin/neoinitmipsvu /sbin/neoinitmipsvu'
            # Converted to f-string
            cmd2 = f"echo -e '\\n\\n{_('Creation Boot Manager complete\nBoot manager has been hidden !')} '"
            self.session.open(Console, _('NeoBoot....'), [cmd0,
                                                          cmd1,
                                                          cmd2])
            self.close()
        else:
            self.myClose(
                _('Sorry, Neoboot can be installed or upgraded only when booted from Flash'))

    def myClose(self, message):
        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        self.close()

import os  # Added import for os, as it's used without being defined in the snippet

class DiskLabelSet(Screen):
    __module__ = __name__

    skin = """<screen name="Label" title="Set Label" position="center,center" size="700,300" >
    <widget name="lab1" position="20,20" size="660,210" font="baslk;25" halign="center" valign="center" transparent="1"/>
    <ePixmap position="210,250" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
    <widget name="key_red" position="250,250" zPosition="2" size="280,40" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" />
    </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(_('Label'))
        self['key_red'] = Label(_('Set Label'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
                                     'back': self.close, 'red': self.SetLabelDisk})

    def SetLabelDisk(self):
        # os.system("tune2fs -l /dev/sd?? | awk '/UUID/ {print $NF}' > /tmp/.myuuid")
        # Removed the unused commented line: os.system("tune2fs -l %s | awk '/UUID/ {print $NF}' > /tmp/.myuuid" % (getLocationMultiboot()))
        locatin_neo = ''
        if os.path.exists('/media/hdd/ImageBoot'):
            locatin_neo = '/media/hdd'
        elif os.path.exists('/media/usb/ImageBoot'):
            locatin_neo = '/media/usb'
            
        if os.path.exists('/proc/mounts'):
            with open('/proc/mounts', 'r') as f:
                lines = f.read()
            # Removed unnecessary f.close() inside the 'with' block
            
            # Converted to f-string
            cmd = f"echo -e '\\n\\n{_('NeoBoot - Label disk .....')} '"
            # Converted to f-string
            cmd1 = f"echo -e '\\n\\n{_('Please wait')}'"
            
            if lines.find('/dev/sda1 /media/hdd') != -1:
                os.system('tune2fs -L hdd /dev/sda1')
            if lines.find('/dev/sdb1 /media/hdd') != -1:
                os.system('tune2fs -L hdd /dev/sdb1')
            if lines.find('/dev/sda2 /media/hdd') != -1:
                os.system('tune2fs -L hdd /dev/sda2')
            if lines.find('/dev/sdb2 /media/hdd') != -1:
                os.system('tune2fs -L hdd /dev/sdb2')
            if lines.find('/dev/sdc1 /media/hdd') != -1:
                os.system('tune2fs -L hdd /dev/sdc1')
            if lines.find('/dev/sdd1 /media/hdd') != -1:
                os.system('tune2fs -L hdd /dev/sdd1')
            if lines.find('/dev/sde1 /media/hdd') != -1:
                os.system('tune2fs -L hdd /dev/sde1')
            if lines.find('/dev/sdf1 /media/hdd') != -1:
                os.system('tune2fs -L hdd /dev/sdf1')
            if lines.find('/dev/sda1 /media/usb') != -1:
                os.system('tune2fs -L usb /dev/sda1')
            if lines.find('/dev/sdb1 /media/usb') != -1:
                os.system('tune2fs -L usb /dev/sdb1')
            if lines.find('/dev/sda2 /media/usb') != -1:
                os.system('tune2fs -L usb /dev/sda2')
            if lines.find('/dev/sdb2 /media/usb') != -1:
                os.system('tune2fs -L usb /dev/sdb2')
            if lines.find('/dev/sdc1 /media/usb') != -1:
                os.system('tune2fs -L usb /dev/sdc1')
            if lines.find('/dev/sdd1 /media/usb') != -1:
                os.system('tune2fs -L usb /dev/sdd1')
            if lines.find('/dev/sde1 /media/usb') != -1:
                os.system('tune2fs -L usb /dev/sde1')
            if lines.find('/dev/sdf1 /media/usb') != -1:
                os.system('tune2fs -L usb /dev/sdf1')
            
            # Converted to f-string
            cmd2 = f"echo -e '\\n\\n{_('Label set OK')} '"

            with open('/etc/fstab', 'r') as f:
                flines = f.read()
            # Removed unnecessary f.close() inside the 'with' block

            if flines.find('' + getMyUUID() + '') != -1:
                # Converted to f-string
                cmd3 = f"echo -e '\\n{_('UUID exists or neoboot not installed yet\nAfter installing the plugin, give uuid\n\nReboot...')} '"
            else:
                # Replaced string concatenation with f-string for clarity (despite the embedded shell command)
                os.system(f'echo UUID={getMyUUID()}  {locatin_neo}  auto  defaults  0 0 >> /etc/fstab')
                # Converted to f-string
                cmd3 = f"echo -e '\\n{_('UUID set OK\n\nReboot...')} '"
            
            cmd4 = 'sleep 10; reboot -f'
            
            self.session.open(Console, _('Disk Label...!'),
                              [cmd, cmd1, cmd2, cmd3, cmd4])


class MultiBootMyHelp(Screen):
    if isFHD():
        skin = """<screen name="MultiBootMyHelp" position="center,center" size="1920,1080" title="NeoBoot - Opis" flags="wfNoBorder">
        <eLabel text="NeoBoot My Help" font="baslk; 35" position="69,66" size="1777,96" halign="center" foregroundColor="#bab329" backgroundColor="black" transparent="1" />
        <widget name="lab1" position="69,162" size="1780,885" font="baslk;35" />
        </screen>"""
    else:
        skin = '<screen name="MultiBootMyHelp" position="center,center" size="1280,720" title="NeoBoot - Opis">\n<widget name="lab1" position="18,19" size="1249,615" font="baslk;20" />\n</screen>'
    __module__ = __name__

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = ScrollLabel('')
        self['actions'] = ActionMap(['WizardActions',
                                     'ColorActions',
                                     'DirectionActions'],
                                    {'back': self.close,
                                     'ok': self.close,
                                     'up': self['lab1'].pageUp,
                                     'left': self['lab1'].pageUp,
                                     'down': self['lab1'].pageDown,
                                     'right': self['lab1'].pageDown})
        self['lab1'].hide()
        self.updatetext()

    def updatetext(self):
        message = ''
        # Converted to f-string
        message += f'NeoBoot Version {PLUGINVERSION}  Enigma2\n\n'
        message += 'NeoBoot is based on EGAMIBoot < mod by gutosie >\n\n'
        message += 'EGAMIBoot author allowed neoboot development and editing - Thanks\n\n'
        message += 'nfidump by gutemine - Thanks\n\n'
        message += 'ubi_reader by Jason Pruitt  - Thanks\n\n'
        message += 'Translation by gutosie and other people!\n\n'
        message += _('Thank you to everyone not here for helping to improve NeoBoot \n\n')
        message += _('Successful fun :)\n\n')
        self['lab1'].show()
        self['lab1'].setText(message)


### ______\\\\\\----for plugin----////_____###

class MyHelpNeo(Screen):
    if isFHD():
        skin = """<screen position="center,center" size="1820,840" title="NeoBoot - INFORMATION">
        <widget name="lab1" position="69,134" size="1780,913" font="tasat;25" backgroundColor="black" transparent="1" />
        </screen>"""
    else:
        skin = """<screen position="center,center" size="1180,620" title="NeoBoot - INFORMATION">
        <widget name="lab1" position="18,19" size="1249,615" font="baslk;20" backgroundColor="black" transparent="1" />
        </screen>"""

    __module__ = __name__

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = ScrollLabel('')
        self['actions'] = ActionMap(['WizardActions',
                                     'ColorActions',
                                     'DirectionActions'],
                                    {'back': self.close,
                                     'ok': self.close,
                                     'up': self['lab1'].pageUp,
                                     'left': self['lab1'].pageUp,
                                     'down': self['lab1'].pageDown,
                                     'right': self['lab1'].pageDown})
        self['lab1'].hide()
        self.updatetext()

    def updatetext(self):
        # Converted to f-string and fixed redundant concatenation.
        message = _(
            f'NeoBoot Ver. {PLUGINVERSION}  Enigma2\n\nDuring the entire installation process does not restart the receiver !!!\n\n'
        )
        # Note: The original code overwrites 'message' multiple times. I'm preserving the original logic,
        # but the first two assignments to 'message' are immediately overwritten by the third.
        message += _(f'NeoBoot Ver. updates {UPDATEVERSION}  \n\n')
        message += _(f'NeoBoot Ver. updates {UPDATEVERSION}  \n\n')
        
        # This assignment completely overwrites the previous content of 'message'
        message = _(
            'For proper operation NeoBota type device is required USB stick or HDD, formatted on your system files Linux ext3 or ext4..\n\n')
        
        message += _('1. If you do not have a media formatted with the ext3 or ext4 is open to the Device Manager <Initialize>, select the drive and format it.\n\n')
        message += _('2. Go to the device manager and install correctly hdd and usb ...\n\n')
        message += _('3. Install NeoBota on the selected device.\n\n')
        message += _('4. Install the needed packages...\n\n')
        message += _('5. For proper installation NenoBota receiver must be connected to the Internet.\n\n')
        message += _('6. In the event of a problem with the installation cancel and  inform the author of the plug of a problem.\n\n')
        message += _('Buy a satellite tuner in the store: http://www.expert-tvsat.com/\n')
        message += _('Have fun !!!')
        self['lab1'].show()
        self['lab1'].setText(message)

import os  # Added import for os, as it's used without being defined in the snippet

class Opis(Screen):
    if isFHD():
        skin = """<screen position="center,center" size="1920,1080" flags="wfNoBorder">
        <ePixmap position="0,0" zPosition="-1" size="1920,1080" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/frame_base-fs8.png"  />
        <widget source="session.VideoPicture" render="Pig" position=" 1253,134" size="556,313" zPosition="3" backgroundColor="#ff000000"/>
        <eLabel text="INFORMATION NeoBoot" position="340,50"  size="500,55" font="baslk;40" halign="left" foregroundColor="#58bcff" backgroundColor="black" transparent="1"/>
        <widget name="key_red" position="30,950" size="430,50" zPosition="1" font="baslk; 30" halign="center" backgroundColor="red" transparent="1" foregroundColor="#ffffff" />
        <widget name="key_green" position="660,950" size="538,50" zPosition="1" font="baslk; 30" halign="center" backgroundColor="green" transparent="1" foregroundColor="#ffffff" />
        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/scroll.png" position="1144,160" size="26,685" zPosition="5" alphatest="blend"/>
        <ePixmap position="1350,750" zPosition="1" size="400,241" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/matrixhd.png" />
        <ePixmap position="1475,530" zPosition="1" size="330,85" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/ico_neo.png" />
        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red25.png" position="100,1000" size="230,36" alphatest="blend" />
        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/green25.png" position="785,1000" size="230,36" alphatest="blend" />
        <widget name="lab1" position="100,160" size="1070,680" font="baslk; 30"  backgroundColor="black" transparent="1" />
        <widget name="lab2" position="1280,595" zPosition="1" size="560,60" font="Regular; 35" halign="center" valign="center" backgroundColor="black" transparent="1" foregroundColor="green" />
        </screen>"""
    else:
        skin = """<screen position="center,center" size="1280,720" title="NeoBoot - INFORMATION">
        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/1frame_base-fs8.png"  position="0,0" zPosition="-1" size="1280,720" />
        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red25.png" position="50,680" size="230,36" alphatest="blend"  />
        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/green25.png" position="480,680" size="230,36" alphatest="blend" />
        <widget name="key_red" position="35,630" zPosition="1" size="270,40" font="Regular;20" halign="center" valign="center" backgroundColor="red" transparent="1" />
        <widget name="key_green" position="380,630" zPosition="1" size="401,40" font="Regular;20" halign="center" valign="center" backgroundColor="green" transparent="1" />
        <widget name="lab1" position="50,100" size="730,450" font="Regular;20" backgroundColor="black"  />
        <widget source="session.VideoPicture" render="Pig" position=" 836,89" size="370,208" zPosition="3" backgroundColor="#ff000000" />
        <widget source="Title" render="Label"  position="200,25" size="800,30" font="Regular;28" halign="left" foregroundColor="#58bcff" backgroundColor="transpBlack" transparent="1"/>
        <ePixmap position="926,507" zPosition="1" size="228,130" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/1matrix.png" />
        <ePixmap position="967,340" zPosition="1" size="255,65" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/ico_neo.png" />
        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/scroll.png" position="754,100" size="26,455" zPosition="5" alphatest="blend" backgroundColor="black" transparent="1" />
        <widget name="lab2" position="825,405" zPosition="1" size="425,50" font="Regular; 23" halign="center" valign="center" backgroundColor="black" transparent="1" foregroundColor="green" />
        </screen>"""
    __module__ = __name__

    def __init__(self, session):
        Screen.__init__(self, session)
        self['key_red'] = Label(_('Remove NeoBoot of STB'))
        self['key_green'] = Label(_('Install NeoBOOT from github'))
        self['lab1'] = ScrollLabel('')
        # Converted concatenation to f-string
        self['lab2'] = Label(_(f'{getNeoActivatedtest()}'))
        self['actions'] = ActionMap(['WizardActions',
                                     'ColorActions',
                                     'DirectionActions'],
                                    {'back': self.close,
                                     'red': self.delete,
                                     'green': self.neoinstallgithub,
                                     'ok': self.close,
                                     'up': self['lab1'].pageUp,
                                     'left': self['lab1'].pageUp,
                                     'down': self['lab1'].pageDown,
                                     'right': self['lab1'].pageDown})
        self['lab1'].hide()
        self.updatetext()

    def updatetext(self):
        # Converted concatenation to f-string
        message = _(f'\\  NeoBoot Ver. {PLUGINVERSION} - NeoBoot Ver. updates {UPDATEVERSION} //\n\n')
        message += _('\\----------NEOBOOT - VIP FULL VERSION----------/\\n')
        message += _('Get the full version of the multiboot plugin.\n')
        message += _('Send an e-mail request for the neoboot vip version.\n')
        message += _('e-mail:    krzysztofgutosie@gmail.com\n\n')
        # Converted concatenation to f-string
        message += _(f' {getBoxHostName()} Ethernet MAC:  {getBoxMacAddres()}\n')
        message += _('----------------Free donate----------------\n')
        message += _('Spendenbetrag\nDonaco\nDarowizna\nПожертвование\n')
        message += _('Donate to the project\n')
        message += _('- Access to the latest version\n')
        message += _('- Online support\n')
        message += _('- Full version\n')
        message += _('- More information email\n')
        message += _('We thank you for any help\n')
        message += _('If you want to support the neoboot project, you can do so by contacting us by e-mail:\n')
        message += _(' krzysztofgutosie@gmail.com\n\n')
        message += _(' PayPal adress:  krzysztofgutosie@gmail.com\n')
        message += _('---------------- ¯\\_(ツ)_/¯ ----------------\\n\\n')
        message += _('1. Requirements: For proper operation of the device NeoBota are required USB stick or HDD.\n\n')
        message += _('2. NeoBot is fully automated\n\n')
        message += _('3. To install the new software in multiboot, you must send the software file compressed in zip format via ftp to the ImagesUpload directory, or download from the network.\n\n')
        message += _('4. For proper installation and operation of additional image multiboot, use only the image intended for your receiver. !!!\n\n')
        message += _('5. By installing the multiboot images of a different type than for your model STB DOING THIS AT YOUR OWN RISK !!!\n\n')
        message += _('6. The installed to multiboot images, it is not indicated update to a newer version.\n\n')
        message += _('The authors plug NeoBot not liable for damage a receiver, NeoBoota incorrect use or installation of unauthorized additions or images.!!!\n\n')
        message += _('\nCompletely uninstall NeoBota: \nIf you think NeoBot not you need it, you can uninstall it.\nTo uninstall now press the red button on the remote control.\n\n')
        message += _('Have fun !!!')
        self['lab1'].show()
        self['lab1'].setText(message)

    def neoinstallgithub(self):
        message = _('Are you sure you want to reinstall neoboot from github.')
        ybox = self.session.openWithCallback(
            self.neogithub, MessageBox, message, MessageBox.TYPE_YESNO)
        ybox.setTitle(_('Install.'))

    def neogithub(self, answer):
        if fileExists('/.multinfo'):
            self.myClose(
                _('Sorry, Neoboot can be installed or upgraded only when booted from Flash'))
            self.close()
        else:
            if answer is True:
                os.system('touch /tmp/.upneo; rm -r /tmp/.*')
                # Converted concatenation to f-string
                if fileExists(f'{LinkNeoBoot}/.location'):
                    # Converted concatenation to f-string
                    system(f'rm -f {LinkNeoBoot}/.location')
                if fileExists('/usr/bin/curl'):
                    cmd1 = 'rm -f /usr/lib/periodon/.kodn; curl -kLs https://raw.githubusercontent.com/gutosie/neoboot/master/iNB.sh|sh'
                    self.session.open(Console, _('NeoBoot....'), [cmd1])
                    self.close()
                elif fileExists('/usr/bin/wget'):
                    cmd1 = 'rm -f /usr/lib/periodon/.kodn; cd /tmp; rm ./*.sh; wget --no-check-certificate https://raw.githubusercontent.com/gutosie/neoboot/master/iNB.sh;chmod 755 ./iNB.sh;sh ./iNB.sh; rm ./iNB.sh; cd /'
                    self.session.open(Console, _('NeoBoot....'), [cmd1])
                    self.close()
                elif fileExists('/usr/bin/fullwget'):
                    cmd1 = 'rm -f /usr/lib/periodon/.kodn; cd /tmp; rm ./*.sh; fullwget --no-check-certificate https://raw.githubusercontent.com/gutosie/neoboot/master/iNB.sh;chmod 755 ./iNB.sh;sh ./iNB.sh; rm ./iNB.sh; cd /'
                    self.session.open(Console, _('NeoBoot....'), [cmd1])
                    self.close()
                else:
                    pass
            else:
                self.close()

    def delete(self):
        message = _('Are you sure you want to completely remove NeoBoota of your image?\n\nIf you choose so all directories NeoBoota will be removed.\nA restore the original image settings Flash.')
        ybox = self.session.openWithCallback(
            self.mbdelete, MessageBox, message, MessageBox.TYPE_YESNO)
        ybox.setTitle(_('Removed successfully.'))

    def mbdelete(self, answer):
        if answer is True:
            for line in open("/etc/hostname"):
                if "dm500hd" not in line or "dm800" not in line or "dm800se" not in line or "dm8000" not in line:
                    os.system('touch /tmp/.upneo')
            if fileExists('/usr/lib/periodon/.activatedmac'):
                os.system(("rm -r /usr/lib/periodon  "))
            if fileExists('/etc/rcS.d/S99neo.local'):
                system('rm -r /etc/rcS.d/S99neo.local')
            if fileExists('/etc/name'):
                system('rm -r /etc/name')
            if fileExists('/usr/lib/libpngneo'):
                system('rm -r /usr/lib/libpngneo')
            if fileExists('/etc/fstab.org'):
                system('rm -r /etc/fstab; mv /etc/fstab.org /etc/fstab')
            if fileExists('/etc/init.d/volatile-media.sh.org'):
                system(' mv /etc/init.d/volatile-media.sh.org /etc/init.d/volatile-media.sh; rm -r /etc/init.d/volatile-media.sh.org; chmod 755 /etc/init.d/volatile-media.sh ')
            # Converted to f-string
            if os.path.isfile(f'{getNeoLocation()}ImageBoot/.neonextboot'):
                # Converted to f-string
                os.system(
                    f'rm -f /etc/neoimage; rm -f /etc/imageboot; rm -f {getNeoLocation()}ImageBoot/.neonextboot; rm -f {getNeoLocation()}ImageBoot/.version; rm -f {getNeoLocation()}ImageBoot/.Flash; ')
            # Converted to f-string
            if os.path.isfile(f'{getNeoLocation()}ImagesUpload/.kernel '):
                # Converted to f-string
                os.system(f'rm -r {getNeoLocation()}ImagesUpload/.kernel')
            # Converted to f-string
            cmd = f"echo -e '\\n\\n{_('Recovering setting....\n')} '"
            # Converted concatenation to f-string
            cmd1 = f'rm -R {LinkNeoBoot}'
            cmd2 = 'rm -R /sbin/neoinit*'
            cmd3 = 'ln -sfn /sbin/init.sysvinit /sbin/init'
            cmd4 = 'rm -rf /usr/lib/enigma2/python/Tools/Testinout.p*'
            cmd5 = 'rm -rf /usr/lib/periodon'
            cmd6 = 'opkg install --force-maintainer --force-reinstall --force-overwrite --force-downgrade volatile-media; sleep 10; PATH=/sbin:/bin:/usr/sbin:/usr/bin; echo -n "Rebooting... "; reboot -d -f'
            self.session.open(
                Console, _('NeoBot was removed !!! \nThe changes will be visible only after complete restart of the receiver.'), [
                    cmd, cmd1, cmd2, cmd3, cmd4, cmd5, cmd6])
            self.close()
        else:
            self.close()

    def myClose(self, message):
        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        self.close()


class ReinstallKernel(Screen):
    __module__ = __name__

    skin = """<screen name="ReinstallKernel" title="Module kernel" position="center,center" size="700,300" >
    <widget name="lab1" position="20,20" size="660,210" font="baslk;25" halign="center" valign="center" transparent="1"/>
    <ePixmap position="210,250" size="34,34" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NeoBoot/images/red.png" alphatest="blend" zPosition="1" />
    <widget name="key_red" position="250,250" zPosition="2" size="280,40" font="baslk;30" halign="left" valign="center" backgroundColor="red" transparent="1" />
    </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(_('Re-installing the kernel. \n\nInstall?'))
        self['key_red'] = Label(_('Installation'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {
                                     'back': self.close, 'red': self.InfoCheck})

    def InfoCheck(self):
        if fileExists('/.multinfo'):
            if getCPUtype() == 'MIPS':
                # Converted concatenation to f-string
                if not fileExists(f'/boot/{getBoxHostName()}.vmlinux.gz'):
                    mess = _('Update available only from the image Flash.')
                    self.session.open(MessageBox, mess, MessageBox.TYPE_INFO)
                else:
                    self.kernel_update()

            elif getCPUtype() == 'ARMv7':
                # Converted concatenation to f-string
                if not fileExists(f'/boot/zImage.{getBoxHostName()}'):
                    mess = _('Update available only from the image Flash.')
                    self.session.open(MessageBox, mess, MessageBox.TYPE_INFO)
                else:
                    self.kernel_update()

        else:
            self.kernel_update()

    def kernel_update(self):
        if not fileCheck(f'{LinkNeoBoot}/.location'): # Converted concatenation to f-string
            pass
        else:
            # Converted concatenation to f-string
            os.system(f'echo "Flash "  > {getNeoLocation()}ImageBoot/.neonextboot')
            # Used 'with open' for proper file closing
            with open(f'{getNeoLocation()}ImagesUpload/.kernel/used_flash_kernel', 'w') as out:
                out.write('Used Kernel:  Flash')
        cmd1 = 'rm -f /home/root/*.ipk; opkg download kernel-image; sleep 2; opkg install --force-maintainer --force-reinstall --force-overwrite --force-downgrade /home/root/*.ipk; opkg configure update-modules; rm -f /home/root/*.ipk'
        self.session.open(Console, _('NeoBoot....'), [cmd1])
        self.close()


class neoDONATION(Screen):
    if isFHD():
        skin = """<screen position="center,center" size="1820,840" title="NeoBoot - INFORMATION">
        <widget name="lab1" position="57,5" size="1780,913" font="tasat;25" backgroundColor="black" transparent="1" />
        </screen>"""
    else:
        skin = """<screen position="center,center" size="1180,620" title="NeoBoot - INFORMATION">
        <widget name="lab1" position="18,19" size="1249,615" font="baslk;20" backgroundColor="black" transparent="1" />
        </screen>"""

    __module__ = __name__

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = ScrollLabel('')
        self['actions'] = ActionMap(['WizardActions',
                                     'ColorActions',
                                     'DirectionActions'],
                                    {'back': self.close,
                                     'ok': self.close,
                                     'up': self['lab1'].pageUp,
                                     'left': self['lab1'].pageUp,
                                     'down': self['lab1'].pageDown,
                                     'right': self['lab1'].pageDown})
        self['lab1'].hide()
        self.updatetext()

    def updatetext(self):
        # Converted concatenation to f-string
        message = _(f'NeoBoot Ver. {PLUGINVERSION}  Enigma2\n')
        # Converted concatenation to f-string
        message += _(f'NeoBoot Ver. updates {UPDATEVERSION}  \n\n')
        message += _('If you want to support the neoboot project, you can do so by contacting us by e-mail:\n')
        message += _(' krzysztofgutosie@gmail.com\n\n')
        message += _(' PayPal adress:  krzysztofgutosie@gmail.com\n')
        # Converted concatenation to f-string
        message += _(f' {getBoxHostName()} Ethernet MAC:  {getBoxMacAddres()}\n')
        message += _('----------------Free donate----------------\n')
        message += _('Spendenbetrag\nDonaco\nDarowizna\nПожертвование\n')
        message += _('Donate to the project\n')
        message += _('- Access to the latest version\n')
        message += _('- Online support\n')
        message += _('- More information email\n')
        message += _('We thank you for any help\n')
        message += _('----------------Free donate----------------\n')
        message += _('¯\\_(ツ)_/¯ Have fun !!!')
        self['lab1'].show()
        self['lab1'].setText(message)


def myboot(session, **kwargs):
    session.open(MBTools)


def Plugins(path, **kwargs):
    global pluginpath
    pluginpath = path
    return PluginDescriptor(
        name='NeoBoot',
        description='MENU NeoBoot',
        icon=None,
        where=PluginDescriptor.WHERE_PLUGINMENU,
        fnc=myboot)