#python .\server.py --hosts "localhost" "localhost" "localhost" --ports 9990 9980 9999
import socket
import pickle
import logging
import threading
import argparse

class Server:
    def __init__(self, hosts, ports, i, n):
        self.hosts, self.ports = hosts, ports
        self.index = i
        self.vectorClock = [0] * n
        self.data = {}
        self.socket = self.initiateServer(hosts[i], ports[i], n)

    def initiateServer(self, host, port, n):
        logMsg = "[" + str(self.index) + "]" + "[1]" + "::Initiating Server"
        logging.info(logMsg)
        print("Welcome to the Server: ", self.index)
        sock = socket.socket()
        print("Socket created")
        sock.bind((host, port))
        sock.listen(n)
        logMsg = "[" + str(self.index) + "]" + "[2]" + "::Socket created"
        logging.info(logMsg)
        return sock

    def acceptConnections(self):
        logMsg = "[" + str(self.index) + "]" + "[3]" + "::Waiting for connections"
        logging.info(logMsg)
        conn, address = self.socket.accept()
        connType = pickle.loads(conn.recv(1024 * 1000))
        connType = connType.split("-")
        connType, index = connType[0], connType[1] if len(connType) == 2 else None
        index = int(index) if index else None
        logMsg = "[" + str(self.index) + "]" + "[4]" + "::Connected with " + str(address) + "-" + str(connType)
        logging.info(logMsg)
        if connType == "Client":
            logMsg = "[" + str(self.index) + "]" + "[5]" + "::Entered Client message deciphering mechanism"
            logging.info(logMsg)
            request = conn.recv(1024 * 1000)
            reply = self.requestHandler(request)
        else:
            logMsg = "[" + str(self.index) + "]" + "[5]" + "::Entered Server message deciphering mechanism"
            logging.info(logMsg)
            data = pickle.loads(conn.recv(1024 * 100))
            logging.info(data)
            if type(data) == tuple:
                logMsg = "[" + str(self.index) + "]" + "[5.1]" + "::Received Add/Update Request"
                logging.info(logMsg)
                request, receiveClock = data
                self.data[request[0]] = request[1]
                self.vectorClock[index] += 1
                reply = pickle.dumps((self.data, self.vectorClock))
            else:
                logMsg = "[" + str(self.index) + "]" + "[5.1]" + "::Received Read Request"
                logging.info(logMsg)
                reply = pickle.dumps((self.data, self.vectorClock))
        conn.send(reply)
        conn.close()
        logMsg = "[" + str(self.index) + "]" + "[17]" + "::Closing current connection"
        logging.info(logMsg)

    def startListening(self):
        flag = True
        while flag:
            try:
                self.acceptConnections()
            except:
                logMsg = "[" + str(self.index) + "]" + "[6]" + "::Error Occurred in Execution, moving ahead"
                logging.info(logMsg)

    def requestHandler(self, request):
        request = pickle.loads(request)
        if type(request) == tuple:
            logMsg = "[" + str(self.index) + "]" + "[6]" + "::Add/Update request received"
            logging.info(logMsg)
            reply = self.updateHandler(request)
        elif type(request) == str:
            logMsg = "[" + str(self.index) + "]" + "[6]" + "::Read request received"
            logging.info(logMsg)
            reply = self.readHandler(request)
        return reply

    def synchronizeServers(self, request ,requestType):
        logMsg = "[" + str(self.index) + "]" + "[8]" + "::Synchronizing with other servers"
        logging.info(logMsg)
        replyData = []
        for i in range(len(self.vectorClock)):
            if i == self.index:
                continue
            try:
                logMsg = "[" + str(self.index) + "]" + "[9]" + "::Attempting connection with other server-" + str(i)
                logging.info(logMsg)
                client = socket.socket()
                client.settimeout(0.05)
                client.connect((self.hosts[i], self.ports[i]))
                logMsg = "[" + str(self.index) + "]" + "[10]" + "::Connection Established"
                logging.info(logMsg)
                msg = "Server-" + str(self.index)
                client.send(pickle.dumps(msg))
                logMsg = "[" + str(self.index) + "]" + "[11]" + "::Sent msg introducing myself as a fellow server"
                logging.info(logMsg)
                if requestType == "updateAdd":
                    client.send(pickle.dumps((request, self.vectorClock)))
                else:
                    client.send(pickle.dumps(self.vectorClock))
                logMsg = "[" + str(self.index) + "]" + "[12]" + "::Sent the local data and clock"
                logging.info(logMsg)
                data = pickle.loads(client.recv(1024 * 100))
                receiveData, receiveClock = data
                logMsg = "[" + str(self.index) + "]" + "[13]" + "::Received data and clock"
                logging.info(logMsg)
                flag1, flag2 = True, True
                for j in range(len(self.vectorClock)):
                    if receiveClock[j] < self.vectorClock[j]:
                        flag1 = False
                    if receiveClock[j] > self.vectorClock[j]:
                        flag2 = False
                conflict = not flag1 and not flag2
                logMsg = "[" + str(self.index) + "]" + "[14]" + "::Conflict/No-Conflict Detection Completed"
                logging.info(logMsg)
                if conflict:
                    logMsg = "[" + str(self.index) + "]" + "[15]" + "::CONFLICT DETECTED with server-"+str(i)
                    logging.info(logMsg)
                    logging.info((self.data, self.vectorClock))
                    logging.info((receiveData, receiveClock))
                    if requestType == "updateAdd":
                        replyData.append((receiveData, receiveClock))
                    else:
                        replyData.append((receiveData[request], receiveClock))
                else:
                    logMsg = "[" + str(self.index) + "]" + "[15]" + "::No conflict"
                    logging.info(logMsg)
                    self.vectorClock = [max(receiveClock[j], self.vectorClock[j]) for j in range(len(receiveClock))]
                    if flag1:
                        self.data = receiveData
            except:
                logMsg = "[" + str(self.index) + "]" + "[Unknown]" + "::Synchronization Failed"
                logging.info(logMsg)
        logMsg = "[" + str(self.index) + "]" + "[16]" + "::Synchronization Attempt Completed"
        logging.info(logMsg)
        if requestType == "updateAdd":
            replyData.append((self.data, self.vectorClock))
        else:
            replyData.append((self.data[request], self.vectorClock))
        return replyData

    def updateHandler(self, request):
        logMsg = "[" + str(self.index) + "]" + "[7]" + "::Updating Local Data for Add/Update Request"
        logging.info(logMsg)
        self.data[request[0]] = request[1]
        self.vectorClock[self.index] += 1
        replyData = self.synchronizeServers(request, "updateAdd")
        reply = pickle.dumps(replyData)
        return reply

    def readHandler(self, request):
        logMsg = "[" + str(self.index) + "]" + "[7]" + "::Handling Read Request"
        logging.info(logMsg)
        replyData = self.synchronizeServers(request, "read")
        reply = pickle.dumps(replyData)
        return reply


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Replicated Database Vector Clock by Karandeep Parashar")
    parser.add_argument('--hosts', nargs="+", help='Hosts', default=["localhost", "localhost", "localhost"])
    parser.add_argument('--ports', nargs="+", help="Ports", default=[9990, 9980, 9999])
    args = parser.parse_args()
    logging.basicConfig(filename='server_logs.log', level=logging.INFO)
    logging.info("\n\nNEW SESSION")
    hosts, ports = args.hosts, args.ports
    ports = [int(element) for element in ports]
    n = len(hosts)
    for i in range(1, n):
        server = Server(hosts, ports, i, n)
        serverThread = threading.Thread(target=server.startListening, args=[], daemon=True)
        serverThread.start()
    server = Server(hosts, ports, 0, n)
    server.startListening()
