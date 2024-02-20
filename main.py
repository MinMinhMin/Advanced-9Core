import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from threading import Thread
import pygame.mixer
import ttkbootstrap as ttk
from ttkbootstrap.toast import ToastNotification
from PIL import Image, ImageTk
from ttkbootstrap import widgets
import data.filedirectory
import data.controlaudio
import os
import data.Reverb
import data.Pitchshifter
import locale

locale.setlocale(locale.LC_ALL, '')


def resource_path(relative):
    return os.path.join(
        os.environ.get(
            "_MEIPASS2",
            os.path.abspath(".")
        ),
        relative
    )


class LogoImage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color='white')
        self.place(relx=0.5, rely=0.13, anchor='center')
        self.columnconfigure(0, weight=1, uniform='a')
        self.rowconfigure((0, 1), weight=1)

        ctk.CTkLabel(self, text='Advanced 9Core', text_color='#f5bcf5', font=('segoe print', 40)).grid(row=0, column=0,
                                                                                                       sticky='we')
        ctk.CTkLabel(self, text='Ver 0.0.0', font=('segoe print', 20), ).grid(row=1, column=0, sticky='we')


class SlidePanel(ctk.CTkFrame):
    def __init__(self, parent, start_pos, end_pos):
        super().__init__(parent, corner_radius=40, fg_color='#f5bcf5')

        # general attributes

        self.start_pos = start_pos + 0.01
        self.end_pos = end_pos - 0.01
        self.width = abs(start_pos - end_pos)

        # animation logic
        self.pos = self.start_pos
        self.in_start_pos = True

        # layout
        self.place(relx=self.start_pos, rely=0, relwidth=self.width, relheight=0.95)

    def animate(self):

        if self.in_start_pos:
            self.animate_forward()
        else:
            self.animate_backward()

    def animate_forward(self):
        if self.pos > self.end_pos:
            self.pos -= 0.01
            self.place(relx=self.pos, rely=0.05, relwidth=self.width, relheight=0.95)

            self.after(10, self.animate_forward)

        else:
            self.in_start_pos = False

    def animate_backward(self):
        if self.pos < self.start_pos:
            self.pos += 0.01
            self.place(relx=self.pos, rely=0.05, relwidth=self.width, relheight=0.95)

            self.after(10, self.animate_backward)

        else:
            self.in_start_pos = True


class SlideButton(ctk.CTkButton):
    def __init__(self, parent, start_pos, end_pos):
        super().__init__(parent, fg_color='#f5bcf5', corner_radius=20, hover_color='#f294f2',
                         text='m\no\nd\ne', text_color='black')

        # general attributes
        self.start_pos = start_pos + 0.01
        self.end_pos = end_pos - 0.01
        # self.width = abs( start_pos - end_pos )
        self.width = 0.06

        # animation logic
        self.pos = self.start_pos
        self.in_start_pos = True

        # layout
        self.place(relx=self.start_pos, rely=0.35, relwidth=self.width, relheight=0.3, anchor='ne')

    def animate_button(self):
        if self.in_start_pos:
            self.animate_forward_button()
        else:
            self.animate_backward_button()

    def animate_forward_button(self):
        if self.pos > self.end_pos:
            self.pos -= 0.01
            self.place(relx=self.pos, rely=0.35, relwidth=self.width, relheight=0.3, anchor='ne')
            self.after(10, self.animate_forward_button)

        else:
            self.in_start_pos = False

    def animate_backward_button(self):
        if self.pos < self.start_pos:
            self.pos += 0.01
            self.place(relx=self.pos, rely=0.35, relwidth=self.width, relheight=0.3, anchor='ne')
            self.after(10, self.animate_backward_button)

        else:
            self.in_start_pos = True


class Directory_button(ctk.CTkButton):
    def __init__(self, parent):
        super().__init__(parent,
                         fg_color='#f5bcf5',
                         text='Add Songs',
                         text_color='black',
                         corner_radius=30,
                         hover_color='#f294f2', border_color='red')
        self.place(relx=0, rely=0, anchor='nw')
        self.file_name = None
        self.titlesong = ctk.CTkLabel(parent, text='    Songs list', text_color='black', font=('Calibri', 25),
                                      justify='right')
        self.songlist = []


class ListFrame(ttk.Frame):
    def __init__(self, parent, text_data, item_height):
        super().__init__(parent)
        self.place(relx=0, rely=0.2, relwidth=0.3, relheight=0.8)

        # widget data
        self.text_data = text_data
        self.item_number = len(text_data)
        self.list_height = self.item_number * item_height
        self.max_pixel = 0
        self.max_length = 0
        self.max_length_song = None
        self.previous_song_index = None
        self.current_song_index = None
        self.current_song_path = None
        self.song = []
        if len(text_data) != 0:
            for text in text_data:
                if len(text) > self.max_length:
                    self.max_length = len(text)
                    self.max_length_song = text

            for i in range(50, 1, -1):
                if (i * len(self.max_length_song) <= 600):
                    self.max_pixel = i
                    break

        # canvas
        self.canvas = ttk.Canvas(self, scrollregion=(0, 0, self.winfo_width(), self.list_height))
        self.canvas.pack(expand=True, fill='both')

        # dislay frame
        self.frame = ttk.Frame(self)
        for index, item in enumerate(self.text_data):
            self.create_item(item, index).pack(expand=True, fill='both', pady=0, padx=0)

        # scroll bar
        self.scroll = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll.set)
        self.scroll.place(relx=1, rely=0, relheight=1, anchor='ne')

        # events
        self.canvas.bind_all('<MouseWheel>',
                             lambda event: self.canvas.yview_scroll(-int(event.delta / 60), "units"))
        self.bind('<Configure>', lambda event: self.update_size(event))

    def update_size(self, event):
        if self.list_height >= self.winfo_height():
            height = self.list_height
            self.canvas.bind_all('<MouseWheel>',
                                 lambda event: self.canvas.yview_scroll(-int(event.delta / 60), "units"))
            self.scroll.place(relx=1, rely=0, relheight=1, anchor='ne')

        else:
            height = self.winfo_height()
            self.canvas.unbind_all('<MouseWheel>')
            self.scroll.place_forget()

        self.canvas.create_window((0, 0), window=self.frame, anchor='nw', width=self.winfo_width(),
                                  height=height)

    def create_item(self, item, index):
        frame = ttk.Frame(self.frame)

        self.song.append(ctk.CTkButton(frame, text=item,
                                       font=('Calibri', -self.max_pixel),
                                       fg_color='white',
                                       text_color='black',
                                       hover_color='#f5bcf5',
                                       anchor='right'
                                       ))
        self.song[index].pack(expand=True, fill='x')
        self.song[index].Mode1 = None
        self.song[index].Mode2 = None
        self.song[index].Mode3 = None
        self.song[index].Mode4 = None
        self.song[index].is_choose = False
        self.song[index].play_click = 0
        self.song[index].apply_mode_button_count = 0

        return frame


class PlayButton(ctk.CTkButton):
    def __init__(self, parent, win_width, win_height):
        self.Image1 = ctk.CTkImage(
            light_image=Image.open(resource_path('play_button1.png')),
            dark_image=Image.open(resource_path('play_button1.png')),
            size=(int(win_width * 0.2 * 0.75), int(win_height * 0.426 * 0.75))

        )

        self.Image2 = ctk.CTkImage(
            light_image=Image.open(resource_path('play_button2.png')),
            dark_image=Image.open(resource_path('play_button2.png')),
            size=(int(win_width * 0.2 * 0.75), int(win_height * 0.426 * 0.75))
        )

        super().__init__(parent, text=' ', fg_color='white', image=self.Image1, hover_color='white')
        self.place(relx=0.5, rely=0.5, relwidth=0.2, relheight=0.426, anchor='center')
        self.bind('<Motion>', command=self.inside)
        self.bind('<Leave>', command=self.outside)

    def inside(self, event):
        self.configure(image=self.Image2)

    def outside(self, event):
        self.configure(image=self.Image1)


class AddMod(ctk.CTkFrame):
    def __init__(self, parent, text, column, row, start_value, end_value, unit, begin_value):
        super().__init__(parent, fg_color='white')
        self.grid(column=column, row=row, sticky='nesw')
        self.rowconfigure(0, weight=1, uniform='a')
        self.columnconfigure((0, 1, 2, 3), weight=1, uniform='a')

        self.label1 = ctk.CTkLabel(self, text=text, text_color='black', )
        self.label1.grid(row=0, column=0)
        self.start_value = begin_value
        self.unit = unit
        self.value_slider = ctk.DoubleVar(value=self.start_value)
        self.value_label = ctk.StringVar(value=f'{self.start_value}')

        self.slider = ctk.CTkSlider(self, orientation='horizontal',
                                    from_=start_value,
                                    state='normal',
                                    to=end_value,
                                    variable=self.value_slider,
                                    command=self.set_label_value)

        self.slider.grid(row=0, column=1, columnspan=2)

        self.label2 = ctk.CTkLabel(self, text='Default', textvariable=self.value_label, text_color='black')
        self.label2.grid(row=0, column=3)

    def set_label_value(self, value):
        self.value_label.set(str(f'{int(value)} {self.unit}'))


class AddOptionMod(ctk.CTkFrame):
    def __init__(self, parent, text, column, row, type1, type2, type3, type4):
        super().__init__(parent, fg_color='white')
        self.grid(column=column, row=row, sticky='nesw')
        self.rowconfigure(0, weight=1, uniform='a')
        self.columnconfigure((0, 1, 2), weight=1, uniform='a')

        self.label = ctk.CTkLabel(self, text=text, text_color='black')
        self.label.grid(row=0, column=0)

        self.option_var = ctk.StringVar(value='None')
        self.option = ctk.CTkOptionMenu(self, values=['Default', f'{type1}', f'{type2}', f'{type3}', f'{type4}'],
                                        variable=self.option_var)
        self.option.grid(row=0, column=1, columnspan=2)


class timeframe(ctk.CTkFrame):
    def __init__(self, parent, win_width, win_height):
        super().__init__(parent, fg_color='white')

        self.start_time = None
        self.end_time = None

        self.time = 0

        self.rowconfigure(0, weight=1, uniform='a')

        self.columnconfigure((0, 1, 2, 3), weight=1, uniform='a')

        self.label_time_var = ctk.StringVar()

        self.label_time = ctk.CTkLabel(self, text_color='black', textvariable=self.label_time_var)

        self.time_slider_var = ctk.DoubleVar(value=1)

        self.time_slider_width = int(win_width * 0.2343)
        self.time_slider_height = int(win_height * 0.03)

        self.time_slider = ctk.CTkSlider(self,
                                         button_color='#f5bcf5', button_hover_color='#f294f2',
                                         variable=self.time_slider_var)

        self.label_time.grid(row=0, column=0)

        self.time_slider.grid(row=0, column=1, columnspan=3, sticky='ew')

        self.place(relx=0.5, rely=0.8, anchor='center', relwidth=0.3, relheight=0.2)

        self.small_label = ctk.CTkLabel(self)


class App(ttk.Window):

    def __init__(self, title):
        super().__init__()

        # window setting
        self.resizable(False, False)
        self.title(title)
        self.width = int((self.winfo_screenwidth() * 4) / 5)
        self.height = int((self.winfo_screenheight() * 2) / 3)
        self.geometry(f'{self.width}x{self.height}')

        # logo
        self.iconbitmap('icon.ico')
        self.canvas = ctk.CTkCanvas(self, background='white')
        self.canvas.pack(expand=True, fill='both')
        self.logo = LogoImage(self.canvas)

        # SlidePanel

        self.slidepanel = SlidePanel(self, 1, 0.7)

        # slidepanel layout
        self.slidepanel.columnconfigure(0, weight=1, uniform='a')
        self.slidepanel.rowconfigure((0, 1, 2, 3, 4), weight=1, uniform='a')
        self.slidepanel.tkraise(aboveThis=self.logo)

        # slidebutton
        self.slidebutton = SlideButton(self, 1, 0.7)
        self.slidebutton.configure(command=lambda: [self.slidebutton.animate_button(), self.slidepanel.animate()])

        # Songs list
        self.list = None
        self.cursong = None

        # directorybutton

        self.directory_button = Directory_button(self)
        self.directory_button.configure(command=self.browse_func1)
        self.add_path_from_log()

        # playbutton
        self.playbutton = PlayButton(self, self.width, self.height)
        self.playbutton.configure(command=self.play_current_song)
        self.playbutton.alert_1 = ToastNotification(
            title='ERROR',
            message='Empty directory',
            duration=5000,
            bootstyle='danger',
            position=(10, 60, 'se'),
            icon='!'
        )
        self.playbutton.alert_2 = ToastNotification(
            title='ERROR',
            message='Choose your song!',
            duration=5000,
            bootstyle='danger',
            position=(10, 60, 'se'),
            icon='!'
        )

        # Add Mod
        self.Mode1 = AddMod(self.slidepanel, 'Semitone', 0, 1, -12, 12, ' ', 2)
        self.Mode2 = AddMod(self.slidepanel, 'Tempo', 0, 2, 50, 300, '%', 120)
        self.Mode3 = AddOptionMod(self.slidepanel, 'Reverb mode', 0, 3, 'None', 'Cave', 'Toilet', 'Sea')
        self.value_mode1 = None
        self.value_mode2 = None
        self.value_mode3 = None
        # Saving button
        self.apply_mode_button = ctk.CTkButton(self.slidepanel, text='Apply', fg_color='#18f553',
                                               hover_color='#00d93a',
                                               font=('Calibri', 30), text_color='black',
                                               command=self.apply_button_func)
        self.apply_mode_button.grid(column=0, row=4, sticky='ns', pady=10)
        self.apply_mode_button_count = 0
        self.apply_mode_button_alert1 = ToastNotification(
            title='ERROR',
            message='Apply your mode first!',
            duration=5000,
            bootstyle='danger',
            position=(10, 60, 'se'),
            icon='!'
        )
        self.apply_mode_button_alert2 = ToastNotification(
            title='ERROR',
            message='Cannot find song !',
            duration=5000,
            bootstyle='danger',
            position=(10, 60, 'se'),
            icon='!'
        )
        self.apply_mode_button_done = ToastNotification(
            title='DONE',
            message='Enjoy!',
            duration=5000,
            bootstyle='success',
            position=(10, 60, 'se'),
        )

        # time bar
        self.timeframe = timeframe(self, self.width, self.height)
        self.timeframe.place_forget()
        self.timeframe.tkraise(aboveThis=self.playbutton)
        self.timeframe.time_slider.bind('<Motion>', lambda event: self.func1(event))
        self.timeframe.time_slider.bind('<Leave>', lambda event: self.func2(event))
        self.timeframe.time_slider.bind('<B1-Motion>', lambda event: self.func3(event))
        self.timeframe.time_slider.bind('<ButtonRelease-1>', lambda event: self.func4(event))
        self.hold_mouse = False
        self.time = 0
        self.end_song = False
        self.AFTER = None
        self.mainloop()

    def add_path_from_log(self):
        self.path = open('library_path.txt', 'r')
        self.content = self.path.read()
        if (len(self.content) != 0):
            self.browse_func2()

    def func1(self, event):
        self.timeframe.time = min(max(int((event.x / self.timeframe.time_slider_width) * self.timeframe.end_time), 0),
                                  self.timeframe.end_time)
        self.timeframe.small_label.place_forget()
        self.timeframe.small_label.place(x=event.x * 1.03, y=event.y, anchor='center')
        self.timeframe.small_label.configure(
            text=f'{self.change_time(self.timeframe.time)}/{self.change_time(self.timeframe.end_time)}',
            text_color='black', font=('Calibri', 11))
        self.timeframe.time_slider.tkraise(aboveThis=self.timeframe.small_label)

    def func2(self, event):
        self.timeframe.small_label.place_forget()
        self.hold_mouse = False

    def func3(self, event):
        self.timeframe.time = min(max(int((event.x / self.timeframe.time_slider_width) * self.timeframe.end_time), 0),
                                  self.timeframe.end_time)
        self.timeframe.small_label.place_forget()
        self.timeframe.small_label.place(x=event.x * 1.03, y=event.y, anchor='center')
        self.timeframe.small_label.configure(
            text=f'{self.change_time(self.timeframe.time)}/{self.change_time(self.timeframe.end_time)}',
            text_color='black', font=('Calibri', 11))
        self.timeframe.time_slider.tkraise(aboveThis=self.timeframe.small_label)

        pygame.mixer.music.pause()
        self.hold_mouse = True
        self.set_pause_button()

    def func4(self, event):
        self.timeframe.time_slider_var.set(self.timeframe.time)
        pygame.mixer.music.set_pos(self.timeframe.time)
        self.time = self.timeframe.time
        pygame.mixer.music.unpause()
        self.hold_mouse = False
        if self.end_song == True:
            self.start_time()
            self.end_song = False
        self.set_play_button()

    def change_time(self, time):
        minute = int(time / 60)
        second = int(time - 60 * minute)
        convertion = f'{minute}:{second}'

        return convertion

    def start_time(self):

        # self.timeframe.time_slider_var.set(120)
        if self.hold_mouse == False and self.list.song[self.list.current_song_index].play_click % 2 == 1:
            time = int(self.timeframe.time_slider_var.get())
            self.timeframe.time_slider_var.set(time + 1)
            self.timeframe.label_time_var.set(
                f'{self.change_time(time)}/{self.change_time(self.timeframe.end_time)}')

            self.AFTER = self.after(1000, self.start_time)
        if self.hold_mouse == True or self.list.song[self.list.current_song_index].play_click % 2 == 0:
            pass
            self.AFTER = self.after(1000, self.start_time)
        if int(self.timeframe.time_slider_var.get()) >= self.timeframe.end_time:
            pygame.mixer.music.pause()
            self.end_song = True
            self.after_cancel(self.AFTER)

    def audioprocess(self):
        self.cursong = data.controlaudio.convert_to_wav(self.list.current_song_path)

        self.cursong = data.Pitchshifter.pitch_shift_ffmpeg_rubberband(self.cursong, self.value_mode1,
                                                                       self.value_mode2, self.value_mode3)

    def disable_apply_button(self):
        self.apply_mode_button.configure(state='disabled')
        self.apply_mode_button.configure(fg_color='#807271')

    def enable_apply_button(self):
        self.apply_mode_button.configure(state='normal')
        self.apply_mode_button.configure(fg_color='#18f553')

    def disable_play_button(self):
        self.playbutton.configure(state='disabled')

    def enable_play_button(self):
        self.playbutton.configure(state='normal')

    def apply_button_func(self):
        if hasattr(self.list, 'song') and (self.list.current_song_index != None):
            self.enable_apply_button()
            self.enable_play_button()
            self.value_mode1 = int(self.Mode1.slider.get())
            self.value_mode2 = int(self.Mode2.slider.get())
            self.value_mode3 = self.Mode3.option_var.get()

            self.reset()

            song_name = self.list.song[self.list.current_song_index].cget('text')

            self.list.current_song_path = f'{self.directory_button.file_name}/{song_name}'

            self.list.current_song_path = self.raw_string_path()

            self.apply_mode_button.configure(text='Wait ...')
            self.apply_mode_button.configure(fg_color='#807271')

            self.apply_mode_button.update()

            if (self.apply_mode_button.cget('text') == 'Wait ...'):
                self.audioprocess()

            self.list.song[self.list.current_song_index].apply_mode_button_count = 1
            self.list.song[self.list.current_song_index].play_click = 0

            self.apply_mode_button_done.show_toast()
            self.apply_mode_button.configure(text='Apply')
            self.apply_mode_button.configure(fg_color='#18f553')
            # self.apply_mode_button_done.show_toast()



        else:
            self.apply_mode_button_alert2.show_toast()
            self.disable_apply_button()

    def browse_func1(self):

        self.directory_button.file_name = filedialog.askdirectory()
        self.enable_play_button()
        self.enable_apply_button()
        self.end_song = False
        self.reset()

        with open('library_path.txt', 'w') as file:
            file.write(self.directory_button.file_name)

        self.directory_button.titlesong.place_forget()
        self.directory_button.titlesong.place(relx=0, rely=0.1, anchor='nw')

        mfdir = self.directory_button.file_name
        self.directory_button.songlist = data.filedirectory.get_audio_files(mfdir)

        self.list = ListFrame(self, self.directory_button.songlist, 50)
        if len(self.list.song) != 0:
            for i in range(len(self.list.song)):
                self.list.song[i].configure(command=self.song_func_out(i))

    def browse_func2(self):

        self.directory_button.file_name = self.content
        self.directory_button.titlesong.place_forget()
        self.end_song = False
        self.directory_button.titlesong.place(relx=0, rely=0.1, anchor='nw')

        mfdir = self.directory_button.file_name
        self.directory_button.songlist = data.filedirectory.get_audio_files(mfdir)

        self.list = ListFrame(self, self.directory_button.songlist, 50)
        if len(self.list.song) != 0:
            for i in range(len(self.list.song)):
                self.list.song[i].configure(command=self.song_func_out(i))

    def play_current_song(self):
        if hasattr(self.list, 'song') and len(self.list.song) != 0:
            self.enable_apply_button()
            if (self.list.current_song_index != None):
                self.enable_apply_button()

                if self.list.song[self.list.current_song_index].apply_mode_button_count == 1:
                    self.enable_apply_button()
                    self.list.song[self.list.current_song_index].play_click += 1
                    if self.list.song[self.list.current_song_index].play_click == 1:
                        self.timeframe.start_time = 0
                        self.timeframe.end_time = data.controlaudio.audio_dur(self.cursong)
                        self.timeframe.time_slider.configure(from_=self.timeframe.start_time,
                                                             to=self.timeframe.end_time)

                        self.timeframe.place(relx=0.49, rely=0.8, anchor='center', relwidth=0.3, relheight=0.2)
                        self.after(1000, self.start_time)
                    self.forget_alert()
                    data.controlaudio.play_song(self.cursong, self.list.song[self.list.current_song_index].play_click)

                else:
                    self.apply_mode_button_alert1.show_toast()
                    self.disable_play_button()


            else:
                self.forget_alert()
                self.playbutton.alert_2.show_toast()
                self.disable_play_button()


        else:
            self.playbutton.alert_1.show_toast()
            self.disable_play_button()

    def raw_string_path(self):
        new_string = ''
        for char in self.list.current_song_path:
            if char == '/':
                new_string += '\\'
            if char != '/':
                new_string += char

        return new_string

    def forget_alert(self):

        if (self.list.current_song_index != None):
            if (self.list.song[self.list.current_song_index].play_click > 1) and (
                    self.list.song[self.list.current_song_index].play_click % 2 == 0):
                self.set_pause_button()

            if (self.list.song[self.list.current_song_index].play_click >= 1) and (
                    self.list.song[self.list.current_song_index].play_click % 2 == 1):
                self.set_play_button()

    def song_time(self):

        self.after(1000, self.song_time)

    def set_pause_button(self):
        self.playbutton.Image1.configure(
            light_image=Image.open(resource_path('play_button1.png')),
            dark_image=Image.open(resource_path('play_button1.png')),
            size=(int(self.width * 0.2 * 0.75), int(self.height * 0.426 * 0.75)))

        self.playbutton.Image2.configure(
            light_image=Image.open(resource_path('play_button2.png')),
            dark_image=Image.open(resource_path('play_button2.png')),
            size=(int(self.width * 0.2 * 0.75), int(self.height * 0.426 * 0.75)))

    def set_play_button(self):
        self.playbutton.Image1.configure(
            light_image=Image.open(resource_path('pause_button1.png')),
            dark_image=Image.open(resource_path('pause_button1.png')),
            size=(int(self.width * 0.2 * 0.75), int(self.height * 0.426 * 0.75)))

        self.playbutton.Image2.configure(
            light_image=Image.open(resource_path('pause_button2.png')),
            dark_image=Image.open(resource_path('pause_button2.png')),
            size=(int(self.width * 0.2 * 0.75), int(self.height * 0.426 * 0.75)))

    def reset(self):
        self.set_pause_button()
        data.controlaudio.stop_song()
        self.timeframe.destroy()
        self.timeframe = timeframe(self, self.width, self.height)
        self.timeframe.place_forget()
        self.timeframe.time_slider.bind('<Motion>', lambda event: self.func1(event))
        self.timeframe.time_slider.bind('<Leave>', lambda event: self.func2(event))
        self.timeframe.time_slider.bind('<B1-Motion>', lambda event: self.func3(event))
        self.timeframe.time_slider.bind('<ButtonRelease-1>', lambda event: self.func4(event))
        self.hold_mouse = False
        if self.AFTER != None:
            self.after_cancel(self.AFTER)

    def song_func_out(self, index):

        def song_func_in():
            self.list.song[index].configure(fg_color='#f5bcf5')
            self.list.previous_song_index = self.list.current_song_index
            self.list.current_song_index = index
            self.enable_apply_button()
            self.enable_play_button()

            if (self.list.previous_song_index != None) and (
                    self.list.previous_song_index != self.list.current_song_index):
                self.list.song[self.list.previous_song_index].configure(fg_color='white')
                self.list.song[self.list.previous_song_index].play_click = 0
                self.reset()
                self.list.song[self.list.previous_song_index].apply_mode_button_count = 0
                self.Mode1.slider.set(self.Mode1.start_value)
                self.Mode2.slider.set(self.Mode2.start_value)
                self.Mode3.option.set('None')
                self.end_song = False

            else:
                self.list.song[self.list.current_song_index].is_choose = True
                self.list.song[self.list.current_song_index].play_click = 0
                self.end_song = False

        return song_func_in


# run
App('Advanced 9Core')
