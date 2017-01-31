:version: 1.3.2
:copyright: 2015 `REANNZ <http://www.reannz.co.nz/>`_.  All Rights Reserved.

.. meta::
   :keywords: OpenFlow, Ryu, Faucet, VLAN, SDN

======
Faucet
======

Faucet is an OpenFlow controller for a layer 2 switch based on Waikato University's `Valve <https://github.com/wandsdn/valve>`_. It handles MAC learning and supports VLANs and ACLs.  It is developed as an application for the `Ryu OpenFlow Controller <http://osrg.github.io/ryu/>`_.

This forked repository is for integration with  `Dot1xForwarder and CapFlow <https://github.com/Bairdo/sdn-authenticator/tree/faucet-integration>`_, as well as the controller in `ACLSwitch <https://github.com/Bairdo/ACLSwitch-1/tree/faucet-integration>`_.

This README is a shortened version of the original, which can be found `here <https://github.com/REANNZ/faucet/blob/master/README.rst>`_
.

=====================
Installation
=====================

Installation automatically installs dependent Python packages [ryu, pyaml, influxdb client] recursively. You may have to install some Python support packages as well.

You have run this as ``root`` or use ``sudo``

.. code:: bash

  apt-get install python-dev # Required for Ubuntu
  pip install ryu-faucet
  pip show -f ryu-faucet


Uninstall
---------
To Uninstall the package

.. code:: bash

  pip uninstall ryu-faucet
  

Installation with CapFlow and ACLSwitch Controller
--------------------------------------------------
The following steps will detail how to use CapFlow and Dot1x with Faucet

Clone the required repositories:
--------------------------------

.. code:: bash

   git clone https://github.com/libunamari/faucet.git
   git clone https://github.com/Bairdo/sdn-authenticator.git 
   git clone https://github.com/Bairdo/ACLSwitch-1.git 

Switch to the appropriate branches
----------------------------------
.. code:: bash

   cd ACLSwitch-1
   git checkout faucet-integration
   cd ../sdn-authenticator
   git checkout faucet-integration
   
Link appropriate folders
-------------------------
.. code:: bash

   cd ../
   ln -s <absolute path to sdn-authenticator> ACLSwitch-1/Ryu_Application/authenticator
   ln -s <absolute path to faucet folder>/src/ryu_faucet/org/onfsdn/faucet ACLSwitch-1/Ryu_Application/faucet

Modify the faucet yaml config file
----------------------------------
Add in the following line to the config file, so that both CapFlow and Dot1xForwarder can install rules on tables 0-1:

.. code:: bash

   table_offset: 2

An example config file is shown below

.. code:: bash

   ---
   version: 2
   vlans:
       100:
           name: vlan100
   dps:
       ovs-switch:
           dp_id: 1
           hardware: Open vSwitch
           table_offset: 2 #start faucet rules from table 2, so able to use tables 0 and 1 for authentication
           interfaces:
               1:
                   name: host1
                   native_vlan: 100
                   acl_in: 100
            
   acls:
       100:
         - rule:
               dl_type: 2048
               actions:
                   allow: 1
         - rule:
               dl_type: 2054
               actions:
                   allow: 1

Install the dependencies
------------------------
.. code:: bash

   pip install ruamel.yaml
   

=======
Running
=======

Note: On your system, depending on how Python is installed, you may have to install some additional packages to run faucet.

Run with ``ryu-manager`` (uses ``/etc/ryu/faucet/faucet.yaml`` as configuration by default):

.. code:: bash

    # export FAUCET_CONFIG=/etc/ryu/faucet/faucet.yaml
    # export GAUGE_CONFIG=/etc/ryu/faucet/gauge.yaml
    # export FAUCET_LOG=/var/log/faucet/faucet.log
    # export FAUCET_EXCEPTION_LOG=/var/log/faucet/faucet_exception.log
    # export GAUGE_LOG=/var/log/faucet/gauge_exception.log
    # export GAUGE_EXCEPTION_LOG=/var/log/faucet/gauge_exception.log
    # export GAUGE_DB_CONFIG=/etc/ryu/faucet/gauge_db.yaml
    # $EDITOR /etc/ryu/faucet/faucet.yaml
    # ryu-manager --verbose faucet.py

To run, the controller in ACLSwitch must be called:

.. code:: bash

    # ryu-manager --verbose <Location_Path>/ACLSwitch-1/Ryu_Application/controller.py

Alternatively, if OF Controller is using a non-default port of 6633, for example 6653, then:

.. code:: bash

   # ryu-manager --verbose  --ofp-tcp-listen-port 6653 <Location_Path>/ACLSwitch-1/Ryu_Application/controller.py

The controller must be run in conjunction with the HTTPServer which is in ACLSwitch-1/Ryu_Application. This can be run by:

.. code:: bash

   # python HTTPServer.py

To specify a different configuration file set the ``FAUCET_CONFIG`` environment variable.

Faucet will log to ``/var/log/faucet/faucet.log`` and ``/var/log/faucet/faucet_exception.log`` by default, this can be changed with the ``FAUCET_LOG`` and ``FAUCET_EXCEPTION_LOG`` environment variables.

Gauge will log to ``/var/log/faucet/gauge.log`` and ``/var/log/faucet/gauge_exception.log`` by default, this can be changed with the ``GAUGE_LOG`` and ``GAUGE_EXCEPTION_LOG`` environment variables.

If running Faucet in ``virtualenv`` and without specifying the environment variables above, the default log and configuration locations will change to reflect the virtual environment's prefix path. For example, the default Faucet log location will be ``<venv prefix>/var/log/faucet/faucet.log``. The Gauge configuration must still be updated in this case by modifying ``<venv prefix>/etc/ryu/faucet/gauge.yaml`` to reflect the location of the configuration file used by Faucet (``<venv prefix>/etc/ryu/faucet/faucet.conf``). When using ``virtualenv``, also create the log directory at its new location, ``<venv prefix>/var/log/ryu/faucet``, rather than the global ``/var/log/ryu/faucet``.

To tell Faucet to reload its configuration file after you've changed it, simply send it a ``SIGHUP``:

.. code:: bash

  pkill -SIGHUP -f "ryu-manager controller.py"

=================
OpenFlow Pipeline
=================
As of Faucet v1.3 release, ACL table is now Table 0 so that actions like port mirroring happen without packet modifications and processing.  VLAN table is now Table 1.

::

    PACKETS IN    +---------------------------+             +-------------------------+ +-------------------------+
      +           |                           |             |                         | |                         |
      |           |                           |             |                         | |        CONTROLLER       |
      |           |                           |             |                         | |            ^            |
      |           |                           v             |                         v |       +----+-----+      v
      |     +-----+----+  +----------+  +-----+----+  +-----+----+  +----------+  +---+-+----+  |6:IPv4_FIB|  +---+------+  +----------+
      |     |0:DOT1X   |  |1:CAPFLOW |  |2:PORT_ACL|  |3:VLAN    |  |4:VLAN_ACL|  |5:ETH_SRC +->+          +->+8:ETH_DST |  |9:FLOOD   |
      +---->+          |  |          |  |          |  |          |  |          |  |          |  |          |  |          |  |          |
            |          |  |          |  |          |  |          |  |          |  |          |  +----------+  |          |  |          |
            |          |  |          |  |          |  |          |  |          |  |          |                |          |  |          |
            |          +->+          +->+          +->+          +->+          +->+          +--------------->+          +->+          |
            |          |  |          |  |          |  |          |  |          |  |          |                |          |  |          |
            |          |  |          |  |          |  |          |  |          |  |          |  +----------+  |          |  |          |
            |          |  |          |  |          |  |          |  |          |  |          |  |7:IPv6_FIB|  |          |  |          |
            |          |  |          |  |          |  |          |  |          |  |          +->+          +->+          |  |          |
            +----+-----+  +----+-----+  +----------+  +----------+  +----------+  +----+-----+  |          |  +------+---+  +--+-------+
                 |             |                                                       |        +----+-----+         |         |
                 v             v                                                       v             v               v         v
              CONTROLLER    CONTROLLER                                             CONTROLLER    CONTROLLER          PACKETS OUT
=======
Testing
=======

Before issuing a Pull Request
-----------------------------
Run the tests to make sure everything works!
Mininet test actually spins up virtual hosts and a switch, and a test FAUCET controller, and checks connectivity between all the hosts given a test config.  If you send a patch, this mininet test must pass.

.. code:: bash

  git clone https://github.com/onfsdn/faucet
  cd faucet/tests
  # (As namespace, etc needs to be setup, run the next command as root)
  sudo ./faucet_mininet_test.py
  ./test_config.py

Working with Real Hardware
--------------------------

If you are a hardware vendor wanting to support FAUCET, you need to support all the matches in src/ryu_faucet/org/onfsdn/faucet/valve.py:valve_in_match().

Faucet has been tested against the following switches:
(Hint: look at src/ryu_faucet/org/onfsdn/faucet/dp.py to add your switch)

1. Open vSwitch v2.1+ - Open Source available at http://www.openvswitch.org
2. Lagopus Openflow Switch - Open Source available at https://lagopus.github.io
3. Allied Telesis x510 and x930 series - https://www.alliedtelesis.com/products/x930-series
4. NoviFlow 1248 - http://noviflow.com/products/noviswitch
5. Northbound Networks - Zodiac FX - http://northboundnetworks.com/collections/zodiac-fx
6. Hewlett Packard Enterprise - Aruba 5400R, 3810 and 2930F - http://www.arubanetworks.com/products/networking/switches/
7. Netronome produces PCIe adaptors, with an OVS interface - Agilio CX 2x10GbE card - https://www.netronome.com/products/agilio-cx/

Faucet's design principle is to be as hardware agnostic as possible and not require Table Type Patterns. This means that Faucet expects the hardware Open Flow Agent (OFA) to hide implementation details, including which tables are best for certain matches or whether there is special support for multicast - Faucet expects the OFA to leverage the right hardware transparently.

============================================================
Buying and running commercial switches supporting ryu-faucet
============================================================

Allied Telesis
--------------

`Allied Telesis <http://www.alliedtelesis.com/sdn>` sells their products via distributors and resellers. To order in USA call `ProVantage <http://www.provantage.com/allied-telesis-splx10~7ALL912L.htm>`. To find a sales office near you, visit `Allied Telesis <http://www.AlliedTelesis.com>`

* On Allied Telesis, all vlans must be included in the vlan database config on the switch before they can be used by OpenFlow.  When ordering, request Openflow license SKU.


NoviFlow
--------
`NoviFlow <http://noviflow.com>`

NorthBound Networks
-------------------
`NorthBound Networks <http://northboundnetworks.com>`

FAUCET supports the Zodiac FX as of v0.60 firmware.

Hewlett Packard Enterprise
--------------------------
`Hewlett Packard Enterprise <http://www.hpe.com>` and its many distributors and resellers.

All the HPE Aruba’s v3 based product line (5400R, 3810 and 2930F) work with FAUCET.

* 5400R - http://www.arubanetworks.com/products/networking/switches/5400r-series/
* 3810  - http://www.arubanetworks.com/products/networking/switches/3810-series/ 
* 2930F - http://www.arubanetworks.com/products/networking/switches/2930f-series/

OpenFlow is available by default on all the firmware releases of each of these products. There is no need for a purchase of separate license to enable OpenFlow on the firmware.

Netronome
---------
`Netronome <https://www.netronome.com/>` 


