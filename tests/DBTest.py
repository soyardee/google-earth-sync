from modules.dbconnect import DBConnect

db = DBConnect("data.db", "D:\Libraries\Google Drive\projects\code\python\kml-sync-tool\history")

db.insert_history("george", 200, "in1.kmz", "in2.kmz", "out.kmz")

rows = db.get_history_rows()
for r in rows:
    print(r)