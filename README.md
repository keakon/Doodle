# Doodle 2
A blog system based on Python 2.7 and Redis. It's a *nix port from Google App Engine of [Doodle 1.x](https://bitbucket.org/keakon/doodle/).

## Installation
Doodle 2 requires Python 2.7 and Redis. It has been tested on Ubuntu 18.04.

1. Clone or download the source code:
  ```bash
  $ git clone https://github.com/keakon/Doodle.git
  ```
2. Install dependencies:
  ```bash
  $ sudo pip install virtualenv
  $ virtualenv .
  $ bin/pip install -r requirements.txt
  ```

## Usage
```bash
$ redis-server &
$ bin/python -m doodle.main
```
Then you can open [http://0.0.0.0:8080](http://0.0.0.0:8080) to check it.

## Run with docker

1. Install Docker
2. Clone or download the source code:
  ```bash
  $ git clone https://github.com/keakon/Doodle.git
  ```
3. Copy config files:
  ```bash
  $ mkdir doodle
  $ cp Doodle/docker-compose.yml doodle/docker-compose.yml
  $ cp -r Doodle/conf doodle/conf
  ```
4. Replace "localhost" into your own domain in conf/Caddyfile.
5. Start docker compose:
  ```bash
  $ cd doodle
  $ docker compose up -d
  ```

## License
Doodle is released under the MIT License. See the [LICENSE](https://raw.githubusercontent.com/keakon/Doodle/master/LICENSE) file for more details.
