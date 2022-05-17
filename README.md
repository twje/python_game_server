## Description
This project is a game server framework that media applications can use to propogate state across multiple clients.

## Features
- Handle multiple client connections in a single thread using the select system call
- Handlers can subscribe to messages recieved by clients
- Network implementation detail is abstracted

## Todo
- Support to send messages to clients
- Error handling and logging
- Implement client

## Run Application

Start Server
```
>> python server.py
```

Start Client
```
>> python client.py
```

Expected server output:
```
Listening on ('127.0.0.1', <server_port>)
Accepted connection from ('127.0.0.1', <client_port>)
{'A': 1, 'B': 2}
Closing connection to ('127.0.0.1', <client_port>)
```