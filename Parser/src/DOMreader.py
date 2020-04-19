from xml.dom.minidom import parse
import xml.dom.minidom as dom
from zipfile import ZipFile

filename = 'test.kmz'

kmz = ZipFile(filename, 'r')
kml = kmz.open('doc.kml', 'r')

DOMTree = dom.parse(kml)
collection = DOMTree.documentElement

places = collection.getElementsByTagName("Placemark")

for place in places:
    print("-------Place-------")
    name = place.getElementsByTagName("name")[0].firstChild.data
    description = place.getElementsByTagName("description")[0].firstChild.data
    print("Name: {}".format(name))
    print("Description: {}".format(description))

