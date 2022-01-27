from socket import *
from threading import Thread
import ctypes


serverName = '127.0.0.1'
serverPort = 12000
#establishing tcp connection
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))

#asking user for their name. If the username is already in the server, it prompts user to enter new name,
#else, success message is displayed.
sender = input ("Enter your name: ")
clientSocket.send(sender.encode('utf-8'))
received = clientSocket.recv(1024).decode('utf-8')
print(received, "\n")
while received == "Username is taken. Use another name.":
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    sender = input ("Enter your name: ")
    clientSocket.send(sender.encode('utf-8'))
    received = clientSocket.recv(1024).decode('utf-8')
    print(received, "\n")


#customizing terminal title name according to username
ctypes.windll.kernel32.SetConsoleTitleW(sender+"'s window")


#function to listen for messages.
def listen_for_messages():
    while True:
        #If message is received, it prints in client's terminal.
        try:
            received = clientSocket.recv(1024).decode('utf-8')
            print(received)
        #if message is not received, notifies user of the status
        except:
            print("No connection with server")
            break

#function to send message by client
def send_message():
    while True:
        sentence = input("")
        to_send = f"{sender}>{sentence}"
        clientSocket.send(to_send.encode('utf-8'))
        #if user enter exit, connection is closed.
        try:
            if sentence.lower() == "exit":
                break
        except:
            print("Closing connection")
    
    clientSocket.close()


#threads to user to send and receive messages at the same time
receiveThread = Thread(target=listen_for_messages)
receiveThread.start()
sendThread = Thread(target=send_message)
sendThread.start()



