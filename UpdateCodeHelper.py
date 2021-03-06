
import os
import sys
import filecmp
from os.path import isdir, join
from shutil import copyfile

COMPARE_TEMP_LIST1 = "1.txt"
COMPARE_TEMP_LIST2 = "2.txt"
RESULT_FILE = "Result.txt"
OUTPUT_SOLUTION_PATH = 'New\\'

OUTPUT_DIFFERENT_LABEL = 'Different      -'
OUTPUT_FILE_NOT_EXIST_LABEL = "File not exist -"

FEATURE_ROOT_PATH = "FEATURE_ROOT_PATH"
CHIPSET_ROOT_PATH = "CHIPSET_ROOT_PATH"
FEATURE_BOARD_PACKAGE_NAME = "FEATURE_BOARD_PACKAGE"
CHIPSET_BOARD_PACKAGE_NAME = "CHIPSET_BOARD_PACKAGE"
CHIPSET_PACKAGE_NAME = "CHIPSET_PACKAGE"

#
#  Verify rules are below.
#  1. Check feature board package with new chipset board package.
#  2. Check feature board package Include folder with chipset Include folder for Header file override.
#  3. Check feature board package Include folder with kernel Include folder for Header file override.
#  4. Check feature platform package with chipset root path and chipset package override folder.
#
#  COMPARE_NORMAL_RULE     = H19ApolloLakeBoardPkg;         ApolloLakeBoardPkg
#  COMPARE_EXIST_ONLY_RULE = H19ApolloLakeBoardPkg\Include; BroxtonChipsetPkg\Include
#  COMPARE_EXIST_ONLY_RULE = H19ApolloLakeBoardPkg\Include; InsydeModulePkg\Include
#  COMPARE_ROOT_RULE       = InsydeH19PlatformPkg;          BroxtonChipsetPkg\Override
RULE_COMPARE_BOARD_PACKAGE = "COMPARE_BOARD_PACKAGE"
RULE_COMPARE_CHIPSET_INCLUDE = "COMPARE_CHIPSET_INCLUDE"
RULE_COMPARE_KERNEL_INCLUDE = "COMPARE_KERNEL_INCLUDE"
RULE_COMPARE_FEATURE_PLATFORM_PACKAGE = "COMPARE_FEATURE_PLATFORM_PACKAGE"

COMPARE_BOARD_PACKAGE   = 0
COMPARE_CHIPSET_INCLUDE = 1
COMPARE_KERNEL_INCLUDE  = 2
COMPARE_FEATURE_PLATFORM_PACKAGE = 3
COMPARE_RULE_END = 4

gCompareRuleList = {COMPARE_BOARD_PACKAGE, COMPARE_CHIPSET_INCLUDE, COMPARE_KERNEL_INCLUDE, COMPARE_FEATURE_PLATFORM_PACKAGE, COMPARE_RULE_END}


gCmpFeatureRootPath = ''
gCmpChipsetRootPath = ''
gCmpFeatureBoardPkg = ''
gCmpChipsetBoardPkg = ''
gCmpChipsetPkg = ''
gCmpKernelPkg = "InsydeModulePkg"
gCmpFeaturePlatformPkg = "InsydeH19PlatformPkg"

DEBUG_MODE = 1
gConfigFile = ''

#=========================================
#    Get configure file setting.
#=========================================
def GetConfigSetting ():
  global gConfigFile
  global gCmpFeatureRootPath
  global gCmpChipsetRootPath
  global gCmpFeatureRootPath
  global gCmpChipsetRootPath
  global gCmpFeatureBoardPkg
  global gCmpChipsetBoardPkg
  global gCmpChipsetPkg

  if len(sys.argv) != 2:
    print ("Usage: UpdateCodeHelper.exe CompareConfig.txt\n")
    sys.exit (1)

  gConfigFile = sys.argv [1]

  try:
    if DEBUG_MODE == 1:
      print ("\n<GetConfigSetting>")

    ConfigFileBuf = open (gConfigFile).readlines ()

    for Line in ConfigFileBuf:

      Line = Line.replace (' ', '')
      Line = Line.replace ('\n', '')

      if Line.find ('=') != -1:
        try:
          EqualLeftOperator  = Line.split ('=') [0]
          EqualRightOperator = Line.split ('=') [1]
        except:
          print ("  GetConfigSetting error! Can't parser config data!!!")
          print ("  error data: " + Line)
          sys.exit (1)

        if EqualLeftOperator == FEATURE_ROOT_PATH:
          gCmpFeatureRootPath = EqualRightOperator

        elif EqualLeftOperator == CHIPSET_ROOT_PATH:
          gCmpChipsetRootPath = EqualRightOperator

        elif EqualLeftOperator == FEATURE_BOARD_PACKAGE_NAME:
          gCmpFeatureBoardPkg = EqualRightOperator

        elif EqualLeftOperator == CHIPSET_BOARD_PACKAGE_NAME:
          gCmpChipsetBoardPkg = EqualRightOperator

        elif EqualLeftOperator == CHIPSET_PACKAGE_NAME:
          gCmpChipsetPkg = EqualRightOperator
    #endof for line in ConfigFileBuf:

    if DEBUG_MODE == 1:
      print ("  FeatureRootPath = " + str (gCmpFeatureRootPath))
      print ("  ChipsetRootPath = " + str (gCmpChipsetRootPath))
      print ("  FeatureBoardPkg = " + str (gCmpFeatureBoardPkg))
      print ("  ChipsetBoardPkg = " + str (gCmpChipsetBoardPkg))
      print ("  KernelPkg       = " + str (gCmpKernelPkg))
      print ("  ChipsetPkg      = " + str (gCmpChipsetPkg))
#      os.system("pause")

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
def CreateListFile (CompareRule):

  CompareRuleString = ''
  ChipsetOverridePath = ''

  if CompareRule == COMPARE_BOARD_PACKAGE:
    FirstPath = gCmpFeatureBoardPkg
    SecondPath = gCmpChipsetBoardPkg

  elif CompareRule == COMPARE_CHIPSET_INCLUDE:
    FirstPath = gCmpFeatureBoardPkg + '\\Include'
    SecondPath = gCmpChipsetPkg + '\\Include'

  elif CompareRule == COMPARE_KERNEL_INCLUDE:
    FirstPath = gCmpFeatureBoardPkg + '\\Include'
    SecondPath = gCmpKernelPkg + '\\Include'

  elif CompareRule == COMPARE_FEATURE_PLATFORM_PACKAGE:
    FirstPath = gCmpFeaturePlatformPkg
    SecondPath = ''

  else:
    return "Others"

  CompletePath1 = gCmpFeatureRootPath + FirstPath
  CompletePath2 = gCmpChipsetRootPath + SecondPath

  if DEBUG_MODE == 1:
    print ("\n\n<CreateListFile>")
    print ("  Complete path 1 = " + CompletePath1)
    print ("  Complete path 2 = " + CompletePath2)
    print ("  FirstPath  = " + FirstPath)
    print ("  SecondPath = " + SecondPath)
    print ("  Now is creating file list, please wait...")

  #gen path 1 file list.
  DataBuffer = ''
  DataBuffer = GetFileListBuf (CompletePath1)
  CreateFile (COMPARE_TEMP_LIST1, DataBuffer)

  #gen path 2 file list.
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
def CompareByFileList (CompareRule, ListFile1, SubPath1, ListFile2, SubPath2):
  try:
    FileFind = 0
    UnderlineFileFromFirst  = 0
    OutputBuffer = ''
    FirstListFile = ''
    SecondListFile = ''
    FirstSubPath = ''
    SecondSubPath = ''

    if CompareRule == COMPARE_FEATURE_PLATFORM_PACKAGE:
      FirstRootPath  = gCmpFeatureRootPath
      SecondRootPath = gCmpChipsetRootPath
      FirstListFile  = ListFile1
      SecondListFile = ListFile2
      FirstSubPath  = SubPath1
      SecondSubPath = SubPath2
    else:
      FirstRootPath  = gCmpChipsetRootPath
      SecondRootPath = gCmpFeatureRootPath
      FirstListFile  = ListFile2
      SecondListFile = ListFile1
      FirstSubPath  = SubPath2
      SecondSubPath = SubPath1

    if DEBUG_MODE == 1:
      print ("  First list file to compare  = " + FirstListFile)
      print ("  Second list file to compare = " + SecondListFile)
      print ("  First sub path to compare  = " + FirstSubPath)
      print ("  Second sub path to compare = " + SecondSubPath)
      os.system("pause")

    if CompareRule == COMPARE_BOARD_PACKAGE:
      OutputBuffer = OutputBuffer + '\nCompareRule = ' + RULE_COMPARE_BOARD_PACKAGE + '\n'
    elif CompareRule == COMPARE_CHIPSET_INCLUDE:
      OutputBuffer = OutputBuffer + '\nCompareRule = ' + RULE_COMPARE_CHIPSET_INCLUDE + '\n'
    elif CompareRule == COMPARE_KERNEL_INCLUDE:
      OutputBuffer = OutputBuffer + '\nCompareRule = ' + RULE_COMPARE_KERNEL_INCLUDE + '\n'
    elif CompareRule == COMPARE_FEATURE_PLATFORM_PACKAGE:
      OutputBuffer = OutputBuffer + '\nCompareRule = ' + RULE_COMPARE_FEATURE_PLATFORM_PACKAGE + '\n'

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
      OriginFilePath = SecondRootPath + SecondSubPath + '\\' + TargetFile
      OriginFile = open (SecondListFile).read ()

      #check chipset pacakge override folder first.
      OriginFileOverridePath = ''
      if CompareRule == COMPARE_FEATURE_PLATFORM_PACKAGE:
        OriginFileOverridePath = SecondRootPath + gCmpChipsetPkg + "\\Override\\" + TargetFile
        print ("OriginFileOverridePath=" + OriginFileOverridePath)
        if OriginFile.find (OriginFileOverridePath + '_') != -1:
          FileFind = 1
          OriginFilePath = OriginFileOverridePath + '_'
        elif OriginFile.find (OriginFileOverridePath) != -1:
          FileFind = 1
          OriginFilePath = OriginFileOverridePath
        else:
          OriginFilePath = SecondRootPath + TargetFile

      if FileFind == 0:
        if OriginFile.find (OriginFilePath + '_') != -1:
          FileFind = 1
          OriginFilePath = OriginFilePath + '_'
        elif OriginFile.find (OriginFilePath) != -1:
          FileFind = 1

      print ("OriginFilePath=" + OriginFilePath)

      if FileFind == 1:
        print ("Compare")
        print ("  " + TargetFilePath)
        print ("  " + OriginFilePath)
#          os.system("pause")
        if filecmp.cmp (TargetFilePath, OriginFilePath) != True:
          OutputBuffer = OutputBuffer + OUTPUT_DIFFERENT_LABEL + TargetFilePath + "\n               -" + OriginFilePath + "\n"

      else:
        if CompareRule == COMPARE_BOARD_PACKAGE:
          OutputBuffer = OutputBuffer + OUTPUT_FILE_NOT_EXIST_LABEL + TargetFilePath + "\n"

    return OutputBuffer

  except:
    print ("CompareByFileList error!!!")
    sys.exit (1)
#endof CompareByFileList (List1, List2):


#===================================================
#    Output result data files to a small solution.
#===================================================
def GenerateSmallSolution (CompareResult):

  try:
    #get result file data buffer.
    print CompareResult

    print ("<GenerateSmallSolution>\n  Copy different file to a small version solution!!!\n")

    try:
      index = 0
      CompareRule = ''
      TotalCount = len (CompareResult.split ('\n'))

      while index < TotalCount - 1:
        LineData = CompareResult.split ('\n') [index]

        #get compare rule.
        if LineData [0:len ('CompareRule = ')] == 'CompareRule = ':
          CompareRule = LineData.split ("=") [1]
          CompareRule = CompareRule.replace ('\n', '').replace (' ', '')
#          print ('CompareRule=' + CompareRule)
          index = index + 1
          continue
        #endof if LineData [0:len ('CompareRule = ')] == 'CompareRule = ':

        #get Different string, start to copy data.
        if LineData [0:len (OUTPUT_DIFFERENT_LABEL)] == OUTPUT_DIFFERENT_LABEL:
          FilePath = ''
          FileName = ''

          #get target file path and file name.
          LineData = LineData [len (OUTPUT_DIFFERENT_LABEL):]

          if CompareRule == RULE_COMPARE_BOARD_PACKAGE: 
            sourceFile = CompareResult.split ('\n') [index]  [len (OUTPUT_DIFFERENT_LABEL):]
            destFile = CompareResult.split ('\n') [index + 1]
            destFile = destFile [len (OUTPUT_DIFFERENT_LABEL) + len (gCmpFeatureRootPath):]

          elif CompareRule == RULE_COMPARE_CHIPSET_INCLUDE or CompareRule == RULE_COMPARE_KERNEL_INCLUDE:
            sourceFile = CompareResult.split ('\n') [index]  [len (OUTPUT_DIFFERENT_LABEL):]
            destFile = CompareResult.split ('\n') [index + 1]
            destFile = destFile [len (OUTPUT_DIFFERENT_LABEL) + len (gCmpFeatureRootPath):]

          elif CompareRule == RULE_COMPARE_FEATURE_PLATFORM_PACKAGE:
            sourceFile = CompareResult.split ('\n') [index + 1]  [len (OUTPUT_DIFFERENT_LABEL):]
            destFile = CompareResult.split ('\n') [index]
            destFile = destFile [len (OUTPUT_DIFFERENT_LABEL) + len (gCmpFeatureRootPath):]

          DataLen = len (destFile)
          while DataLen > 0:
            if destFile [DataLen - 1] == '\\':
              #get file path.
              FilePath = destFile [0:DataLen]
              if FilePath.find (gCmpChipsetRootPath) != -1:
                FilePath = FilePath [len (gCmpChipsetRootPath) : ]
              elif FilePath.find (gCmpFeatureRootPath) != -1:
                FilePath = FilePath [len (gCmpFeatureRootPath) : ]
              FilePath = OUTPUT_SOLUTION_PATH + FilePath

              #get file name.
              FileName = destFile [DataLen:]
              break

            DataLen = DataLen - 1
          #end of while DataLen > 0:

          #copy different file to output folder.
          genFolderIndex = 0
          genFolderSubIndex = 0
          while genFolderIndex < len (FilePath) - 1:

            #create folder by each layer.
            while FilePath [genFolderSubIndex] != '\\':
              genFolderSubIndex = genFolderSubIndex + 1

            createFolderName = FilePath [:genFolderSubIndex]
            #print ('createFolderName='+createFolderName)

            try:
              os.stat (createFolderName)
            except:
              os.mkdir (createFolderName)

            genFolderIndex = genFolderSubIndex
            genFolderSubIndex = genFolderSubIndex + 1
          #end of while genFolderIndex > 0:

          destFile = os.getcwd () + '\\' + OUTPUT_SOLUTION_PATH + destFile

          try:
            print ('  Source File = ' + sourceFile + '\n  Destination File = ' + destFile + '\n')
            copyfile (sourceFile , destFile)
          except:
            print ('  Copy file fail!!!')
            print ('  Source File = ' + sourceFile + '\n  Destination File = ' + destFile)
            sys.exit (1)

        index = index + 1
      #endof if LineData [0:len (OUTPUT_DIFFERENT_LABEL)] == OUTPUT_DIFFERENT_LABEL:

    except:
      print (' ')

  except:
    print ("GenerateSmallSolution error!!!")
    sys.exit (1)
#endof GenerateSmallSolution ():


#============================================
#    Compare main function.
#============================================
def StartCompare ():
  try:
    if gCmpFeatureRootPath == '' or gCmpChipsetRootPath == '':
      print ("Compare root path not find.")
      sys.exit (1)

    CompareResult = ''

    if DEBUG_MODE == 1:
      print ("\n\n<StartCompare>")

    CompareRule = 0
    for CompareRule in gCompareRuleList:

      CreateListPath = CreateListFile (CompareRule)

      if CreateListPath == "Others":
        continue

      else:
        FirstPath = CreateListPath [0]
        SecondPath = CreateListPath [1]

      NewResult = CompareByFileList (CompareRule, COMPARE_TEMP_LIST1, FirstPath, COMPARE_TEMP_LIST2, SecondPath)
      CompareResult = CompareResult + NewResult

    if CompareResult != '':
      CreateFile (RESULT_FILE, CompareResult)
#      print (CompareResult)
    else:
      print ("These file is totally same!!!")
    #endof for Line in ConfigFileBuf

    # gen small version solution.
    GenerateSmallSolution (CompareResult)

  except:
    print ("CompareFolder error!!!")
    sys.exit (1)
#endof CompareFolder ():


if __name__ == '__main__':

  #check argument and config file setting.
  GetConfigSetting ()

  #start compare.
  StartCompare ()

  #remove list files.
  try:
    ListFileName = COMPARE_TEMP_LIST1
    os.remove (ListFileName)
    ListFileName = COMPARE_TEMP_LIST2
    os.remove (ListFileName)
  except:
    print ('Remove list file ' + ListFileName + 'fail!!!')

  print ("\nUpdateCodeHelper complete!!!")
