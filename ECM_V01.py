import threading
import time
import random
import json
import pika
from pika.exchange_type import ExchangeType
from tkinter import *
from PIL import ImageTk, Image,ImageDraw
import math
from tkinter import ttk
from tkinter import font as tkFont

ECM_info = {"timestamp":0.0, "arbitration_id":hex(0x200), "is_extended_id":True, "is_remote_frame":False,"is_error_frame":False, "channel":None, "dlc":8, 
            "data":{"BrakeSwitch2":0, "ignstatus":0}, "is_fd":False, "is_rx":True, "bitrate_switch":False, "error_state_indicator":False, "check":False}
            
def ECMdashboard():
    
    global root # set root as global
    root=Tk()  # to create a window
    root.geometry("300x300")   # Set the size of the window
    canvas_width, canvas_height = 300, 300  # create variables to hold size of canvas
  
    # creating button to BrakeSwitch2 press GUI
    button_open2 = ttk.Button(
    root,
    text="BSW2")
    button_open2.bind("<ButtonPress-1>",BSW2_pressed,add="+") # attach the event procedure for button press 
    button_open2.bind("<ButtonRelease-1>",BSW2_released,add="+")  # attach even procedure for button release
    button_open2.pack()
    button_open2.place(x=100, y=200) # create a button to open Cruise switches GUI
    
    frame=LabelFrame(root,text="Ignition Status",padx=5,pady=5)
    r=IntVar()
    radiobutton1=Radiobutton(frame, text="Off",bd=10,variable=r,value=0,command=lambda:SetIgnitionState(r.get())).pack()  
    radiobutton2=Radiobutton(frame, text="ACC",bd=10,variable=r,value=1,command=lambda:SetIgnitionState(r.get())).pack() 
    radiobutton3=Radiobutton(frame, text="Run",bd=10,variable=r,value=2,command=lambda:SetIgnitionState(r.get())).pack()
    frame.pack()
    root.mainloop() # wait for user input
    
def SetIgnitionState(value):
    ECM_info["data"]["ignstatus"]=value
    
def BSW2_pressed(state):
    ECM_info["data"]["BrakeSwitch2"] = 1
    
def BSW2_released(state):
    ECM_info["data"]["BrakeSwitch2"] = 0
    
def TransmitMsg():
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='ECMExchange',exchange_type=ExchangeType.fanout)
    #channel.queue_declare(queue='',exclusive=True)
    result=json.dumps(ECM_info)
    print("Transmitting .. %s"%result)

    channel.basic_publish(
        exchange='ECMExchange',
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
    threading.Timer(0.150,TransmitMsg).start()
    #threading.Timer(1,ChangeVehicleSpeed).start()
    
threading.Thread(target = ECMdashboard).start()
TransmitMsg()

