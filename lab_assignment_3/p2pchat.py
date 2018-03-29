import socket
import os
import threading
from datetime import datetime

class ChatRoom(object):
    def __init__(self):
        self.listOfUsers = []

    def newUser(self, user):
        self.listOfUsers.append(user)

    def getUsers(self):
        return self.listOfUsers

def buildMessage(username, command, userMessage):
    return username + "\n" + command + "\n" + userMessage

def joinUserToConversation(s, username, ip, port):
    command = 'join'
    joinMessage = buildMessage(username, command, '')
    chatRoom.newUser(username)
    s.sendto(joinMessage.encode('utf-8'), (ip, port))

def readCommands(s, username, ip, port):
    running = True
    while running:
        userInput = input()
        command = 'talk'
        if userInput == '/leave':
            command = 'quit'
            appMessage = buildMessage(username, command, userInput)
            s.sendto(appMessage.encode('utf-8'), ('localhost', port))
            command = 'leave'
            read = False
        if userInput == '/who':
            print('The users in the conversation are: ', chatRoom.getUsers())
        else:
            appMessage = buildMessage(username, command, userInput)
            s.sendto(appMessage.encode('utf-8'), (ip, port))

def receiveMessage(s):
    running = True
    while running:
        applicationMessage = s.recv(4096)
        (user, command, userMessage) = parseMessage(applicationMessage)
        if command == 'talk':
            print(datetime.now(), ' [', user, ']: ', userMessage)
        if command == 'join':
            print(datetime.now(), user, 'Joined successfully!')
            chatRoom.newUser(user)
        if command == 'leave':
            print(datetime.now(), user, " has left the conversation.")
        if command == 'quit':
            print("Have a nice day! Come again soon :)")

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
    joinUserToConversation(s, username, ip, port)
    #Read text from user input
    readCommands(s, username, ip, port)

def receiver(username, ip, port):
    #Setup UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', port))
    print("Connected to port: ", port)
    #Receive message
    receiveMessage(s)

chatRoom = ChatRoom()
quitReceiver = False
name = input('Please enter your name: ')
peers = os.fork()
if peers == 0:
    receiver(name, '', 1996)
else:
    sender(name, '255.255.255.255', 1996)
