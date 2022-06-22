#python .\client.py --hosts "localhost" "localhost" "localhost" --ports 9990 9980 9999
import socket
import pickle
import argparse
import logging
import time

class Client:
    def __init__(self, hosts, ports):
        self.hosts = hosts
        self.ports = ports

    def inputRequest(self):
        print("Please describe your request details as follow:")
        flag = True
        while flag:
            try:
                n = int(input("Which server to send the request?\n"))
                self.establishConnection(n)
                logging.info("User decides to send request to server "+str(n))
                requestType = input("1 for \"read\" or 2 for \"updateAdd\" \n")
                start = 0
                if requestType == '1':
                    logging.info("Read requested from servers")
                    key = input("Please Enter the key \n")
                    start = time.time()
                    self.readDataRequest(key)
                elif requestType == '2':
                    logging.info("Update requested from servers")
                    key = input("Please enter the key: \n")
                    value = input("Please enter the value: \n")
                    start = time.time()
                    self.updateDataRequest(key, value)
                else:
                    continue
                self.receiveData()
                end = time.time()
                print("Time Elapsed: " + str(end - start))
                logging.info("Time Elapsed: " + str(end - start))
                self.closeConnection()
                logging.info("Connection closed with "+str(n)+" server")
                flag = input("Do you want to continue? y or n \n")
                if flag == "n":
                    flag = False
            except:
                self.closeConnection()
                logging.info("Error Occured in client side request handling")
                print("Restarting request sending mechanism. Error occured during execution")

    def readDataRequest(self, key):
        request = pickle.dumps(key)
        self.client.send(request)

    def updateDataRequest(self, key, value):
        request = pickle.dumps((key, value))
        self.client.send(request)

    def establishConnection(self, i):
        self.client = socket.socket()
        self.client.connect((self.hosts[i], self.ports[i]))
        self.client.send(pickle.dumps("Client"))

    def receiveData(self):
        data = pickle.loads(self.client.recv(1024 * 100))
        if len(data) == 1:
            print("Data Received: \n", data)
        else:
            print("Data received with conflict:\n", data)
        logging.info("Data is received:")
        logging.info(data)
        return data

    def closeConnection(self):
        self.client.close()


if __name__ == '__main__':
    logging.basicConfig(filename='client_logs.log', level=logging.INFO)
    logging.info("\n\nNEW SESSION")
    parser = argparse.ArgumentParser(description="Replicated Database Vector Clock by Karandeep Parashar")
    parser.add_argument('--hosts', nargs="+", help='Hosts', default=["localhost", "localhost", "localhost"])
    parser.add_argument('--ports', nargs="+", help="Ports", default=[9990, 9980, 9999])
    args = parser.parse_args()
    hosts, ports = args.hosts, args.ports
    ports = [int(element) for element in ports]
    logging.info("Received Hosts and Ports:")
    logging.info((hosts, ports))
    client = Client(hosts, ports)
    client.inputRequest()
