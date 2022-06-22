<!-- ABOUT THE PROJECT -->

## About The Project

This application is a replicated key-value data store maintained by N servers. Each server maintains a copy of the data store, a vector clock for each entry in the data store and expose two functions.

- Read(key): reads the value associated with the key and the vector clock value. If there is a conflict, it returns all conflicted values and their corresponding value.
- Add_Update(key, value): add/update the value associated with the key and return the vector clock value to the client.

#### Testing

Includes a driver test program that will spawns the servers and client to test the following scenarios.

- Deploys 5 servers. A server can become offline anytime. If a server is offline, the server will have outdated values when a client makes an add/update request to other servers. Simulate
  the scenario when (a) there is no conflict and (b) there is conflict.
- When there is no conflict, the sever value should merge the key values and local clock based on the clock values (local versus remote). This can be done by the client sending an update request twice --- when the server is down, and the failed server is back up.
- When there is a conflict, the server should store conflicted values and return these to the client.

<p align="right">(<a href="#top">back to top</a>)</p>

### Built With

- [Python](https://www.python.org/)
- [Socket](https://docs.python.org/3/library/socket.html)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Getting Started

These are the instructions on setting up your project locally.

### Prerequisites

Following are the prerequisites for running the project:

- Python

### Installation

_For running the project please follow the following commands._

1. Clone the repo
   ```sh
   git clone https://github.com/karandeepParashar/GroupChat-VectorClocks.git
   ```
2. Enter the project directory.
   ```sh
   cd GroupChat-VectorClocks
   ```
3. run the server

   ```js
   python .\client.py --hosts "localhost" "localhost" "localhost" --ports 9990 9980 9999
   ```

4. Open seperate terminal for each client and run

   ```js
   python .\server.py --hosts "localhost" "localhost" "localhost" --ports 9990 9980 9999
   ```

5. Run the driver test cases
   ```js
   python .\driver.py
   ```

<p align="right">(<a href="#top">back to top</a>)</p>
