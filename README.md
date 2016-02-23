# Doodle ![Travis CI test result](https://travis-ci.org/keakon/Doodle.svg?branch=master)
A blog system based on Python 2.7 and Redis. It's a *nix port from Google App Engine of [Doodle 1.x](https://bitbucket.org/keakon/doodle/).

## Progress
It's under heavy development currently.  
Don't use it in production environment right now since it might be changed frequently.

## Installation
Doodle requires Python 2.7 and Redis. It has been tested in OS X 10.8 ~ 10.11 and Ubuntu 15.10.

1. Clone or download code:
  ```bash
  $ git clone https://github.com/keakon/Doodle.git
  ```
  
2. Put your own config files under the **private** directory. (optional)
  ```bash
  $ cd doodle
  $ mkdir private
  ```

3. Run buildout:
  ```bash
  $ scripts/buildout.sh
  ```
  Use Google to figure out any problem occurs.

## Usage
```bash
$ redis-server &
$ bin/web
```
Then you can open [http://0.0.0.0:8080](http://0.0.0.0:8080) to check it.
