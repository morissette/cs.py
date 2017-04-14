#!/usr/bin/python
"""
Source: /root/bin/cs.py
Revision: 2.0
Author: Matthew Harris
Description: Provide a feature to check the status of websites across a
web server
"""

import httplib
import re
import os
import sys
import subprocess
import socket
from optparse import OptionParser


def checksite(domain):
    """
    Main function for checking status of domain passed
    """
    try:
        domain = checkdom(domain)
        conn = httplib.HTTPConnection(domain, timeout=5)
        conn.request('HEAD', '/')
        response = conn.getresponse()
        if options.verbose and response.status < 400:
            print '%-50s %-1s %-1s' % \
                (domain, response.status, response.reason)
        elif response.status > 400:
            print '%-50s %-1s %-1s' % \
                (domain, response.status, response.reason)
    except (httplib.HTTPException, socket.error) as ex:
        print '%-50s %-5s' % (domain, ex)


def checkdom(domain):
    """
    Ensure only the domain is checked
    """
    result = re.match(r"^http://(\S+)", domain)
    if result:
        domain = result.group(1)
        return domain
    else:
        return domain


def checkall():
    """
    Do magic with apache and domains
    """
    domains = []
    if os.path.exists('/etc/init.d/httpd'):
        proc = subprocess.Popen(
            ["/bin/sh", "/etc/init.d/httpd", "-V"], stdout=subprocess.PIPE)
        output = proc.communicate()
        output = output[0].split('\n')
        conf = {}
        for line in output:
            setting = re.match(r'\s+-D\s+HTTPD_ROOT="(\S+)"', line)
            if setting:
                conf['root'] = setting.group(1)

            setting = re.match(r'\s+-D\s+SERVER_CONFIG_FILE="(\S+)"', line)
            if setting:
                conf['conf'] = setting.group(1)

            conf_path = conf['root'] + "/" + conf['conf']
            file_handle = open(conf_path, 'r')
            for line in file_handle.readlines():
                servername = re.match(r'\s+ServerName\s+(\S+)', line)
                if servername:
                    domains.append(servername.group(1))
            file_handle.close()

            for domain in domains:
                checksite(domain)
    elif os.path.exists('/etc/init.d/apache'):
        print "apache"
    elif os.path.exists('/etc/init.d/apache2'):
        print "apache2"
    else:
        print "no apache"


def checkuser(user):
    """
    Cpanel only function for checking domains of a user
    """
    domains = []
    try:
        file_handle = open('/var/cpanel/userdata/' + user + '/main')
        for line in file_handle.readlines():
            result = re.match(r"main_domain: (\S+)", line)
            if result:
                domains.append(result.group(1))
            result = re.match(r"\s+(\S+):", line)
            if result:
                domains.append(result.group(1))
            result = re.match(r"\s+-\s(\S+)", line)
            if result:
                domains.append(result.group(1))
            result = re.match("sub_domains:", line)
            if result:
                break
        file_handle.close()
        for domain in domains:
            checksite(domain)
    except OSError:
        print "User does not exist"

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option(
        "-w",
        "--working",
        action="store_true",
        dest="verbose",
        help="shows domains that return a status between 200 and 399"
    )

    parser.add_option(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        help="shows domains that return a status between 200 and 399"
    )

    parser.add_option(
        "-c",
        "--content-check",
        action="store_true",
        dest="content",
        help="checks content for common errors"
    )

    parser.add_option(
        "-a",
        "--all",
        action="store_true",
        dest="all",
        help="checks all domains on the server for bad http statuses"
    )

    parser.add_option(
        "-d",
        "--domain",
        action="store",
        dest="domain",
        help="checks the status of the domain provided"
    )

    parser.add_option(
        "-u",
        "--user",
        action="store",
        dest="user",
        help="checks the status of the domains for the user provided"
    )

    (options, args) = parser.parse_args()
    print "\nCheckSites v2.0 by admin@mattharris.org"
    print "------------------------------------------------------"
    print "%-50s %-5s" % ("DOMAIN", "STATUS")
    sys.stdout.flush()
    if options.domain:
        checksite(options.domain)
    if options.all:
        checkall()
    if options.user:
        if os.path.isdir("/usr/local/cpanel"):
            checkuser(options.user)
        else:
            print "This option only works on cPanel"
            print "\n"
