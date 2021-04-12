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
        self.game = game
        self.list_id = self.game.other_player_list.keys #use by calling self.list_id() 
        # self.number_peers = 0
        print("[Python] Thread Python is running!")
        self.first_message = True
        self.list_peer_connected_before_me = {} # {id : True/False}

    def add_new_player(self, new_id, connected_before_me=False):
        print("[Python] Welcome player id %i!" %(new_id))
        new_player = OtherPlayer(self.game, 352, 224)
        new_player.id = new_id
        self.list_peer_connected_before_me[new_id] = connected_before_me
        self.game.other_player_list[new_id] = new_player
        print("[Python] Created new instance of OtherPlayer() ")
        print("[Python] List of players : ", self.game.other_player_list)
	
    def init_master(self):
        print("[Python] your are the master peer! with port "+str(self.game.port))
        Cnetwork.create_and_bind(self.game.port)
        Cnetwork.listen_and_accept()
        Cnetwork.master_peer_start_loop()

    def run_master(self, key):
        # Send data of master to all peers
        # Cnetwork.master_send_all("Data;%i,%i;" %(100, 100))
        # Reieive data of peers
        message = "Data;"+key+";"
        Cnetwork.master_send_all(message)
        print("Master sent to all:" + message)
	
    #  MASTER Get data from other peers
    def master_get_data(self):
        # Get data from master_buffer to know :
        # 1. if someone connected to master
        # 2. if someone disconnected
        try:
            data = Cnetwork.master_get_to_know_new_connection()
            if data != None and data != "":
                print("Received new connection :", data)
                data = data.split(';')
                if data[0] == "New":
                    new_id = int(data[1])
                    self.add_new_player(new_id)
        except Exception as E:
            print(str(E))

        # Get data from other players => to update status
        # To do : add a loop to get all peers
        try:
            for i in self.list_id():
                data = Cnetwork.master_get_message_from_player(i)
                if data != None:
                    print("[Python] Master received data from player ",i ," : ", data)
                    data = data.split(';')
                    if data[0] == "Data":
                        #  x, y = data[1].split(',')
                        key = data[1]
                        self.game.other_player_list[i].updateKey(key)
        except Exception as E:
            print(str(E))

    def init_peer(self):
        print("[Python] your are the normal peer! with port "+str(self.game.port))
        ip = "127.0.0.1"
        port = self.game.port
        # port = 2510
        self.num_other_players = 0
        Cnetwork.peer_connect_to_master(port, ip)
        self.add_new_player(-1, True)
    
    def run_peer(self,key):
        # send 
        message="Data;"+key+";"
        Cnetwork.peer_send_all(message)
        print("Peer sent to all : " , message)
        
    def analyse_data_received(self, data, id_player):
        if data != None and data != "":
            data = data.split(';')
            if (id_player == -1) :
                print("data_master:", data)
            if data[0] == "Data":
                key = data[1]
                print("[Python] received from player ", id_player, " :", key)
                self.game.other_player_list[id_player].updateKey(key)

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
                if data != "" : print("Worked : ", data)

            # Receive data from new peers 
            for i in self.list_id():
                if i == -1 or self.list_peer_connected_before_me[i]: continue # != id master
                data = Cnetwork.peer_get_message_from_player(i)
                self.analyse_data_received(data, i)

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
