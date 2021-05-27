# Author: Emran Kebede
# GUI for Smart CPM Chair

import os
import re
import time
# library for GUI
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk, PhotoImage

# library for I2C
from smbus2 import SMBus

i2cAdd = 0x9
bus = SMBus(1)

path = "/home/pi/Downloads/users/"
# The 7″ touchscreen monitor for Raspberry has 800 x 480 display
canvasHeight = 740
canvasWidth = 480
############################

buttonRelWidth = 0.48
buttonRelHeight = 0.21

lang = 'USEnglish'


def rmv_dot_txt(filename):
    # convert here
    temp = filename.split('.')
    return temp[0]


class CPMGUI(tk.Tk):

    # __init__ function for class CPMGUI
    def __init__(self, *args, **kwargs):
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)
        canvas = tk.Canvas(self, height=canvasHeight, width=canvasWidth, bg='#ffe3d8')
        canvas.pack()
        ###########################################################################
        self.container = tk.Frame(self, bg='#ffe3d8')
        self.container.place(relheight=1, relwidth=1)
        ###########################################################################
        self.currentName = ""
        self.flag = ""
        self.arr = []
        self.currentFile = ""
        self.Number_of_profiles = 0
        files = os.listdir(path)
        self.profile_name_sets = set()

        for f in files:
            self.Number_of_profiles = self.Number_of_profiles + 1
            self.profile_name_sets.add(f)

        self.frames = {}
        self.sec_frames = {}
        # iterating through a tuple consisting
        # of the different page layouts
        for F in (HomePage, ExtensionSettings, FlexionSettings, CycleSettings,
                  Manual, Preferences, Brightness, Language, PauseLimit, Profiles,
                  CreateProfile, DisplayProfile, EditProfile, Welcome, SeatConfig,
                  PinInput, PainRegister):
            frame = F(self.container, self)
            # initializing frame of that object from
            # HomePage, ExtensionSettings, FlexionSettings, CycleSettings respectively with
            # for loop
            self.frames[F] = frame

            frame.place(relheight=1, relwidth=1)

        self.show_frame(Welcome)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def add_profile(self, controller):
        self.Number_of_profiles = self.Number_of_profiles + 1

        frame = Profiles(self.container, self)

        controller.frames[Profiles] = frame

        frame.place(relheight=1, relwidth=1)

        frame = controller.frames[Profiles]
        frame.tkraise()

    def del_profile(self, controller, name):
        self.Number_of_profiles = self.Number_of_profiles - 1
        self.profile_name_sets.discard(name)
        os.remove("/home/pi/Downloads/users/"+name)
        frame = Profiles(self.container, self)

        controller.frames[Profiles] = frame

        frame.place(relheight=1, relwidth=1)

        frame = controller.frames[Profiles]
        frame.tkraise()

    def display_edit_profile(self, controller, name):

        self.currentFile = open("/home/pi/Downloads/users/" + name, "r")
        self.currentName = name
        frame = EditProfile(self.container, self)

        controller.frames[EditProfile] = frame

        frame.place(relheight=1, relwidth=1)

        frame = controller.frames[EditProfile]
        frame.tkraise()

    def get_curr_file(self):
        return self.currentFile
    
    def write_pain_level(self, flag):
        file = self.get_profile_name()
        file_obj = open("/home/pi/Downloads/users/" + file, 'a')
        date = time.asctime(time.localtime(time.time()))
        if flag == 0:
            file_obj.write("\n**************************\n")
            file_obj.write("p: " + "nopain" + " on " + date)
            file_obj.close()
            self.show_frame(HomePage)
        elif flag == 1:
            file_obj.write("\n**************************\n")
            file_obj.write("p: " + "nuetral" + " on " + date)
            file_obj.close()
            self.show_frame(HomePage)
        elif flag == 2:
            file_obj.write("\n**************************\n")
            file_obj.write("p: " + "pain" + " on " + date)
            file_obj.close()
            self.show_frame(HomePage)      

    def change_lang(self, controller):
        for F in (HomePage, ExtensionSettings, FlexionSettings, CycleSettings,
                  Manual, Preferences, Brightness, Language, PauseLimit,
                  Profiles, CreateProfile, DisplayProfile):
            frame = F(self.container, self)
            # initializing frame of that object from
            # HomePage, ExtensionSettings, FlexionSettings, CycleSettings respectively with
            # for loop
            controller.frames[F] = frame

            frame.place(relheight=1, relwidth=1)

        frame = controller.frames[Language]
        frame.tkraise()
                                                                         
    def save_profile(self, name, speed_choices, angleChoices, strtAngleChoices, maxCycleChoices, pinChoices, controller):
        # messagebox.showinfo("Say Hello", "Hello World")
        # write input validation for profile creation here
        
        validEntries = True
        
        if len(name.get()) > 10:
            validEntries = False
            messagebox.showinfo("Error!", "Name is too long!")
        elif len(name.get()) < 2:
            messagebox.showinfo("Error!", "Name is too short!")
            validEntries = False
        
        if not speed_choices.get().isdigit():
            messagebox.showinfo("Error!", "Invalid Speed")
            validEntries = False       
            
        if not angleChoices.get().isdigit():
            messagebox.showinfo("Error!", "Invalid Angle")
            validEntries = False
        
        if not strtAngleChoices.get().isdigit():
            messagebox.showinfo("Error!", "Invalid Starting Angle")
            validEntries = False
        
        if not pinChoices.get().isdigit():
            messagebox.showinfo("Error!", "Invalid Pin")
            validEntries = False
        
        if not len(pinChoices.get()) == 4:
            messagebox.showinfo("Error!", "Pin must be 4 digits")
            validEntries = False
        
        if not maxCycleChoices.get().isdigit():
            messagebox.showinfo("Error!", "Invalid Max Cycle")
            validEntries = False
        
        if int(angleChoices.get()) < 0 or int(angleChoices.get()) > 90:
            messagebox.showinfo("Error!", "Angle requirments not met! 0-90 only")
            validEntries = False    
        
        if int(maxCycleChoices.get()) < 1:
            messagebox.showinfo("Error!", "Valid Max Cycle value is 1 or more")
            validEntries = False
        
        if int(speed_choices.get()) < 1 or int(speed_choices.get()) > 5:
            messagebox.showinfo("Error!", "Speed requirments not met! 1-5 only")
            validEntries = False 
      
        if validEntries:    
            self.profile_name_sets.add(name.get() + ".txt")
            f = open("/home/pi/Downloads/users/" + name.get() + ".txt", "at")
            f.write(pinChoices.get() + "\n")
            f.write(name.get() + "\n")
            f.write(speed_choices.get() + "\n")
            f.write(angleChoices.get() + "\n")
            f.write(strtAngleChoices.get() + "\n")
            f.write(maxCycleChoices.get() + "\n")
            f.close()
            
            # clear all entry fields here
            name.delete(0, 'end')
            speed_choices.delete(0, 'end')
            angleChoices.delete(0, 'end')
            strtAngleChoices.delete(0, 'end')
            pinChoices.delete(0, 'end')
            maxCycleChoices.delete(0, 'end')
        
            self.add_profile(controller)
    
    def edit_profile(self, name, speed_choices, angleChoices, strtAngleChoices, maxCycleChoices, pinChoices, controller):
        # messagebox.showinfo("Say Hello", "Hello World")
        # write input validation for profile creation here
        
        validEntries = True
        
        if len(name) > 10:
            validEntries = False
            messagebox.showinfo("Error!", "Name is too long!")
        elif len(name) < 2:
            messagebox.showinfo("Error!", "Name is too short!")
            validEntries = False
        
        if not speed_choices.get().isdigit():
            messagebox.showinfo("Error!", "Invalid Speed")
            validEntries = False       
            
        if not angleChoices.get().isdigit():
            messagebox.showinfo("Error!", "Invalid Angle")
            validEntries = False
        
        if not strtAngleChoices.get().isdigit():
            messagebox.showinfo("Error!", "Invalid Starting Angle")
            validEntries = False
        
        if not pinChoices.isdigit():
            messagebox.showinfo("Error!", "Invalid Pin")
            validEntries = False
        
        if not len(pinChoices) == 4:
            messagebox.showinfo("Error!", "Pin must be 4 digits")
            validEntries = False
        
        if not maxCycleChoices.get().isdigit():
            messagebox.showinfo("Error!", "Invalid Max Cycle")
            validEntries = False
        
        if int(angleChoices.get()) < 0 or int(angleChoices.get()) > 90:
            messagebox.showinfo("Error!", "Angle requirments not met! 0-90 only")
            validEntries = False    
        
        if int(maxCycleChoices.get()) < 1:
            messagebox.showinfo("Error!", "Valid Max Cycle value is 1 or more")
            validEntries = False
        
        if int(speed_choices.get()) < 1 or int(speed_choices.get()) > 5:
            messagebox.showinfo("Error!", "Speed requirments not met! 1-5 only")
            validEntries = False 
      
        if validEntries:
            with open("/home/pi/Downloads/users/" + name + ".txt", "rt") as file:
                data = file.readlines()
                     
            data[0] = pinChoices + "\n"
            data[1] = name + "\n"
            data[2] = speed_choices.get() + "\n"
            data[3] = angleChoices.get() + "\n"
            data[4] = strtAngleChoices.get() + "\n"
            data[5] = maxCycleChoices.get() + "\n"
            
            with open("/home/pi/Downloads/users/" + name + ".txt", "wt") as file:
                file.writelines(data)
            
            # clear all entry fields here
            speed_choices.delete(0, 'end')
            angleChoices.delete(0, 'end')
            strtAngleChoices.delete(0, 'end')
            maxCycleChoices.delete(0, 'end')
        
            self.profile_displayer(controller, name+".txt")
    
    def pin_displayer(self, controller, flag, name):
        self.currentName = name
        self.flag = flag
        
        frame = PinInput(self.container, self)

        controller.frames[PinInput] = frame

        frame.place(relheight=1, relwidth=1)

        frame = controller.frames[PinInput]
        frame.tkraise()
    
    def profile_displayer(self, controller, name):
        self.currentName = name
        frame = DisplayProfile(self.container, self)

        controller.frames[DisplayProfile] = frame

        frame.place(relheight=1, relwidth=1)

        frame = controller.frames[DisplayProfile]
        frame.tkraise()

    def get_profile_name(self):
        return self.currentName
    
    def get_flag(self):
        return self.flag
    
    def num_of_profile(self):
        return self.Number_of_profiles

    def name_of_profiles(self):
        arr = [0 for a in range(5)]
        i = 0
    
        for e in self.profile_name_sets:
            arr[i] = str(e)
            i = i + 1
        # add more string processing to remove txt
        return arr
    
    def retract_act(self):
        bus.write_byte(i2cAdd, 0x1)
    
    def extend_act(self):
        bus.write_byte(i2cAdd, 0x2)

    def stop_act(self): 
        bus.write_byte(i2cAdd, 0x3)
        
    def inc_seat(self):
        bus.write_byte(i2cAdd, 0x4)
        
    def dec_seat(self):
        bus.write_byte(i2cAdd, 0x5)
         
    def stop_seat(self):
        bus.write_byte(i2cAdd, 0x6)
    
    def verify_profile_pin(self, flag, name, pinChoices):
        f = open("/home/pi/Downloads/users/" + name, "r")
        pin = tk.StringVar()
        myLine = f.readline()
        pin = myLine
        
        validEntries = True
        
        if not pinChoices.get().isdigit():
            validEntries = False
            
        if validEntries:
            if int(pin) == int(pinChoices.get()):
                if flag != 0:
                    pinChoices.delete(0, 'end')
                    self.profile_to_run(name)
                else:
                    pinChoices.delete(0, 'end')
                    self.display_edit_profile(self, name)
            else:
                messagebox.showinfo("Error!", "Incorrect Pin!")
        else:
            messagebox.showinfo("Error!", "Incorrect Pin!")
    
    def profile_to_run(self, name):
        f = open("/home/pi/Downloads/users/" + name, "r")
        self.currentName = name
        pin = tk.StringVar()
        myLine = f.readline()
        pin = myLine
        
        nameVal = tk.StringVar()
        myLine = f.readline()
        nameVal = myLine

        speedVal = tk.StringVar()
        myLine = f.readline()
        speedVal = myLine

        angleVal = tk.StringVar()
        myLine = f.readline()
        angleVal = myLine

        strtAngleVal = tk.StringVar()
        myLine = f.readline()
        strtAngleVal = myLine
        
        maxCycleVal = tk.StringVar()
        myLine = f.readline()
        maxCycleVal = myLine

        f.close()
        
        self.arr = [21, int(maxCycleVal), int(angleVal), int(speedVal), int(strtAngleVal)]
        self.show_frame(PainRegister)
    
    def log_out(self):
        # i2c read from slave and store infile 
        self.show_frame(Welcome)
        
    def activate_profile(self):
        for i in self.arr:
            bus.write_byte(i2cAdd, i)
             
    def show_pos(self):
        posData = bus.read_i2c_block_data(i2cAdd, 0, 3)
            
        final = ''.join(chr(x) for x in posData)
        
        if final[0] == 'x':
            pos = 0
        else:
            finalized = re.sub("[^0-9]", "", final)
            pos = int(finalized)/10
        print(str(pos) + " Degrees")
        

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        background = tk.Frame(self, bg='#ffe3d8')
        background.place(relwidth=1, relheight=1)
        if lang == "USEnglish":
            flexion_button = tk.Button(self, text="Flexion",
                                       command=lambda: controller.show_frame(FlexionSettings))
            flexion_button.place(relwidth=buttonRelWidth, relheight=buttonRelHeight)
            flexion_button.config(font=("Courier", 20))

            extension_button = tk.Button(self, text="Extension",
                                         command=lambda: controller.show_frame(ExtensionSettings))
            extension_button.place(relx=0.52, relwidth=buttonRelWidth, relheight=buttonRelHeight)
            extension_button.config(font=("Courier", 20))

            cycle_button = tk.Button(self, text="Cycle", command=lambda: controller.show_frame(CycleSettings))
            cycle_button.place(rely=0.23, relwidth=buttonRelWidth, relheight=buttonRelHeight)
            cycle_button.config(font=("Courier", 20))

            manual_button = tk.Button(self, text="Manual", command=lambda: controller.show_frame(Manual))
            manual_button.place(relx=0.52, rely=0.23, relwidth=buttonRelWidth, relheight=buttonRelHeight)
            manual_button.config(font=("Courier", 20))

            start_button = tk.Button(self, text=" Start \nSession",
                                          command=lambda: controller.activate_profile())
            start_button.place(relx=0.52, rely=0.46, relwidth=buttonRelWidth, relheight=buttonRelHeight)
            start_button.config(font=("Courier", 20))

            profiles_button = tk.Button(self, text="Profiles",
                                        command=lambda: controller.show_frame(Profiles))
            #profiles_button = tk.Button(self, text="Inc Height",
                         #               command=lambda: controller.dec_seat())
            profiles_button.place(rely=0.46, relwidth=buttonRelWidth, relheight=buttonRelHeight)
            profiles_button.config(font=("Courier", 20))

            log_out_button = tk.Button(self, text="Log Out",
                                     command=lambda: controller.log_out())
            
            #pause_button = tk.Button(self, text="Dec Height",
                           #          command=lambda: controller.inc_seat())
            log_out_button.place(rely=0.69, relwidth=buttonRelWidth, relheight=buttonRelHeight)
            log_out_button.config(font=("Courier", 20))

            pref_button = tk.Button(self, text="Preferences",
                                    command=lambda: controller.show_frame(Preferences))
            #pref_button = tk.Button(self, text="Stop Seat",
             #                       command=lambda: controller.stop_seat())
            pref_button.place(relx=0.52, rely=0.69, relwidth=buttonRelWidth, relheight=buttonRelHeight)
            pref_button.config(font=("Courier", 20))

            info = tk.LabelFrame(self, text="Stats", labelanchor='n')
            info.place(rely=0.92, relwidth=1, relheight=0.08)
            info.config(font=("Courier", 20))

        elif lang == "Spanish":
            flexion_button = tk.Button(self, text="Flexión",
                                       command=lambda: controller.show_frame(FlexionSettings))
            flexion_button.place(relwidth=buttonRelWidth, relheight=buttonRelHeight)
            flexion_button.config(font=("Courier", 20))

            extension_button = tk.Button(self, text="Extensión",
                                         command=lambda: controller.show_frame(ExtensionSettings))
            extension_button.place(relx=0.52, relwidth=buttonRelWidth, relheight=buttonRelHeight)
            extension_button.config(font=("Courier", 20))

            cycle_button = tk.Button(self, text="Ciclo", command=lambda: controller.show_frame(CycleSettings))
            cycle_button.place(rely=0.23, relwidth=buttonRelWidth, relheight=buttonRelHeight)
            cycle_button.config(font=("Courier", 20))

            manual_button = tk.Button(self, text="Manual", command=lambda: controller.show_frame(Manual))
            manual_button.place(relx=0.52, rely=0.23, relwidth=buttonRelWidth, relheight=buttonRelHeight)
            manual_button.config(font=("Courier", 20))

            stop_start_button = tk.Button(self, text="Alto/Comienzo")
            stop_start_button.place(relx=0.52, rely=0.46, relwidth=buttonRelWidth, relheight=buttonRelHeight)
            stop_start_button.config(font=("Courier", 20))

            profiles_button = tk.Button(self, text="Perfiles", command=lambda: controller.show_profile(Profiles))
            profiles_button.place(rely=0.46, relwidth=buttonRelWidth, relheight=buttonRelHeight)
            profiles_button.config(font=("Courier", 20))

            pause_button = tk.Button(self, text="Pausa")
            pause_button.place(rely=0.69, relwidth=buttonRelWidth, relheight=buttonRelHeight)
            pause_button.config(font=("Courier", 20))

            pref_button = tk.Button(self, text="Preferencias", command=lambda: controller.show_frame(Preferences))
            pref_button.place(relx=0.52, rely=0.69, relwidth=buttonRelWidth, relheight=buttonRelHeight)
            pref_button.config(font=("Courier", 20))

            info = tk.LabelFrame(self, text="Estadísticas", labelanchor='n')
            info.place(rely=0.92, relwidth=1, relheight=0.08)
            info.config(font=("Courier", 20))

        elif lang == "Chinese":
            flexion_button = tk.Button(self, text="屈曲",
                                       command=lambda: controller.show_frame(FlexionSettings))
            flexion_button.place(relwidth=buttonRelWidth, relheight=buttonRelHeight)
            flexion_button.config(font=("Courier", 20))

            extension_button = tk.Button(self, text="延期",
                                         command=lambda: controller.show_frame(ExtensionSettings))
            extension_button.place(relx=0.52, relwidth=buttonRelWidth, relheight=buttonRelHeight)
            extension_button.config(font=("Courier", 20))

            cycle_button = tk.Button(self, text="週期", command=lambda: controller.show_frame(CycleSettings))
            cycle_button.place(rely=0.23, relwidth=buttonRelWidth, relheight=buttonRelHeight)
            cycle_button.config(font=("Courier", 20))

            manual_button = tk.Button(self, text="手冊", command=lambda: controller.show_frame(Manual))
            manual_button.place(relx=0.52, rely=0.23, relwidth=buttonRelWidth, relheight=buttonRelHeight)
            manual_button.config(font=("Courier", 20))

            stop_start_button = tk.Button(self, text="停止/開始")
            stop_start_button.place(relx=0.52, rely=0.46, relwidth=buttonRelWidth, relheight=buttonRelHeight)
            stop_start_button.config(font=("Courier", 20))

            profiles_button = tk.Button(self, text="型材", command=lambda: controller.show_profile(Profiles))
            profiles_button.place(rely=0.46, relwidth=buttonRelWidth, relheight=buttonRelHeight)
            profiles_button.config(font=("Courier", 20))

            pause_button = tk.Button(self, text="暫停")
            pause_button.place(rely=0.69, relwidth=buttonRelWidth, relheight=buttonRelHeight)
            pause_button.config(font=("Courier", 20))

            pref_button = tk.Button(self, text="偏好", command=lambda: controller.show_frame(Preferences))
            pref_button.place(relx=0.52, rely=0.69, relwidth=buttonRelWidth, relheight=buttonRelHeight)
            pref_button.config(font=("Courier", 20))

            info = tk.LabelFrame(self, text="統計資料", labelanchor='n')
            info.place(rely=0.92, relwidth=1, relheight=0.08)
            info.config(font=("Courier", 20))

    def __del__(self):
        print('object deleted')


###########################################################################
class ExtensionSettings(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        background = tk.Frame(self, bg='#ffe3d8')
        background.place(relwidth=1, relheight=1)
        global lang
        lang = 'Spanish'
        extension_speed_label = tk.Label(self, text="Speed of \n Ext.", bg='#ffe3d8')
        extension_speed_label.place(relx=0.15, rely=0.25, relwidth=0.3)
        extension_speed_label.config(font=("Courier", 18))

        # command option needed to take on input and use it for linear actuator
        ext_speed_choices = tk.Spinbox(self, from_=0, to=5, justify='center', state='readonly')
        ext_speed_choices.place(relx=0.45, rely=0.17, relwidth=0.3, relheight=0.2)
        ext_speed_choices.config(font=("Courier", 40))

        extension_limit_label = tk.Label(self, text="Limit of \n Ext.", bg='#ffe3d8')
        extension_limit_label.place(relx=0.15, rely=0.65, relwidth=0.3)
        extension_limit_label.config(font=("Courier", 18))

        # command option needed to take on input and use it for linear actuator
        ext_limit_choices = tk.Spinbox(self, from_=0, to=5, justify='center', state='readonly')
        ext_limit_choices.place(relx=0.45, rely=0.57, relwidth=0.3, relheight=0.2)
        ext_limit_choices.config(font=("Courier", 40))

        back_button = tk.Button(self, text="Home Page", command=lambda: controller.show_frame(HomePage))
        back_button.place(relx=0.05, rely=0.93, relwidth=0.3, relheight=0.05)

    # third window frame FlexionSettings


###########################################################################
class FlexionSettings(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        background = tk.Frame(self, bg='#ffe3d8')
        background.place(relwidth=1, relheight=1)

        flexion_speed_label = tk.Label(self, text="Speed of \n Flex.", bg='#ffe3d8')
        flexion_speed_label.place(relx=0.15, rely=0.25, relwidth=0.3)
        flexion_speed_label.config(font=("Courier", 18))

        # command option needed to take on input and use it for linear actuator
        flex_speed_choices = tk.Spinbox(self, from_=0, to=5, justify='center', state='readonly')
        flex_speed_choices.place(relx=0.45, rely=0.17, relwidth=0.3, relheight=0.2)
        flex_speed_choices.config(font=("Courier", 40))

        flexion_limit_label = tk.Label(self, text="Limit of \n Flex.", bg='#ffe3d8')
        flexion_limit_label.place(relx=0.15, rely=0.65, relwidth=0.3)
        flexion_limit_label.config(font=("Courier", 18))

        # command option needed to take on input and use it for linear actuator
        flex_limit_choices = tk.Spinbox(self, from_=0, to=5, justify='center', state='readonly')
        flex_limit_choices.place(relx=0.45, rely=0.57, relwidth=0.3, relheight=0.2)
        flex_limit_choices.config(font=("Courier", 40))

        back_button = tk.Button(self, text="Home Page", command=lambda: controller.show_frame(HomePage))
        back_button.place(relx=0.05, rely=0.93, relwidth=0.3, relheight=0.05)


###########################################################################
class CycleSettings(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        background = tk.Frame(self, bg='#ffe3d8')
        background.place(relwidth=1, relheight=1)

        cycle_limit_label = tk.Label(self, text="Cycle\nLimit", bg='#ffe3d8')
        cycle_limit_label.place(relx=0.15, rely=0.25, relwidth=0.3)
        cycle_limit_label.config(font=("Courier", 18))

        # command option is needed to take in input and use it for linear actuator
        cycle_limit_choices = tk.Spinbox(self, from_=1, to=50, justify='center', state='readonly')
        cycle_limit_choices.place(relx=0.45, rely=0.17, relwidth=0.3, relheight=0.2)
        cycle_limit_choices.config(font=("Courier", 40))

        back_button = tk.Button(self, text="Home Page", command=lambda: controller.show_frame(HomePage))
        back_button.place(relx=0.05, rely=0.93, relwidth=0.3, relheight=0.05)


###########################################################################
class Manual(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        background = tk.Frame(self, bg='#ffe3d8')
        background.place(relwidth=1, relheight=1)

        # command option is needed to take in input and use it for linear actuator
        extend_speed_choices = tk.Spinbox(self, from_=0, to=5, justify='left', width=5, state='readonly')
        extend_speed_choices.place(relx=0.63, rely=0.20, relwidth=0.17, relheight=0.2)
        extend_speed_choices.config(font=("Courier", 40))

        extend_button = tk.Button(self, text="Extend",
                                  command=lambda: controller.extend_act())
        extend_button.place(relx=0.25, rely=0.20, relwidth=0.38, relheight=0.2)
        extend_button.config(font=("Courier", 20))
        
        stop_button = tk.Button(self, text="Stop",
                                  command=lambda: controller.stop_act())
        stop_button.place(relx=0.35, rely=0.47, relwidth=0.20, relheight=0.1)
        stop_button.config(font=("Courier", 20))
        
        
        # command option is needed to take in input and use it for linear actuator
        flex_speed_choices = tk.Spinbox(self, from_=0, to=5, justify='left', width=5, state='readonly')
        flex_speed_choices.place(relx=0.63, rely=0.65, relwidth=0.17, relheight=0.2)
        flex_speed_choices.config(font=("Courier", 40))
        
        flex_button = tk.Button(self, text="Flex",
                                  command=lambda: controller.retract_act())
        flex_button.place(relx=0.25, rely=0.65, relwidth=0.38, relheight=0.2)
        flex_button.config(font=("Courier", 20))

        back_button = tk.Button(self, text="Home Page", command=lambda: controller.show_frame(HomePage))
        back_button.place(relx=0.05, rely=0.93, relwidth=0.3, relheight=0.05)


###########################################################################
class SeatConfig(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        background = tk.Frame(self, bg='#ffe3d8')
        background.place(relwidth=1, relheight=1)

        # command option is needed to take in input and use it for linear actuator
        
        increase_button = tk.Button(self, text="Increase Height",
                                  command=lambda: controller.inc_seat())
        increase_button.place(relx=0.25, rely=0.15, relwidth=0.55, relheight=0.2)
        increase_button.config(font=("Courier", 20))


        stop_button = tk.Button(self, text="STOP",
                                  command=lambda: controller.stop_seat())
        stop_button.place(relx=0.38, rely=0.42, relwidth=0.30, relheight=0.1)
        stop_button.config(font=("Courier", 20))


        # command option is needed to take in input and use it for linear actuator
        decrease_button = tk.Button(self, text="Decrease Height",
                                  command=lambda: controller.dec_seat())
        decrease_button.place(relx=0.25, rely=0.60, relwidth=0.55, relheight=0.2)
        decrease_button.config(font=("Courier", 20))

        home_button = tk.Button(self, text="Home Page", command=lambda: controller.show_frame(HomePage))
        home_button.place(relx=0.05, rely=0.93, relwidth=0.3, relheight=0.05)


###########################################################################
class Preferences(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        background = tk.Frame(self, bg='#ffe3d8')
        background.place(relwidth=1, relheight=1)

        page_label = tk.Label(self, text="Preferences", bg='#ffe3d8')
        page_label.place(relx=0.23, rely=0.05)
        page_label.config(font=("Courier", 30))

        lang_button = tk.Button(self, text="Language", command=lambda: controller.show_frame(Language))
        lang_button.place(relx=0.2, rely=0.15, relwidth=0.6, relheight=0.15)
        lang_button.config(font=("Courier", 20))

        brightness_button = tk.Button(self, text="Brightness", command=lambda: controller.show_frame(Brightness))
        brightness_button.place(relx=0.2, rely=0.3, relwidth=0.6, relheight=0.15)
        brightness_button.config(font=("Courier", 20))

        pause_limit_button = tk.Button(self, text="Pause\nTime Limit",
                                       command=lambda: controller.show_frame(PauseLimit))
        pause_limit_button.place(relx=0.2, rely=0.45, relwidth=0.6, relheight=0.15)
        pause_limit_button.config(font=("Courier", 20))

        seat_arranging_button = tk.Button(self, text="Arrange Seat",
                                       command=lambda: controller.show_frame(SeatConfig))
        seat_arranging_button.place(relx=0.2, rely=0.60, relwidth=0.6, relheight=0.15)
        seat_arranging_button.config(font=("Courier", 20))

        back_button = tk.Button(self, text="Home Page", command=lambda: controller.show_frame(HomePage))
        back_button.place(relx=0.05, rely=0.93, relwidth=0.3, relheight=0.05)


###########################################################################
class Brightness(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        background = tk.Frame(self, bg='#ffe3d8')
        background.place(relwidth=1, relheight=1)

        page_label = tk.Label(self, text="Brightness", bg='#ffe3d8')
        page_label.place(relx=0.25, rely=0.05)
        page_label.config(font=("Courier", 30))

        inc_button = tk.Button(self, text="Increase")
        inc_button.place(relx=0.2, rely=0.15, relwidth=0.6, relheight=0.2)
        inc_button.config(font=("Courier", 20))

        dec_button = tk.Button(self, text="Decrease")
        dec_button.place(relx=0.2, rely=0.60, relwidth=0.6, relheight=0.2)
        dec_button.config(font=("Courier", 20))

        back_button = tk.Button(self, text="Home Page", command=lambda: controller.show_frame(HomePage))
        back_button.place(relx=0.05, rely=0.93, relwidth=0.3, relheight=0.05)


###########################################################################
class Language(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        background = tk.Frame(self, bg='#ffe3d8')
        background.place(relwidth=1, relheight=1)

        lang_choice = tk.StringVar()
        lang_choice.set(None)
        page_label = tk.Label(self, text='Language', bg='#ffe3d8')
        page_label.place(relx=0.3, rely=0.03)
        page_label.config(font=("Courier", 30))

        option_1 = tk.Radiobutton(self, text='US English', variable=lang_choice, value='USEnglish', bg='#ffe3d8',
                                  tristatevalue='lola')
        option_1.place(relx=0.2, rely=0.10, relwidth=0.6, relheight=0.2)
        option_1.config(font=("Courier", 20))

        option_2 = tk.Radiobutton(self, text='中文', variable=lang_choice, value='Chinese', bg='#ffe3d8',
                                  command=sel(lang_choice))
        option_2.place(relx=0.2, rely=0.25, relwidth=0.6, relheight=0.2)
        option_2.config(font=("Courier", 20))

        option_3 = tk.Radiobutton(self, text='Español', variable=lang_choice, value='Spanish', bg='#ffe3d8')
        option_3.place(relx=0.2, rely=0.40, relwidth=0.6, relheight=0.2)
        option_3.config(font=("Courier", 20))

        back_button = tk.Button(self, text='Home Page', command=lambda: controller.show_frame(HomePage))
        back_button.place(relx=0.05, rely=0.93, relwidth=0.3, relheight=0.05)


def sel(t):
    selection = "You selected the option " + t.get()
    print(selection)


###########################################################################
class PauseLimit(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        background = tk.Frame(self, bg='#ffe3d8')
        background.place(relwidth=1, relheight=1)
        var = tk.IntVar()

        page_label = tk.Label(self, text="Pause Time Limit", bg='#ffe3d8')
        page_label.place(relx=0.10, rely=0.05)
        page_label.config(font=("Courier", 30))

        option_1 = tk.Radiobutton(self, text="1 Minute", variable=var, value=60, bg='#ffe3d8')
        option_1.place(relx=0.2, rely=0.14, relwidth=0.6, relheight=0.2)
        option_1.config(font=("Courier", 20))

        option_2 = tk.Radiobutton(self, text="30 Seconds", variable=var, value=30, bg='#ffe3d8')
        option_2.place(relx=0.2, rely=0.29, relwidth=0.6, relheight=0.2)
        option_2.config(font=("Courier", 20))

        option_3 = tk.Radiobutton(self, text="15 Seconds", variable=var, value=15, bg='#ffe3d8')
        option_3.place(relx=0.2, rely=0.44, relwidth=0.6, relheight=0.2)
        option_3.config(font=("Courier", 20))

        back_button = tk.Button(self, text="Home Page", command=lambda: controller.show_frame(HomePage))
        back_button.place(relx=0.05, rely=0.93, relwidth=0.3, relheight=0.05)


###########################################################################
class xxxProfiles(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        background = tk.Frame(self, bg='#ffe3d8')
        background.place(relwidth=1, relheight=1)

        add_profile_button = tk.Button(self, text="+", justify='center',
                                       command=lambda: controller.show_frame(CreateProfile))
        add_profile_button.place(relx=0.85, rely=0.93, relwidth=0.1, relheight=0.05)
        add_profile_button.config(font=("Courier", 40))

        back_button = tk.Button(self, text="Home Page", command=lambda: controller.show_frame(HomePage))
        back_button.place(relx=0.05, rely=0.93, relwidth=0.3, relheight=0.05)


###########################################################################
class Welcome(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        background = tk.Frame(self, bg='#ffe3d8')
        background.place(relwidth=1, relheight=1)
        
        global logo_photo
        
        logo_photo = PhotoImage(file='logo.png')     
            
        logo = tk.Label(self, image=logo_photo, bg='#ffe3d8')
        logo.place(relx=0.25, rely=0.12, relwidth=buttonRelWidth, relheight=buttonRelHeight)
        
        num = controller.num_of_profile()
        a = controller.name_of_profiles()

        if num == 0:
            pass
        elif num == 1:
            setFlag = 1
            profile1 = tk.Button(self, text=rmv_dot_txt(a[num - 1]),
                                 command=lambda: controller.pin_displayer(controller, setFlag, a[num  - 1]))
            profile1.place(relx=0.2, rely=0.35, relwidth=0.6, relheight=0.1)
            profile1.config(font=("Courier", 30))
        elif num == 2:
            setFlag = 1
            profile1 = tk.Button(self, text=rmv_dot_txt(a[num - 2]),
                                 command=lambda: controller.pin_displayer(controller, setFlag, a[num  - 2]))
            profile1.place(relx=0.2, rely=0.35, relwidth=0.6, relheight=0.1)
            profile1.config(font=("Courier", 30))

            profile2 = tk.Button(self, text=rmv_dot_txt(a[num - 1]),
                                 command=lambda: controller.pin_displayer(controller, setFlag, a[num  - 1]))
            profile2.place(relx=0.2, rely=0.45, relwidth=0.6, relheight=0.1)
            profile2.config(font=("Courier", 30))
        elif num == 3:
            setFlag = 1
            profile1 = tk.Button(self, text=rmv_dot_txt(a[num - 3]),
                                 command=lambda: controller.pin_displayer(controller, setFlag, a[num  - 3]))
            profile1.place(relx=0.2, rely=0.35, relwidth=0.6, relheight=0.1)
            profile1.config(font=("Courier", 30))

            profile2 = tk.Button(self, text=rmv_dot_txt(a[num - 2]),
                                 command=lambda: controller.pin_displayer(controller, setFlag, a[num  - 2]))
            profile2.place(relx=0.2, rely=0.45, relwidth=0.6, relheight=0.1)
            profile2.config(font=("Courier", 30))

            profile3 = tk.Button(self, text=rmv_dot_txt(a[num - 1]),
                                 command=lambda: controller.pin_displayer(controller, setFlag, a[num  - 1]))
            profile3.place(relx=0.2, rely=0.55, relwidth=0.6, relheight=0.1)
            profile3.config(font=("Courier", 30))

        elif num == 4:
            setFlag = 1
            profile1 = tk.Button(self, text=rmv_dot_txt(a[num - 4]),
                                 command=lambda: controller.pin_displayer(controller, setFlag, a[num  - 4]))
            profile1.place(relx=0.2, rely=0.35, relwidth=0.6, relheight=0.1)
            profile1.config(font=("Courier", 30))

            profile2 = tk.Button(self, text=rmv_dot_txt(a[num - 3]),
                                 command=lambda: controller.pin_displayer(controller, setFlag, a[num  - 3]))
            profile2.place(relx=0.2, rely=0.45, relwidth=0.6, relheight=0.1)
            profile2.config(font=("Courier", 30))

            profile3 = tk.Button(self, text=rmv_dot_txt(a[num - 2]),
                                 command=lambda: controller.pin_displayer(controller, setFlag, a[num  - 2]))
            profile3.place(relx=0.2, rely=0.55, relwidth=0.6, relheight=0.1)
            profile3.config(font=("Courier", 30))

            profile4 = tk.Button(self, text=rmv_dot_txt(a[num - 1]),
                                 command=lambda: controller.pin_displayer(controller, setFlag, a[num  - 1]))
            profile4.place(relx=0.2, rely=0.65, relwidth=0.6, relheight=0.1)
            profile4.config(font=("Courier", 30))
        elif num == 5:
            setFlag = 1
            profile1 = tk.Button(self, text=rmv_dot_txt(a[num - 5]),
                                 command=lambda: controller.pin_displayer(controller, setFlag, a[num  - 5]))
            profile1.place(relx=0.2, rely=0.35, relwidth=0.6, relheight=0.1)
            profile1.config(font=("Courier", 30))

            profile2 = tk.Button(self, text=rmv_dot_txt(a[num - 4]),
                                 command=lambda: controller.pin_displayer(controller, setFlag, a[num  - 4]))
            profile2.place(relx=0.2, rely=0.45, relwidth=0.6, relheight=0.1)
            profile2.config(font=("Courier", 30))

            profile3 = tk.Button(self, text=rmv_dot_txt(a[num - 3]),
                                 command=lambda: controller.pin_displayer(controller, setFlag, a[num  - 3]))
            profile3.place(relx=0.2, rely=0.55, relwidth=0.6, relheight=0.1)
            profile3.config(font=("Courier", 30))

            profile4 = tk.Button(self, text=rmv_dot_txt(a[num - 2]),
                                 command=lambda: controller.pin_displayer(controller, setFlag, a[num  - 2]))
            profile4.place(relx=0.2, rely=0.65, relwidth=0.6, relheight=0.1)
            profile4.config(font=("Courier", 30))

            profile5 = tk.Button(self, text=rmv_dot_txt(a[num - 1]),
                                 command=lambda: controller.pin_displayer(controller, setFlag, a[num  - 1]))
            profile5.place(relx=0.2, rely=0.75, relwidth=0.6, relheight=0.1)
            profile5.config(font=("Courier", 30))

        add_profile_button = tk.Button(self, text="New User", justify='center',
                                       command=lambda: controller.show_frame(CreateProfile))
        add_profile_button.place(relx=0.55, rely=0.93, relwidth=0.4, relheight=0.05)
        add_profile_button.config(font=("Courier", 25))


###########################################################################
class Profiles(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        background = tk.Frame(self, bg='#ffe3d8')
        background.place(relwidth=1, relheight=1)
        num = controller.num_of_profile()
        a = controller.name_of_profiles()

        if num == 0:
            pass
        elif num == 1:
            profile1 = tk.Button(self, text=rmv_dot_txt(a[num - 1]),
                                 command=lambda: controller.profile_displayer(controller, a[num - 1]))
            profile1.place(relx=0.2, rely=0.15, relwidth=0.6, relheight=0.1)
            profile1.config(font=("Courier", 30))
        elif num == 2:
            profile1 = tk.Button(self, text=rmv_dot_txt(a[num - 2]),
                                 command=lambda: controller.profile_displayer(controller, a[num - 2]))
            profile1.place(relx=0.2, rely=0.15, relwidth=0.6, relheight=0.1)
            profile1.config(font=("Courier", 30))

            profile2 = tk.Button(self, text=rmv_dot_txt(a[num - 1]),
                                 command=lambda: controller.profile_displayer(controller, a[num - 1]))
            profile2.place(relx=0.2, rely=0.25, relwidth=0.6, relheight=0.1)
            profile2.config(font=("Courier", 30))
        elif num == 3:
            profile1 = tk.Button(self, text=rmv_dot_txt(a[num - 3]),
                                 command=lambda: controller.profile_displayer(controller, a[num - 3]))
            profile1.place(relx=0.2, rely=0.15, relwidth=0.6, relheight=0.1)
            profile1.config(font=("Courier", 30))

            profile2 = tk.Button(self, text=rmv_dot_txt(a[num - 2]),
                                 command=lambda: controller.profile_displayer(controller, a[num - 2]))
            profile2.place(relx=0.2, rely=0.25, relwidth=0.6, relheight=0.1)
            profile2.config(font=("Courier", 30))

            profile3 = tk.Button(self, text=rmv_dot_txt(a[num - 1]),
                                 command=lambda: controller.profile_displayer(controller, a[num - 1]))
            profile3.place(relx=0.2, rely=0.35, relwidth=0.6, relheight=0.1)
            profile3.config(font=("Courier", 30))

        elif num == 4:
            profile1 = tk.Button(self, text=rmv_dot_txt(a[num - 4]),
                                 command=lambda: controller.profile_displayer(controller, a[num - 4]))
            profile1.place(relx=0.2, rely=0.15, relwidth=0.6, relheight=0.1)
            profile1.config(font=("Courier", 30))

            profile2 = tk.Button(self, text=rmv_dot_txt(a[num - 3]),
                                 command=lambda: controller.profile_displayer(controller, a[num - 3]))
            profile2.place(relx=0.2, rely=0.25, relwidth=0.6, relheight=0.1)
            profile2.config(font=("Courier", 30))

            profile3 = tk.Button(self, text=rmv_dot_txt(a[num - 2]),
                                 command=lambda: controller.profile_displayer(controller, a[num - 2]))
            profile3.place(relx=0.2, rely=0.35, relwidth=0.6, relheight=0.1)
            profile3.config(font=("Courier", 30))

            profile4 = tk.Button(self, text=rmv_dot_txt(a[num - 1]),
                                 command=lambda: controller.profile_displayer(controller, a[num - 1]))
            profile4.place(relx=0.2, rely=0.45, relwidth=0.6, relheight=0.1)
            profile4.config(font=("Courier", 30))
        elif num == 5:
            profile1 = tk.Button(self, text=rmv_dot_txt(a[num - 5]),
                                 command=lambda: controller.profile_displayer(controller, a[num - 5]))
            profile1.place(relx=0.2, rely=0.15, relwidth=0.6, relheight=0.1)
            profile1.config(font=("Courier", 30))

            profile2 = tk.Button(self, text=rmv_dot_txt(a[num - 4]),
                                 command=lambda: controller.profile_displayer(controller, a[num - 4]))
            profile2.place(relx=0.2, rely=0.25, relwidth=0.6, relheight=0.1)
            profile2.config(font=("Courier", 30))

            profile3 = tk.Button(self, text=rmv_dot_txt(a[num - 3]),
                                 command=lambda: controller.profile_displayer(controller, a[num - 3]))
            profile3.place(relx=0.2, rely=0.35, relwidth=0.6, relheight=0.1)
            profile3.config(font=("Courier", 30))

            profile4 = tk.Button(self, text=rmv_dot_txt(a[num - 2]),
                                 command=lambda: controller.profile_displayer(controller, a[num - 2]))
            profile4.place(relx=0.2, rely=0.45, relwidth=0.6, relheight=0.1)
            profile4.config(font=("Courier", 30))

            profile5 = tk.Button(self, text=rmv_dot_txt(a[num - 1]),
                                 command=lambda: controller.profile_displayer(controller, a[num - 1]))
            profile5.place(relx=0.2, rely=0.55, relwidth=0.6, relheight=0.1)
            profile5.config(font=("Courier", 30))

        add_profile_button = tk.Button(self, text="+", justify='center',
                                       command=lambda: controller.show_frame(CreateProfile))
        add_profile_button.place(relx=0.85, rely=0.93, relwidth=0.1, relheight=0.05)
        add_profile_button.config(font=("Courier", 30))

        back_button = tk.Button(self, text="Home Page", command=lambda: controller.show_frame(HomePage))
        back_button.place(relx=0.05, rely=0.93, relwidth=0.3, relheight=0.05)


###########################################################################
class CreateProfile(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        background = tk.Frame(self, bg='#ffe3d8')
        background.place(relwidth=1, relheight=1)

        name = tk.Label(self, text="Name", bg='#ffe3d8', anchor="w")
        name.config(font=("Courier", 15))
        name.place(relx=0.05, rely=0.13)

        nameEntry = tk.Entry(self, bd=5)
        nameEntry.place(relx=0.45, rely=0.13)

        speed = tk.Label(self, text="Speed", bg='#ffe3d8', anchor="w")
        speed.config(font=("Courier", 15))
        speed.place(relx=0.05, rely=0.23)

        speed_choices = tk.Entry(self, bd=5)
        speed_choices.place(relx=0.45, rely=0.23)

        angle = tk.Label(self, text="Angle", bg='#ffe3d8', anchor="w")
        angle.config(font=("Courier", 15))
        angle.place(relx=0.05, rely=0.33)

        angleChoices = tk.Entry(self, bd=5)
        angleChoices.place(relx=0.45, rely=0.33)

        strtAngle = tk.Label(self, text="Starting Angle", bg='#ffe3d8', anchor="w")
        strtAngle.config(font=("Courier", 15))
        strtAngle.place(relx=0.05, rely=0.43)

        strtAngleChoices = tk.Entry(self, bd=5)
        strtAngleChoices.place(relx=0.45, rely=0.43)

        maxCycle = tk.Label(self, text="Max Cycles", bg='#ffe3d8', anchor="w")
        maxCycle.config(font=("Courier", 15))
        maxCycle.place(relx=0.05, rely=0.53)

        maxCycleChoices = tk.Entry(self, bd=5)
        maxCycleChoices.place(relx=0.45, rely=0.53)
        
        pin = tk.Label(self, text="Security Pin", bg='#ffe3d8', anchor="w")
        pin.config(font=("Courier", 15))
        pin.place(relx=0.05, rely=0.63)

        pinChoices = tk.Entry(self, bd=5)
        pinChoices.place(relx=0.45, rely=0.63)

        cancel_button = tk.Button(self, text="Cancel", command=lambda: controller.show_frame(Profiles))
        cancel_button.place(relx=0.05, rely=0.93, relwidth=0.3, relheight=0.05)

        submit_button = tk.Button(self, text="Submit",
                                  command=lambda: controller.save_profile(nameEntry,
                                                                          speed_choices,
                                                                          angleChoices,
                                                                          strtAngleChoices,
                                                                          maxCycleChoices,
                                                                          pinChoices,
                                                                          controller))
        submit_button.place(relx=0.64, rely=0.93, relwidth=0.3, relheight=0.05)


###########################################################################
class EditProfile(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        background = tk.Frame(self, bg='#ffe3d8')
        background.place(relwidth=1, relheight=1)

        f = controller.get_curr_file()
        if f == "":
            pass
        elif f != "":
            pin = tk.StringVar()
            myLine = f.readline()
            pin = myLine.replace("\n", "")

            nameVal = tk.StringVar()
            myLine = f.readline()
            nameVal = myLine.replace("\n", "")

            speedVal = tk.StringVar()
            myLine = f.readline()
            speedVal = myLine.replace("\n", "")

            angleVal = tk.StringVar()
            myLine = f.readline()
            angleVal = myLine.replace("\n", "")

            strtAngleVal = tk.StringVar()
            myLine = f.readline()
            strtAngleVal = myLine.replace("\n", "")

            maxCycleVal = tk.StringVar()
            myLine = f.readline()
            maxCycleVal = myLine.replace("\n", "")

            f.close()

            name = tk.Label(self, text="Name", bg='#ffe3d8', anchor="w")
            name.config(font=("Courier", 15))
            name.place(relx=0.05, rely=0.13)

            nameEntry = tk.Label(self, text=nameVal, bg='#ffe3d8')
            nameEntry.place(relx=0.45, rely=0.13)

            speed = tk.Label(self, text="Speed", bg='#ffe3d8', anchor="w")
            speed.config(font=("Courier", 15))
            speed.place(relx=0.05, rely=0.23)
            
            speed_choice = tk.Entry(self, bd=5)
            speed_choice.config(font=("Courier", 15))
            speed_choice.insert('end', speedVal)
            speed_choice.place(relx=0.45, rely=0.23, relwidth=0.2)

            angle = tk.Label(self, text="Angle", bg='#ffe3d8', anchor="w")
            angle.config(font=("Courier", 15))
            angle.place(relx=0.05, rely=0.33)

            angleChoice = tk.Entry(self, bd=5)
            angleChoice.config(font=("Courier", 15))
            angleChoice.insert('end', angleVal)
            angleChoice.place(relx=0.45, rely=0.33, relwidth=0.2)

            strtAngle = tk.Label(self, text="Starting Angle", bg='#ffe3d8', anchor="w")
            strtAngle.config(font=("Courier", 15))
            strtAngle.place(relx=0.05, rely=0.43)

            strtAngleChoice = tk.Entry(self, bd=5)
            strtAngleChoice.config(font=("Courier", 15))
            strtAngleChoice.insert('end', strtAngleVal)
            strtAngleChoice.place(relx=0.45, rely=0.43, relwidth=0.2)

            maxCycle = tk.Label(self, text="Max Cycles", bg='#ffe3d8', anchor="w")
            maxCycle.config(font=("Courier", 15))
            maxCycle.place(relx=0.05, rely=0.53)

            maxCycleChoice = tk.Entry(self, bd=5)
            maxCycleChoice.config(font=("Courier", 15))
            maxCycleChoice.insert('end', maxCycleVal)
            maxCycleChoice.place(relx=0.45, rely=0.53, relwidth=0.2)

        back_button = tk.Button(self, text="Cancel", command=lambda: controller.show_frame(Profiles))
        back_button.place(relx=0.05, rely=0.93, relwidth=0.3, relheight=0.05)

        del_button = tk.Button(self, text="Delete",
                               command=lambda: controller.del_profile(controller, controller.get_profile_name()))
        del_button.place(relx=0.345, rely=0.93, relwidth=0.3, relheight=0.05)

        save_button = tk.Button(self, text="Save", command=lambda: controller.edit_profile(nameVal,
                                                                          speed_choice,
                                                                          angleChoice,
                                                                          strtAngleChoice,
                                                                          maxCycleChoice,
                                                                          pin,
                                                                          controller))
        save_button.place(relx=0.64, rely=0.93, relwidth=0.3, relheight=0.05)


###########################################################################
class DisplayProfile(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        background = tk.Frame(self, bg='#ffe3d8')
        background.place(relwidth=1, relheight=1)

        fName = controller.get_profile_name()

        if len(fName) > 0:
            setFlag = 2
            f = open("/home/pi/Downloads/users/" + fName, "r")
            
            pin = tk.StringVar()
            myLine = f.readline()
            pin = myLine

            nameVal = tk.StringVar()
            myLine = f.readline()
            nameVal = myLine

            speedVal = tk.StringVar()
            myLine = f.readline()
            speedVal = myLine

            angleVal = tk.StringVar()
            myLine = f.readline()
            angleVal = myLine

            strtAngleVal = tk.StringVar()
            myLine = f.readline()
            strtAngleVal = myLine

            maxCycleVal = tk.StringVar()
            myLine = f.readline()
            maxCycleVal = myLine

            f.close()

            name = tk.Label(self, text="Name", bg='#ffe3d8', anchor="w")
            name.config(font=("Courier", 15))
            name.place(relx=0.05, rely=0.13)

            nameEntry = tk.Label(self, text=nameVal, bg='#ffe3d8')
            nameEntry.place(relx=0.45, rely=0.13)

            speed = tk.Label(self, text="Speed", bg='#ffe3d8', anchor="w")
            speed.config(font=("Courier", 15))
            speed.place(relx=0.05, rely=0.23)

            speed_choice = tk.Label(self, text=speedVal, bg='#ffe3d8')
            speed_choice.place(relx=0.45, rely=0.23)

            angle = tk.Label(self, text="Angle", bg='#ffe3d8', anchor="w")
            angle.config(font=("Courier", 15))
            angle.place(relx=0.05, rely=0.33)

            angleChoice = tk.Label(self, text=angleVal, bg='#ffe3d8')
            angleChoice.place(relx=0.45, rely=0.33)

            strtAngle = tk.Label(self, text="Starting Angle", bg='#ffe3d8', anchor="w")
            strtAngle.config(font=("Courier", 15))
            strtAngle.place(relx=0.05, rely=0.43)

            strtAngleChoice = tk.Label(self, text=strtAngleVal, bg='#ffe3d8')
            strtAngleChoice.place(relx=0.45, rely=0.43)

            maxCycle = tk.Label(self, text="Max Cycles", bg='#ffe3d8', anchor="w")
            maxCycle.config(font=("Courier", 15))
            maxCycle.place(relx=0.05, rely=0.53)

            maxCycleChoices = tk.Label(self, text=maxCycleVal, bg='#ffe3d8')
            maxCycleChoices.place(relx=0.45, rely=0.53)

        back_button = tk.Button(self, text="<-", command=lambda: controller.show_frame(Profiles))
        back_button.place(relx=0.05, rely=0.93, relwidth=0.3, relheight=0.05)

        use_button = tk.Button(self, text="Use", command=lambda: controller.pin_displayer(controller, setFlag, fName))
        use_button.place(relx=0.345, rely=0.93, relwidth=0.3, relheight=0.05)

       # edit_button = tk.Button(self, text="Edit", command=lambda: controller.display_edit_profile(controller, fName))
       # edit_button.place(relx=0.64, rely=0.93, relwidth=0.3, relheight=0.05)
        edit_button = tk.Button(self, text="Edit", command=lambda: controller.pin_displayer(controller, 3, fName))
        edit_button.place(relx=0.64, rely=0.93, relwidth=0.3, relheight=0.05)
        
###########################################################################
class PinInput(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        background = tk.Frame(self, bg='#ffe3d8')
        background.place(relwidth=1, relheight=1)

        fName = controller.get_profile_name()
        flag = controller.get_flag()
        
        if flag == 1:
            pin = tk.Label(self, text="Security Pin", bg='#ffe3d8', anchor="w")
            pin.config(font=("Courier", 15))
            pin.place(relx=0.05, rely=0.23)

            pin_input = tk.Entry(self, bd=5)
            pin_input.place(relx=0.45, rely=0.23)

            back_button = tk.Button(self, text="<-", command=lambda: controller.show_frame(Welcome))
            back_button.place(relx=0.05, rely=0.93, relwidth=0.3, relheight=0.05)

            login_button = tk.Button(self, text="Log in", command=lambda: controller.verify_profile_pin(1, fName, pin_input))
            login_button.place(relx=0.64, rely=0.93, relwidth=0.3, relheight=0.05)
        elif flag == 2:
            pin = tk.Label(self, text="Security Pin", bg='#ffe3d8', anchor="w")
            pin.config(font=("Courier", 15))
            pin.place(relx=0.05, rely=0.23)

            pin_input = tk.Entry(self, bd=5)
            pin_input.place(relx=0.45, rely=0.23)

            back_button = tk.Button(self, text="<-", command=lambda: controller.profile_displayer(controller, fName))
            back_button.place(relx=0.05, rely=0.93, relwidth=0.3, relheight=0.05)

            login_button = tk.Button(self, text="Log in", command=lambda: controller.verify_profile_pin(1, fName, pin_input))
            login_button.place(relx=0.64, rely=0.93, relwidth=0.3, relheight=0.05)
        elif flag == 3:
            pin = tk.Label(self, text="Security Pin", bg='#ffe3d8', anchor="w")
            pin.config(font=("Courier", 15))
            pin.place(relx=0.05, rely=0.23)

            pin_input = tk.Entry(self, bd=5)
            pin_input.place(relx=0.45, rely=0.23)

            back_button = tk.Button(self, text="<-", command=lambda: controller.profile_displayer(controller, fName))
            back_button.place(relx=0.05, rely=0.93, relwidth=0.3, relheight=0.05)

            edit_button = tk.Button(self, text="Edit", command=lambda: controller.verify_profile_pin(0, fName, pin_input))
            edit_button.place(relx=0.64, rely=0.93, relwidth=0.3, relheight=0.05)


###########################################################################    
class PainRegister(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        background = tk.Frame(self, bg='#ffe3d8')
        background.place(relwidth=1, relheight=1)

        global happy_photo, neutral_photo, in_pain_photo
        
        happy_photo = PhotoImage(file='happy.png')
        neutral_photo = PhotoImage(file="neutral.png")
        in_pain_photo = PhotoImage(file="in_pain.png")
       
        painLevel = tk.Label(self, text="What is your pain level?", bg='#ffe3d8', anchor="w")
        painLevel.config(font=("Courier", 20))
        painLevel.place(relx=0.10, rely=0.13)
            
        happy_button = tk.Button(self, image=happy_photo, bg='#00ff00', command=lambda: controller.write_pain_level(0))
        happy_button.place(relx=0.25, rely=0.23, relwidth=buttonRelWidth, relheight=buttonRelHeight)
        
        neutral_button = tk.Button(self, image=neutral_photo, bg='#ffff00', command=lambda: controller.write_pain_level(1))
        neutral_button.place(relx=0.25, rely=0.43, relwidth=buttonRelWidth, relheight=buttonRelHeight)
        
        in_pain_button = tk.Button(self, image=in_pain_photo, bg='#ff0000', command=lambda: controller.write_pain_level(2))
        in_pain_button.place(relx=0.25, rely=0.63, relwidth=buttonRelWidth, relheight=buttonRelHeight)
        

###########################################################################
app = CPMGUI()
# locks the screen size
app.resizable(width=False, height=False)
app.title("Smart CPM Chair")
app.mainloop()
