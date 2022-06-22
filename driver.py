import server
import client
import threading
import logging

def test_case_no_conflict(client1, dummy_client):
    print("----Test-Case-1----")
    client1.establishConnection(0)
    threading.Event().wait(1)
    print("Established Connection with Server 0")
    dummy_client.establishConnection(1)
    threading.Event().wait(1)
    print("Made Server 1 BUSY")
    client1.updateDataRequest("test_key", "test_value")
    print("Sent Update Request-1")
    data = client1.receiveData()
    client1.closeConnection()

    client1.establishConnection(2)
    threading.Event().wait(1)
    client1.updateDataRequest("test_key2", "test_value2")
    print("Sent Update Request-2")
    data = client1.receiveData()
    client1.closeConnection()
    dummy_client.closeConnection()

    print("Making Server-1 Go Up Again")
    client1.establishConnection(1)
    threading.Event().wait(1)
    print("Established Connection with Server 1")
    client1.readDataRequest("test_key2")
    print("Sent Read Request")
    data = client1.receiveData()
    client1.closeConnection()
    expectedData = [('test_value2', [1, 0, 1, 0, 0])]
    try:
        assert data == expectedData
        print("--%%%-TEST-CASE-1-PASSED-%%%--")
    except:
        print("--%%--TEST-CASE FAILED--%%--")


def test_case_conflict(client1, dummy_client1, dummy_client2, dummy_client3, dummy_client4):
    print("----Test-Case-2----")
    client1.establishConnection(0)
    threading.Event().wait(1)
    print("Established Connection with Server 0")
    dummy_client1.establishConnection(1)
    threading.Event().wait(1)
    print("Made Server 1 Busy")
    client1.updateDataRequest("test_key4", "test_value4")
    print("Sent Update Request-1")
    data = client1.receiveData()
    client1.closeConnection()
    dummy_client1.closeConnection()

    print("Made Server 0,2,3,4 Busy")
    dummy_client1.establishConnection(0), dummy_client2.establishConnection(2)
    dummy_client3.establishConnection(3), dummy_client4.establishConnection(4)
    client1.establishConnection(1)
    threading.Event().wait(1)
    print("Established Connection with Server 1")
    client1.updateDataRequest("test_key4", "test_value5")
    print("Sent Update Request-2")
    data = client1.receiveData()
    client1.closeConnection()

    dummy_client1.closeConnection(), dummy_client2.closeConnection()
    dummy_client3.closeConnection(), dummy_client4.closeConnection()
    print("Making Server 0,2,3,4 Go Up Again")
    client1.establishConnection(4)
    threading.Event().wait(1)
    print("Established Connection with Server 4")
    client1.readDataRequest("test_key4")
    print("Sent Update Request-5")
    data = client1.receiveData()
    client1.closeConnection()
    expectedData = [('test_value5', [1, 1, 1, 0, 0]), ('test_value4', [2, 0, 1, 0, 0])]
    try:
        assert data == expectedData
        print("--%%%-TEST-CASE-2-PASSED-%%%--")
    except:
        print("--%%--TEST-CASE FAILED--%%--")

if __name__ == '__main__':
    logging.basicConfig(filename='server_test.log', level=logging.INFO)
    logging.info("\n\nNEW SESSION")
    hosts, ports = ["localhost", "localhost", "localhost", "localhost", "localhost"], [9920, 9950, 9990, 9980, 9999]
    # Spawn 5 servers
    server1 = server.Server(hosts, ports, 0, 5)
    server2 = server.Server(hosts, ports, 1, 5)
    server3 = server.Server(hosts, ports, 2, 5)
    server4 = server.Server(hosts, ports, 3, 5)
    server5 = server.Server(hosts, ports, 4, 5)
    threading.Thread(target=server1.startListening, args=[], daemon=True).start()
    threading.Thread(target=server2.startListening, args=[], daemon=True).start()
    threading.Thread(target=server3.startListening, args=[], daemon=True).start()
    threading.Thread(target=server4.startListening, args=[], daemon=True).start()
    threading.Thread(target=server5.startListening, args=[], daemon=True).start()

    client1 = client.Client(hosts, ports)
    dummy_client = client.Client(hosts, ports)
    dummy_client1 = client.Client(hosts, ports)
    dummy_client2 = client.Client(hosts, ports)
    dummy_client3 = client.Client(hosts, ports)
    dummy_client4 = client.Client(hosts, ports)
    test_case_no_conflict(client1, dummy_client)
    print()
    test_case_conflict(client1, dummy_client1, dummy_client2, dummy_client3, dummy_client4)
