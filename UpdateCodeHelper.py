
import os
import sys
import filecmp
from os.path import isdir, join

COMPARE_TEMP_LIST1 = "1.txt"
COMPARE_TEMP_LIST2 = "2.txt"
RESULT_FILE = "Result.txt"

COMPARE_ROOT_PATH_1 = "COMPARE_ROOT_PATH1"
COMPARE_ROOT_PATH_2 = "COMPARE_ROOT_PATH2"
NORMAL_COMPARE_RULE = 'COMPARE_NORMAL_RULE'
EXIST_COMPARE_RULE  = 'COMPARE_EXIST_ONLY_RULE'
CHST_OVERRIDE_COMPARE_RULE = 'COMPARE_CHST_OVERRIDE_RULE'
ROOT_COMPARE_RULE   = 'COMPARE_ROOT_RULE'

DEBUG_MODE = 1
gConfigFile = ''
gCmpRootPath1 = ''
gCmpRootPath2 = ''
gCompareRule  = ''

#=========================================
#    Get configure file setting.
#=========================================
def GetConfigSetting ():
  global gConfigFile
  global gCmpRootPath1
  global gCmpRootPath2

  if len(sys.argv) != 2:
    print ("Usage: UpdateCodeHelper.exe CompareConfig.txt\n")
    sys.exit (1)

  gConfigFile = sys.argv [1]

  try:
    if DEBUG_MODE == 1:
      print ("\n<GetConfigSetting>")

    ConfigFileBuf = open (gConfigFile).readlines ()

    for Line in ConfigFileBuf:

      if Line.find (COMPARE_ROOT_PATH_1) != -1:
        Line = Line.replace (' ', '')
        Line = Line.replace ('\n', '')
        gCmpRootPath1 = Line.split ('=') [1]

      elif Line.find (COMPARE_ROOT_PATH_2) != -1:
        Line = Line.replace (' ', '')
        Line = Line.replace ('\n', '')
        gCmpRootPath2 = Line.split ('=') [1]
    #endof for line in ConfigFileBuf:

    if DEBUG_MODE == 1:
      print ("  gCmpRootPath1 = " + str (gCmpRootPath1))
      print ("  gCmpRootPath2 = " + str (gCmpRootPath2))

  except:
    print ("  GetConfigSetting error! Can't open CompareConfig file!!!")
    sys.exit (1)
#endof GetConfigSetting ():

#============================================
#    Return argument file list data buffer.
#============================================
def GetFileListBuf (FolderPath):
  FileListBuffer = ''

  for root, dirs, files in os.walk (FolderPath):
    # skip .svn folder.
    if root [len(root) - 4 :] == '.svn':
      continue

    if files != '':
      for fileName in files:
        # skip svn files.
        if (len (fileName) > 9 and fileName [len(fileName) - 9 :] == ".svn-base"):
          continue

        FileListBuffer = FileListBuffer + os.path.join (root, fileName) + "\n"

  return FileListBuffer
#endof GetFileListBuf ():

#============================================
#    Create file by arguments.
#============================================
def CreateFile (FilePath, FileBuffer):
  try:
    if FileBuffer == '':
      print ("  CreateFile buffer is null!!!")
      sys.exit (1)

    OutputFile = open (FilePath, mode = 'wb')
    OutputFile.write (FileBuffer)
    OutputFile.close ()

  except:
    print ("  CreateFile error!!!")
    print ("  FilePath = " + FilePath)
    sys.exit (1)
#endof CreateFile (FilePath, FileBuffer):

#=========================================
#    Create files lists to a txt file.
#=========================================
def CreateListFile (Line):

  global gCompareRule
  CompareRuleString = ''

  if Line.find (ROOT_COMPARE_RULE) != -1:
    FirstPath = Line.split ('=') [1]
    SecondPath = "Root"
    CompletePath1 = gCmpRootPath1 + FirstPath
    CompletePath2 = gCmpRootPath2
    gCompareRule = ROOT_COMPARE_RULE
    CompareRuleString = "ROOT_COMPARE_RULE"
  else:
    if Line.find (NORMAL_COMPARE_RULE) != -1:
      gCompareRule = NORMAL_COMPARE_RULE
      CompareRuleString = "NORMAL_COMPARE_RULE"
    elif Line.find (EXIST_COMPARE_RULE) != -1:
      gCompareRule = EXIST_COMPARE_RULE
      CompareRuleString = "COMPARE_EXIST_ONLY_RULE"
    elif Line.find (CHST_OVERRIDE_COMPARE_RULE) != -1:
      gCompareRule = CHST_OVERRIDE_COMPARE_RULE
      CompareRuleString = "COMPARE_CHST_OVERRIDE_RULE"
    else:
      return "Others"

    TempPath = Line.split ('=') [1]
    FirstPath = TempPath.split (';') [0]
    SecondPath = TempPath.split (';') [1]
    CompletePath1 = gCmpRootPath1 + FirstPath
    CompletePath2 = gCmpRootPath2 + SecondPath

  if DEBUG_MODE == 1:
    print ("\n<CreateListFile>")
    print ("  Compare Rule = " + CompareRuleString)
    print ("  Complete path 1 = " + CompletePath1)
    print ("  Complete path 2 = " + CompletePath2)
    print ("  FirstPath  = " + FirstPath)
    print ("  SecondPath = " + SecondPath)
    print ("  Now is creating list files, please wait...")

  #gen path 1 file list.
  DataBuffer = ''
  DataBuffer = GetFileListBuf (CompletePath1)
  CreateFile (COMPARE_TEMP_LIST1, DataBuffer)

  #gen path 1 file list.
  DataBuffer = ''
  DataBuffer = GetFileListBuf (CompletePath2)
  CreateFile (COMPARE_TEMP_LIST2, DataBuffer)

  if DEBUG_MODE == 1:
    print ("  Create file lists success!!!")

  return FirstPath,SecondPath
#endof CreateListFile ():

#============================================
#    Compare by argument file lists.
#============================================
def CompareByFileList (ListFile1, SubPath1, ListFile2, SubPath2):
  try:
    global gCompareRule
    FileFind = 0
    UnderlineFileFromFirst  = 0
    OutputBuffer = ''
    FirstListFile = ''
    SecondListFile = ''
    FirstSubPath = ''
    SecondSubPath = ''

    if gCompareRule == NORMAL_COMPARE_RULE:
      FirstRootPath  = gCmpRootPath2
      SecondRootPath = gCmpRootPath1
      FirstListFile  = ListFile2
      SecondListFile = ListFile1
      FirstSubPath  = SubPath2
      SecondSubPath = SubPath1
    elif gCompareRule == EXIST_COMPARE_RULE or gCompareRule == CHST_OVERRIDE_COMPARE_RULE or gCompareRule == ROOT_COMPARE_RULE:
      FirstRootPath  = gCmpRootPath1
      SecondRootPath = gCmpRootPath2
      FirstListFile  = ListFile1
      SecondListFile = ListFile2
      FirstSubPath  = SubPath1
      SecondSubPath = SubPath2
    else:
      print ("CompareByFileList error, compare rule is invalid!!!")
      sys.exit (1)

    if DEBUG_MODE == 1:
      print ("  First list file to compare  = " + FirstListFile)
      print ("  Second list file to compare = " + SecondListFile)
      print ("  First sub path to compare  = " + FirstSubPath)
      print ("  Second sub path to compare = " + SecondSubPath)
      os.system("pause")

    TargetFileBuffer = open (FirstListFile).readlines ()
    for TargetFilePath in TargetFileBuffer:
      FileFind = 0
      TargetFilePath = TargetFilePath.replace ('\n', '')

      #restore override flag if override file exist and flag was set by previous item.
      if UnderlineFileFromFirst == 1 and TargetFilePath [len (TargetFilePath) - 1] == '_':
        UnderlineFileFromFirst = 0
        continue

      #get target file name.
      RootPathSize = len (FirstRootPath) + len (FirstSubPath) + 1
      TargetFile = TargetFilePath [RootPathSize : ]

      #check underline file exist?
      for CheckOverrideLine in TargetFileBuffer:
        if CheckOverrideLine.find (TargetFile + '_') != -1:
          TargetFilePath = TargetFilePath + '_'
          UnderlineFileFromFirst = 1
          break

      #check original file exist?
      if gCompareRule == ROOT_COMPARE_RULE:
        OriginFilePath = SecondRootPath + TargetFile
      else:
        OriginFilePath = SecondRootPath + SecondSubPath + '\\' + TargetFile

      print ("OriginFilePath="+OriginFilePath)
      OriginFile = open (SecondListFile).read ()
      if OriginFile.find (OriginFilePath + '_') != -1:
        FileFind = 1
        OriginFilePath = OriginFilePath + '_'
      elif OriginFile.find (OriginFilePath) != -1:
        FileFind = 1

      if FileFind == 1:
        print ("Compare")
        print ("  " + TargetFilePath)
        print ("  " + OriginFilePath)
#          os.system("pause")
        if filecmp.cmp (TargetFilePath, OriginFilePath) != True:
          OutputBuffer = OutputBuffer + "Different      -" + TargetFilePath + "\n               -" + OriginFilePath + "\n"

      else:
        if gCompareRule == NORMAL_COMPARE_RULE:
          OutputBuffer = OutputBuffer + "File not exit  -" + TargetFilePath + "\n"

    return OutputBuffer

  except:
    print ("CompareByFileList error!!!")
    sys.exit (1)
#endof CompareByFileList (List1, List2):

#============================================
#    Compare main function.
#============================================
def StartCompare ():
  try:
    if gCmpRootPath1 == '' or gCmpRootPath2 == '':
      print ("Compare root path not find.")
      sys.exit (1)

    CompareResult = ''

    if DEBUG_MODE == 1:
      print ("\n<StartCompare>")

    ConfigFileBuf = open (gConfigFile).readlines ()
    for Line in ConfigFileBuf:
      #remove space and end of line symbol
      Line = Line.replace (' ', '')
      Line = Line.replace ('    ', '')
      Line = Line.replace ('\n', '')

      CreateListPath = CreateListFile (Line)

      if CreateListPath == "Others":
        continue
      else:
        FirstPath = CreateListPath [0]
        SecondPath = CreateListPath [1]

      NewResult = CompareByFileList (COMPARE_TEMP_LIST1, FirstPath, COMPARE_TEMP_LIST2, SecondPath)
      CompareResult = CompareResult + NewResult

    if CompareResult != '':
      CreateFile (RESULT_FILE, CompareResult)
#      print (CompareResult)
    else:
      print ("These file is totally same!!!")
    #endof for Line in ConfigFileBuf

  except:
    print ("CompareFolder error!!!")
    sys.exit (1)
#endof CompareFolder ():


if __name__ == '__main__':
  #check argument and config file setting.
  GetConfigSetting ()

  #start compare.
  StartCompare ()
  print ("\nUpdateCodeHelper complete!!!")
