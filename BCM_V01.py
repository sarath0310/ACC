import threading
import time
import random
import json
import pika
from pika.exchange_type import ExchangeType
from tkinter import *
global horizantal
global veh_free_time
veh_free_time =0 

BCM_info = {"timestamp":0.0, "arbitration_id":hex(0x80), "is_extended_id":True, "is_remote_frame":False,"is_error_frame":False, "channel":None, "dlc":8, "data":{"vehicle_speed":0}, "is_fd":False, 
            "is_rx":True, "bitrate_switch":False, "error_state_indicator":False, "check":False}
            
def print_msg():
    print(ACC_info)
    threading.Timer(0.250, print_msg).start()

def updated_speed():
    ACC_info["data"]["vehicle_speed"] = random.randint(0,250)
    threading.Timer(1,updated_speed).start()
    
#print_msg()
#updated_speed()

def TransmitMsg():
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='BCMExchange',exchange_type=ExchangeType.fanout)
    #channel.queue_declare(queue='',exclusive=True)
    result=json.dumps(BCM_info)
    #print("Transmitting .. %s"%result)

    channel.basic_publish(
        exchange='BCMExchange',
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
    threading.Timer(0.250,TransmitMsg).start()
    #threading.Timer(1,ChangeVehicleSpeed).start()
    
def onmsg():
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    #channel.exchange_declare(exchange='ICMExchange',exchange_type=ExchangeType.fanout)
    queue=channel.queue_declare(queue='',exclusive=True)
    channel.queue_bind(exchange='ACCExchange',queue=queue.method.queue)
    channel.basic_consume(
    queue=queue.method.queue, on_message_callback=callback, auto_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
    
def callback(ch, method, properties, body):
    global horizantal
    global veh_free_time
    res = json.loads(body) # convert string to dictionary
    if int(res["arbitration_id"],0)== 0x160:    
        if res["data"]["ACC_state"]==3:
            if res["data"]["Brake_Decel_Request"]==1 and int(BCM_info["data"]["vehicle_speed"]) > int(res["data"]["target_speed"]):
                diff=int(BCM_info["data"]["vehicle_speed"]) - int(res["data"]["target_speed"])
                #print(diff)
                horizantal.set(int(horizantal.get())-(diff))
                veh_free_time=0
                #print(res["Data"]["Brake_Decel_Request"])
                #BCM_Info["Data"]["vehicle_speed"]=-2
                
            else:
                veh_free_time+=0.120
                if veh_free_time >=5 and int(BCM_info["data"]["vehicle_speed"]) < int(res["data"]["target_speed"]):
                    horizantal.set(horizantal.get()+2)
    
def setVehicleSpeed(v):
    #global veh_speed
    #veh_speed=v
    BCM_info["data"]["vehicle_speed"]=v
    
def VehicleCtrl():
    global horizantal
    root=Tk()  # to create a window
    root.title("BCM")
    root.geometry("700x200")   # set the dimension for window
    horizantal=Scale(root,label="Vehicle Speed",from_=0,to=250,orient=HORIZONTAL,width=20,length=500,tickinterval=50,command=setVehicleSpeed,troughcolor="Black",sliderlength=20,highlightcolor="Red",cursor="bottom_side",activebackground="Green",bg="Gray",bd =10)
    horizantal.pack()
    #img.show()
    #my_pen = turtle.Turtle()
    #my_pen.color("orange")
    #my_pen.fd(100)
    root.mainloop()
    
threading.Thread(target = VehicleCtrl).start()   
TransmitMsg()
onmsg()