jerrybuild
==========

![Status: Unstable](https://img.shields.io/badge/status-unstable-red.svg)
![Build Status](http://build.electricmonk.nl/job/jerrybuild/shield)
![Activity: Active development](https://img.shields.io/badge/activity-active%20development-green.svg)
![License: GPLv3](https://img.shields.io/badge/license-GPLv3-blue.svg)

## About

Jerrybuild is a lightweight project build and Continuous Integration server
written in Python. Basically, it's a web server that listens for webhook
notifications and then runs scripts.

Features:

* Easy to set up and configure via a simple configuration file
* Low in resident memory usage (17 to 30 Mb)
* Support for generic webhooks, Github and Gogs
* Written in Python (v3+) with zero other dependencies. A stand-alone binary
  is available, which doesn't require Python at all.
* Utilizes scripts to do the building. Any programming language can be used to
  create build scripts.
* Pass custom environment variables to the scripts based on globally
  or job-specificly configured environment settings.
* Send email on job build failures and recovery.
* Web interface front-end.
* Shield support (http://shields.io/)

Since Jerrybuild is supposed to be lightweight, it doesn't implement some
features found in other CI servers:

* Jerrybuild does not control your version control system for you. Updating
  clones and checking out the correct branches should be handled in your build
  script. The Github, Gogs and other providers will pass environment values to
  your script containing information on which repo/commit to build. #FIXME:
  Examples.
* The job build queue can currently only build one job at a time. 
* Jerrybuild cannot be configured via the web interface, only via the
  configuration file.
* Jerrybuild doesn't try to do things other programs are better at. As such:
  - There is no scheduling mechanism. You can use Cron to do scheduled builds.
  - The web interface has no authentication. If you require authentication,
    you should put Apache or Nginx in front of it. See the Cookbook for a
    How-to.
  - Doesn't support SSL. Put Apache or Nginx in front of it. See the Cookbook
    for a How-to.

## Documentation

See the [Documentation](https://jerrybuild.readthedocs.io/en/latest/) for
installation, configuration and usage instructions.

## License

Jerrybuild is released under the [General Public License v3](LICENSE).
