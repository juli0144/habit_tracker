import customtkinter as ctk
import json
import datetime


def check_today(day, tar_time, mode):
    today_obj = datetime.datetime.today()
    if mode == 'day':
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Time']
        wday = today_obj.weekday()
        return days.index(day) == wday
    elif mode == 'time':
        # Converts the given time in minutes
        tar_time_obj = datetime.datetime.strptime(tar_time, "%H:%M")
        tar_time_in_min = (tar_time_obj.hour * 60) + tar_time_obj.minute
        # Converts current time in minutes
        today_time_in_min = (today_obj.hour * 60) + today_obj.minute

        # Calculates time diff, positive means diff to time in the past
        timediff = tar_time_in_min - today_time_in_min

        return 15 > timediff >= 0

    else:
        print('Mode error in check_today')


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

        label1 = ctk.CTkLabel(self, text="No users where found, please enter a username")
        entry = ctk.CTkEntry(self, textvariable=self.name)
        entry.bind("<Return>", command=lambda eventbutton: self.setup())
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
            users_options = [layout]

            # Convert pyton list into json, create a file and add the new user in it
            f = open('users.json', 'w')
            f.write(json.dumps(users_options, indent=1))
            f.close()

            # Writes user options to the parent and destroys self
            self.parent.user_options = users_options[0]
            self.destroy()
            self.parent.load_frame('main')


class Calender(ctk.CTkScrollableFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        ctk.CTkScrollableFrame.__init__(self, parent, *args, **kwargs)

        self.times_list = controller.time_list
        self.height = (controller.height - 20) / controller.segments
        self.width = ((controller.width * 0.8)-30) / 8
        self.data = controller.data
        self.segments = {}
        self.refresh_interval = 10000    # ms

        # Creates the segments
        self._create_segments()
        self.conf_all_segments()

        # Starts refreshing time elements
        self.start_refresh()

    def _create_segments(self):
        day_list = ['Time', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # Grids the segments and saves them in a dict
        column = 1
        for d in day_list:
            row = 1

            day_label = ctk.CTkLabel(self, height=20, width=self.width)
            day_label.grid(column=column, row=0, pady=10)
            temp_dict = {'top': day_label}

            for t in self.times_list:
                segment = ctk.CTkLabel(self, height=self.height, width=self.width)
                segment.grid(column=column, row=row)
                temp_dict[t] = segment
                row += 1
            self.segments[d] = temp_dict
            column += 1

    def conf_all_segments(self):
        self._conf_top()
        self._conf_time()
        self.conf_tasks()

    def _conf_time(self):
        # Configures the time segments
        for time, segment in self.segments['Time'].items():
            if time != 'top':
                segment.configure(text=time if time.endswith('00') or time.endswith('30') else '')
                # Timecheck
                if check_today(None, time, 'time'):
                    segment.configure(fg_color='white', bg_color='white', text_color='black')

    def _conf_top(self):
        # Configuring the segments top
        for day, segments in self.segments.items():
            segments['top'].configure(text=day)
            # Daycheck
            if check_today(day, None, 'day'):
                segments['top'].configure(fg_color='white', bg_color='white', text_color='black')

    def conf_tasks(self):
        # Configure callender segments
        for day, segments in self.segments.items():
            if day == 'Time':
                continue

            a_string = ''
            for time, segment in segments.items():
                if time == 'top':
                    continue

                try:
                    seg_data = self.data['sced'][day][time]
                    seg_text, seg_color = seg_data
                    segment.configure(text=seg_text if a_string != seg_text else '',
                                      bg_color=seg_color, fg_color=seg_color)
                    a_string = seg_text
                except KeyError:
                    segment.configure(text='')
                    a_string = ''

    def start_refresh(self):
        self.after(self.refresh_interval, self.refresh)

    def refresh(self):
        self._conf_time()
        self._conf_top()
        self.start_refresh()


class Sceduler(ctk.CTkFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        ctk.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = controller
        self.times_list = controller.time_list
        self.user = controller.user

        self.output_str = ctk.StringVar(self, '')

        output_label = ctk.CTkLabel(self, textvariable=self.output_str, width=200)
        output_label.grid(column=0, row=0)

        self.add_scedule = AddScedFrame(self, width=200)
        self.add_scedule.grid(column=1, row=0)

    def add_scedule(self):
        times = self.times_list
        name = self.add_scedule.name.get()
        day = self.add_scedule.day.get()
        color = self.add_scedule.c_pick_color

        # Checks if value has been picked
        try:
            start = times.index(self.add_scedule.start.get())
            end = times.index(self.add_scedule.end.get())
            # Checks if scedule possible
            if start >= end:
                self.output_str.set('Times are set incorrect')
            elif name == '':
                self.output_str.set('Please enter a taskname')
            elif len(name) > 10:
                self.output_str.set('The name is too long\nPlease keep the name less then\n 10 characters')
            else:
                for t in times[start:end]:
                    self.parent.data['sced'][day][t] = [name, color]

                file = open(f'{self.user}.json', 'w')
                file.write(json.dumps(self.parent.data, indent=4))
                file.close()

        except ValueError:
            self.output_str.set('Times are set incorrect')


class AddScedFrame(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        ctk.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.c_pick_color = '#00cc66'
        self.start = ctk.StringVar(self)
        self.end = ctk.StringVar(self)
        self.day = ctk.StringVar(self, 'Monday')
        self.name = ctk.StringVar(self)

        fg_color = parent.cget('fg_color')[1]

        # Lists for OptionMenus
        day_options = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # Label "Add a new Task"
        add_label = ctk.CTkLabel(self, text='Add a new Task')

        # Entry for Taskname
        name_frame = ctk.CTkFrame(self, fg_color=fg_color)
        name_label = ctk.CTkLabel(name_frame, text='Name of the Task:')
        name_entry = ctk.CTkEntry(name_frame, textvariable=self.name)

        # Optionmenu Weekday
        day_frame = ctk.CTkFrame(self, fg_color=fg_color)
        day_label = ctk.CTkLabel(day_frame, text='Choose a day', font=('', 20))
        day_optmenu = ctk.CTkOptionMenu(day_frame, variable=self.day, values=day_options, font=('', 18))

        # Optionmenu Starttime
        start_frame = ctk.CTkFrame(self, fg_color=fg_color)
        start_label = ctk.CTkLabel(start_frame, text='Start', font=('', 20))
        start_optmenu = ctk.CTkComboBox(start_frame, variable=self.start, values=parent.times_list, font=('', 18))

        # Optionmenu Endtime
        end_frame = ctk.CTkFrame(self, fg_color=fg_color)
        end_label = ctk.CTkLabel(end_frame, text='End', font=('', 20))
        end_optmenu = ctk.CTkComboBox(end_frame, variable=self.end, values=parent.times_list, font=('', 18))

        # Color Menu
        c_frame = ctk.CTkFrame(self, fg_color=fg_color)
        self.c_label = ctk.CTkLabel(c_frame, textvariable=self.name, font=('', 15), corner_radius=100,
                                    fg_color='#00cc66')
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
        self.c_pick_color = color
