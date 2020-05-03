import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
from kmlmodules.dbconnect import DBConnect as DBConnect
from kmlmodules.domtransformer import DOMTransformer as xml
import os


class UserMain(ttk.Frame):
    def __init__(self, parent):
        # set up database object, stores all file processing history
        self.db = DBConnect("data.db", "./history")

        ttk.Frame.__init__(self, parent)

        UserFrame(self).grid(column=0, row=0)
        HistoryPanel(self, self.db).grid(column=0, row=1)

        self.pack()

class UserFrame(ttk.Frame):
    def __init__(self, parent):
        self.DIR_TEXT_SIZE = 50

        ttk.Frame.__init__(self, parent, padding="10 10 10 10")

        self.current_user = ""
        self.templatePath = ""
        self.copyPath = ""
        self.outputPath = ""
        self.conflictCount = 0


        ttk.Label(self, text="Original KMZ File:").grid(column=0, row=0, sticky=tk.W)
        self.templateFilePath = tk.StringVar()
        ttk.Entry(self, width=self.DIR_TEXT_SIZE, textvariable=self.templateFilePath).grid(column=0, row=1, sticky="ew")
        ttk.Button(self, width=10, text="Browse...", command=self.askopenfiletemplate).grid(column=1, row=1)

        ttk.Label(self, text="Comparison KMZ File:").grid(column=0, row=2, sticky=tk.W)
        self.copyFilePath = tk.StringVar()
        ttk.Entry(self, textvariable=self.copyFilePath).grid(column=0, row=3, sticky="ew")
        ttk.Button(self, width=10, text="Browse...", command=self.askopencopy).grid(column=1, row=3)

        ttk.Separator(self, orient="horizontal").grid(column=0, row=4, columnspan=3, sticky="ew", pady=10)

        ttk.Label(self, text="Output KMZ File:").grid(column=0, row=5, sticky=tk.W)
        self.outFilePath = tk.StringVar()
        ttk.Entry(self, textvariable=self.outFilePath).grid(column=0, row=6, sticky="ew")
        ttk.Button(self, width=10, text="Browse...", command=self.askopenoutputfile).grid(column=1, row=6)
        ttk.Label(self, text="User Name:").grid(column=0, row=8, sticky=tk.W)
        self.userNameEntry = tk.StringVar()
        ttk.Entry(self, textvariable=self.userNameEntry).grid(column=0, row=9, sticky=tk.W)

        ttk.Button(self, text="Convert", width=10, command=self.processXML).grid(column=1, row=9)

        ttk.Separator(self, orient="horizontal").grid(column=0, row=10, columnspan=3, sticky="ew", pady=10)

        ttk.Label(self, text="History").grid(column=0, row=11, sticky="w")

        self.pack()


    def askopenfiletemplate(self):
        path = filedialog.askopenfilename(initialdir= "../", title="Select template file", filetypes=(("kmz files", "*.kmz"),))
        self.templatePath = path
        self.templateFilePath.set(self.templatePath)
        return

    def askopencopy(self):
        path = filedialog.askopenfilename(initialdir= "../", title="Select comparison file", filetypes=(("kmz files", "*.kmz"),))
        self.copyPath = path
        self.copyFilePath.set(self.templatePath)
        return

    def askopenoutputfile(self):
        path = filedialog.asksaveasfilename(initialdir="../", title="Save out file to", filetypes=(("kmz files", "*.kmz"),))
        self.outputPath = path
        self.outFilePath.set(self.outputPath)
        return

    def processXML(self):
        return



class HistoryPanel(ttk.Frame):
    def __init__(self, parent, connection):
        self.parent = parent
        self.conn = connection

        ttk.Frame.__init__(self, parent)

        self.text = tk.Listbox(self, width=60)

        for i in range(100):
            self.text.insert(tk.END, str(i))

        scrollbar = ttk.Scrollbar(self)

        scrollbar.config(command=self.text.yview)
        self.text.config(yscrollcommand=scrollbar.set)

        self.text.pack(side=tk.LEFT, fill=tk.BOTH)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)



    def getHistoryStringList(self):
        return



    def writedb(self):
            self.db.insert_history(
                self.current_user,
                self.conflictCount,
                os.path.basename(self.templatePath),
                os.path.basename(self.copyPath),
                os.path.basename(self.outputPath)
            )





if __name__ == "__main__":
    root = tk.Tk()
    root.title("KML Importer Tool")
    root.geometry("500x500")
    UserMain(root)
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.mainloop()

