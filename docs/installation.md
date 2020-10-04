# Running directly from repo

You can run Jerrybuild directly from a git clone of the repository:

    $ git clone git@github.com:fboender/jerrybuild.git
    $ cd jerrybuild/
    $ python3 ./jerrybuild.py example/jerrybuild.cfg

This is mostly useful for evaluating Jerrybuild. If you're satisfied that
Jerrybuild suits your needs, you should do a real install.

# System installation

The follow commands install Jerrybuild for production usage.

Create a user:

    sudo adduser --system --group --home /var/lib/jerrybuild --disabled-password --disabled-login jerrybuild

Create the required directory structure:

    sudo mkdir -p /etc/jerrybuild/jobs.d /var/lib/jerrybuild/status/jobs/_all
    sudo chown -R jerrybuild:jerrybuild /etc/jerrybuild/ /var/lib/jerrybuild/
    sudo chmod 750 /etc/jerrybuild/ /var/lib/jerrybuild/

Now we should install Jerrybuild itself. You've got the choice between using
`pip` to install Jerrybuild, or install it using the standalone binary x86-64.

With pip:

    sudo pip install jerrybuild

With the standalone binary, first download a binary release from the [Releases
Github page](https://github.com/fboender/jerrybuild/releases). Then install
it:
    
    sudo tar -xvf jerrybuild-*-bin64.tar.gz --strip-components=1 -C /usr/local/
    
Next configure Jerrybuild and install the systemd service file so it starts at
boot time:

    sudo cp /usr/local/lib/jerrybuild/jerrybuild.cfg.dist /etc/jerrybuild//jerrybuild.cfg
    sudo cp /usr/local/lib/jerrybuild/jerrybuild.service.dist /etc/systemd/system/jerrybuild.service
    sudo systemctl daemon-reload

You can now start Jerrybuild:

    sudo systemctl start jerrybuild

Check the logs to see if everything starter properly:

    sudo journalctl -u jerrybuild

You can now start creating jobs! Check the
[tutorial](https://jerrybuild.readthedocs.io/en/latest/tutorial) for how to do
that.

It is highly recommended to run Jerrybuild behind a webserver that can provide
SSL and authentication. See the
[Cookbook](https://jerrybuild.readthedocs.io/en/latest/cookbook) for
information on how to do that.
