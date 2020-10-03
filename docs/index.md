Jerrybuild is a lightweight project build and Continuous Integration server
written in Python. Basically, it's a web server that listens for webhook
notifications and then runs scripts.

Jerrybuild is Open Source and released under the [GPL
v3](https://www.gnu.org/licenses/gpl-3.0.en.html). It can be found on
[github](https://github.com/fboender/jerrybuild).


# Philosophy

The design goals are to be light on disk space, features and memory usage. You
can easily run it on cheap hardware such as the Raspberry Pi or on a cheap
online VPS.

Jerrybuild follows the unix philosophy of "do one thing, and do it well".  The
thing Jerrybuild does (and hopefully, well) is listening for incoming webhooks
and setting up a proper environment for calling a build script.

# Features

* Easy to set up and configure via a simple configuration file
* Low in resident memory usage (17 to 30 Mb)
* Support for generic webhooks, Github and Gogs
* Written in Python (v3+) with zero other dependencies. A stand-alone x86-64
  binary is available, which doesn't require Python at all.
* Utilizes scripts to do the building. Any programming language can be used to
  create build scripts.
* Pass custom environment variables to the scripts based on globally
  or job specific configured environment settings.
* Send email on job build failures and recovery.
* Web interface front end.
* Shield support (http://shields.io/)

Since Jerrybuild is supposed to be lightweight, it doesn't implement some
features found in other CI servers:

* Jerrybuild does not control your version control system for you. Updating
  clones and checking out the correct branches should be handled in your build
  script.
* The job build queue can currently only build one job at a time.
* Jerrybuild cannot be configured via the web interface, only via the
  configuration file. 
* There are no agents or remote building. You can use ssh for that.
* There is no scheduling mechanism. You can use Cron to do scheduled builds.
* The built-in web interface doesn't support SSL and has no authentication. If
  you require those, you should put Apache or Nginx in front of it. See the
  [Cookbook](cookbook) for a How-to.
