import xml.dom.minidom as dom
from zipfile import ZipFile
import os
import shutil
import pathlib

"""
@author Sawyer Timperley
@date   2020-04-20
@title  KML Transforming Module With File IO
"""

# TODO (someday) upgrade to XSLT (it's faster, has support for namespaces, and formats correctly)
class DOMTransformer:
    def __init__(self, inputKMZtemplate, inputKMZcompare, outputKMZdir="./processed/out.kmz", tempDir="./tmp"):
        # user variables
        self.inputTemplate = inputKMZtemplate
        self.inputCompare = inputKMZcompare
        self.outputPath = outputKMZdir
        self.workingDir = tempDir

        self.TEMPLATE_WORKING_PATH = self.workingDir + '/templatetmp'
        self.COMPARE_WORKING_PATH = self.workingDir + '/comparetmp'
        self.OUTPUT_WORKING_PATH = self.workingDir + '/outtmp'

        # counter variables
        self.xmlData = ""
        self.conflictCount = 0

    # unzip the kmz file to the temp directory, retaining the zip folder structure
    def extractKMZ(self, file, dest):
        with ZipFile(file, 'r') as zf:
            zf.extractall(dest)

    # setup the temporary working directories
    # TODO make this work without unnecessary disk usage
    def setupWorkingDir(self):
        self.extractKMZ(self.inputTemplate, self.TEMPLATE_WORKING_PATH)
        self.extractKMZ(self.inputCompare, self.COMPARE_WORKING_PATH)

    # does not run automatically, as one can reconfigure the object using the accessors
    def process(self):
        self.conflictCount = 0
        self.setupWorkingDir()

        # parse template xml document
        originalDataStruct = dom.parse('{}/doc.kml'.format(self.TEMPLATE_WORKING_PATH))
        docRootOriginal = originalDataStruct.documentElement
        templatePlaces = docRootOriginal.getElementsByTagName("Placemark")

        # parse secondary document
        newDataStruct = dom.parse('{}/doc.kml'.format(self.COMPARE_WORKING_PATH))
        docRootNew = newDataStruct.documentElement
        comparePlaces = docRootNew.getElementsByTagName("Placemark")

        # O(n^2), ouch. However, there is no easy way to sort the data based on this scope.
        for new_place in comparePlaces:
            append_flag = True  # if not set to false, append the new_place to the import folder
            test_name = new_place.getElementsByTagName("name")[0].firstChild.data

            for old_place in templatePlaces:
                original_name = old_place.getElementsByTagName("name")[0].firstChild.data
                # found the same entry name in the original, so we can skip it from appending
                if str(test_name).lower() == str(original_name).lower():
                    append_flag = False
                    break

            if append_flag:
                self.conflictCount += 1  # Used in later documentation
                folder = docRootOriginal.getElementsByTagName("Folder")  # Look in all custom places folder struct
                folderExists = False
                folder_pointer = ""  # The import folder pointer
                for name in folder:
                    if name.getElementsByTagName("name")[0].firstChild.data == "Import":
                        folderExists = True
                        folder_pointer = name

                # create new xml folder entry if one does not exist
                if not folderExists:
                    import_folder = originalDataStruct.createElement("Folder")

                    # code block that builds the xml tree
                    folder_name = originalDataStruct.createElement("name")
                    folder_name.appendChild(originalDataStruct.createTextNode("Import"))
                    folder_open = originalDataStruct.createElement("open")
                    folder_open.appendChild(originalDataStruct.createTextNode("1"))
                    folder_desc = originalDataStruct.createElement("description")
                    folder_desc.appendChild(originalDataStruct.createTextNode("Imported from synchronization tool"))
                    import_folder.appendChild(folder_name)
                    import_folder.appendChild(folder_open)
                    import_folder.appendChild(folder_desc)

                    doc_root = originalDataStruct.getElementsByTagName("Document")[0]
                    doc_root.appendChild(import_folder)
                    folder_pointer = import_folder

                # like setting up a window panel, place the tree structure in the root
                folder_pointer.appendChild(new_place)

        # save the raw xml data to memory, waiting to be written to.
        self.xmlData = originalDataStruct.toxml()

    # write the preprocessed xml to disk
    def writeOut(self, clean=True):
        os.makedirs(self.OUTPUT_WORKING_PATH, exist_ok=True)
        output_file = open("{}/doc.kml".format(self.OUTPUT_WORKING_PATH), "w")
        output_file.write(self.xmlData)
        output_file.close()

        os.makedirs(os.path.dirname(self.outputPath), exist_ok=True)
        output_zip = ZipFile(self.outputPath, 'w')
        output_zip.write("{}/doc.kml".format(self.OUTPUT_WORKING_PATH), "doc.kml")
        if os.path.isdir("{}/files".format(self.TEMPLATE_WORKING_PATH)):
            output_zip.write("{}/files".format(self.TEMPLATE_WORKING_PATH))
        output_zip.close()

        if clean:
            self.cleanWorkingDirectories()

    def cleanWorkingDirectories(self):
        shutil.rmtree(self.workingDir)

    # get the amount of additions after the last process() call
    def getAppendCount(self):
        return self.conflictCount

    # class accessors (may remove if not used later)
    def getTemplateKMZPath(self):
        return self.inputTemplate

    def getCompareKMZPath(self):
        return self.inputCompare

    def getOutputKMZPath(self):
        return pathlib.Path(self.outputPath).absolute()

    def setTemplateKMZ(self, path):
        self.inputTemplate = path

    def setCompareKMZPath(self, path):
        self.inputCompare = path

    def setOutputKMZ(self, path):
        self.outputPath = path