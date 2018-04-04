import socket
import os
import threading
from datetime import datetime

#This class is used to store the list of active users
class ChatRoom(object):
    def __init__(self):
        self.listOfUsers = []

    def newUser(self, user):
        self.listOfUsers.append(user)

    def getUsers(self):
        return self.listOfUsers

    def removeUser(self, user):
        self.listOfUsers.remove(user)

#Formats messages to be send from client to server
def buildMessage(username, command, userMessage):
    return username + "\n" + command + "\n" + userMessage

#Handles messages received from client
def clientCommands(s, username, ip, port):
    running = True
    while running:
        #Reads what the user types and stores it in the variable
        userInput = input()
        #Unless otherwise specified, the user is assumed to be talking
        command = 'talk'
        if userInput == '/leave':
            appMessage = buildMessage(username, 'quit', userInput)
            s.sendto(appMessage.encode('utf-8'), ('localhost', port))
            command = 'leave'
            #The user has left the conversation, they can no longer send messages
            running = False
        if userInput == '/who':
            appMessage = buildMessage(username, 'who', userInput)
            s.sendto(appMessage.encode('utf-8'), ('localhost', port))
        else:
            appMessage = buildMessage(username, command, userInput)
            s.sendto(appMessage.encode('utf-8'), (ip, port))

#Handles messages at the server side
def serverCommands(s, chatRoom):
    running = True
    while running:
        applicationMessage = s.recv(4096)
        (user, command, userMessage) = parseMessage(applicationMessage)
        #If the user sending the message is not part of the list of chat room users, add them
        if user not in chatRoom.getUsers():
            chatRoom.newUser(user)
        #Print what the user is saying
        if command == 'talk':
            print(datetime.now(), ' [', user, ']: ', userMessage)
        #Join the user to the chatroom
        if command == 'join':
            print(datetime.now(), user, 'Joined successfully!')
        #Return a list of users currently in the chatroom
        if command == 'who':
            print('The users in the conversation are: ', chatRoom.getUsers())
        #The user is leaving the chatroom so remove them from the list of users
        if command == 'leave':
            print(datetime.now(), user, " has left the conversation.")
            chatRoom.removeUser(user)
        #The user should no longer be able to contact the server
        if command == 'quit':
            print("Have a nice day! Come again soon :)")
            running = False
            #exit(0)

def parseMessage(applicationMessage):
    applicationMessage = applicationMessage.decode('utf-8')
    applicationMessage = applicationMessage.split('\n')
    username = applicationMessage[0]
    command = applicationMessage[1]
    userMessage = applicationMessage[2]
    return(username, command, userMessage)

def sender(username, ip, port):
    #Setup UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    #Join user to conversation
    joinMessage = buildMessage(username, 'join', '')
    s.sendto(joinMessage.encode('utf-8'), (ip, port))
    #Read text from user input
    clientCommands(s, username, ip, port)

def receiver(username, ip, port):
    #Setup UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', port))
    print("Connected to port: ", port)
    #Receive message
    chatRoom = ChatRoom()
    if username not in chatRoom.getUsers():
        chatRoom.newUser(username)
    serverCommands(s, chatRoom)

name = input('Please enter your name: ')
peers = os.fork()
if peers == 0:
    receiver(name, '', 1996)
else:
    sender(name, '255.255.255.255', 1996)
