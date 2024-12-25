import threading
import time
import random
import json
import pika
import tkinter as tk
from pika.exchange_type import ExchangeType
from tkinter import *
from PIL import ImageTk, Image,ImageDraw
import math
from tkinter import ttk
from tkinter import font as tkFont
global ignstatus
ignstatus = 0
global veh_speed
global set_speed
global BSW1
global BSW2
global car1_xcalib
global car2_xcalib
global car3_xcalib
global carchoosen
global car2_speed
global car3_speed
global carchoosen
global spinbox
global label1
global label2
global label3
car2_speed = 0
car3_speed = 0
car1_xcalib = 0
car2_xcalib = 0
car3_xcalib = 0
global set_speed_dyn
global clearance
clearance = 300
global root


ACC_info = {"timestamp":0.0, "arbitration_id":hex(0x160), "is_extended_id":True, "is_remote_frame":False,"is_error_frame":False, "channel":None, "dlc":8, 
            "data":{"ACC_state":0, "target_speed":0, "Brake_Decel_Request":0, "ACC_Driver_Info":0}, "is_fd":False, "is_rx":True, "bitrate_switch":False, 
            "error_state_indicator":False, "check":False}
            
def TransmitMsg():
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='ACCExchange',exchange_type=ExchangeType.fanout)
    #channel.queue_declare(queue='',exclusive=True)
    result=json.dumps(ACC_info)
    print("Transmitting .. %s"%result)

    channel.basic_publish(
        exchange='ACCExchange',
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
    threading.Timer(0.200,TransmitMsg).start()
    #threading.Timer(1,ChangeVehicleSpeed).start()
    
def onmsg():
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    #channel.exchange_declare(exchange='ACCExchange',exchange_type=ExchangeType.fanout)
    queue=channel.queue_declare(queue='',exclusive=True)
    channel.queue_bind(exchange='ICMExchange',queue=queue.method.queue)
    channel.basic_consume(
    queue=queue.method.queue, on_message_callback=callback, auto_ack=True) 
    channel.queue_bind(exchange='ECMExchange',queue=queue.method.queue)
    channel.basic_consume(
    queue=queue.method.queue, on_message_callback=callback, auto_ack=True) 
    channel.queue_bind(exchange='BCMExchange',queue=queue.method.queue)
    channel.basic_consume(
    queue=queue.method.queue, on_message_callback=callback, auto_ack=True) 
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
    
def callback(ch, method, properties, body):
    global ignstatus
    global veh_speed
    global set_speed
    global BSW1
    global BSW2
    global car1_xcalib
    global set_speed_dyn
    global clearance
    res = json.loads(body) # convert string to dictionary
    #print(body)
    if int(res["arbitration_id"],0) == 0x120:
        BSW1 = res["data"]["BrakeSwitch1"]
        match int(res["data"]["cruise_switch_request"]):
            case 0: 
                ACC_info["data"]["ACC_state"] = 0 #off
                ACC_info["data"]["ACC_Driver_Info"] = 0
                #print("hi")
            case 1:
                if ignstatus == 2:
                    ACC_info["data"]["ACC_state"] = 2 #standby
                    ACC_info["data"]["ACC_Driver_Info"] = 2
            case 2:
                if int(BSW1) == 0 and int(BSW2) == 0 and int(veh_speed) > 40 and int(ignstatus) == 2 and ACC_info["data"]["ACC_state"] == 2  :
                
                    f = open("speeds.csv", "w")
                    f.write("vehicle_set_speed = ")
                    set_speed = veh_speed
                    record = str(set_speed)
                    f.write(record)
                    f.close()
                    
                    set_speed_dyn = set_speed
                    ACC_info["data"]["target_speed"] = set_speed
                    ACC_info["data"]["ACC_state"] = 3 #Active
                    ACC_info["data"]["ACC_Driver_Info"] = 3
            case 3:
                ACC_info["data"]["ACC_state"] = 3
                ACC_info["data"]["ACC_Driver_Info"] = 3
            case 4:
                ACC_info["data"]["ACC_state"] = 3
                ACC_info["data"]["ACC_Driver_Info"] = 3
            case 5:
                ACC_info["data"]["ACC_state"] = 3
                ACC_info["data"]["ACC_Driver_Info"] = 3
                clearance+=5
            case 6:
                ACC_info["data"]["ACC_state"] = 3
                ACC_info["data"]["ACC_Driver_Info"] = 3
                clearance-=5
             
        if int(res["data"]["BrakeSwitch1"]) == 1:
            if int(ACC_info["data"]["ACC_state"]) == 3:
                ACC_info["data"]["ACC_state"] = 2
                ACC_info["data"]["ACC_Driver_Info"] = 2
                
    if int(res["arbitration_id"],0) == 0x200:
        ignstatus = res["data"]["ignstatus"]
        BSW2 = res["data"]["BrakeSwitch2"]
        if ignstatus < 2:
            ACC_info["data"]["ACC_state"] = 0
            ACC_info["data"]["ACC_Driver_Info"] = 0
        if int(res["data"]["BrakeSwitch2"]) == 1:
            if int(ACC_info["data"]["ACC_state"]) == 3:
                ACC_info["data"]["ACC_state"] = 2
                ACC_info["data"]["ACC_Driver_Info"] = 2
                
                
    if int(res["arbitration_id"],0) == 0x80:
        veh_speed = res["data"]["vehicle_speed"]
        car1_xcalib=(float(veh_speed)/(3.6 * 5*0.25))
        if int(ACC_info["data"]["ACC_state"]) == 3 and int(res["data"]["vehicle_speed"])<40:
            ACC_info["data"]["Brake_Decel_Request"]=0
            ACC_info["data"]["ACC_Driver_Info"]=4
            ACC_info["data"]["ACC_state"]=2
                    


def ACCRoadView():
        global carchoosen
        global spinbox
        global label1
        global label2
        global label3
        global root

        root = Tk()
        root.geometry("1000x700")
        l = Label(root,text = "car")
        l.config(font = ("courier,14"))
        l.grid(column=0,row=0)
        n = tk.StringVar()
        carchoosen = ttk.Combobox(root,width=27,textvariable=n,name="carlist")
        
        carchoosen['values'] = ('Car1','Car2','Car3') 
        #carchoosen.current(1)
        carchoosen.grid(column=1,row=0)
        
        l2= Label(root, text="Speed")
        l2.config(font =("Courier", 14))
        l2.grid(column=0,row=1)
        
        root.bind("<Up>",move_up)
        root.bind("<Down>",move_down)
        root.bind("<Left>",move_left)
        root.bind("<Right>",move_right)

        # Creating a Spinbox
        spinbox = tk.Spinbox(root, from_=0, to=200, width=10, relief="sunken", repeatdelay=500, repeatinterval=100,
                     font=("Courier", 12), bg="lightgrey", fg="blue", command=on_spinbox_change,name="speedinput")

        # Setting options for the Spinbox
        spinbox.config(state="normal", cursor="hand2", bd=3, justify="center", wrap=True)
        spinbox.grid(column=1,row=1)
        
        image1 = Image.open(r"car1.png")
        image1 = image1.resize((32, 32))
        image1 = ImageTk.PhotoImage(image1)

        image2 = Image.open(r"car2.png")
        image2 = image2.resize((32, 32))
        image2 = ImageTk.PhotoImage(image2)

        image3 = Image.open(r"car3.png")
        image3 = image3.resize((32, 32))
        image3 = ImageTk.PhotoImage(image3)

        
        label1 = tk.Label(image=image1,name="car1")
        #label1.bind("<Up>",move_up)
        label2 = tk.Label(image=image2, name="car2")
        label3 = tk.Label(image=image3, name= "car3")   
        
        label1.place(x=0, y=200)
        label2.place(x=0, y=250)
        label3.place(x=0, y=300)
        root.focus_set()
        root.bind("<1>", lambda event: root.focus_set())
        
        moveperiodic()
        
        root.mainloop()
        
def move_up(event):
    global label1
    global label2
    global label3
    global carchoosen
    match  carchoosen.get():
        case "Car1":
            label1.place(x=label1.winfo_x(), y=label1.winfo_y()-10)
        case "Car2":
            label2.place(x=label2.winfo_x(), y=label2.winfo_y()-10)
        case "Car3":
            label3.place(x=label3.winfo_x(), y=label3.winfo_y()-10)
       

def move_down(event):
    global label1
    global label2
    global label3
    global carchoosen
    match  carchoosen.get():
        case "Car1":
            #print("Car1 down")
            label1.place(x=label1.winfo_x(), y=label1.winfo_y()+10)
        case "Car2":
            label2.place(x=label2.winfo_x(), y=label2.winfo_y()+10)
        case "Car3":
            label3.place(x=label3.winfo_x(), y=label3.winfo_y()+10) 

def move_left(event):
    global label1
    global label2
    global label3
    global carchoosen
    match  carchoosen.get():
        case "Car1":
            label1.place(x=label1.winfo_x()-10, y=label1.winfo_y())
        case "Car2":
            label2.place(x=label2.winfo_x()-10, y=label2.winfo_y())
        case "Car3":
            label3.place(x=label3.winfo_x()-10, y=label3.winfo_y())

def move_right(event):
    global label1
    global label2
    global label3
    global carchoosen
   #label.place(x=label.winfo_x()+10, y=label1.winfo_y())
    match carchoosen.get():
        case "Car1":
            label1.place(x=label1.winfo_x()+10, y=label1.winfo_y())
        case "Car2":
            label2.place(x=label2.winfo_x()+10, y=label2.winfo_y())
        case "Car3":
            label3.place(x=label3.winfo_x()+10, y=label3.winfo_y()) 
            
def on_spinbox_change():
        global car1_xcalib
        global car2_xcalib
        global car3_xcalib
        global carchoosen
        global car2_speed
        global car3_speed
        global spinbox
    
        match carchoosen.get():
            #case "Car1":
                #car1_xcalib=(float(spinbox.get())/(3.6 * 5*0.25))
            case "Car2":
                #print("xcalib changes")
                car2_speed=int(spinbox.get())
                car2_xcalib=(float(spinbox.get())/(3.6 * 5*0.25))
            case "Car3":
                car3_speed=int(spinbox.get())
                car3_xcalib=(float(spinbox.get())/(3.6 * 5*0.25))
                
def find_widget(x,y,id):
    global clearance
    print(clearance)
    for child in root.children.values():
        if isinstance(child,tk.Label) and y==child.winfo_y() and (child.winfo_name()=="car2" or child.winfo_name()=="car3") and abs(child.winfo_x()-x)<=clearance and label1.winfo_x() < child.winfo_x():
            return child
    return None
    
def moveperiodic():
    global label1
    global label2
    global label3
    global car1_xcalib
    global car2_xcalib
    global car3_xcalib
    global car2_speed
    global car3_speed
    global target_speed
    global set_speed_dyn
    global clearance

    k = None
    #print(car1_xcalib)
    label1.place(x=(label1.winfo_x()+round(car1_xcalib))%1000, y=label1.winfo_y())
    label2.place(x=(label2.winfo_x()+round(car2_xcalib))%1000, y=label2.winfo_y())
    label3.place(x=(label3.winfo_x()+round(car3_xcalib))%1000, y=label3.winfo_y())
    # for i in range (0,12):
    k=find_widget(label1.winfo_x(),label1.winfo_y(),label1.winfo_name())
    print(clearance)
    print(str(car2_speed) +" "+ str(car3_speed))      
    if ACC_info["data"]["ACC_state"]==3:
        if k != None:
            if k.winfo_name() == "car2":
                print("car2 found")
                ACC_info["data"]["Brake_Decel_Request"]=1
                ACC_info["data"]["target_speed"]=car2_speed
                target_speed=car2_speed
            elif k.winfo_name() =="car3":
                ACC_info["data"]["Brake_Decel_Request"]=1
                ACC_info["data"]["target_speed"]=car3_speed
                target_speed=car3_speed
        elif int(set_speed_dyn) > int(ACC_info["data"]["target_speed"]):
            #print(str(set_speed))
            ACC_info["data"]["Brake_Decel_Request"]=0
            ACC_info["data"]["target_speed"]=set_speed_dyn
            target_speed=set_speed_dyn
    
    threading.Timer(0.250,moveperiodic).start()
    
TransmitMsg()
threading.Thread(target=ACCRoadView).start()
onmsg()