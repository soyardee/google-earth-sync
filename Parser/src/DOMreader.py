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
DOMTree1 = dom.parse('./file1/doc.kml')
collection1 = DOMTree1.documentElement
places1 = collection1.getElementsByTagName("Placemark")

# parse secondary document
DOMTree2 = dom.parse('./file2/doc.kml')
collection2 = DOMTree2.documentElement
places2 = collection2.getElementsByTagName("Placemark")


name_conflict_count = 0
desc_conflict_count = 0
test_name = ""
for new_place in places2:
    test_name = new_place.getElementsByTagName("name")[0]
    test_description = new_place.getElementsByTagName("description")[0]
    test_coordinates_string = new_place.getElementsByTagName("coordinates")[0]


    for old_place in places1:
        original_name = old_place.getElementsByTagName("name")[0]
        original_description = old_place.getElementsByTagName("description")[0]
        original_coordinates_string = old_place.getElementsByTagName("coordinates")[0]

        print("{} == {} ?". format(test_name.firstChild.data, original_name.firstChild.data))

            




