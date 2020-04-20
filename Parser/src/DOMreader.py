from xml.dom.minidom import parse
import xml.dom.minidom as dom
from zipfile import ZipFile
import shutil

def extractKMZ(file, dest):
    with ZipFile(file, 'r') as zf:
        zf.extractall(dest)

extractKMZ('test.kmz', './file1')
extractKMZ('kmz2test.kmz', './file2')

# parse "original" xml document
originalDataStruct = dom.parse('./file1/doc.kml')
docRootOriginal = originalDataStruct.documentElement
places1 = docRootOriginal.getElementsByTagName("Placemark")

# parse secondary document
DOMTree2 = dom.parse('./file2/doc.kml')
docRootNew = DOMTree2.documentElement
places2 = docRootNew.getElementsByTagName("Placemark")


name_conflict_count = 0
desc_conflict_count = 0
test_name = ""

for new_place in places2:
    append_flag = True     # if not set to false, append the new_place to the import folder
    desc_update = False
    test_name = new_place.getElementsByTagName("name")[0].firstChild.data
    test_description = new_place.getElementsByTagName("description")[0].firstChild.data
    test_coordinates_string = new_place.getElementsByTagName("coordinates")[0].firstChild.data

    for old_place in places1:
        original_name = old_place.getElementsByTagName("name")[0].firstChild.data
        original_description = old_place.getElementsByTagName("description")[0].firstChild.data
        original_coordinates_string = old_place.getElementsByTagName("coordinates")[0].firstChild.data

        #print("{} == {} ?". format(test_name.firstChild.data, original_name.firstChild.data))

        # found the same entry name in the old one, so we can skip it from appending
        if str(test_name).lower() == str(original_name).lower():
            append_flag = False
            if test_description != original_description:
                desc_update = True
                #TODO prompt the user dialog (up the callstack)
                print("Non-matching description for element: {}".format(original_name))
                print("Original: {}".format(original_description))
                print("New: {}".format(test_description))
                #TODO update the old entry with the new description

    if append_flag:
        folder = docRootOriginal.getElementsByTagName("Folder")
        folderExists = False
        for name in folder:
            if name.getElementsByTagName("name")[0].firstChild.data == "Import":
                folderExists = True

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

            docRootOriginal.appendChild(import_folder)


print(originalDataStruct.toprettyxml())

            




