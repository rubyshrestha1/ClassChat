import socket
from threading import Thread
import json
import ctypes

#changing terminal window title name as "Server Window"
ctypes.windll.kernel32.SetConsoleTitleW("Server Window")


#function to display menu in client's window.
def menu(client):
    menu0 = "----------------------------------------------------------------------------------------------------\n"
    menu1 = " Tips on Getting Started \n"
    menu2 = " 1. To send message in ClassChat, type message and press Enter.\n"
    menu3 = " 2. To send private message, type receiver's name followed by colon and message. \n"
    menu4 = " 3. To create group, type group followed by space, groupname, space and members separated by comma.\n"
    menu5 = "    For example: group group413 Alice,Bob,John,Mary \n"
    menu6 = "    ***NOTE: *** groupname should start with word 'group'. \n"
    menu7 = "    To send message to group type groupname followed by colon and message. \n"
    menu8 = " 4. To exit out of chat system, type exit and hit enter. \n"
    menu9 = " 5. To get this menu again, type menu and press enter. \n"
    finalMenu = menu0+menu1+menu2+menu3+menu4+menu5+menu6+menu7+menu8+menu9+menu0
    client.send(finalMenu.encode('utf-8'))



#function to create group wwith specified group name and active clients
def create_group(message, sender):
    groupedClientSockets = []                       #array to store sockets when group is created
    groupedClients=[]                               #array to store  name of clients in group
    listWords =message.split()
    #condition to handle when proper syntax is not used
    if len(listWords)<3:
        to_send="Syntax error. Please use format - group groupName member1,member2,..."
        status=0
        print("Syntax error")
        clients[sender].send(to_send.encode('utf-8'))
        
    #when group name is provided in syntax
    else:
        groupName=listWords[1]
        clientListGroup = listWords[2].split(",")
        #condition to check whether clientListGroup has valid data
        if clientListGroup:
            #group is not created if there are less than three people in a group
            if len(clientListGroup)< 3:
                message = "Group should have atleast three members"
                clients[sender].send(message.encode('utf-8'))
                print("Group creation unsuccessful")
                
            #creating group successfully when syntax is followed and number of members >=3
            else:
                print("GroupName: ",groupName)
                for client in clientListGroup:
                    #adding clients in group if they are active
                    if client in clients:
                        groupedClients.append(client)
                        groupedClientSockets.append(clients[client])
                    #printing message in server and sending message to sender if client(s) sleected for group is not active
                    else:
                        message=f"{client} is not active"
                        print(message)
                        clients[sender].send(message.encode())
        #printing information about group created
                print(f"Group of {len(groupedClients)} people created.")
                print(groupedClients)
                clients[groupName] =groupedClientSockets
        
        #notifying all users except group creater in group that they have been added in the group.
        #Group creater does not necessarily have to be in group they created.
                for csockets in clients[groupName]:
                    #condition to display message to clients who were added to group
                    if csockets!= clients[sender]:
                         message=f"{sender} added you in {groupName}"
                         csockets.send(message.encode('utf-8'))
                #message to display that group has been created to the client who created group
                message = f"Group {groupName} is created successfully"
                clients[sender].send(message.encode('utf-8'))
                groupedClients =[]



#function to message in group
def group_message(sender, receiver, message):
    #condition to handle when sender is not in the group they are trying to send message to 
    if clients[sender] not in clients[receiver]:
        to_send = f"You are not in {receiver}"
        send_to_socket=clients[sender]
        send_to_socket.send(to_send.encode('utf-8'))
        
    # conditions when sender is in group they are trying to send message to
    else:
        count=0
        to_send = f"<{sender}> in {receiver}: {message}"
        send_to_sockets = clients[receiver]
        for csocket in send_to_sockets:
            #condition to check whether the client is connected to server and whether it is not sender
            if csocket in clients.values() and csocket!=clients[sender]:
                count+=1
                csocket.send(to_send.encode('utf-8'))
        print ("sent to ", count)

        #when the sender is only one user in group, the group is deleted from server
        if count == 0:
            status = 0
            print(f"{sender} is only in the group. Deleting group")
            to_send = f"You are alone in group. Server will now delete the group"
            clients[sender].send(to_send.encode('utf-8'))

            del clients[receiver]

        
#function to listen for clients
def listen_for_client(cs,):
    status = 0                                       #starts = 0 implies message has not been delivered to any other clients
    while True:
        data = cs.recv(2048)                         #data received from client
        received = data.decode('utf-8') 
        greater_than_index = received.index(">")
        #condition to handle when user presses enter or any keywords except for menu, exit, group  or does not specify receiver 
        if len(received[greater_than_index:])==1:
            continue
        print(received)
        #determining sender name
        sender = received[:greater_than_index]
        colon = ':'
        #condition to handle if user has used keywords menu, exit or group
        if colon not in received:
            message = received[greater_than_index+1 : ]
            #break the loop if user enter exit
            if message.lower() == 'exit':
                break
            #call menu function to display menu if sender sends menu keyword
            elif message.lower() == 'menu':
                menu(clients[sender])
                continue
            # condition to create group when sender uses group keyword
            elif message[:5].lower() == "group":
                create_group(message, sender)
                continue
            #if any of the other words are used, it is broadcasted to all connected clients but self
            else:
                for client in clients:
                    #condition to not send message to itself and to group
                    if client != sender and client[0:5] != "group":
                        status = 1                      #status =1 mean message has been delivered to at least one other client
                        receiver = "everyone"
                        message = received[received.index(">")+1:]
                        to_send = f'{sender} in ClassChat : {message}'
                        clients[client].send(to_send.encode('utf-8'))
            
        #conditions when sender sends message to other user (receiver)
        else:
            message = received[received.index(":")+1 : ]
            receiver = received[greater_than_index+1:received.index(":")]
            
            #condition to handle when receiver is not connected to server
            if receiver not in clients:
                status = 0
                message = "[ From server ] \n Client not active. Message not delivered. Try later"
                send_to_socket = clients[sender]
                send_to_socket.send(message.encode('utf-8'))
                
            #conditions when receiver is connected to server
            else:
                #when sender is trying to send message to group
                if "group" in receiver:
                    group_message(sender, receiver, message)
                    if clients[sender] in clients[receiver]:
                        status = 1
                    else:
                        status = 0
                   

                # if sender is trying to directly message to receiver          
                else:
                    status = 1
                    to_send = f"<{sender}> : {message}"
                    send_to_socket = clients[receiver]
                    send_to_socket.send(to_send.encode('utf-8'))
        #dictionary to hold the message status and details to display in server
        dictionary = {"status" : status, "sender" : sender, "receiver" : receiver, "text" : message}
        #converting dictionary to json format
        jsonD = json.dumps(dictionary, indent = 2)
        print(jsonD)
       
                    
    #statements executed when client enters exit keyword. Message is printed in server and the client connection is closed.       
    print (sender , " disconnected...")
    clientsockets.remove(cs)
    del clients[sender]
    cs.close()


HOST = "127.0.0.1"
PORT = 12000
#establishing tcp connection
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind((HOST, PORT))
#printing information about server being ready
print("Server started")
print("Waiting for client requests..")
print ("If you want to close server, close the window")
clients ={}                                             #dictionary to hold client's username as keys and socket as values
clientsockets=set()                                     #set to hold clientsockets
threadcount=0                                           #variable to keep track of total number of threads in server

while True:
    serverSocket.listen()                               #listedning for client connection
    clientsock, clientAddress = serverSocket.accept()   #accepting client connection
    threadcount+=1                                      #updating thread count
    print("Total thread count: ",threadcount)
    clientsockets.add(clientsock)                       #adding connected client to set of client sockets 
    clientName = clientsock.recv(1024).decode('utf-8')  #receiving username from client
    
    #condition to handle duplicate username
    if clientName in clients:
        print("Duplicate username")
        error_message = "Username is taken. Use another name."
        clientsock.send(error_message.encode('utf-8'))
        continue
    
    #condition to execute when username is not duplicate
    else:
        success_msg = "Username accepted"
        clientsock.send(success_msg.encode('utf-8'))
        
    clients[clientName]=clientsock                      #adding to dictionary when username is accepted
    print(f"{clientName} has connected")                #printing the connection infor,ation in server
    print(f"Number of active clients: {len(clients)}")  #kepping track of active clients in server

    #function call to display menu to client connected
    menu(clientsock)

    #Threading to handle multiple clients
    newthread = Thread(target = listen_for_client, args=(clientsock,))
    newthread.start()


