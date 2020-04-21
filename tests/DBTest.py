from kmlmodules.dbconnect import DBConnect

db_interpreter = DBConnect("D:\Libraries\Google Drive\projects\code\python\kml-sync-tool\history")
db_interpreter.createTables()
db_interpreter.insert_test("bob")
db_interpreter.insert_test("joe")
db_interpreter.insert_test("bob")