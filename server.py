import socket
import threading



server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_add = ('localhost', 8080)

socket_table = {}
flag = False
curr_user = ""
#Bind server socket with port 
server.bind(server_add)

def send_msg(recipient_username, sender_username, client_send, Length, message):
    global socket_table
    forward_client = socket_table[recipient_username]
    forward_msg = "FORWARD " + sender_username + "\nContent-length: " +  str(Length) + "\n\n" + message
    total_length = len(forward_msg)
    if(total_length > 2048):
        parts = total_length//2048
        for i in range(parts):
            temp_msg = forward_msg[i:(i+1)*parts]
            forward_client.sendall(temp_msg.encode("utf-8"))
    else:
        forward_client.sendall(forward_msg.encode("utf-8"))
        #print("line27")
    while True:
        received_msg = forward_client.recv(1024)
        received_msg = received_msg.decode("utf-8") 
        if received_msg:
            #print("line32")
            #print(received_msg)
            if(received_msg == "RECEIVED " + sender_username + "\n \n"):
                akn_msg = "SENT " + recipient_username  + "\n \n"
                #print("line36")
                # print(akn_msg)
                client_send.sendall(akn_msg.encode("utf-8"))
            elif(received_msg == "ERROR 103 Header Incomplete\n \n"):
                akn_msg = "ERROR 102 Unable to send\n \n"
                client_send.sendall(akn_msg.encode("utf-8"))
            break
    #print("line41")


def TORECV(client_recv):
    global flag
    global socket_table
    while True:
        msg = client_recv.recv(1024)
        msg = msg.decode("utf-8") 
        if msg:
            msg = msg.split()
            if(len(msg) != 3):
                data = "ERROR 101 No user registered \n \n"
                client_recv.sendall(data.encode("utf-8"))
                client_recv.close()
                return False
            if(msg[0] + " " + msg[1] != "REGISTER TORECV"):
                data = "ERROR 101 No user registered \n \n"
                client_recv.sendall(data.encode("utf-8"))
                client_recv.close()
                return False
            username = msg[2]
            for i in username:
                if(not i.isdigit() and not i.isalpha()):
                    data = "ERROR 100 Malformed username\n \n"
                    client_recv.sendall(data.encode("utf-8"))
                    client_recv.close()
                    return False
            curr_user = username
            socket_table[username] = client_recv
            data = "REGISTERED TORECV " + username + "\n \n"
            client_recv.sendall(data.encode("utf-8"))
            flag = True
            return True

def removeRecv(username):
    global socket_table
    client_recv = socket_table[username]
    del socket_table[username]
    client_recv.close()
    print(username + " disconnected")

def TOSEND(client_send):
    global flag
    global socket_table
    msg = client_send.recv(1024)
    msg = msg.decode("utf-8") 
    while True:
        if msg:
            msg = msg.split()
            if(len(msg) != 3):
                data = "ERROR 101 No user registered \n \n"
                client_send.sendall(data.encode("utf-8"))
                client_send.close()
                return False
            if(msg[0] + " " + msg[1] != "REGISTER TOSEND"):
                data = "ERROR 101 No user registered \n \n"
                client_send.sendall(data.encode("utf-8"))
                client_send.close()
                return False
            username = msg[2]
            data = "REGISTERED TOSEND " + username + "\n \n"
            client_send.sendall(data.encode("utf-8"))
            print(username + " connected to the server")
            flag = True
            while True:
                msg = client_send.recv(2048)
                msg = msg.decode("utf-8") 
                if msg:
                    #print("line 104")
                    #print(msg)
                    msg = msg.split("\n")
                    if(len(msg) < 2):
                        data = "ERROR 103 Header incomplete\n \n"
                        client_send.sendall(data.encode("utf-8"))
                        client_send.close()
                        removeRecv(username)
                        return False
                    header1 = msg[0]
                    header1_part = header1.split()
                    recipient_username = ""
                    if(header1_part[0] == "SEND"):
                        recipient_username = header1_part[1]
                        #print("line118")
                        #print(recipient_username)
                    else:
                        data = "ERROR 103 Header incomplete\n \n"
                        client_send.sendall(data.encode("utf-8"))
                        client_send.close()
                        removeRecv(username)
                        return False
                    header2 = msg[1]
                    header2_part = header2.split()
                    Length = 0
                    if(header2_part[0] == "Content-length:"):
                        if(len(header2_part) == 2):
                            Length = int(header2_part[1])
                            #print("line132")
                            #print(Length)
                        else:
                            data = "ERROR 103 Header incomplete\n \n"
                            client_send.sendall(data.encode("utf-8"))
                            client_send.close()
                            removeRecv(username)
                            return False
                    else:
                        data = "ERROR 103 Header incomplete\n \n"
                        client_send.sendall(data.encode("utf-8"))
                        client_send.close()
                        removeRecv(username)
                        return False
                    message = msg[3]
                    #print("line148")
                    #print(message)
                    while(len(message) < Length):
                        new_msg = client_send.recv(2048)
                        new_msg = new_msg.decode("utf-8") 
                        if(new_msg):
                            message += new_msg
                        else:
                            break
                    if(len(message) != Length):
                        data = "ERROR 103 Header incomplete\n \n"
                        client_send.sendall(data.encode("utf-8"))
                        client_send.close()
                        removeRecv(username)
                        return False

                    if(recipient_username in socket_table):
                        #print("line 156")
                        send_msg(recipient_username, username, client_send, Length, message)
                    elif(recipient_username == "ALL"):
                        for key in socket_table:
                            if(key != username):
                                send_msg(key, username, client_send, Length, message)
                    else:
                        data = "ERROR 102 Unable to send\n \n"
                        client_send.sendall(data.encode("utf-8"))

                

    



# listening for connection 
if __name__ == '__main__':
    server.listen(1)
    #print("ok")
    while True:
        #print("line159")
        client_recv, recv_add = server.accept()
        #print("line161")
        thread1 = threading.Thread(target = TORECV, args = (client_recv,))
        flag = False
        thread1.start()
        thread1.join()

        if(flag):
            flag = False
            #print("Here")
            client_send, send_add = server.accept()
            #print("line171")
            thread2 = threading.Thread(target = TOSEND, args = (client_send,))
            thread2.start()
            # if(not flag):
            #     print("line177")
            #     thread2.join()
        
        

    

    
    