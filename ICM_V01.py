import threading
import time
import random
import json
import pika
from pika.exchange_type import ExchangeType
from tkinter import *
from PIL import ImageTk, Image,ImageDraw
import math
global vs_prv
vs_prv=0
from tkinter import ttk
from tkinter import font as tkFont
global onoffbtn_status
onoffbtn_status = 0
global drvinfo_prv
drvinfo_prv = 0
global txt_id

ICM_info = {"timestamp":0.0, "arbitration_id":hex(0x120), "is_extended_id":True, "is_remote_frame":False,"is_error_frame":False, "channel":None, "dlc":8, 
            "data":{"cruise_switch_request":7,"BrakeSwitch1":0}, "is_fd":False, "is_rx":True, "bitrate_switch":False, "error_state_indicator":False, "check":False}
            
def TransmitMsg():
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='ICMExchange',exchange_type=ExchangeType.fanout)
    #channel.queue_declare(queue='',exclusive=True)
    result=json.dumps(ICM_info)
    print("Transmitting .. %s"%result)

    channel.basic_publish(
        exchange='ICMExchange',
        routing_key='',
        body=result)
    #channel.queue_declare(queue='',exclusive=True)
    #result=json.dumps(BCM_Info)
    #print("Transmitting .. %s"%result)
    #channel.basic_publish(
     #   exchange='',
     #   routing_key='BCMQ',
     #   body=result)
    connection.close()
    # print(BCM_Info)
    threading.Timer(0.120,TransmitMsg).start()
    #threading.Timer(1,ChangeVehicleSpeed).start()
    
def onmsg():
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    #channel.exchange_declare(exchange='ICMExchange',exchange_type=ExchangeType.fanout)
    queue=channel.queue_declare(queue='',exclusive=True)
    channel.queue_bind(exchange='BCMExchange',queue=queue.method.queue)
    channel.basic_consume(
    queue=queue.method.queue, on_message_callback=callback, auto_ack=True) 
    channel.queue_bind(exchange='ACCExchange',queue=queue.method.queue)
    channel.basic_consume(
    queue=queue.method.queue, on_message_callback=callback, auto_ack=True) 
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
    
def callback(ch, method, properties, body):
    global vs_prv
    global lineid
    global txt_id
    global drvinfo_prv
    res = json.loads(body) # convert string to dictionary
    if int(res["arbitration_id"],0)== 0x80:
        ang=(1.33*int(res["data"]["vehicle_speed"])+85)%360
        endy   = y + 115 * math.sin(math.radians(ang))
        endx   = x + 115 * math.cos(math.radians(ang))
        if int(vs_prv) != int(res["data"]["vehicle_speed"]):
            canvas.delete(lineid)
            lineid=canvas.create_line(x,y, endx,endy,fill="Red",arrow="last",smooth=True,width=5)
            vs_prv=int(res["data"]["vehicle_speed"])
            
    elif int(res["arbitration_id"],0)== 0x160:
        #print("body")
        #if 'txt_id' in globals() and txt_id:
        #    canvas.delete(txt_id)
        
        match int(res["data"]["ACC_Driver_Info"]):
            case 0: 
                if drvinfo_prv != int(res["data"]["ACC_Driver_Info"]):
                    canvas.delete(txt_id)
                    txt_id=canvas.create_text(350,250, text="ACC Off", fill="#77FF63", font=('Arial 15 bold'))
            #case 1:
            case 2:
                if drvinfo_prv != int(res["data"]["ACC_Driver_Info"]):
                    canvas.delete(txt_id)
                    txt_id=canvas.create_text(350,250, text="ACC Standby", fill="#77FF63", font=('Arial 15 bold'))
            case 3:
                if drvinfo_prv != int(res["data"]["ACC_Driver_Info"]):
                    canvas.delete(txt_id)
                    txt_id=canvas.create_text(350,250, text="ACC Active", fill="#77FF63", font=('Arial 15 bold'))
            case 4:
                if drvinfo_prv != int(res["data"]["ACC_Driver_Info"]):
                    canvas.delete(txt_id)
                    txt_id=canvas.create_text(350,250, text="Intervention\nNeeded", fill="#77FF63", font=('Arial 15 bold'))
        drvinfo_prv = int(res["data"]["ACC_Driver_Info"])   
        
def ICMdashboard():
    global txt_id
    global root # set root as global
    root=Tk()  # to create a window
    root.geometry("700x700")   # Set the size of the window
    canvas_width, canvas_height = 700, 700  # create variables to hold size of canvas
    img = Image.open("meter.png")    # read image from the file to a object
    #resized_image= img.resize((700,600), Image.Resampling.LANCZOS)
    img = ImageTk.PhotoImage(img)   # create Tk image object from the image object
    global canvas  # set canvas object to global
    canvas = Canvas(root, width=canvas_width, height=canvas_height)  # create a canvas
    canvas.pack() # pack the canvas to screen
    canvas.create_image(20, 20, anchor=NW, image=img)  # embed the image on the canvas
    global x  # create global varibale x
    x=560   # x - coordinate of needle
    global y # create a global variable y
    y=260   # y - coordinate of needle
    global endy  
    endy = y + 115 * math.sin(math.radians(87)) # find angular end y coordinate
    global endx
    endx = x + 115 * math.cos(math.radians(87)) # find angular end x coordinate
    global lineid  # create global line id varible
    canvas.create_oval(x-20,y-20,x+20,y+20,fill="Red")  # draw a red circle at the centre
    canvas.create_oval(x-10,y-10,x+10,y+10,fill="Gray") # draw a gray inner circle at the centre
    lineid=canvas.create_line(x,y, endx,endy,fill="Red",arrow="last",smooth=True,width=5) # draw the needle
    
    global window_count
    window_count=0
    global cimg
    cimg = Image.open("cruise_switch1.png") 
    cimg = ImageTk.PhotoImage(cimg) # create Cruise Switches Image to display in the GUI
    
    # creating button to open Cruise Switches GUI
    button_open = ttk.Button(
    root,
    text="CB",
    command=CruiseSwitches )
    button_open.place(x=600, y=550) # create a button to open Cruise switches GUI
    
    # creating button to BrakeSwitch1 press GUI
    button_open2 = ttk.Button(
    root,
    text="BSW1")
    button_open2.bind("<ButtonPress-1>",BSW1_pressed,add="+") # attach the event procedure for button press 
    button_open2.bind("<ButtonRelease-1>",BSW1_released,add="+")  # attach even procedure for button release
    button_open2.pack()
    button_open2.place(x=600, y=600) # create a button to open Cruise switches GUI
    txt_id=canvas.create_text(350,250, text="ACC Off", fill="#77FF63", font=('Arial 15 bold'))
    root.mainloop() # wait for user input
    
def CruiseSwitches():
    global window_count   # count cruise GUI instance
    if window_count<1:    # check no. of window is onely 1
        cs = Toplevel(root) # create a window for cruise switches
        global cimg         # image object to store cruise sw image
        cs.title("Cruise Buttons")    # giving title to cruise window
        cs.config(width=500, height=370)  # give dimension for cruise sw window
        canvas_width, canvas_height = 450, 300  # create variables to hold size of canvas
        #global canvas  # set canvas object to global
        canvas2 = Canvas(cs, width=canvas_width, height=canvas_height)  # create a canvas
        canvas2.pack() # pack the canvas to screen
        canvas2.create_image(20, 20, anchor=NW, image=cimg)  # creat cruise sw img in Canvas
        Ar14 = tkFont.Font(family='Arial', size=14, weight=tkFont.BOLD) # create a font variable to use
        onoff = Button(cs, text="ON/Off",bg="#454346",fg="White",width=5,height=1,font=Ar14,activebackground="Green") # create a button for on/ off
        onoff.bind("<ButtonPress-1>",onoff_pressed,add="+") # attach the event procedure for button press 
        onoff.bind("<ButtonRelease-1>",released,add="+")  # attach even procedure for button release
        onoff.pack() # pack the button to GUI
        onoff.place(x=240, y=78) # define the location to place
        
        setbtn = Button(cs, text="Set/Accel",bg="#454346",fg="White",width=5,height=1,font=Ar14,activebackground="Green") # create a button for on/ off
        setbtn.bind("<ButtonPress-1>",setbtn_pressed,add="+") # attach the event procedure for button press 
        setbtn.bind("<ButtonRelease-1>",released,add="+")  # attach even procedure for button release
        setbtn.pack() # pack the button to GUI
        setbtn.place(x=223, y=225) # define the location to place
        
        coastbtn = Button(cs, text="Coast",bg="#454346",fg="White",width=5,height=1,font=Ar14,activebackground="Green") # create a button for on/ off
        coastbtn.bind("<ButtonPress-1>",coastbtn_pressed,add="+") # attach the event procedure for button press 
        coastbtn.bind("<ButtonRelease-1>",released,add="+")  # attach even procedure for button release
        coastbtn.pack() # pack the button to GUI
        coastbtn.place(x=145, y=77) # define the location to place
        
        resumebtn = Button(cs, text="Resume",bg="#454346",fg="White",width=5,height=1,font=Ar14,activebackground="Green") # create a button for on/ off
        resumebtn.bind("<ButtonPress-1>",resumebtn_pressed,add="+") # attach the event procedure for button press 
        resumebtn.bind("<ButtonRelease-1>",released,add="+")  # attach even procedure for button release
        resumebtn.pack() # pack the button to GUI
        resumebtn.place(x=176, y=164) # define the location to place
        
        tplusbtn = Button(cs, text="T+",bg="#454346",fg="White",width=5,height=1,font=Ar14,activebackground="Green") # create a button for on/ off
        tplusbtn.bind("<ButtonPress-1>",tplusbtn_pressed,add="+") # attach the event procedure for button press 
        tplusbtn.bind("<ButtonRelease-1>",released,add="+")  # attach even procedure for button release
        tplusbtn.pack() # pack the button to GUI
        tplusbtn.place(x=310, y=223) # define the location to place
        
        tminusbtn = Button(cs, text="T-",bg="#454346",fg="White",width=5,height=1,font=Ar14,activebackground="Green") # create a button for on/ off
        tminusbtn.bind("<ButtonPress-1>",tminusbtn_pressed,add="+") # attach the event procedure for button press 
        tminusbtn.bind("<ButtonRelease-1>",released,add="+")  # attach even procedure for button release
        tminusbtn.pack() # pack the button to GUI
        tminusbtn.place(x=290, y=160) # define the location to place
        
        window_count += 1
        

def BSW1_pressed(state):
    ICM_info["data"]["BrakeSwitch1"] = 1
    
def BSW1_released(state):
    ICM_info["data"]["BrakeSwitch1"] = 0
    
    
def onoff_pressed(state):
    global onoffbtn_status
    if onoffbtn_status:
        ICM_info["data"]["cruise_switch_request"] = 0
        onoffbtn_status = 0
    else:
        ICM_info["data"]["cruise_switch_request"] = 1
        onoffbtn_status = 1
def released(state):
    ICM_info["data"]["cruise_switch_request"] = 7
def setbtn_pressed(state):
    ICM_info["data"]["cruise_switch_request"] = 2
def coastbtn_pressed(state):
    ICM_info["data"]["cruise_switch_request"] = 3
def resumebtn_pressed(state):
    ICM_info["data"]["cruise_switch_request"] = 4
def tplusbtn_pressed(state):
    ICM_info["data"]["cruise_switch_request"] = 5
def tminusbtn_pressed(state):
    ICM_info["data"]["cruise_switch_request"] = 6    
    
threading.Thread(target = ICMdashboard).start()
TransmitMsg()
onmsg()
