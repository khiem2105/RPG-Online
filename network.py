from sys import setdlopenflags
import Cnetwork
import time
import _thread
from sprites import OtherPlayer
# Send to all others peer:
# 1. Master : master_send_all(message)
# 2. Peer   : peer_send_all(message)

# Receive to all others peer:
# 1. Master : master_get_message_from_player(index)
# 2. Peer   : peer_get_message_from_player(index) (Cnetwork.peer_receive_from_master()   for master)

class Network:
    def __init__(self, game):
        self.DEBUG = False
        self.game = game
        self.player_name = input("Your name :")
        self.list_id = self.game.other_player_list.keys #use by calling self.list_id() 
        # self.number_peers = 0
        print("[Python] Thread Python is running!")
        self.first_message = True
        self.list_peer_connected_before_me = {} # {id : True/False}
        self.data_frame = ""

    def add_new_player(self, new_id, connected_before_me=False):
        print("[Python] Welcome player id %i!" %(new_id))
        new_player = OtherPlayer(self.game, 128, 128, player_name=str(new_id))
        new_player.id = new_id
        self.list_peer_connected_before_me[new_id] = connected_before_me
        self.game.other_player_list[new_id] = new_player
        print("[Python] Created new instance of OtherPlayer() ")
        print("[Python] List of players : ", self.game.other_player_list)

    def init_master(self):
        print("[Python] you are the master peer! with port "+str(self.game.port))
        Cnetwork.create_and_bind(self.game.port)
        Cnetwork.listen_and_accept()
        Cnetwork.master_peer_start_loop()

    def add_pos_to_data(self, x, y, rot):
        self.data_frame  += (" ").join(["Pos:", str(x), str(y), str(rot)]) + ";"

    def add_action_to_data(self, action="S"):
        self.data_frame += (" ").join(["Action:", action]) + ";"
    
    def add_message_to_data(self, mess):  #For chatting
        self.data_frame += (" ").join(["Chat:", mess]) + ";"
        
    def sync_resize_map(self, direction, data):
        # Sync unlimited map
        # Package : Extend_map <Direction:Right/Bottom> <Row> <Col> <X*Y numbers: Wall or Not>
        self.data_frame += (" ").join(["Extend_map", direction, str(len(data[0])), str(len(data))] + [str(i) for line in data for i in line]) + ';'
        if self.DEBUG : print(self.data_frame)
        
    def run_master(self):
        # Send data of master to all peers
        # Cnetwork.master_send_all("Data;%i,%i;" %(100, 100))
        # Check if data_frame = NULL => return (not send)
        if self.data_frame == "":
            return
        # add name
        message = self.data_frame
        message += (" ").join(["Name:", self.player_name]) + ";"
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
                    self.game.other_player_list[id_player].kill()
                    self.game.other_player_list.pop(id_player, None)
        except Exception as E:
            print(str(E))

        # Get data from other players => to update status
        # To do : add a loop to get all peers
        try:
            for i in self.list_id():
                data = Cnetwork.master_get_message_from_player(i)
                if data != None:
                    if self.DEBUG: print("[Python] Master received data from player ",i ," : ", data)
                    self.analyse_data_received(data, i)
                    # data = data.split(';')
                    # if data[0] == "Data":
                        # #  x, y = data[1].split(',')
                        # key = data[1]
                        # self.game.other_player_list[i].updateKey(key)
        except Exception as E:
            print(str(E))

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
        Cnetwork.peer_send_all(message)
        if self.DEBUG: print("Peer sent to all : " , message)
        # reset message
        self.data_frame = ""
        
    def analyse_data_received(self, data_received, id_player):
        if data_received != None and data_received != "":
            data_received = data_received.split(';')
            for data in data_received:
                data = data.split(" ")
                if self.DEBUG: 
                    if id_player == -1: print("data_master:", data)
                # update position
                if data[0] == "Pos:":
                    pos = float(data[1]), float(data[2])
                    rot = float(data[3])
                    if self.DEBUG: print("[Python] received from player ", id_player, " :", pos, rot)
                    self.game.other_player_list[id_player].updatePosRot(pos, rot)
                elif data[0] == "Action:":
                    action = data[1]
                    if self.DEBUG: print("[Python] received from player ", id_player, " :", action)
                    self.game.other_player_list[id_player].updateAction(action)
                elif data[0] == "Chat:":
                    print(len(data))
                    mess = self.game.other_player_list[id_player].player_name + ": "
                    for i in range(1, len(data)):
                        mess = mess + data[i] + " " 
                    self.game.chat_box.is_text_reveived = True
                    self.game.chat_box.write_log(mess)
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
            print(str(E))

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
            print(str(E))
           
    def receive_first_message(self):
        welcome = Cnetwork.peer_receive_from_master()
        print("[Python] Data raw :", welcome)
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
                        Cnetwork.peer_connect_to_peer(newId, newPort, newIp)
                        self.add_new_player(newId, True)
                    except:
                        pass
            self.first_message = False

    def trash(self):
        first_rev = True
        test = True
        #  _thread.start_new_thread(peer, ())
        while True:
            #  Message welcome : 
            #  If first : "First;myId,myPort;"
            #  Else => new connection of others : 
            #       "newId,newIp,newPort;newId2,newIp2,newPort2;"
            try :
                welcome = Cnetwork.peer_receive_from_master()
                print("[Python] Data raw :", welcome)
                welcome = welcome.split(";")
                if welcome != None:
                    if welcome[0] == "First":
                        myId, myPort = welcome[1].split(",")
                        # set id
                        Cnetwork.set_my_id(int(myId))
                        print("[Python] My id: ", myId)
                        print("[Python] My port: ", myPort)
                        myPort = int(myPort) + 1 
                        # Bind a socket data
                        Cnetwork.peer_create_bind_listen_and_accept(myPort)
                        Cnetwork.normal_peer_start_loop()
                        for i in range(2, len(welcome)):
                            if (welcome[i] != ''):
                                newId, newIp, newPort = welcome[i].split(",")
                                print("[Python] New connection: ", newId, newIp, newPort)
                                newId = int(newId)  
                                newPort = int(newPort) + 1 
                                Cnetwork.peer_connect_to_peer(newId, newPort, newIp)
                                self.add_new_player(newId)
                        # Send first message :
                        Cnetwork.peer_send_all("THIS IS PEER!")

                    elif welcome[0] == "Disconnected":
                        print("[Python] Player " + welcome[1] + " was disconnected!")
                    else:
                        for i in range(len(welcome)):
                            if (welcome[i] != ''):
                                newId, newIp, newPort = welcome[i].split(",")
                                print("[Python] New connection: ", newId, newIp, newPort)
            except Exception as E:
                print(str(E))
            #  print(Cnetwork.peer_get_message_from_player(1) )
            Cnetwork.peer_send_all("THIS IS PEER")
            time.sleep(2)
