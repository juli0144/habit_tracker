from setup import *


# Main window and frame parent
class Mainwindow(ctk.CTk):
    def __init__(self, *args, **kwargs):
        ctk.CTk.__init__(self, *args, **kwargs)
        self.resizable(width=False, height=False)

        self.user_options = {}
        self.username = ''
        self.frames = {'main': Main, "Options": Options}
        self.frame = None

        # Layout for a user save:
        # active: To load the last active user
        # start: Starting hour for the scedule, len: length of a day in 15 min parts
        self.optionlayout = {'usr': 'Username', 'active': False, 'height': 600, 'width': 800, 'start': 6, 'len': 64}
        self.load_user_options()

    # Loading the save file/dict {Username:{active:TRUE, height:600, width:800}}
    def load_user_options(self):
        try:
            with open('users.json') as users_json:
                userlist = json.load(users_json)
                for usr in userlist:
                    if usr['active']:
                        self.user_options = usr
                self.geometry(str(self.user_options['width'])+'x'+str(self.user_options['height']))
                self.load_frame('main')

        except FileNotFoundError:
            setupwin = Setup(self)
            setupwin.pack()
            self.geometry('800x600')

    def load_frame(self, cont):
        if self.frame:
            self.frame.destroy()
        self.frame = self.frames[cont](self)
        self.frame.pack()


# Main screen with callender, user_options and other funktions
class Main(ctk.CTkFrame):
    def __init__(self, parent):
        ctk.CTkFrame.__init__(self, parent)
        self.height = parent.user_options['height']
        self.width = parent.user_options['width']
        self.user_options = parent.user_options
        self.segments = parent.user_options['len']
        self.toggle = False
        self.user = parent.user_options['usr']

        self.time_list = timecount(self.user_options['start'], self.segments)

        # Loads scedule data
        try:
            with open(f'{self.user}.json') as sced_data_json:
                self.data = json.load(sced_data_json)
        except FileNotFoundError:
            self.data = {'sced': {
                'Monday': {}, 'Tuesday': {}, 'Wednesday': {}, 'Thursday': {}, 'Friday': {}, 'Saturday': {}, 'Sunday': {}
            },
                         'data': {

                         }}

        # Left side Menu
        menuframe = ctk.CTkFrame(self, height=self.height, width=self.width*0.2)
        madeby = ctk.CTkLabel(menuframe, text='Made by juli144')
        label1 = ctk.CTkLabel(menuframe, text=parent.user_options['usr'],
                              height=20, width=self.width*0.2, font=('', 20))
        btn_opt = ctk.CTkButton(menuframe, text='user_options', width=1,
                                command=lambda: parent.load_frame('user_options'))
        self.btn_newscedule = ctk.CTkButton(menuframe, text='Add a new scedule', width=1, command=self.set_scedule)

        menuframe.grid(row=0, column=0)
        madeby.grid(column=0, row=0, pady=15)
        label1.grid(column=0, row=1, pady=15)
        self.btn_newscedule.grid(column=0, row=2, pady=5)
        # btn_opt.grid(column=0, row=3, pady=5)

        self.sceduler = Sceduler(self, self, width=self.width*0.8, height=self.height)
        self.sceduler.grid(row=0, column=1, sticky='nsew')

        self.calender = Calender(self, self, width=self.width*0.8, height=self.height)
        self.calender.grid(row=0, column=1)

    def set_scedule(self):
        if self.toggle:
            self.calender.conf_tasks()
            self.sceduler.lower()
            self.btn_newscedule.configure(text='Add a new scedule')
        else:
            self.sceduler.tkraise()
            self.btn_newscedule.configure(text='Back to Callender')

        self.toggle = not self.toggle


# Options window
class Options(ctk.CTkFrame):
    def __init__(self, parent):
        ctk.CTkFrame.__init__(self, parent)

        label = ctk.CTkLabel(self, text='user_options')
        label.pack()

        button1 = ctk.CTkButton(self, text='back', command=lambda: parent.load_frame('main'))
        button1.pack(side='bottom')


if __name__ == '__main__':
    root = Mainwindow()
    root.mainloop()
