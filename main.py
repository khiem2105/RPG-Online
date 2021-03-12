import Cnetwork
import time
import _thread

if __name__ == "__main__":
	# # Use Extension C to connect to server
	print("Thread Python is running!")
	s = input("Choose : 1 = master - 2 = peer\n")
	if s == "1":
		Cnetwork.create_and_bind(2510)
		Cnetwork.listen_and_accept()
		Cnetwork.master_peer_start_loop()
		# ip_public = Cnetwork.get_ip_public()
		# print("Python: ip external : " , ip_public)
		print("Python sleep 360s ...")
		time.sleep(360)
		Cnetwork.master_peer_end_loop()
		print("Python wake up, and shutdown C master loop!")
	else:
		ip = "127.0.0.1"
		port = 2510
		Cnetwork.peer_connect_to(port, ip) 
		while True:
			welcome = Cnetwork.peer_receive_from_master()
			print(welcome)
			time.sleep(2)
