import socket
import argparse
import os

#Parse arguments for simple file server
parser = argparse.ArgumentParser()

parser.add_argument('-v', help = 'Prints debubgging messages.', type = str)
parser.add_argument('-p', help = 'Specifies the port number that the server will listen and serve at. Default is 8080', type = int)
parser.add_argument('-d', help = 'Specifies the directory that the server will use to read/write requested '
                                 'files. Default is the current directory when launching the application.', type = str)

args = parser.parse_args()

#Default port is 8080
port = 8080

if args.p is not None:
    port = args.p

#Default file directory
directory = os.path.dirname(os.path.realpath(__file__))

if args.d is not None:
    directory = args.d

#Files in the directory. This will be used for the GET request.
filesInDirectory = os.listdir(directory)

#Remove the httpfs.py file from the list of files to retrieve.
if directory == os.path.dirname(os.path.realpath(__file__)):
    filesInDirectory.remove("httpfs.py")

#Setup server socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind(('', port))
serverSocket.listen(1)

def getGETorPOST(clientRequest):
    clientRequest = clientRequest.split('\r\n')
    getOrPostHeader = clientRequest[0].split()
    return getOrPostHeader

def getData(clientRequest):
    dataLines = clientRequest.index('')
    data = ""
    for dataLine in clientRequest[dataLines + 1:]:
        data += dataLine
    return data

def getFunction(path):
    #We are in the current directory
    getResponse = ""
    if path == "/":
        #display all files in the directory
        for file in filesInDirectory:
            getResponse += file + '\n'
    #We are in a file
    else:
        #display the file contents
        if path[1:] in filesInDirectory:
            thisFile = open(directory + path, 'r')
            getResponse = thisFile.read()
            thisFile.close()
        else:
            getResponse = "This file does not exist or cannot be found in the current directory."
    return getResponse

def postFunction(path, clientRequest):
    postResponse = ''
    # If the file is in the directory, write to the file. Otherwise, return an error code.
    if path[1:] in filesInDirectory:
        thisFile = open(directory + path, 'w')
        thisData = getData(clientRequest)
        thisFile.write(thisData)
        thisFile.close()
        postResponse = "Writing to existing file."
    else:
        thisFile = open(directory + path, 'w')
        thisData = getData(clientRequest)
        thisFile.write(thisData)
        thisFile.close()
        postResponse = "writing to new file."
    return postResponse



while True:
    connection, address = serverSocket.accept()
    clientRequest = connection.recv(4096).decode("utf-8")
    #Decode to get GET or POST
    getOrPostHeader = getGETorPOST(clientRequest)
    getOrPost = getOrPostHeader[0]
    #Decode to get the path
    path = getOrPostHeader[1]
    #Decode to get the data
    data = getData(clientRequest)
    #Decode to get response
    requestResponse = ""
    if getOrPost == 'GET':
        requestResponse = getFunction(path)
    elif getOrPost == 'POST':
        requestResponse = postFunction(path, clientRequest)
    #Send the response
    connection.sendall(bytes(requestResponse, "utf-8"))
    connection.close()


