import xml.dom.minidom as dom
from zipfile import ZipFile
import os
import shutil


class DOMReader:
    def __init__(self, inputKMZtemplate, inputKMZcompare, outputKMZdir, tempDir="./tmp"):
        self.inputTemplate = inputKMZtemplate
        self.inputCompare = inputKMZcompare
        self.outputPath = outputKMZdir
        self.workingDir = tempDir

        self.TEMPLATE_WORKING_PATH = self.workingDir + '/templatetmp'
        self.COMPARE_WORKING_PATH = self.workingDir + '/comparetmp'
        self.OUTPUT_WORKING_PATH = self.workingDir + '/outtmp'

        self.xmlData = ""

        self.conflictCount = 0

    def extractKMZ(self, file, dest):
        with ZipFile(file, 'r') as zf:
            zf.extractall(dest)

    def setupWorkingDir(self):
        self.extractKMZ(self.inputTemplate, self.TEMPLATE_WORKING_PATH)
        self.extractKMZ(self.inputCompare, self.COMPARE_WORKING_PATH)

    def process(self):
        self.conflictCount = 0
        self.setupWorkingDir()
        # parse "original" xml document
        originalDataStruct = dom.parse('{}/doc.kml'.format(self.TEMPLATE_WORKING_PATH))
        docRootOriginal = originalDataStruct.documentElement
        templatePlaces = docRootOriginal.getElementsByTagName("Placemark")

        # parse secondary document
        newDataStruct = dom.parse('{}/doc.kml'.format(self.COMPARE_WORKING_PATH))
        docRootNew = newDataStruct.documentElement
        comparePlaces = docRootNew.getElementsByTagName("Placemark")

        for new_place in comparePlaces:
            append_flag = True  # if not set to false, append the new_place to the import folder
            test_name = new_place.getElementsByTagName("name")[0].firstChild.data

            for old_place in templatePlaces:
                original_name = old_place.getElementsByTagName("name")[0].firstChild.data

                # found the same entry name in the old one, so we can skip it from appending
                if str(test_name).lower() == str(original_name).lower():
                    append_flag = False
                    break

            if append_flag:
                self.conflictCount += 1
                folder = docRootOriginal.getElementsByTagName("Folder")
                folderExists = False
                folder_pointer = ""
                for name in folder:
                    if name.getElementsByTagName("name")[0].firstChild.data == "Import":
                        folderExists = True
                        folder_pointer = name

                if not folderExists:
                    import_folder = originalDataStruct.createElement("Folder")

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

                # now append that sucker to the import folder!
                folder_pointer.appendChild(new_place)

        self.xmlData = originalDataStruct.toxml()

    def writeOut(self):
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

    def cleanWorkingDirectories(self):
        shutil.rmtree(self.workingDir)

    # get the amount of additions after the last process() call
    def getAppendCount(self):
        return self.conflictCount
