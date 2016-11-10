Jerrybuild is a lightweight project build and Continuous Integration server
written in Python. Basically, it's a web server that listens for webhook
notifications and then runs scripts.

Jerrybuild is Open Source and release under the [GPL
v3](https://www.gnu.org/licenses/gpl-3.0.en.html). Jerrybuild can be found on
[github](https://github.com/fboender/jerrybuild).


# Philosophy

The design goals of Jerrybuild are: to be lightweight both in on-disk size,
features and memory usage. You can run Jerrybuild on cheap hardware such as
the Raspberry Pi or on a cheap online VPS.

Jerrybuild follows the unix philosophy of "do one thing, and do it well".  The
thing Jerrybuild does (and hopefully, well) is listening for incoming webhooks
and setting up a proper environment for calling a build script. It offers
tools to simplify your build scripts.

# Features

* Easy to set up and configure via a simple configuration file.
* Consumes only 17 Mb of memory.
* Support for generic webhooks, Github and Gogs.
* Written in Python (v2.7+, v3+) with zero other dependencies.
* Utilizes scripts to do the building. Any programming language can be used to
  create build scripts.
* Pass custom environment variables to the scripts based on globally or
  job-specificly configured environment settings.
* Send email on job build failures and recovery.
* Web interface front-end.
* Shield support (http://shields.io/).

Since Jerrybuild is supposed to be lightweight, it doesn't implement some
features found in other CI servers:

* Jerrybuild does not control your version control system for you. Updating
  clones and checking out the correct branches should be handled in your build
  script. The Github, Gogs and other providers will pass environment values to
  your script containing information on which repo/commit to build. #FIXME:
  Examples.
* The job build queue can currently only build one job at a time.
* Jerrybuild cannot be configured via the web interface, only via the configuration file. 
* Jerrybuild doesn't try to do things other programs are better at. As such:
    - There is no scheduling mechanism. You can use Cron to do scheduled builds.
    - The web interface has no authentication. If you require authentication,
      you should put Apache or Nginx in front of it. See the Cookbook for a
      How-to.
    - Doesn't support SSL. Put Apache or Nginx in front of it. See the Cookbook for a How-to.

