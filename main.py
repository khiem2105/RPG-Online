import Cnetwork
import time
import _thread

class Network:
	def __init__(self):
		print("Thread Python is running!")
		s = input("Choose : 1 = master - 2 = peer\n")
		if s == "1":
			self.init_master()
		else:
			self.init_peer()
	
	def init_master(self):
		Cnetwork.create_and_bind(2510)
		Cnetwork.listen_and_accept()
		Cnetwork.master_peer_start_loop()
		# ip_public = Cnetwork.get_ip_public()
		# print("Python: ip external : " , ip_public)
		print("Python sleep 360s ...")
		time.sleep(360)
		Cnetwork.master_peer_end_loop()
		print("Python wake up, and shutdown C master loop!")
	
	def init_peer(self):
		ip = "127.0.0.1"
		port = 2510
		Cnetwork.peer_connect_to_master(port, ip)
		#Cnetwork.data_peer_start_loop()
		#Cnetwork.data_peer_end_loop()
		first_rev = True
		while True:
			#  Message welcome : 
			#  If first : "First;myId,myPort;"
			#  Else => new connection of others : 
			#       "newId,newIp,newPort;newId2,newIp2,newPort2;"
			try :
				welcome = Cnetwork.peer_receive_from_master()
				print("Data raw :", welcome)
				welcome = welcome.split(";")
				if welcome != None:
					if welcome[0] == "First":
						myId, myPort = welcome[1].split(",")
						print("My id: ", myId)
						print("My port: ", myPort)
						myPort = int(myPort) + 1 
						# Bind a socket data
						Cnetwork.peer_create_bind_listen_and_accept(myPort)
						Cnetwork.normal_peer_start_loop()
						for i in range(2, len(welcome)):
							if (welcome[i] != ''):
								newId, newIp, newPort = welcome[i].split(",")
								print("New connection: ")
								print(newId, newIp, newPort)
								newId = int(newId)  
								newPort = int(newPort) + 1 
								Cnetwork.peer_connect_to_peer(newId, newPort, newIp)
					elif welcome[0] == "Disconnected":
						print("Player " + welcome[1] + " was disconnected!")
					else:
						for i in range(len(welcome)):
							if (welcome[i] != ''):
								newId, newIp, newPort = welcome[i].split(",")
								print("New connection: ")
								print(newId, newIp, newPort)
			except Exception as E:
				print(str(E))
			time.sleep(0.5)

if __name__ == "__main__":
	# # Use Extension C to connect to server
	n = Network()

