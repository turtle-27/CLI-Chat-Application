import socket
import threading

username = input("Username: ")
IP_add = input("IP address: ")

client_recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = (IP_add, 8080)


send_data = "REGISTER TORECV " + username + "\n \n"
client_recv.connect(server_address)
client_recv.sendall(send_data.encode("utf-8"))
isAlive = True

def SEND_MSG():
    global isAlive

    if(isAlive):
        rmsg = input()
        i = -1
        for i in range(len(rmsg)):
            if(rmsg[i] == " "):
                break
        if(i == -1):
            print("Please type again")
            return False
        msg = [rmsg[0:i], rmsg[i+1:]]
        if(msg[0][0] != "@"):
            print("Please type again")
            return False

        recipient_username = msg[0][1:]
       #print(recipient_username)
        Length = 0
        if(len(msg) > 1):
            Length = len(msg[1])
            message = "SEND " + recipient_username + "\nContent-length: " + str(Length) + "\n\n" + msg[1]
            if(Length > 2048):
                parts = Length/2048
                for i in range(parts):
                    temp_msg = message[i:(i+1)*parts]
                    client_send.sendall(temp_msg.encode("utf-8"))
            else:
                #print("line40")
                client_send.sendall(message.encode("utf-8"))
        else:
            message = "SEND " + recipient_username + "\nContent-length: " + str(Length) + "\n\n" 
            client_sendall(message.encode("utf-8"))
    
        while True:
            received_msg = client_send.recv(1024)
            received_msg = received_msg.decode("utf-8") 
            if received_msg:
                #print("line51")
                #print(received_msg)
                if(received_msg == "SENT " + recipient_username  + "\n \n"):
                    #print("Server: " + received_msg)
                    return True
                elif(received_msg == "ERROR 102 Unable to send\n \n"):
                    print("Server: ERROR 102 Unable to send\n \n")
                elif(received_msg == "ERROR 103 Header incomplete\n \n"):
                    print("Server: " +  received_msg)
                    isAlive = False
                    client_send.close()
                    client_recv.close()
                    return False
                break
    return False

def SEND():
    global isAlive
    while(isAlive):
        msg = SEND_MSG()
    return 

def RECV():
    global isAlive
    #print("line73")
    while(isAlive):
        msg = client_recv.recv(2048)
        msg = msg.decode("utf-8") 
        if msg:
            #print("line78")
            #print(msg)
            msg = msg.split("\n")
            if(len(msg) < 2):
                data = "ERROR 103 Header Incomplete\n \n"
                client_recv.sendall(data.encode("utf-8"))
            header1 = msg[0]
            header1_part = header1.split()
            sender_username = ""
            if(header1_part[0] == "FORWARD"):
                sender_username = header1_part[1]
            else:
                data = "ERROR 103 Header Incomplete\n \n"
                client_recv.sendall(data.encode("utf-8"))
                return False
            header2 = msg[1]
            header2_part = header2.split()
            Length = 0
            if(header2_part[0] == "Content-length:"):
                if(len(header2_part) == 2):
                    Length = int(header2_part[1])
                else:
                    data = "ERROR 103 Header incomplete\n \n"
                    client_recv.sendall(data.encode("utf-8"))
                    return False
            else:
                data = "ERROR 103 Header incomplete\n \n"
                client_recv.sendall(data.encode("utf-8"))
                return False
            message = msg[3]
            while(len(message) < Length):
                new_msg = client_send.recv(2048)
                new_msg = new_msg.decode("utf-8") 
                if(new_msg):
                    message += new_msg
                else:
                    break
            print(sender_username + ": " + message)
            client_recv.sendall(("RECEIVED " + sender_username + "\n \n").encode("utf-8"))
            #print("line116")


flag = True

final_msg = ""

while True:
    #print("110")
    msg = client_recv.recv(1024)
    #print("112")
    msg = msg.decode("utf-8") 
    final_msg = msg
    if (msg == "REGISTERED TORECV " + username + "\n \n"):
        #print(msg)
        break
    elif(msg == "ERROR 100 Malformed username\n \n"):
        print("Server: " + msg)
        flag = False
        client_send.close()
        client_recv.close()
        break
    elif(msg == "ERROR 101 No user registered \n \n"):
        print("Server: " + msg)
        flag  = False
        client_send.close()
        client_recv.close()
        break
if(flag):
    send_data = "REGISTER TOSEND " + username + "\n \n"
    #print("line130")
    client_send.connect(server_address)
    #print("line132")
    client_send.sendall(send_data.encode("utf-8"))
while flag:
    msg = client_send.recv(1024)
    msg = msg.decode("utf-8")
    #print("line138")
    if (msg == "REGISTERED TOSEND " + username + "\n \n"):
        final_msg = msg + final_msg
        print(final_msg)
        break
    elif(msg == "ERROR 100 Malformed username\n \n"):
        print("Server: " + msg)
        flag = False
        client_recv.close()
        client_send.close()
        break
    elif(msg == "ERROR 101 No user registered \n \n"):
        print("Server: " + msg)
        flag = False
        client_recv.close()
        client_send.close()
        break

if(flag):
    #Sender
    thread1 = threading.Thread(target=SEND)
    thread2 = threading.Thread(target=RECV)
    thread1.start()
    thread2.start()
