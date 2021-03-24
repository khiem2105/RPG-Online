 #define PY_SSIZE_T_CLEAN
#include <Python.h>
// Best tutorial to understand this file: https://www.youtube.com/watch?v=a65JdvOaygM&list=PL1A2CSdiySGIPxpSlgzsZiWDavYTAx61d&index=9
// Docs: https://docs.python.org/3/extending/extending.html
// Args: https://docs.python.org/3/c-api/arg.html#c.PyArg_ParseTuple
#include <unistd.h>
#include <string.h>   
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>   
#include <arpa/inet.h>    
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/time.h> 
#include <sys/wait.h>
#include <fcntl.h>
#include <time.h>
#include <pthread.h>


#define BUF_SIZE 1024
#define false 0
#define true 1
#define MAX_CONNECTION 5
typedef int bool;
// ------------------------------------------------------------
// ------------------- Delaration variable ---------------------

// ip public
char ip[20];
char global_buf[BUF_SIZE];
char global_buf2[BUF_SIZE];
int sd, activity, new_socket, val_read;

//----------------------MASTER PEER ----------------------
// To avoid confusion between master_peer and peer,
// We structure the data by Struct
struct PeerSocket {
    int fd;
    int id;
    char* ip;
    int port;
    char last_message[BUF_SIZE];
};

struct MasterPeer {
    struct sockaddr_in address;
    int master_socket;
    int opt;
    int port;
    int addrlen;
    int max_sd;
    char buffer[BUF_SIZE];
    // table of peer's socket
    struct PeerSocket peer_socket[5];
    int max_peer;

    // variable which maintains the master loop 
    bool running_master_thread;

    // Master.readfds : argument not NULL, it points to an object of type fd_set 
    // that on iput specifies the file descriptors to be checked for being 
    // ready to read, and on ouput indicates which file descriptors are ready to write
    // basically , it's a set of socket descriptors
    fd_set readfds;
};

// Initialization
struct MasterPeer Master;
void Cinit_master_peer(void) {
    Master.opt = 1;
    Master.running_master_thread = false;
    Master.max_peer = 5;
    memset(Master.peer_socket, 0, sizeof(Master.peer_socket));
}
//--------------------END MASTER PEER ----------------------


//-------------------- PEER ----------------------
// Data of Peer
struct NormalPeer {
    int master_file_desc;
    struct sockaddr_in address;
    int master_socket;
    int opt;
    int port;
    int addrlen;
    int max_sd;
    char buffer[BUF_SIZE];
    int number_of_other_peers;
    // table of other peer's socket
    struct PeerSocket peer_socket[5];
    int max_peer;
    int myId;
    // variable which maintains the master loop 
    bool running_master_thread;
    fd_set readfds;
};

//Initialization
struct NormalPeer Peer;
void Cinit_normal_peer(void) {
    bzero(Peer.buffer, BUF_SIZE);
    Peer.opt = 1;
    Peer.running_master_thread = false;
    Peer.max_peer = 5;
    Peer.number_of_other_peers = 0;
    memset(Peer.peer_socket, 0, sizeof(Master.peer_socket));
}
//--------------------END PEER ----------------------


// thread which runs master_loop
pthread_t master_thread;
pthread_t peer_thread;
// -------------------END Delaration variable ---------------------
// ---------------------------------------------------------------


// --------COLLECTION OF FUNCTIONS "PASSE PARTOUT"-------------
// ------------- STOP = PERROR + EXIT -------------------
void stop(char* msg) {
	perror(msg);
	exit(EXIT_FAILURE);
}
// --------------- Send Message Function------------------------
void Csend_message(int soc, char* message) {
    if ((size_t)send(soc, message, strlen(message), 0) != strlen(message)) 
	stop("[C] Send message function !");
}
//------ MASTER : LOOP TO ALL PEER and send a message USING GLOBAL_BUF  -------------
void Cmaster_send_message_to_all_others_peer(void) {
    for (int i=0; i<Master.max_peer; i++) {
		if (Master.peer_socket[i].fd != 0) {
			Csend_message(Master.peer_socket[i].fd, global_buf);
		}
    }
}

void Cmaster_send_message_to_all_other_peer_v2(char *message) {
	  for (int i=0; i<Master.max_peer; i++) {
		if (Master.peer_socket[i].fd != 0) {
			Csend_message(Master.peer_socket[i].fd, message);
		}
    }
}

static PyObject* master_send_message_to_all_other_peer(PyObject* self, PyObject* args) {
	char *message;
	if(!PyArg_ParseTuple(args, "s", &message))
		return NULL;
	Cmaster_send_message_to_all_other_peer_v2(message);
	return Py_BuildValue("s", "success");
}
//------ PEER : LOOP TO ALL PEER and send a message USING GLOBAL_BUF  -------------
// Fix : not send to master yet
void Cpeer_send_message_to_all_others_peer(void) {
    for (int i=0; i<Peer.max_peer; i++) {
	if (Peer.peer_socket[i].fd != 0) {
	    Csend_message(Peer.peer_socket[i].fd, global_buf);
	}
    }
}
<<<<<<< HEAD:cnetwork.c
//------ FOR PYTHON : PEERs LOOP TO ALL PEER and send a message by arguments  -------------
void Cpeer_send_all(char* message) {
    // send to master :
    Csend_message(Peer.master_file_desc, message);
    // send to all peers
    for (int i=0; i<Peer.max_peer; i++) {
	if (Peer.peer_socket[i].fd != 0) {
	    Csend_message(Peer.peer_socket[i].fd, message);
	}
    }
}

static PyObject* peer_send_all(PyObject* self, PyObject* args) {
    char * message;
    if (!PyArg_ParseTuple(args, "s", &message)) return NULL;
    Cpeer_send_all(message);
    return Py_BuildValue("s", "Success");
}
//------ FOR PYTHON : MASTER LOOP TO ALL PEERs and send a message by arguments  -------------
void Cmaster_send_all(char* message) {
    for (int i=0; i<Master.max_peer; i++) {
	if (Master.peer_socket[i].fd != 0) {
	    Csend_message(Master.peer_socket[i].fd, message);
	}
    }
}

static PyObject* master_send_all(PyObject* self, PyObject* args) {
    char * message;
    if (!PyArg_ParseTuple(args, "s", &message)) return NULL;
    Cmaster_send_all(message);
    return Py_BuildValue("s", "Success");
=======

void Cpeer_send_message_to_all_others_peer_v2(char *message) {
	for (int i=0; i<Peer.max_peer; i++) {
		if (Peer.peer_socket[i].fd != 0) {
			Csend_message(Peer.peer_socket[i].fd, message);
		}
    }
}

static PyObject* peer_send_message_to_all_other_peer(PyObject* self, PyObject* args) {
	char *message;
	if(!PyArg_ParseTuple(args, "s", &message))
		return NULL;
	Cpeer_send_message_to_all_other_peer_v2(message);
	return Py_BuildValue("s", "success");
>>>>>>> 3d6b036f36357ec9b526bba90846147d68ede64a:Network/cnetwork.c
}
// -------------------------------------------------------------------------
// -------------------------------------------------------------------------


// -------------------------------------------------------
// --------------- Get IP Public -------------------------
char* Cget_ip_public(void) {
	FILE* file; bzero(ip, 20);
	// https://www.cyberciti.biz/faq/how-to-find-my-public-ip-address-from-command-line-on-a-linux/	
	// save ip public to file by direction, then read the file
	if (system("dig +short myip.opendns.com @resolver1.opendns.com > ip") < 0) stop("[C] System(dig) : ")	;
	if ((file = fopen("ip", "r")) == NULL ) stop("[C] Open file : ");
	fscanf(file, "%s", ip);
	fclose(file);
	// Delete file ip
	if (system("rm ip") < 0) stop("[C] System(rm) : ");
	return ip;
}

// Note : variable ip must be global to prevent Code-Dumped
static PyObject* get_ip_public(PyObject* self) {
	return Py_BuildValue("s", Cget_ip_public());
}
// ---------------------------------------------------------
// ---------------------------------------------------------


// -------------------------------------------------------
// --------------- Listen and accept -------------------------
void Clisten_and_accept(void) {
    printf("[C] [C] Listener on port %d \n", Master.port);
    //try to specify maximum of 3 pending connections for the master socket
    if (listen(Master.master_socket, 3) < 0) stop("[C] Listen() : ");
     
    //accept the incoming connection
    Master.addrlen = sizeof(Master.address);
    puts("Waiting for connections ...");
}

static PyObject* listen_and_accept(PyObject* self) {
    Clisten_and_accept();
    return Py_BuildValue("s", "Success");
}
// ---------------------------------------------------------
// ---------------------------------------------------------



// -------------------------------------------------------
// --------------- Peer Create and Bind -----------------
void Cpeer_create_bind_listen_and_accept(void) {
    //create a peer socket
    if ((Peer.master_socket = socket(AF_INET , SOCK_STREAM , 0)) == 0) 
	stop("[C] Socket() failed : ");
 
    // set master socket to allow multiple connections 
    if( setsockopt(Peer.master_socket, SOL_SOCKET, SO_REUSEADDR, (char *)&Peer.opt, sizeof(Peer.opt)) < 0 ) 
	stop("[C] SocketPeer.opt : ");
 
    //type of socket created
    Peer.address.sin_family = AF_INET;
    Peer.address.sin_addr.s_addr = INADDR_ANY; // inet_addr(ip)
    Peer.address.sin_port = htons(Peer.port);
     
    //bind the socket 
    if (bind(Peer.master_socket, (struct sockaddr *)&Peer.address, sizeof(Peer.address))<0) 
	stop("[C] Bind() failed : ");
    printf("[C] Peer : Create and bind port %i successfully!\n", Peer.port);
    // listen 
    printf("[C] Peer listen on port %i \n", Peer.port);
    if (listen(Peer.master_socket, 3) < 0) stop("[C] Listen() : ");

    //accept
    Peer.addrlen = sizeof(Peer.address);
    puts("Peer is waiting for connections ...");
}

static PyObject* peer_create_bind_listen_and_accept(PyObject* self, PyObject* args) {
	if (!PyArg_ParseTuple(args, "i", &Peer.port)) return NULL;
	Cpeer_create_bind_listen_and_accept();
	return Py_BuildValue("s", "Success");
}
// ---------------------------------------------------------
// ---------------------------------------------------------


// -------------------------------------------------------
// --------------- Create and Bind -------------------------
void Ccreate_and_bind(void) {
    //create a master socket
    if ((Master.master_socket = socket(AF_INET , SOCK_STREAM , 0)) == 0) 
	stop("[C] Socket() failed : ");
 
    // set master socket to allow multiple connections 
    if( setsockopt(Master.master_socket, SOL_SOCKET, SO_REUSEADDR, (char *)&Master.opt, sizeof(Master.opt)) < 0 ) 
	stop("[C] SocketMaster.opt : ");
 
    //type of socket created
    Master.address.sin_family = AF_INET;
    Master.address.sin_addr.s_addr = INADDR_ANY; // inet_addr(ip)
    Master.address.sin_port = htons(Master.port);
     
    //bind the socket 
    if (bind(Master.master_socket, (struct sockaddr *)&Master.address, sizeof(Master.address))<0) 
	stop("[C] Bind() failed : ");
    printf("[C] Create and bind successfully!\n");
}

static PyObject* create_and_bind(PyObject* self, PyObject* args) {
	if (!PyArg_ParseTuple(args, "i", &Master.port)) return NULL;
	Ccreate_and_bind();
	return Py_BuildValue("s", "Success");
}
// ---------------------------------------------------------
// ---------------------------------------------------------


// ---------------------------------------------------------
// ------------------- INCOMMING CONNECTION ----------------------
//If something happened on the master socket ,
//then its an incoming connection
void Cincomming_connection(void) {
    if (FD_ISSET(Master.master_socket, &Master.readfds)) {
	if ((new_socket = accept(Master.master_socket, (struct sockaddr *)&Master.address, (socklen_t*)&Master.addrlen)) < 0) stop("[C] Accept function ! ");
	char* new_connection_ip = inet_ntoa(Master.address.sin_addr);
	int new_connection_port = ntohs(Master.address.sin_port);
	printf("[C] New connection , socket fd is %d , ip is : %s , port : %d \n" , new_socket , new_connection_ip, new_connection_port);
	
	// add new socket to the table peer socket
	int new_id=-1;
	for (int i=0; i< Master.max_peer; i++) {
	    if (Master.peer_socket[i].fd == 0) {
		Master.peer_socket[i].fd = new_socket;
		// send welcome message 
		bzero(global_buf, BUF_SIZE);
		sprintf(global_buf, "First;%i,%i;", i, new_connection_port); // id; port
		// information of others 
		char temp_buf[BUF_SIZE];
		for (int j=0; j<Master.max_peer; j++) {
		    if (i != j) {
			if (Master.peer_socket[j].fd != 0) {
			    bzero(temp_buf, BUF_SIZE);
			    sprintf(temp_buf, "%i,%s,%i;",Master.peer_socket[j].id, Master.peer_socket[j].ip, Master.peer_socket[j].port);
			    strcat(global_buf, temp_buf);
			}
		    } 
		}	
		Csend_message(new_socket, global_buf);
		Master.peer_socket[i].id = i;
		Master.peer_socket[i].ip = new_connection_ip;
		Master.peer_socket[i].port = new_connection_port;
		
		new_id = i;
		break;
	    } 
	}
	// Send information of this new_peer to old peers
	bzero(global_buf, BUF_SIZE);
	sprintf(global_buf, "%i,%s,%d;", new_id, new_connection_ip, new_connection_port);
	for (int i=0; i<Master.max_peer; i++) {
	    if (i == new_id) continue;
	    else if (Master.peer_socket[i].fd != 0) {
		Csend_message(Master.peer_socket[i].fd, global_buf);
	    }
	}
    }
}
//--------------------- END INCOMMING CONNECTION -----------------
// -------------------------------------------------------------


// -------------------------------------------------------------
//-------------------- INCOMMING MESSAGE ------------------------
void Cincomming_message(void) {
    for (int i=0; i<Master.max_peer; i++) {
	sd = Master.peer_socket[i].fd;
	if (FD_ISSET(sd, &Master.readfds)) {
	    // Check if it was closing
	    if ((val_read = read(sd, Master.buffer, BUF_SIZE)) == 0) {
		// Someone disconnected, print the details
		getpeername(sd, (struct sockaddr*)&Master.address, (socklen_t*)&Master.addrlen);
		printf("[C] Host disconnected, ip %s, port %d \n", inet_ntoa(Master.address.sin_addr), ntohs(Master.address.sin_port));
		close(sd);
		Master.peer_socket[i].fd = 0;
		// Send message to all others Peers to inform
		sprintf(global_buf, "Disconnected;%i;", i);
		Cmaster_send_message_to_all_others_peer();	
	    }
	    // Print the messgage received
	    else {
		Master.buffer[val_read] = '\0';
		strcpy(Master.peer_socket[i].last_message , Master.buffer);
		printf("[C] Message received from %i : %s --- Saved!\n", i, Master.peer_socket[i].last_message);
	    }
	}
    }
}
//----------------- END INCOMMING MESSAGE ----------------------
// -------------------------------------------------------------



// --------------------------------------------------------
// -------------- Master peer start loop ------------------
void* Cmaster_loop(void *args) {
    printf("[C] Running = %i\n", Master.running_master_thread);
    // while running is True : 
    // 1. listen and accept others Peers 
    // 2. when accept => send welcome packet 
    // (all the addresse of others peers)
    while (Master.running_master_thread){
	printf("[C] Thread C is running \n");
	// Initializes the file descriptor set fdset to have zero bits 
	// for all file descriptors
	FD_ZERO(&Master.readfds);

	// add master socket to the set
	FD_SET(Master.master_socket, &Master.readfds);
	Master.max_sd = Master.master_socket;
	
	// add peer's socket to the set of file descriptors
	for (int i=0; i<Master.max_peer; i++) {
	    // socket descriptors
	    sd = Master.peer_socket[i].fd;

	    // if sd==0 : haven't  connection
	    // else : it's a valid socket descriptor => add to the list
	    if (sd>0) FD_SET(sd, &Master.readfds);

	    //highest file descriptor number,
	    //need it for the select function
	    if (sd > Master.max_sd) Master.max_sd = sd;
	}

	//wait for an activity on one of the sockets,
	//timeout is NULL , so wait indefinitely 
	activity = select(Master.max_sd + 1, &Master.readfds, NULL, NULL, NULL);
	if ((activity<0) && (errno != EINTR)) stop("[C] Select error! ");

	Cincomming_connection();

	Cincomming_message();

	sleep(0.1);
    }
    printf("[C] Master thread stopped!\n");
    return NULL;
}

void Cmaster_peer_start_loop(void) {
    // Init the struct
    Cinit_master_peer();
    Master.running_master_thread = true;
    // Create Thread LOOP
    printf("[C] Python create C-master-thread - multiplayers!\n");
    if (pthread_create(&master_thread, NULL, &Cmaster_loop, NULL)) 
	stop("[C] Creation thread failed ! "); // 0 = ok ; >0 = error

}

static PyObject* master_peer_start_loop(PyObject* self) {
	Cmaster_peer_start_loop();
	return Py_BuildValue("s", "Success");
}
// ---------------------------------------------------------
// ---------------------------------------------------------


// --------------------------------------------------------
// ------------------ Master peer end loop -----------------
void Cmaster_peer_end_loop(void) {
    // Change variable global running_master_thread to false
    // => break while loop
    Master.running_master_thread = false;
}

static PyObject* master_peer_end_loop(PyObject* self) {
	Cmaster_peer_end_loop();
	return Py_BuildValue("s", "Success");
}
// ---------------------------------------------------------
// ---------------------------------------------------------


// --------------------------------------------------------
// ------------------ Peer receive from master -----------------
char* Cpeer_receive_from_master(void) {
    bzero(Peer.buffer, 1024);
    if (recv(Peer.master_file_desc, Peer.buffer, 1023, 0) < 0) {
	if (errno != EAGAIN) perror("[C] Peer_receive_from_master failed! ");
    }
    return Peer.buffer;
}

static PyObject* peer_receive_from_master(PyObject* self) {
	return Py_BuildValue("s", Cpeer_receive_from_master());
}
// ---------------------------------------------------------
// ---------------------------------------------------------


// -------------------------------------------------------
// -------------------- Connect to -------------------------
int Cpeer_connect_to(int connect_port, char* connect_ip) {
    // Input : port, ip	    ( of destination )
    // Do : create file descriptor (socket) + connect to ip destination 
    // Return : file descriptor of socket 
    int socket_desc;
    struct sockaddr_in dest;

    // Create socket
    if ((socket_desc = socket(AF_INET, SOCK_STREAM, 0)) < 0) 
	perror("[C] Creation socket failed !" );

    dest.sin_addr.s_addr = inet_addr(connect_ip);
    dest.sin_family = AF_INET;
    dest.sin_port = htons(connect_port);

    // Connect to remote destination
    if (connect(socket_desc, (struct sockaddr *)&dest, sizeof(dest)) < 0) 
	perror("[C] Connect failed !");
    else  
	printf("[C] Connected to %s\n" , connect_ip);
    return socket_desc;
}

// ------------------Peer connect to peer ------------------------
static PyObject* peer_connect_to_peer(PyObject* self, PyObject* args) {
    int connect_port;
    int connect_id;
    char* connect_ip;// bzero(connect_ip, 20); 
    // get 2 arguments from the function
    if (!PyArg_ParseTuple(args, "iis",&connect_id, &connect_port,  &connect_ip)) return NULL;
    printf("[C] Connecting to the peer whose port : %i and ip: %s ... " ,connect_port, connect_ip);
    // Add file descriptor of new peer to a table
    if (Peer.number_of_other_peers < MAX_CONNECTION) {
	int p = Peer.number_of_other_peers; Peer.number_of_other_peers++;
	Peer.peer_socket[p].fd =  Cpeer_connect_to(connect_port, connect_ip);
	Peer.peer_socket[p].ip = connect_ip;
	Peer.peer_socket[p].port = connect_port;
	Peer.peer_socket[p].id = connect_id;
	printf("[C] Connected to player %i\n", connect_id);
	// Send id to the peer connected
	// First message + id : F%i
	sprintf(global_buf, "F%i", Peer.myId);
	Csend_message(Peer.peer_socket[p].fd , global_buf);
	int sd = Peer.peer_socket[p].fd;
	// if sd==0 : haven't  connection
	// else : it's a valid socket descriptor => add to the list
	if (sd>0) FD_SET(sd, &Peer.readfds);

	//highest file descriptor number,
	//need it for the select function
	if (sd > Peer.max_sd) Peer.max_sd = sd;

    } else {
	printf("[C] Can't establish new connection because it reached the maximum !\n");
    }
    return Py_BuildValue("s", "Success");
}

// ------------------Peer connect to master ------------------------
static PyObject* peer_connect_to_master(PyObject* self, PyObject* args) {
    int connect_port;
    char* connect_ip;// bzero(connect_ip, 20); 
    // get 2 arguments from the function
    if (!PyArg_ParseTuple(args, "is", &connect_port,  &connect_ip)) return NULL;
    printf("[C] Connecting to master port : %i, ip: %s ... " ,connect_port, connect_ip);
    Cinit_normal_peer();
    Peer.master_file_desc =  Cpeer_connect_to(connect_port, connect_ip);
    return Py_BuildValue("s", "Success");
}
// ---------------------------------------------------------
// ---------------------------------------------------------


// -------------------------------------------------------
// -------------------- Peer incomming connection -------------------------
void Cpeer_incomming_connection(void) {
    if (FD_ISSET(Peer.master_socket, &Peer.readfds)) {
	if ((new_socket = accept(Peer.master_socket, (struct sockaddr *)&Peer.address, (socklen_t*)&Peer.addrlen)) < 0) stop("[C] Accept function ! ");
	char* new_connection_ip = inet_ntoa(Peer.address.sin_addr);
	int new_connection_port = ntohs(Peer.address.sin_port);
	printf("[C] Connected socket fd is %d , ip is : %s , port : %d \n" , new_socket , new_connection_ip, new_connection_port);
	
	// add new socket to the table peer socket
	for (int i=0; i< Peer.max_peer; i++) {
	    if (Peer.peer_socket[i].fd == 0) {
		Peer.peer_socket[i].fd = new_socket;
		Peer.peer_socket[i].id = -1;//  Set id later 
		Peer.peer_socket[i].ip = new_connection_ip;
		Peer.peer_socket[i].port = new_connection_port;
		break;
	    } 
	}
    }
}
// -------------------- Peer incomming message -------------------------
void Cpeer_incomming_message(void) {
    for (int i=0; i<Peer.max_peer; i++) {
	sd = Peer.peer_socket[i].fd;
	if (FD_ISSET(sd, &Peer.readfds)) {
	    // Check if it was closing
	    if ((val_read = read(sd, Peer.buffer, BUF_SIZE)) == 0) {
		// Someone disconnected, print the details
		getpeername(sd, (struct sockaddr*)&Peer.address, (socklen_t*)&Peer.addrlen);
		printf("[C] Host disconnected, ip %s, port %d \n", inet_ntoa(Peer.address.sin_addr), ntohs(Peer.address.sin_port));
		close(sd);
		Peer.peer_socket[i].fd = 0;
	    }
	    // Print the messgage received
	    else {
		Peer.buffer[val_read] = '\0';
		// If first message => id of the player
		if (Peer.buffer[0] == 'F') {
		    char c = Peer.buffer[1] ; int int_c = c - '0';
		    printf("[C] Connected to player %i\n", int_c);
		    Peer.peer_socket[i].id = int_c;
		} else {
		    strcpy(Peer.peer_socket[i].last_message , Peer.buffer);
		    printf("[C] Message received from %i : %s --- Saved!\n", Peer.peer_socket[i].id, Peer.peer_socket[i].last_message);
		}
	    }
	}
    }
}
// ---------------------------------------------------------
// ---------------------------------------------------------


// --------------------------------------------------------
// -------------- Normal peer start loop ------------------
void* Cpeer_loop(void *args) {
    printf("[C] Peer's loop is running ...\n");
    // while running is True : 
    // 1. listen and accept others Peers 
    // 2. when accept => send welcome packet 
    // (all the addresse of others peers)
    while (Peer.running_master_thread){
	/*printf("[C] Thread C is running \n");*/
	// Initializes the file descriptor set fdset to have zero bits 
	// for all file descriptors
	FD_ZERO(&Peer.readfds);

	// add master socket to the set
	FD_SET(Peer.master_socket, &Peer.readfds);
	Peer.max_sd = Peer.master_socket;
	
	// add peer's socket to the set of file descriptors
	for (int i=0; i<Peer.max_peer; i++) {
	    // socket descriptors
	    sd = Peer.peer_socket[i].fd;

	    // if sd==0 : haven't  connection
	    // else : it's a valid socket descriptor => add to the list
	    if (sd>0) FD_SET(sd, &Peer.readfds);

	    //highest file descriptor number,
	    //need it for the select function
	    if (sd > Peer.max_sd) Peer.max_sd = sd;
	}

	//wait for an activity on one of the sockets,
	//timeout is NULL , so wait indefinitely 
	activity = select(Peer.max_sd + 1, &Peer.readfds, NULL, NULL, NULL);
	if ((activity<0) && (errno != EINTR)) stop("[C] Select error! ");

	Cpeer_incomming_connection();

	Cpeer_incomming_message();

	sleep(0.1);
    }
    printf("[C] Peer thread stopped!\n");
    return NULL;
}

void Cnormal_peer_start_loop(void) {
    // Init the struct
    Cinit_normal_peer();
    Peer.running_master_thread = true;
    // Create Thread LOOP
    printf("[C] Python create C thread : run peer_loop!\n");
    if (pthread_create(&peer_thread, NULL, &Cpeer_loop, NULL)) 
	stop("[C] Creation thread failed ! "); // 0 = ok ; >0 = error

}

static PyObject* normal_peer_start_loop(PyObject* self) {
	Cnormal_peer_start_loop();
	return Py_BuildValue("s", "Success");
}
// ---------------------------------------------------------
// ---------------------------------------------------------


// -------------------------------------------------------
// --------------- Set my id-------------------------
static PyObject* set_my_id(PyObject* self, PyObject* args) {
	if (!PyArg_ParseTuple(args, "i", &Peer.myId)) return NULL;
	return Py_BuildValue("s", "Success");
}
// ---------------------------------------------------------
// ---------------------------------------------------------


// ----------------------------------------------------------------
// --------------- Peer get message saved from player ------------------
char* Cpeer_get_message_from_player(int index) {
    // Master isn't in the peer_socket
    // so => index == -1 to get the last_message of Master
    return Peer.peer_socket[index].last_message;
}

static PyObject* peer_get_message_from_player(PyObject* self, PyObject* args) {
    int index ;
    if (!PyArg_ParseTuple(args, "i", &index)) return NULL;
    return Py_BuildValue("s", Cpeer_get_message_from_player(index));
}
// --------------- MASTER get message saved from player ------------------
char* Cmaster_get_message_from_player(int index) {
    // Master isn't in the peer_socket
    // so => index == -1 to get the last_message of Master
    return Master.peer_socket[index].last_message;
}

static PyObject* master_get_message_from_player(PyObject* self, PyObject* args) {
    int index ;
    if (!PyArg_ParseTuple(args, "i", &index)) return NULL;
    return Py_BuildValue("s", Cmaster_get_message_from_player(index));
}
// ---------------------------------------------------------
// ---------------------------------------------------------


// ------------------ Build Module --------------------------
// ----------------------------------------------------------
// If a method hasn't arguments => you must add (PyCFunction)
static PyMethodDef networkMethods[] = { // (PyCFunction)
    {"master_send_all", master_send_all, METH_VARARGS, "MASTER send message to all Peers"},
    {"peer_send_all", peer_send_all, METH_VARARGS, "Peer send message to Master + all Peers"},
    {"master_get_message_from_player", peer_get_message_from_player, METH_VARARGS, "Master get message from player with id"},
    {"peer_get_message_from_player", master_get_message_from_player, METH_VARARGS, "Peer get message from player with id; -1 for master"},
    {"set_my_id", set_my_id, METH_VARARGS, "Set id received from master"},
    {"peer_connect_to_peer", peer_connect_to_peer, METH_VARARGS, "Create a connection to an other peer by an addresse and a port specify"},
    {"normal_peer_start_loop", (PyCFunction)normal_peer_start_loop, METH_NOARGS, "Start normal peer loop, to wait for connections"},
    {"peer_create_bind_listen_and_accept", peer_create_bind_listen_and_accept, METH_VARARGS, "Create and bind socket normal peer"},
    {"peer_receive_from_master", (PyCFunction)peer_receive_from_master, METH_NOARGS, "Receive packet (string) from master"},
    {"peer_connect_to_master", peer_connect_to_master, METH_VARARGS, "Create a connection to master_peer by an addresse and a port specify"},
    {"master_peer_end_loop", (PyCFunction)master_peer_end_loop, METH_NOARGS, "End master peer loop"},
    {"master_peer_start_loop", (PyCFunction)master_peer_start_loop, METH_NOARGS, "Start master peer loop, to wait for connections"},
    {"listen_and_accept", (PyCFunction)listen_and_accept, METH_NOARGS, "Create and bind socket master"},
    {"create_and_bind", create_and_bind, METH_VARARGS, "Create and bind socket master"},
    {"get_ip_public", (PyCFunction)get_ip_public, METH_NOARGS, "Get IP public of this machine"},
	{"master_send_message_to_all_others_peer", master_send_message_to_all_others_peer, METH_VARARGS, "Send a message from master peer to all others peer"},
	{"peer_send_message_to_all_others_peer", peer_send_message_to_all_others_peer, METH_VARARGS, "Send a message from a peer to all anothers peer"},
    {NULL, NULL, 0, NULL} // terminator
};

// Build Module
static struct PyModuleDef Cnetwork = {
		PyModuleDef_HEAD_INIT,
		"Cnetwork", // name the moudule
		"Networking PTP by C", // Doc
		-1, // state
		networkMethods
};

// important : PyInit_  +  name_module
PyMODINIT_FUNC PyInit_Cnetwork(void) {
	return PyModule_Create(&Cnetwork);
}
// ----------------------------------------------------------
// ----------------------------------------------------------





/*
// -------------------------------------------------------
// -------------------- Template -------------------------
void C(void) {
}

static PyObject* template(PyObject* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "i", &port)) return NULL;
    Cfunction();
    return Py_BuildValue("s", "Success");
}
// ---------------------------------------------------------
// ---------------------------------------------------------

*/


