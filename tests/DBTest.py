from kmlmodules.dbconnect import DBConnect
from datetime import datetime

db = DBConnect("data.db", "D:\Libraries\Google Drive\projects\code\python\kml-sync-tool\history")

db.insert_history("bobbin", datetime.now(), "kmzin1.kmz", "kmzin2.kmz", "kmzout.kmz", 115)