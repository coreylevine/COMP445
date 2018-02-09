import socket
import argparse
from urllib.parse import urlparse


def get(url,v):
   # 1: is to initialize the socket
   listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   # use urlparse to extract the hostname from the url
   url = urlparse(url)
   # 2: Connect to the server at port 80
   listener.connect((url.hostname, 80))
   # 3: using GET to request from the server and \r\n\r\n to send the request
   req = "GET " + url.path + "?" + url.query + " HTTP/1.1\r\nHost: " + url.hostname + "\r\n\r\n"
   # 4: send out the request
   listener.sendall(req.encode("utf-8"))
   response = listener.recv(4096).decode("utf-8")
   #5: a response variable receives the response at post 1024

   #If the request is a verbose type, include the 9 first lines which is the header info included in a verbose request
   if not v:
       response = response.split("\n")
       for i in range(9,len(response)):
           print(response[i])

   else:
       print(response)
   listener.close()

def post(url, header, data, v):
   # first step is to initialize the socket
   listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   # use urlparse to extract the hostname from the url
   url = urlparse(url)
   listener.connect((url.hostname, 80))
   req = "POST " + url.path + " HTTP/1.1" + "\r\n" + "Host: " + url.hostname + "\r\n" + "Content-Length: " + str(len(data)) + "\r\n" + header + "\r\n\r\n" + data + "\r\n\r\n"
   # 4: send out the request
   listener.sendall(req.encode("utf-8"))
   response = listener.recv(4096).decode("utf-8")
   #5: a response variable receives the response at post 1024
   # If the request is a verbose type, include the 9 first lines which is the header info included in a verbose request

   if not v:
       response = response.split("\n")
       for i in range(9, len(response)):
           print(response[i])

   else:
       print(response)
   listener.close()


# argument parsing for use in the command line
parser = argparse.ArgumentParser()
get_verbose_post = parser.add_mutually_exclusive_group()
get_verbose_post.add_argument('-g', '--get', help= 'get with URL argument', type=str)
get_verbose_post.add_argument('-p', '--post', help= 'post with URL argument', type=str)
parser.add_argument('--h', '--header', help='header for HTTP post', type=str)
dataVsFile = parser.add_mutually_exclusive_group()
dataVsFile.add_argument('-d', '--data', help='data string for HTTP post', type=str)
dataVsFile.add_argument('-f', '--file', help='file for HTTP post', type=str)
verbose = parser.add_argument('-v', '--verbose', help='show verbose output',
       action='store_true')

args = parser.parse_args()
if args.get is not None:
   get(args.get, args.verbose)
elif args.post is not None and args.h is not None:
   if args.data is not None:
       post(args.post, args.h, args.data, args.verbose)
   elif args.file is not None:
       f = open(args.file, 'r')
       data = f.read()
       f.close()
       post(args.post, args.header, data, args.verbose)
   else:
       print("error: expected either a data string (-d) or file (-f) for post request.")
       parser.print_help()
elif args.post is not None and args.header is None:
   print("error: expected a header (--header) for post request.")
   parser.print_help()
else:
   parser.print_help()