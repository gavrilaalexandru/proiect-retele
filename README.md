# News Channel Subscription and Notification System

## Project Description

This project represents a distributed client-server application developed for the Computer Networks course.

The application allows multiple clients to connect to a central server and manage news channels in real time.

Clients can:

- view available channels
- create their own channels
- delete channels they own
- subscribe/unsubscribe to channels
- publish news on owned channels

The server distributes accepted news to all subscribed clients and filters messages containing banned words.

---

## Technologies Used

- Python 3.11
- TCP Socket Programming
- Multithreading
- JSON Application Protocol
- Docker / Docker Compose

---

## Project Structure

- `news-channel-subscription-system/`
  - `server/`
    - `server.py`
    - `requirements.txt`
    - `Dockerfile`
  - `client/`
    - `client.py`
  - `docker-compose.yml`
  - `README.md`

---

## Running the Server with Docker

From the project root folder run:

docker compose up --build

The server will start on port:

5000

---

## Running the Clients

Open one or more terminals and run:

python client/client.py

Each client must choose a unique username.

---

## Supported Operations

The system supports the following client requests:

- connect
- list_channels
- create_channel
- delete_channel
- subscribe
- unsubscribe
- publish_news

The server also sends asynchronous notifications:

- channel_created_notification
- channel_deleted_notification
- news_notification

---

## Server Side Stored Data

The server maintains in memory:

- registered channels (name, description, owner)
- subscriptions for each channel
- connected clients
- banned words list

---

## Content Filtering

The server blocks any published news containing banned words.

Current banned words:

- bomb
- drugs
- violence
- terror

Blocked news are not delivered to subscribers.

---

## Concurrency Model

The server is concurrent and creates a dedicated thread for every connected client.

Shared resources are protected using threading.Lock() in order to avoid race conditions.

---

## Disconnect Handling

When a client disconnects:

- the client is removed from all subscriptions
- the TCP socket is closed safely
- the server continues running without interruption

---

## Demonstration Video

Video link:

PASTE_VIDEO_LINK_HERE
