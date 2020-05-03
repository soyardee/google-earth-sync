import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk
from datetime import datetime
from kmlmodules.dbconnect import DBConnect as DBConnect
from kmlmodules.domtransformer import DOMTransformer
import os

"""
@author Sawyer Timperley
@date   2020-05-03
@title  User Interface Construction
"""


# frame containing two sub frames
# allows the independent frames to communicate via object reference. Not ideal, but could be worse (co-dependent)
class UserMain(ttk.Frame):
    def __init__(self, parent):
        # set up database object, stores all file processing history
        self.db = DBConnect("data.db", "../history")
        ttk.Frame.__init__(self, parent)
        history = HistoryPanel(self, self.db)
        history.grid(column=0, row=1)
        UserFields(self, self.db, history).grid(column=0, row=0)
        self.pack()


# a grid of all user input fields and buttons
class UserFields(ttk.Frame):
    def __init__(self, parent, connection, history):
        self.DIR_TEXT_SIZE = 70
        self.conn = connection
        self.historyPane = history
        ttk.Frame.__init__(self, parent, padding="10 10 10 10")

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

    # dialog boxes that open when the browse button is clicked

    def askopenfiletemplate(self):
        path = filedialog.askopenfilename(initialdir="../", title="Select template file",
                                          filetypes=(("kmz files", "*.kmz"),))
        self.templatePath = path
        self.templateFilePath.set(self.templatePath)
        return

    def askopencopy(self):
        path = filedialog.askopenfilename(initialdir="../", title="Select comparison file",
                                          filetypes=(("kmz files", "*.kmz"),))
        self.copyFilePath.set(path)
        return

    def askopenoutputfile(self):
        path = ""
        path = filedialog.asksaveasfilename(initialdir="../",
                                            title="Save out file to",
                                            filetypes=(("kmz files", "*.kmz"),))
        # appends the kmz file type to the end if the user only types in a name, and not the type.
        if ".kmz" not in path and path != "":
            path += ".kmz"

        self.outFilePath.set(path)
        return

    # validates and runs xml transform with user file entries
    def processXML(self):
        if self.templateFilePath.get() == "":
            tk.messagebox.showinfo('Missing Data', 'Please input template file!')
            return
        if self.copyFilePath.get() == "":
            tk.messagebox.showinfo('Missing Data', 'Please input imported file!')
            return
        if self.userNameEntry.get() == "":
            tk.messagebox.showinfo('Missing Data', 'Please input username!')
            return

        # xml transform engine reference
        runtime = ""

        convert_success = False
        try:
            if self.outFilePath.get() != "":
                # unorthodox programming practice below. Typically, you would pass the empty string into the class and
                # it figures out the rest from there. This looks gross, but does work.
                runtime = DOMTransformer(self.templateFilePath.get(), self.copyFilePath.get(), self.outFilePath.get())
            else:
                runtime = DOMTransformer(self.templateFilePath.get(), self.copyFilePath.get())
            runtime.process()
            runtime.writeOut()
            tk.messagebox.showinfo('Success', f"Number of imported locations: {runtime.getAppendCount()}")
            convert_success = True
        # catch a non-kmz file if it cannot be opened, or if some other error occurs.
        except Exception as e:
            tk.messagebox.showinfo('Error', f'Error opening files!: {e}')

        if convert_success:
            name = self.userNameEntry.get().lower()
            count = runtime.getAppendCount()
            templateName = os.path.basename(self.templateFilePath.get())
            copyName = os.path.basename(self.copyFilePath.get())
            outputName = os.path.basename(runtime.getOutputKMZPath())

            self.conn.insert_history(name, count, templateName, copyName, outputName)

            time = datetime.now().strftime("%Y-%m-%d %H:%M")
            # add entry to the panel without requiring another database read.
            self.historyPane.update_history(time, name, copyName, templateName, count)


# display all previous processes by user
class HistoryPanel(ttk.Frame):
    def __init__(self, parent, connection):
        self.parent = parent
        self.conn = connection

        ttk.Frame.__init__(self, parent)
        self.historyBox = tk.Listbox(self, width=80)
        db_rows = self.conn.get_history_rows()

        for i in db_rows:
            time = datetime.fromisoformat(i[0]).strftime("%Y-%m-%d %H:%M")
            user = i[1]
            copyfile = i[4]
            infile = i[3]
            count = i[2]
            listEntry = f"{time}: {user} merged {copyfile} into {infile}, {count} imported."
            self.historyBox.insert(tk.END, listEntry)

        scrollbar = ttk.Scrollbar(self)
        scrollbar.config(command=self.historyBox.yview)
        self.historyBox.config(yscrollcommand=scrollbar.set)

        self.historyBox.pack(side=tk.LEFT, fill=tk.BOTH)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # don't pull from the database each time a file is converted.
    # It is already added, and will be pulled properly on the next reload.
    # not unlike dirty tracking, seen in angular apps on the web.
    def update_history(self, time, user, copyfile, infile, count):
        entry = f"{time}: {user} merged {copyfile} into {infile}, {count} imported."
        self.historyBox.insert(0, entry)
        return


if __name__ == "__main__":
    root = tk.Tk()
    root.title("KML Importer Tool")
    root.geometry("600x500")
    UserMain(root)
    root.mainloop()
