from sys import path as sys_path
from Tkinter import *
import subprocess
import ttk
import threading

sys_path.append('libs')
from PIL import ImageTk, Image
import tkFont
import webbrowser

class MongoApp():

    pidPath = 'logs/mongo.pid'

    def __init__(self, maxConns=10, dbpath='data/db', noauth=1):
        self.maxConns = maxConns
        self.dbpath = dbpath
        self.noauth = noauth
        self.CreateQuery()

    def CreateQuery(self):
        self.MongoQuery =  ' --pidfilepath '+str(self.pidPath)+' --maxConns ' + str(self.maxConns) + ' --dbpath ' + str(self.dbpath)
        if self.noauth == 1:
            self.MongoQuery = self.MongoQuery + ' --noauth'

    def StartMongo(self):
        query = "bin/mongod "+self.MongoQuery
        MongoProcess = subprocess.Popen([query], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        return MongoProcess

    def Start(self):
        SM = threading.Thread(target=self.StartMongo, args=())
        SM.start()

# Application structure: http://docs.python.org/2/library/tkinter.html#a-simple-hello-world-program
class Application(Frame):

    Mongo = MongoApp(maxConns=100)
    Status = 0

    def __init__(self, master=None):
        Frame.__init__(self, master)
        #self.m = master
        self.pack(expand=0, fill='both', padx=10, pady=10)
        self.ConsoleLogFrame = Frame(master)
        self.ConsoleLogFrame.pack(expand=1, fill='both')

        self.ActiveIconImage = ImageTk.PhotoImage(Image.open("assets/images/icon-active.gif"))
        self.ErrorIconImage = ImageTk.PhotoImage(Image.open("assets/images/icon-error.gif"))
        self.OffIconImage = ImageTk.PhotoImage(Image.open("assets/images/icon-off.gif"))
        self.MongoDBLogo = ImageTk.PhotoImage(Image.open("assets/images/MongoDBLogo.gif"))

        self.menubar = Menu(self)

        MenuRoot = Menu(master, tearoff=0)
        MenuBar = Menu(MenuRoot, tearoff=0)
        MenuBar.add_command(label="GitHub Page", command=self.LinkGitHubPage)
        MenuBar.add_command(label="MongoDB Docs", command=self.LinkMongoDBDocs)

        MenuRoot.add_cascade(label="About MongoApp", menu=MenuBar)
        master.config(menu=MenuRoot)


        self.CreateWidgets()
        master.protocol("WM_DELETE_WINDOW", self.QuitEvent)

    def LinkGitHubPage(self):
        webbrowser.open('https://github.com/yildizberkay/MongoApp')

    def LinkMongoDBDocs(self):
        webbrowser.open('http://docs.mongodb.org/manual/')

    def OpenDBFolder(self):
        subprocess.call(["open", "./data/db"])

    def StartServer(self):
        self.MongoObject = self.Mongo.StartMongo()
        SStatus = 0
        while True:
            Line = self.MongoObject.stdout.readline()
            self.AppendLog(Line)

            if str(self.MongoObject.poll()) == 'None':
                self.IconPanel.config(image=self.ActiveIconImage)
                self.Status = 1
                SStatus = 1
            elif str(self.MongoObject.poll()) == '100':
                SStatus = 0
            else:
                self.IconPanel.config(image=self.OffIconImage)

            if not Line:
                break
        self.Status = 0
        self.MongoObject.stdout.close()

        if SStatus == 0:
            self.StopButton["state"] = DISABLED
            self.StartButton["state"] = NORMAL
            self.IconPanel.config(image=self.ErrorIconImage)
            self.AppendLog("Error!\n", 'ErrorHead')
            self.AppendLog("Mongo DB is not working, please check console log.\n", 'NotificationHead')
        self.AppendLog("--------------------------------------------------\n",'NotificationHead')

    def StartServerMulti(self):
        self.StartButton["state"] = DISABLED
        self.StopButton["state"] = NORMAL
        self.AppendLog("Mongo DB is starting.\n", 'NotificationHead')
        self.SM = threading.Thread(target=self.StartServer, args=())
        self.SM.setDaemon(1)
        self.SM.start()

    def StopServer(self):
        self.MongoObject.terminate()
        self.StopButton["state"] = DISABLED
        self.StartButton["state"] = NORMAL
        self.Status = 0

    def ClearConsole(self):
        self.LogArea.delete("0.0", END)

    def CreateWidgets(self):
        self.StartButton = Button(self)
        self.StartButton["text"] = "Start Mongo"
        self.StartButton["fg"]   = "red"
        self.StartButton["command"] = self.StartServerMulti
        self.StartButton.pack({"side": "left"})

        self.StopButton = Button(self)
        self.StopButton["text"] = "Stop"
        self.StopButton["command"] = self.StopServer
        self.StopButton["state"] = DISABLED
        self.StopButton.pack({"side": "left"})

        self.GetInfo = Button(self)
        self.GetInfo["text"] = "Clear"
        self.GetInfo["command"] = self.ClearConsole
        self.GetInfo.pack({"side": "left"})

        self.OpenFolder = Button(self)
        self.OpenFolder["text"] = "Open DB Folder"
        self.OpenFolder["command"] = self.OpenDBFolder
        self.OpenFolder.pack({"side": "left"})

        self.PoweredMongoPanel = Label(self, image=self.MongoDBLogo)
        self.PoweredMongoPanel.image = self.MongoDBLogo
        self.PoweredMongoPanel.pack({"side": "right"})

        self.IconPanel = Label(self, image=self.OffIconImage)
        self.IconPanel.image = self.OffIconImage
        self.IconPanel.pack({"side": "right"})

        self.LogArea = Text(self.ConsoleLogFrame)
        self.LogArea["bd"] = "0px"
        self.LogArea["bg"] = "black"
        self.LogArea["fg"] = "green"
        self.LogArea["highlightthickness"] = "0px"
        self.LogArea.insert(INSERT, "Click to \"Start Mongo\" button for start the server.\nGitHub repository: http://git.io/MongoApp\n")
        self.LogArea.pack(expand=1, fill='both')

        self.LogArea.tag_config("NotificationHead", background="#f1c40f", foreground="#2c3e50")
        self.LogArea.tag_config("ErrorHead", background="#e74c3c", foreground="#ffffff", font=tkFont.Font(weight='bold'))

    def AppendLog(self, logline, tag='None'):
        if tag == 'None':
            self.LogArea.insert(END, logline)
        else:
            self.LogArea.insert(END, logline, (tag))
        self.LogArea.see('end')

    def QuitEvent(self):
        if self.Status == 1:
            self.MongoObject.terminate()
        self.master.destroy()
        self.master.quit()


root = Tk()
app = Application(master=root)
app.master.title("MongoApp")
app.master.geometry("640x480")
app.mainloop()
