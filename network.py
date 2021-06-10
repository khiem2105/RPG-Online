from settings import MAX_LENGTH
from sys import setdlopenflags
import Cnetwork
import time
import _thread
from sprites import OtherPlayer
from rsa import *
from key import *
# Send to all others peer:
# 1. Master : master_send_all(message)
# 2. Peer   : peer_send_all(message)

# Receive to all others peer:
# 1. Master : master_get_message_from_player(index)
# 2. Peer   : peer_get_message_from_player(index) (Cnetwork.peer_receive_from_master()   for master)

class Network:
    def __init__(self, game):
        self.DEBUG = True
        self.game = game
        self.player_name = input("Your name :")
        self.list_id = self.game.other_player_list.keys #use by calling self.list_id() 
        # self.number_peers = 0
        print("[Python] Thread Python is running!")
        self.first_message = True
        self.list_peer_connected_before_me = {} # {id : True/False}
        self.data_frame = ""
        self.is_master = True
        self.data_store = {} # key : value === name : data

    def add_new_player(self, new_id, connected_before_me=False):
        print("[Python] Welcome player id %i!" %(new_id))
        new_player = OtherPlayer(self.game, 128, 128, player_name=str(new_id))
        new_player.id = new_id
        self.list_peer_connected_before_me[new_id] = connected_before_me
        self.game.other_player_list[new_id] = new_player
        print("[Python] Created new instance of OtherPlayer() ")
        print("[Python] List of players : ", self.game.other_player_list)
        if new_id != -1:
            self.add_items_to_data(self.game.items_data)
            Cnetwork.master_send_to_peer_with_id(self.data_frame, new_id)

    def init_master(self):
        print("[Python] you are the master peer! with port "+str(self.game.port))
        Cnetwork.create_and_bind(self.game.port)
        Cnetwork.listen_and_accept()
        Cnetwork.master_peer_start_loop()

    def add_puclic_key_to_data(self):
        self.data_frame += (" ").join(["Public_key:", str(self.game.key_pair.pub_key.value1), str(self.game.key_pair.pub_key.value2)]) + ";"

    def add_pos_to_data(self, x, y, rot):
        self.data_frame  += (" ").join(["Pos:", str(x), str(y), str(rot)]) + ";"

    def add_action_to_data(self, action="S"):
        self.data_frame += (" ").join(["Action:", action]) + ";"

    def add_mobs_to_data(self, mobs_data):
        self.data_frame += "Zombie:" + " "
        for id in mobs_data.keys():
            self.data_frame += (",").join(["id:" + str(id), "Pos:" + str(mobs_data[id]["Pos"][0]) + "&" + str(mobs_data[id]["Pos"][1]), "Rot:" + str(mobs_data[id]["Rot"]), "Hp:" + str(mobs_data[id]["Hp"])]) + "!"
        self.data_frame += ";"
    
    def add_message_to_data(self, mess):  #For chatting
        self.data_frame += (" ").join(["Chat:", mess]) + ";"
    
    def add_items_to_data(self,items_data):
        self.data_frame += "Items:"+" "
        for item in items_data:
            self.data_frame += (",").join(["x:"+str(item["x"]),"y:"+str(item["y"]),"type:"+str(item["type"]),"id:"+str(item["id"])])+"!"
        self.data_frame+= ";"

    def add_remove_item_to_data(self, id):
        
        self.data_frame += "Remove_Item:"+" "+str(id)+";"
        if self.DEBUG: print(self.data_frame)
        
    def sync_resize_map(self, direction, data):
        # Sync unlimited map
        # Package : Extend_map <Direction:Right/Bottom> <Row> <Col> <X*Y numbers: Wall or Not>
        self.data_frame += (" ").join(["Extend_map", direction, str(len(data[0])), str(len(data))] + [str(i) for line in data for i in line]) + ';'
        if self.DEBUG : print(self.data_frame)

    def add_padding_to_message(self, message):
        if(len(message) < MAX_LENGTH):
            padding = " " * (MAX_LENGTH - len(message) - 1)
            message += padding + ";"
            print(len(message))
        # if self.DEBUG : print(self.data_frame)
        
    def run_master(self):
        # test
        # Send data of master to all peers
        # Cnetwork.master_send_all("Data;%i,%i;" %(100, 100))
        # Check if data_frame = NULL => return (not send)
        if self.data_frame == "":
            return
        # add name
        message = self.data_frame
        message += (" ").join(["Name:", self.player_name]) + ";"
        self.add_padding_to_message(message)
        Cnetwork.master_send_all(message)
        if self.DEBUG: print("Master sent to all:" + message)
        # reset message
        self.data_frame = ""
	
    #  MASTER Get data from other peers
    def master_get_data(self):
        # Get data from master_buffer to know :
        # 1. if someone connected to master
        # 2. if someone disconnected
        try:
            data = Cnetwork.master_get_to_know_new_connection()
            if data != None and data != "":
                if self.DEBUG: print("Received new connection :", data)
                data = data.split(';')
                if data[0] == "New":
                    new_id = int(data[1])
                    self.add_new_player(new_id)
                elif data[0] == "Disconnected":
                    id_player = int(data[1])
                    if self.DEBUG : print("Player", id_player, "disconnected! Deleted from the list...")
                    player = self.game.other_player_list[id_player]
                    # Store data 
                    # @LONG : have to insert inventory
                    self.data_store[player.player_name] = {
                            "Pos" : player.pos,
                            "Hp" : player.health
                            }
                    self.game.other_player_list[id_player].kill()
                    self.game.other_player_list.pop(id_player, None)
        except Exception as E:
            print(str(E), "first try in : method master_get_data/network.py")

        # Get data from other players => to update status
        # To do : add a loop to get all peers
        try:
            for i in self.list_id():
                data = Cnetwork.master_get_message_from_player(i)
                if data != None:
                    # if self.DEBUG: print("[Python] Master received data from player ",i ," : ", data)
                    self.analyse_data_received(data, i)
                    # data = data.split(';')
                    # if data[0] == "Data":
                        # #  x, y = data[1].split(',')
                        # key = data[1]
                        # self.game.other_player_list[i].updateKey(key)
        except Exception as E:
            print(str(E), "second try in : method master_get_data/network.py")

    def init_peer(self):
        print("[Python] you are the normal peer! with port "+str(self.game.port))
        ip = "127.0.0.1"
        port = self.game.port
        # port = 2510
        self.num_other_players = 0
        Cnetwork.peer_connect_to_master(port, ip)
        self.add_new_player(-1, True)
    
    def run_peer(self):
        # Check if data_frame = NULL => return (not send)
        if self.data_frame == "":
            return
        # Send data
        message = self.data_frame
        # add name
        message += (" ").join(["Name:", self.player_name]) + ";"
        self.add_padding_to_message(message)
        Cnetwork.peer_send_all(message)
        # if self.DEBUG: print("Peer sent to all : " , message)
        # reset message
        self.data_frame = ""

    def peer_send_data_to_master(self):
        if self.data_frame == "":
            return
        #Send data
        message = self.data_frame
        # add name
        message += (" ").join(["Name:", self.player_name]) + ";"
        Cnetwork.peer_send_data_to_master(message)
        # if self.DEBUG: print("Peer sent to all : " , message)
        # reset message
        self.data_frame = ""

    def analyse_zombie_data(self, zombie_data):
        id = 0
        pos = (0, 0)
        rot = 0
        hp = 0
        for individual_data in zombie_data.split("!"):
            if individual_data != "":
                for attribute in individual_data.split(","):
                    value = attribute.split(":")
                    if value[0] == "id":
                        id = int(value[1])
                    elif value[0] == "Pos":
                        x, y = value[1].split("&")
                        pos = (float(x), float(y))
                    elif value[0] == "Rot":
                        rot = float(value[1])
                    elif value[0] == "Hp":
                        hp = float(value[1])
            #print(f"Id: {id}, Pos: {pos}, Rot: {rot}, Hp: {hp}")
            self.game.player.updateZombie(id, pos, rot, hp)
    
    def analyse_items_data(self,items_data):
        for item in items_data.split("!") :
            if item != "":
                for attribute in item.split(","):   
                    value = attribute.split(":")
                    if value[0]=="x":
                        x =int(value[1])
                    elif value[0]=="y":
                        y =int(value[1])
                    elif value[0]=="type":
                        type =str(value[1])
                    elif value[0]=="id":
                        id =str(value[1])
            self.game.create_item(x,y,type,id)

    def send_chat_message_to_all(self, message):
        for id in self.list_id():
            print(f"{id}: {self.game.pub_key_list}")
            encoded_message = encode(message, self.game.pub_key_list[id])
            print(encoded_message)
            encoded_message = "Chat: " + encoded_message + ";"
            # print(encoded_message)
            if self.is_master:
                Cnetwork.master_send_to_peer_with_id(encoded_message, id)
            else:
                Cnetwork.peer_send_to_peer_with_id(encoded_message, id)
            encoded_message = ""


    def send_private_chat_message(self, message, player_name):
        pass
        
    def analyse_data_received(self, data_received, id_player):
        if data_received != None and data_received != "":
            # if self.DEBUG: print(data_received)
            
            data_received = data_received.split(';')
            for data in data_received:
                if data != "" and data[0] == " ":
                    continue
                data = data.split(" ")
                # if self.DEBUG: 
                #     if id_player == -1: print("data_master:", data)
                # update position
                if data[0] == "Pos:":
                    pos = float(data[1]), float(data[2])
                    rot = float(data[3])
                    #if self.DEBUG: print("[Python] received from player ", id_player, " :", pos, rot)
                    self.game.other_player_list[id_player].updatePosRot(pos, rot)
                elif data[0] == "Action:":
                    action = data[1]
                    #if self.DEBUG: print("[Python] received from player ", id_player, " :", action)
                    self.game.other_player_list[id_player].updateAction(action)
                elif data[0] == "Zombie:":
                    zombie_data = data[1]
                    self.analyse_zombie_data(zombie_data)
                    pass
                elif data[0] == "Chat:":
                    if self.DEBUG:
                        for i in range(1, len(data)):
                            print(data[i])
                    mess = "@"+self.game.other_player_list[id_player].player_name + ": "
                    for i in range(1, len(data)):
                        mess = mess + data[i] + " "
                    self.game.chat_box.write_log([mess,1])
                elif data[0] == "Name:": # update name
                    self.game.other_player_list[id_player].player_name = data[1]
                elif data[0] == "Extend_map": # update name
                    # Package : Extend_map <Direction:Right/Bottom> <Row> <Col> <X*Y numbers: Wall or Not>
                    i = 4
                    cols = int(data[2])
                    rows = int(data[3])
                    extend_data = []
                    for row in range(rows):
                        line = []
                        for col in range(cols):
                            line.append(int(data[i]))
                            i += 1
                        extend_data.append(line)
                    if self.DEBUG: print(extend_data)
                    self.game.peer_extend_map(data[1], 15, extend_data)
                elif data[0] =="Items:":
                    self.analyse_items_data(data[1])
                elif data[0] =="Remove_Item:":
                    self.game.remove_item(data[1])
                elif data[0] == "Public_key:":
                    # print("Update public key list...")
                    # print(int(data[1]), int(data[2]))
                    if not self.game.pub_key_list[id_player]:
                        self.game.pub_key_list[id_player] = Key(int(data[1]), int(data[2]))

    #  PEER Get data from other peers
    def peer_get_data(self):
        if self.first_message :
            return
        try: 
            # Receive data from master
            data_master = Cnetwork.peer_receive_from_master()
            self.analyse_data_received(data_master, -1)

            # Receive data from old peers 
            for i in self.list_id():
                if i == -1 or not self.list_peer_connected_before_me[i]: continue
                data = Cnetwork.peer_receive_from_old_peer(i)
                self.analyse_data_received(data, i)
                if data != "" : 
                    if self.DEBUG: print("Worked : ", data)

            # Receive data from new peers 
            for i in self.list_id():
                if i == -1 or self.list_peer_connected_before_me[i]: continue # != id master
                # print("Tentative get data from player ", i)
                data = Cnetwork.peer_get_message_from_player(i)
                self.analyse_data_received(data, i)
                if data != "" and data is not None:
                    print("Works :", data)
        except Exception as E:
            print(str(E), "! First try in peer_get_data/network.py")

        # Get data from peer_buffer to know :
        # 1. if someone connected 
        # 2. if someone disconnected
        try:
            data = Cnetwork.peer_get_to_know_new_connection()
            if data != None and data != "":
                data = data.split(';')
                if data[0] == "New":
                    new_id = int(data[1])
                    self.add_new_player(new_id)
                elif data[0] == "Disconnected":
                    id_player = int(data[1])
                    if self.DEBUG : print("Player", id_player, "disconnected! Deleted from the list...")
                    self.game.other_player_list[id_player].kill()
                    # self.game.other_player_list.pop(int(data[1]), None)
                    self.game.other_player_list.pop(id_player, None)
                # if data[0] == "Disconnected":
                    # player_id = int(data[1])
        except Exception as E:
            print(str(E), "! Second try in peer_get_data/network.py")
           
    def receive_first_message(self):
        welcome = Cnetwork.peer_receive_from_master()
        print("[Python] Data raw :", welcome)
        self.analyse_data_received(welcome,-1)
        welcome = welcome.split(";")
        if welcome != None and welcome[0] == "First":
            self.myId, self.myPort = welcome[1].split(",")
            self.myId = int(self.myId)
            self.myPort = int(self.myPort)
            # set id
            Cnetwork.set_my_id(self.myId)
            print("[Python] My id: ", self.myId)
            print("[Python] My port: ", self.myPort)
            self.myPort = self.myPort + 1 
            # Bind a socket data
            Cnetwork.peer_create_bind_listen_and_accept(self.myPort)
            Cnetwork.normal_peer_start_loop()
            for i in range(2, len(welcome)):
                if (welcome[i] != ''):
                    try:
                        newId, newIp, newPort = welcome[i].split(",")
                        print("[Python] New connection: ", newId, newIp, newPort)
                        newId = int(newId)  
                        newPort = int(newPort) + 1 
                        # self.add_items_to_data(self.game.items_data)
                        # Cnetwork.master_send_to_peer_with_id(self.data_frame, newId)
                        Cnetwork.peer_connect_to_peer(newId, newPort, newIp)
                        self.add_new_player(newId, True)
                    except Exception as E:
                        print(str(E), "! Func receive_first_message/network")
            self.first_message = False

    def receive_mobs_from_master(self):
        pass
