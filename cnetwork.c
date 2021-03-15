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


#define BUFFER_SIZE 512
#define false 0
#define true 1
typedef int bool;
// ------------------------------------------------------------
// ------------------- Delaration variable ---------------------

// ip public
char ip[20];
char global_buf[1024];
char global_buf2[1024];
int sd, activity, new_socket, val_read;

//----------------------MASTER PEER ----------------------
// To avoid confusion between master_peer and peer,
// We structure the data by Struct
struct PeerSocket {
    int fd;
    int id;
    char* ip;
    int port;
};
struct MasterPeer {
    struct sockaddr_in address;
    int master_socket;
    int opt;
    int port;
    int addrlen;
    int max_sd;
    char buffer[1024];
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
    char buffer[1024];
};

//Initialization
struct NormalPeer Peer;
void Cinit_normal_peer(void) {
    bzero(Peer.buffer, 1024);
}
//--------------------END PEER ----------------------


// thread which runs master_loop
pthread_t master_thread;
pthread_t data_thread;
// -------------------END Delaration variable ---------------------
// ---------------------------------------------------------------


// -------------------------------------------------------
// ------------- STOP = PERROR + EXIT -------------------
void stop(char* msg) {
	perror(msg);
	exit(EXIT_FAILURE);
}
// -------------------------------------------------------
// -------------------------------------------------------


// -------------------------------------------------------
// --------------- Get IP Public -------------------------
char* Cget_ip_public(void) {
	FILE* file; bzero(ip, 20);
	// https://www.cyberciti.biz/faq/how-to-find-my-public-ip-address-from-command-line-on-a-linux/	
	// save ip public to file by direction, then read the file
	if (system("dig +short myip.opendns.com @resolver1.opendns.com > ip") < 0) stop("System(dig) : ")	;
	if ((file = fopen("ip", "r")) == NULL ) stop("Open file : ");
	fscanf(file, "%s", ip);
	fclose(file);
	// Delete file ip
	if (system("rm ip") < 0) stop("System(rm) : ");
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
    printf("Listener on port %d \n", Master.port);
    //try to specify maximum of 3 pending connections for the master socket
    if (listen(Master.master_socket, 3) < 0) stop("Listen() : ");
     
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
// --------------- Create and Bind -------------------------
void Ccreate_and_bind(void) {
    //create a master socket
    if ((Master.master_socket = socket(AF_INET , SOCK_STREAM , 0)) == 0) 
	stop("Socket() failed : ");
 
    // set master socket to allow multiple connections 
    if( setsockopt(Master.master_socket, SOL_SOCKET, SO_REUSEADDR, (char *)&Master.opt, sizeof(Master.opt)) < 0 ) 
	stop("SocketMaster.opt : ");
 
    //type of socket created
    Master.address.sin_family = AF_INET;
    Master.address.sin_addr.s_addr = INADDR_ANY; // inet_addr(ip)
    Master.address.sin_port = htons(Master.port);
     
    //bind the socket 
    if (bind(Master.master_socket, (struct sockaddr *)&Master.address, sizeof(Master.address))<0) 
	stop("Bind() failed : ");
    printf("Create and bind successfully!\n");
}

static PyObject* create_and_bind(PyObject* self, PyObject* args) {
	if (!PyArg_ParseTuple(args, "i", &Master.port)) return NULL;
	Ccreate_and_bind();
	return Py_BuildValue("s", "Success");
}
// ---------------------------------------------------------
// ---------------------------------------------------------


// -------------------------------------------------------
// --------------- Send Message Function------------------------
void Csend_message(int soc, char* message) {
    if ((size_t)send(soc, message, strlen(message), 0) != strlen(message)) 
	stop("Send message function !");
}
// ---------------------------------------------------------
// ---------------------------------------------------------


// ---------------------------------------------------------
// ------------------- INCOMMING CONNECTION ----------------------
//If something happened on the master socket ,
//then its an incoming connection
void Cincomming_connection(void) {
    if (FD_ISSET(Master.master_socket, &Master.readfds)) {
	if ((new_socket = accept(Master.master_socket, (struct sockaddr *)&Master.address, (socklen_t*)&Master.addrlen)) < 0) stop("Accept function ! ");
	char* new_connection_ip = inet_ntoa(Master.address.sin_addr);
	int new_connection_port = ntohs(Master.address.sin_port);
	printf("New connection , socket fd is %d , ip is : %s , port : %d \n" , new_socket , new_connection_ip, new_connection_port);
	
	// add new socket to the table peer socket
	int new_id=-1;
	for (int i=0; i< Master.max_peer; i++) {
	    if (Master.peer_socket[i].fd == 0) {
		Master.peer_socket[i].fd = new_socket;
		// send welcome message 
		sprintf(global_buf, "%s%i;", "id=", i);
		// information of others 
		char temp_buf[1024];
		for (int j=0; j<Master.max_peer; j++) {
		    if (i != j) {
			if (Master.peer_socket[j].fd != 0) {
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
	sprintf(global_buf, "%i,%s,%d", new_id, new_connection_ip, new_connection_port);
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
	    if ((val_read = read(sd, Master.buffer, 1024)) == 0) {
		// Someone disconnected, print the details
		getpeername(sd, (struct sockaddr*)&Master.address, (socklen_t*)&Master.addrlen);
		printf("Host disconnected, ip %s, port %d \n", inet_ntoa(Master.address.sin_addr), ntohs(Master.address.sin_port));
		close(sd);
		Master.peer_socket[i].fd = 0;
	    }
	    // Print the messgage received
	    else {
		Master.buffer[val_read] = '\0';
		printf("Message received : %s", Master.buffer);
	    }
	}
    }
}
//----------------- END INCOMMING MESSAGE ----------------------
// -------------------------------------------------------------



// --------------------------------------------------------
// -------------- Master peer start loop ------------------
void* Cmaster_loop(void *args) {
    printf("Running = %i\n", Master.running_master_thread);
    // while running is True : 
    // 1. listen and accept others Peers 
    // 2. when accept => send welcome packet 
    // (all the addresse of others peers)
    while (Master.running_master_thread){
	printf("Thread C is running \n");
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
	if ((activity<0) && (errno != EINTR)) stop("Select error! ");

	Cincomming_connection();

	Cincomming_message();

	sleep(0.1);
    }
    printf("Master thread stopped!\n");
    return NULL;
}

void Cmaster_peer_start_loop(void) {
    // Init the struct
    Cinit_master_peer();
    Master.running_master_thread = true;
    // Create Thread LOOP
    printf("Python create C thread - multiplayers!\n");
    if (pthread_create(&master_thread, NULL, &Cmaster_loop, NULL)) 
	stop("Creation thread failed ! "); // 0 = ok ; >0 = error

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
    if (recv(Peer.master_file_desc, Peer.buffer, 1023, 0) < 0) {
	if (errno != EAGAIN) perror("Peer_receive_from_master failed! ");
    } 
    return Peer.buffer ;
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
	perror("Creation socket failed !" );

    dest.sin_addr.s_addr = inet_addr(connect_ip);
    dest.sin_family = AF_INET;
    dest.sin_port = htons(connect_port);

    // Connect to remote destination
    if (connect(socket_desc, (struct sockaddr *)&dest, sizeof(dest)) < 0) 
	perror("Connect failed !");
    else  
	printf("Connected to %s\n" , connect_ip);
    return socket_desc;
}

static PyObject* peer_connect_to(PyObject* self, PyObject* args) {
    int connect_port;
    char* connect_ip;// bzero(connect_ip, 20); 
    // get 2 arguments from the function
    if (!PyArg_ParseTuple(args, "is", &connect_port,  &connect_ip)) return NULL;
    printf("Connecting to port : %i, ip: %s ... " ,connect_port, connect_ip);
    Cinit_normal_peer();
    Peer.master_file_desc =  Cpeer_connect_to(connect_port, connect_ip);
    return Py_BuildValue("s", "Success");
}
// ---------------------------------------------------------
// ---------------------------------------------------------


// ------------------ Build Module --------------------------
// ----------------------------------------------------------
// If a method hasn't arguments => you must add (PyCFunction)
static PyMethodDef networkMethods[] = { // (PyCFunction)
    {"peer_receive_from_master", (PyCFunction)peer_receive_from_master, METH_NOARGS, "Receive packet (string) from master"},
    {"peer_connect_to", peer_connect_to, METH_VARARGS, "Create a connection to a addresse and port specify"},
    {"master_peer_end_loop", (PyCFunction)master_peer_end_loop, METH_NOARGS, "End master peer loop"},
    {"master_peer_start_loop", (PyCFunction)master_peer_start_loop, METH_NOARGS, "Start master peer loop, to wait for connections"},
    {"listen_and_accept", (PyCFunction)listen_and_accept, METH_NOARGS, "Create and bind socket master"},
    {"create_and_bind", create_and_bind, METH_VARARGS, "Create and bind socket master"},
    {"get_ip_public", (PyCFunction)get_ip_public, METH_NOARGS, "Get IP public of this machine"},
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


