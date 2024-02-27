import customtkinter as ctk
import json
import datetime
import time


def weekday(day):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Time']
    today = datetime.datetime.today()
    return True if days.index(day) == today.weekday() else False


def get_segment(parent, day, t):
    # Logic for time display
    if day == 'Time':
        # Returns time or False to simplify shown time to every 30 min
        if t.endswith('00') or t.endswith('30'):
            text = t
        else:
            text = ''
        segment = ctk.CTkLabel(parent, text=text, height=parent.height, width=parent.width)

    # Logic for rendering labels for scedule
    else:
        try:
            # Checks if a task exists
            if parent.data['sced'][day][t]:
                name = parent.data['sced'][day][t][0]
                color = parent.data['sced'][day][t][1]
                # Checks if it is a label of the same task
                if parent.var == name:
                    segment = ctk.CTkLabel(parent, text='',
                                           fg_color=color, bg_color=color,
                                           height=parent.height, width=parent.width)
                else:
                    segment = ctk.CTkLabel(parent, text=name,
                                           fg_color=color, bg_color=color,
                                           height=parent.height, width=parent.width)
                parent.var = name
        except KeyError:
            segment = ctk.CTkLabel(parent,
                                   text='', height=parent.height, width=parent.width)
            parent.var = ''
    return segment


def timecount(hour, segments):
    minute = 0
    time_list = []
    for i in range(segments):
        if minute == 60:
            hour += 1
            minute = 0

        time_list.append(str(hour)+':'+(str(minute) if minute != 0 else '00'))
        minute += 15
    return time_list


# Fist time setup to create a user and the users file
class Setup(ctk.CTkFrame):
    def __init__(self, parent):
        ctk.CTkFrame.__init__(self, parent)
        self.parent = parent
        self.name = ctk.StringVar(self, '')
        self.error = ctk.StringVar(self, '')

        label1 = ctk.CTkLabel(self, text="No users found, please enter a username")
        entry = ctk.CTkEntry(self, textvariable=self.name)
        button = ctk.CTkButton(self, text='Create', command=self.setup)
        label2 = ctk.CTkLabel(self, textvariable=self.error)

        label1.grid(column=0, columnspan=2)
        entry.grid(column=0, row=1)
        button.grid(column=1, row=1)
        label2.grid(column=0, row=2, columnspan=2)

    # Check name and catch those that could cause errors
    def setup(self):
        name = self.name.get()
        if name == '':
            self.error.set('Please enter a name')
        elif name == 'Username' or name == 'users' or name == 'usr':
            self.error.set('Please choose a different name')
        else:
            # Changes generall layout to fit for the first user
            layout = self.parent.optionlayout
            layout['active'] = True
            layout['usr'] = name

            # Puts current user into a list to make it appendable
            useroptions = [layout]

            # Convert pyton list into json, create a file and add the new user in it
            f = open('users.json', 'w')
            f.write(json.dumps(useroptions, indent=1))
            f.close()

            # Writes user options to the parent and destroys self
            self.parent.options = useroptions[0]
            self.destroy()
            self.parent.load_frame('main')


class Callender(ctk.CTkScrollableFrame):
    def __init__(self, parent, *args, **kwargs):
        ctk.CTkScrollableFrame.__init__(self, parent, *args, **kwargs)
        # List and len for rows and collumns
        days = ['Time', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.height = (parent.height - 20) / parent.segments
        self.width = ((parent.width * 0.8)-30) / 8
        self.data = parent.data
        self.var = ''
        times = timecount(parent.options['start'], parent.segments)

        column = 1
        for d in days:
            row = 1

            # Highlights and grids the current day
            if weekday(d):
                day = ctk.CTkLabel(self, text=d, height=20, width=self.width, fg_color='purple')
            else:
                day = ctk.CTkLabel(self, text=d, height=20, width=self.width)
            day.grid(column=column, row=0, pady=10)

            for t in times:
                segment = get_segment(self, d, t)
                segment.grid(column=column, row=row)
                row += 1
            column += 1


class Sceduler(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        ctk.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.day = ctk.StringVar(self, 'Monday')
        self.name = ctk.StringVar(self)
        self.c_pick_color = '#00cc66'

        self.start = ctk.StringVar(self)
        self.end = ctk.StringVar(self)
        self.parent = parent

        self.times = timecount(parent.options['start'], parent.segments)
        self.user = parent.user

        add_scedule = AddScedFrame(self, width=parent.width)
        add_scedule.pack()

    def add_scedule(self):
        times = self.times
        name = self.name.get()
        day = self.day.get()
        color = self.c_pick_color

        # Checks if value has been picked
        try:
            start = times.index(self.start.get())
            end = times.index(self.end.get())
            # Checks if scedule possible
            if start >= end:
                print(f"junge start {start} end {end}")
            elif name == '':
                print(f'name error')
            else:
                for t in times[start:end]:
                    self.parent.data['sced'][day][t] = [name, color]

                file = open(f'{self.user}.json', 'w')
                file.write(json.dumps(self.parent.data, indent=4))
                file.close()

        except ValueError:
            print('Pick was error')


class AddScedFrame(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        ctk.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        fg_color = parent.cget('fg_color')

        # Lists for OptionMenus
        day_options = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # Label "Add a new Task"
        add_label = ctk.CTkLabel(self, text='Add a new Task')

        # Entry for Taskname
        name_frame = ctk.CTkFrame(self, fg_color=fg_color)
        name_label = ctk.CTkLabel(name_frame, text='Name of the Task:')
        name_entry = ctk.CTkEntry(name_frame, textvariable=parent.name)

        # Optionmenu Weekday
        day_frame = ctk.CTkFrame(self, fg_color=fg_color)
        day_label = ctk.CTkLabel(day_frame, text='Choose a day', font=('', 20))
        day_optmenu = ctk.CTkOptionMenu(day_frame, variable=parent.day, values=day_options, font=('', 18))

        # Optionmenu Starttime
        start_frame = ctk.CTkFrame(self, fg_color=fg_color)
        start_label = ctk.CTkLabel(start_frame, text='Start', font=('', 20))
        start_optmenu = ctk.CTkComboBox(start_frame, variable=parent.start, values=parent.times, font=('', 18))

        # Optionmenu Endtime
        end_frame = ctk.CTkFrame(self, fg_color=fg_color)
        end_label = ctk.CTkLabel(end_frame, text='End', font=('', 20))
        end_optmenu = ctk.CTkComboBox(end_frame, variable=parent.end, values=parent.times, font=('', 18))

        # Color Menu
        c_frame = ctk.CTkFrame(self, fg_color=fg_color)
        self.c_label = ctk.CTkLabel(c_frame, textvariable=parent.name, font=('', 15), corner_radius=100, fg_color='#00cc66')
        cn_label = ctk.CTkLabel(c_frame, text='Colorpicker')
        c_b1 = ctk.CTkButton(c_frame, text='', width=30, height=30, fg_color='#00cc66', hover_color='#006633',
                             command=lambda: self.colorpicker('#00cc66'))
        c_b2 = ctk.CTkButton(c_frame, text='', width=30, height=30, fg_color='#00cc66', hover_color='#006633',
                             command=lambda: self.colorpicker('#00cc66'))
        c_b3 = ctk.CTkButton(c_frame, text='', width=30, height=30, fg_color='#33cc33', hover_color='#1f7a1f',
                             command=lambda: self.colorpicker('#33cc33'))
        c_b4 = ctk.CTkButton(c_frame, text='', width=30, height=30, fg_color='#ccff33', hover_color='#739900',
                             command=lambda: self.colorpicker('#ccff33'))
        c_b5 = ctk.CTkButton(c_frame, text='', width=30, height=30, fg_color='#ff6600', hover_color='#803300',
                             command=lambda: self.colorpicker('#ff6600'))
        c_b6 = ctk.CTkButton(c_frame, text='', width=30, height=30, fg_color='#ff0000', hover_color='#800000',
                             command=lambda: self.colorpicker('#ff0000'))
        c_b7 = ctk.CTkButton(c_frame, text='', width=30, height=30, fg_color='#ff0066', hover_color='#800033',
                             command=lambda: self.colorpicker('#ff0066'))
        c_b8 = ctk.CTkButton(c_frame, text='', width=30, height=30, fg_color='#ff33cc', hover_color='#800060',
                             command=lambda: self.colorpicker('#ff33cc'))
        c_b9 = ctk.CTkButton(c_frame, text='', width=30, height=30, fg_color='#9933ff', hover_color='#5900b3',
                             command=lambda: self.colorpicker('#9933ff'))
        c_b10 = ctk.CTkButton(c_frame, text='', width=30, height=30, fg_color='#6600ff', hover_color='#330080',
                              command=lambda: self.colorpicker('#6600ff'))
        c_b11 = ctk.CTkButton(c_frame, text='', width=30, height=30, fg_color='#6699ff', hover_color='#0055ff',
                              command=lambda: self.colorpicker('#6699ff'))
        c_b12 = ctk.CTkButton(c_frame, text='', width=30, height=30, fg_color='#0000ff', hover_color='#000080',
                              command=lambda: self.colorpicker('#0000ff'))
        c_b13 = ctk.CTkButton(c_frame, text='', width=30, height=30, fg_color='#33ccff', hover_color='#0099cc',
                              command=lambda: self.colorpicker('#33ccff'))
        c_b14 = ctk.CTkButton(c_frame, text='', width=30, height=30, fg_color='#737373', hover_color='#262626',
                              command=lambda: self.colorpicker('#737373'))
        c_b15 = ctk.CTkButton(c_frame, text='', width=30, height=30, fg_color='#663300', hover_color='#331a00',
                              command=lambda: self.colorpicker('#663300'))

        # Button
        btn = ctk.CTkButton(self, text='Add Task', command=parent.add_scedule)

        # Packed inside of frames for better order
        day_label.pack()
        day_optmenu.pack()
        name_label.pack(padx=20)
        name_entry.pack(padx=20)
        start_label.pack()
        start_optmenu.pack()
        end_label.pack()
        end_optmenu.pack()

        cn_label.grid(column=0, row=0, columnspan=5, sticky='we')
        c_b1.grid(column=0, row=1, pady=5, padx=5)
        c_b2.grid(column=0, row=2, pady=5, padx=5)
        c_b3.grid(column=0, row=3, pady=5, padx=5)
        c_b4.grid(column=1, row=1, pady=5, padx=5)
        c_b5.grid(column=1, row=2, pady=5, padx=5)
        c_b6.grid(column=1, row=3, pady=5, padx=5)
        c_b7.grid(column=2, row=1, pady=5, padx=5)
        c_b8.grid(column=2, row=2, pady=5, padx=5)
        c_b9.grid(column=2, row=3, pady=5, padx=5)
        c_b10.grid(column=3, row=1, pady=5, padx=5)
        c_b11.grid(column=3, row=2, pady=5, padx=5)
        c_b12.grid(column=3, row=3, pady=5, padx=5)
        c_b13.grid(column=4, row=1, pady=5, padx=5)
        c_b14.grid(column=4, row=2, pady=5, padx=5)
        c_b15.grid(column=4, row=3, pady=5, padx=5)
        self.c_label.grid(column=0, row=4, columnspan=5, sticky='we')

        # Column 0
        add_label.grid(column=0, row=0)
        day_frame.grid(column=0, row=1, pady=10, padx=20)
        name_frame.grid(column=0, row=2, pady=10, padx=20)
        c_frame.grid(column=0, row=3, pady=10, padx=20)
        start_frame.grid(column=0, row=4, pady=10)
        end_frame.grid(column=0, row=5, pady=10)
        btn.grid(column=0, row=6, pady=10)

    def colorpicker(self, color):
        self.c_label.configure(fg_color=color)
        self.parent.c_pick_color = color
