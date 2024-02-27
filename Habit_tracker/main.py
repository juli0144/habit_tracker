import time

from setup import *


# Main window and frame parent
class Mainwindow(ctk.CTk):
    def __init__(self, *args, **kwargs):
        ctk.CTk.__init__(self, *args, **kwargs)
        self.resizable(width=False, height=False)

        self.options = {}
        self.username = ''
        self.frames = {'main': Main, "options": Options}
        self.frame = None
        # Layout for a user save:
        # active: To load the last active user
        # start: Starting hour for the scedule, len: length of a day in 15 min parts
        self.optionlayout = {'usr': 'Username', 'active': False, 'height': 600, 'width': 800, 'start': 6, 'len': 64}

        self.load_options()

    # Loading the save file/dict {Username:{active:TRUE, height:600, width:800}}
    def load_options(self):
        try:
            with open('users.json') as users_json:
                userlist = json.load(users_json)
                for usr in userlist:
                    print(usr)
                    if usr['active']:
                        self.options = usr
                self.geometry(str(self.options['width'])+'x'+str(self.options['height']))
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


# Main screen with callender, options and other funktions
class Main(ctk.CTkFrame):
    def __init__(self, parent):
        ctk.CTkFrame.__init__(self, parent)
        self.height = parent.options['height']
        self.width = parent.options['width']
        self.options = parent.options
        self.segments = parent.options['len']
        self.sced = True
        self.user = parent.options['usr']

        self.frame = None
        self.current_frame = ctk.CTkFrame(self, width=self.width*0.8, height=self.height)

        try:
            with open(f'{self.user}.json') as sced_data_json:
                self.data = json.load(sced_data_json)
        except FileNotFoundError:
            self.data = {'sced': {
                'Monday': {}, 'Tuesday': {}, 'Wednesday': {}, 'Thursday': {}, 'Friday': {}, 'Saturday': {}, 'Sunday': {}
            },
                         'data': {

                         }}

        menuframe = ctk.CTkLabel(self, height=self.height, width=self.width*0.2)
        madeby = ctk.CTkLabel(menuframe, text='Made by juli144')
        label1 = ctk.CTkLabel(menuframe, text=parent.options['usr'], height=20, width=self.width*0.2, font=('', 20))
        btn_opt = ctk.CTkButton(menuframe, text='Options', width=1,
                                command=lambda: parent.load_frame('options'))
        self.btn_newscedule = ctk.CTkButton(menuframe, text='Add a new scedule', width=1, command=self.set_scedule)

        menuframe.pack(side='left')
        madeby.grid(column=0, row=0, pady=15)
        label1.grid(column=0, row=1, pady=15)
        self.btn_newscedule.grid(column=0, row=2, pady=5)
        btn_opt.grid(column=0, row=3, pady=5)

        self.set_scedule()

    def set_scedule(self):
        if self.sced:
            # Setup for a smooth relaod of frames
            self.frame = Callender(self, width=self.width*0.8, height=self.height)
            self.frame.pack(side='right')
            self.current_frame.pack_forget()
            self.current_frame = self.frame

            self.btn_newscedule.configure(text='Add a new scedule')
        else:
            self.frame = Sceduler(self, width=self.width*0.8, height=self.height)
            self.frame.pack(side='right')
            self.current_frame.pack_forget()
            self.current_frame = self.frame

            self.btn_newscedule.configure(text='Return to callender')
        self.sced = not self.sced


# Options window
class Options(ctk.CTkFrame):
    def __init__(self, parent):
        ctk.CTkFrame.__init__(self, parent)

        label = ctk.CTkLabel(self, text='OPTIONS')
        label.pack()

        button1 = ctk.CTkButton(self, text='back', command=lambda: parent.load_frame('main'))
        button1.pack(side='bottom')


if __name__ == '__main__':
    root = Mainwindow()
    root.mainloop()
