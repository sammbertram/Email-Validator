#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" SMTP Enumeration Script """
"""Uses time-based delays in responses and RCPT to identify valid emails on an SMTP server. Particularly created for a certain email appliance."""

__author__     = "Sam Bertram"
__version__     = "0.1"

hello_msg = '''
____ _  _ ____ _ _       _  _ ____ _    _ ___  ____ ___ ____ ____ 
|___ |\/| |__| | |       |  | |__| |    | |  \ |__|  |  |  | |__/ 
|___ |  | |  | | |___     \/  |  | |___ | |__/ |  |  |  |__| |  \ 
                                                                 
                                                 version: %s
                     
''' % __version__

data = {}


import io
import csv
import re
import platform
import argparse
import csv
import os
import datetime
import urllib2
import io
from random import randint
from time import sleep
from tempfile import NamedTemporaryFile
import urllib
import pprint
import csv
import time
import socket

# pretty print
pp = pprint.PrettyPrinter(indent=4)

parser = argparse.ArgumentParser(description="Work in progress...email-validator.py --host TARGETHOST -p 25 -f doesnotexist@gmail.com -r recipients.txt -D target.com -vv --delay 2000")
parser.add_argument('-H','--host', help='The host to target for enumeration (hostname or IP)',required=True)
parser.add_argument('-p','--port', help='The default SMTP service port (default 25)', default=25)
parser.add_argument('-f','--from', help='MAIL FROM address (include the @domain.com)', default="recruitment@gmail.com")
parser.add_argument('-r','--recipient', help='RCPT TO address to validate (include the @domain.com), or the filename of addresses',required=True)
parser.add_argument('-i','--index',help="Start from this count (index). Good for fast-forwarding through a file",default=0)
# TODO parse banner from response if not set??
parser.add_argument('-b','--banner', help='The HELO command to send (typically banner)', default="x")
parser.add_argument('-D','--domain', help='Domain to append on recipients (ex: gmail.com)')
parser.add_argument('-t','--threshold',help="The timeout threshold for a valid user account (default 500ms)", default=500)
parser.add_argument('-d','--delay',help="The delay between attempts (default 5000ms)", default=6000)
parser.add_argument('-j','--jitter',help="The delay jitter between attempts. Multiplied by sleep delay (default 0.3)", default=0.5)
parser.add_argument('-c','--csv',help="The CSV file to save the found accounts at", default="output_smtp.csv" )
parser.add_argument('-v','--verbose', help='Verbose output', action="store_true")
parser.add_argument('-vv','--debug', help='Less tool output, only shows good/bad/info error messages.', action="store_true")
args = vars(parser.parse_args())

#2018-11-19 16:12:47 ubuntu@ip-172-31-17-190:~$ nc -vn  159.50.101.86 25
#Connection to 159.50.101.86 25 port [tcp/*] succeeded!
#220-target.TARGET.com ESMTP
#220 TARGET.com ESMTP Ready
#HELO x
#250 target.TARGET.com
#MAIL FROM: hiring@TARGET.com
#501 #5.5.2 syntax error 'MAIL FROM: hiring@TARGET.com'
#MAIL FROM: foo@gmail.com
#501 #5.5.2 syntax error 'MAIL FROM: foo@gmail.com'
#VRFY test@TARGET.com
#252 ok
#VRFY TARGET@TARGET.com
#252 ok
#VRFY TARGET222@TARGET.com
#252 ok
#VRFY TARGET222222@TARGET.com
#252 ok
#VRFY test2@TARGET.com
#252 ok
#MAIL FROM: foo
#501 #5.5.2 syntax error 'MAIL FROM: foo'
#MAIL FROM: <foo@example.com>
#250 sender <foo@example.com> ok
#RCPT TO: testing@TARGET.com
#501 #5.5.2 syntax error 'RCPT TO: testing@TARGET.com'
#RCPT TO: <testing@TARGET.com>
#550 #5.1.0 Address rejected.
#RCPT TO: <TARGET@TARGET.com>
#250 recipient <TARGET@TARGET.com> ok
#RCPT TO: <TARGET222@TARGET.com>
#550 #5.1.0 Address rejected.
#QUIT
#221 target.TARGET.com







def main():
    
    # if debug is enabled, enable verbose as well 
    if args['debug']: args['verbose'] = True 

    # target options 
    host = args['host']
    port = int(args['port'])

    # enumeration information
    mail_from = args['from']
    
    domain = args['domain']
    rcpts = args['recipient']

    # timing options
    delay = int(args['delay'])
    jitter = float(args['jitter'])
    threshold = int(args['threshold'])
    
    # csv file
    csv = args['csv']
    banner = args['banner']

    # start option
    index = int(args['index'])
    
    if args['debug'] or args['verbose']:
      ALERT("host - %s:%s" % (host,port),ALERT.INFO)
      ALERT("enum - from: %s, domain: %s, recipient: %s" % (mail_from,domain,rcpts),ALERT.INFO)
      ALERT("time - delay: %s, jitter: %s, threshold: %s" % (delay,jitter,threshold),ALERT.INFO)
      ALERT("csv: %s" % csv, ALERT.INFO)
      ALERT("index: %s" % index, ALERT.INFO)

    # try and validate the recipient, could be a single or could be a file
    if os.path.isfile(rcpts):
        ALERT("Recipient input is a file... reading")
        rcpts = open(rcpts).read().splitlines()
        ALERT("Testing multiple accounts (%s)" % len(rcpts))
    else:
        ALERT("Testing single account (%s)" % rcpts)
        rcpts = [rcpts]

    keep_running = True
    connected = False
    count = 0
    
    while keep_running:
        
        # attempt to connect. if too many invalid recipients, then retry
        # after three minutes
        if not connected:
            #220-target.TARGET.com ESMTP
            #220 TARGET.com ESMTP Ready
            # first connect to server
            print_time()
            # TODO what happens if i can't connect to the port? 
            
            # keep trying to connected
            while not connected:
                ALERT("Connecting to %s:%s..." % (host,port))
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				
                try:
                    s.connect((host, port))
                except socket.error, e:
                    ALERT("Cannot connect (%s). Sleeping for 3 minutes" % e, ALERT.SEVERE)
                    s.close()
                    time.sleep(180)
                    continue
                    #socket.error: [Errno 110] Connection timed out
                    
                s.settimeout(1)
                fn = s.makefile('rwb')
                
                resp = recv_data(s)
                if "Too many invalid recipients" in resp: 
                    ALERT("Cannot connect. Too many invalid recipients. Sleeping for 3 minutes", ALERT.SEVERE)
                    s.close()
                    time.sleep(180)
                    connected = False
                    continue
                else: connected = True
            
            ALERT("Connected.")
        
    # if we get this far, that means we have a valid socket.
    #HELO x
    #250 target.TARGET.com
        snooze(delay,jitter)
        helo = "HELO %s" % banner
        if args['debug']: ALERT(helo,ALERT.INFO) 
        fn.write('%s\r\n' % helo)
        fn.flush()
        resp = recv_data(s)
        #resp = fn.readline().rstrip('\n')
        #ALERT(resp)
        
    #MAIL FROM: <foo@example.com>
    #250 sender <foo@example.com> ok
        snooze(delay,jitter) 
        mf = "MAIL FROM: <%s>" % mail_from
        if args['debug']: ALERT(mf,ALERT.INFO)
        fn.write('%s\r\n' % mf)
        fn.flush()
        resp = recv_data(s)
        
        
    #RCPT TO: <TARGET@TARGET.com>
    #250 recipient <TARGET@TARGET.com> ok
        # loop through users

        for rcpt_to in rcpts:
            count = count + 1
            
            # if we are starting from an index, try and go to top of loop
            if index and count < index: continue
                
            snooze(delay,jitter) 
            if domain: rcpt_to = "%s@%s" % (rcpt_to, domain)
            if args['verbose']: ALERT("Enumerating %s account (%s/%s)..." % (rcpt_to, count, len(rcpts)))

            # start timekeeping
            start = datetime.datetime.now()

            rcpt = "RCPT TO: <%s>" % rcpt_to
            if args['debug']: ALERT(rcpt,ALERT.INFO)
            fn.write('%s\r\n' % rcpt)
            fn.flush()
            resp = recv_data(s)
            end = datetime.datetime.now()
            
            # delay in ms
            response_time = int((end - start).total_seconds() * 1000)
           # if ms < threshold:
           #     ALERT("%s, delay of %sms, valid" % (rcpt_to, ms), ALERT.GOOD)
           #     response = "valid"
           # else:
           #     ALERT("%s, delay of %sms, invalid" % (rcpt_to,ms), ALERT.BAD)
           #     response = "invalid"

            # if user is valid, output and log to csv
            # start,end,host,port,domain,mail_from,response_time,resp
            
            csvrow = "%s,%s,%s,%s,%s,%s,%s,%s,%s" % (start.strftime('%Y-%m-%d %H:%M:%S:%f'),end.strftime('%Y-%m-%d %H:%M:%S:%f'),host,port,domain,mail_from,rcpt_to,response_time,resp.rstrip('\r\n'))
            fd = open(csv,'a')
            fd.write(csvrow)
            fd.write("\r\n")
            fd.close()

            if "Too many recipients" in resp or "550 Too many invalid recipients" in resp:
                ALERT("Received too many recipients on %s. Disconnected." % count, ALERT.SEVERE)
                index = count
                connected = False
                break
            if "451 Internal resource temporarily unavailable" in resp:
                ALERT("Mimecast 451 received on %s. Disconnected!" % count, ALERT.SEVERE)
                connected = False
                break

            # after looping through all recipients, we don't want to keep running                
            if count == len(rcpts): keep_running = False
        
        # only disconnected if connected
        if connected:
            # disconnect from the server
            snooze(delay,jitter) 
            quit = "QUIT"
            ALERT(quit,ALERT.INFO)
            fn.write('%s\r\n' % quit)
            fn.flush()
            s.close()
            print_time()

# nc -v mail.DOMAIN.com 25
#Connection to mail.DOMAIN.com 25 port [tcp/smtp] succeeded!
#220 DOMAIN.com.local APPLIANCE
#HELO DOMAIN.com.local
#250 DOMAIN.com.local
#MAIL FROM: recruitment@DOMAIN.com
#250 2.1.0 Ok
#RCPT TO: recruitment22222@DOMAIN.com
#250 2.1.5 Ok
#RCPT TO: recruitment@DOMAIN.com
#250 2.1.5 Ok
#RCPT TO: careers@DOMAIN.com
#250 2.1.5 Ok
#RCPT TO: consultation@DOMAIN.com
#250 2.1.5 Ok
#421 4.4.2 DOMAIN.com.local Error: timeout exceeded
    # append to CSV file as soon as response comes
    # date,host,port,domain,mail_from,response_time,response
    # save to CSV
    
    ALERT("done")

        
def recv_data(s):
    full_msg = ""
    while True:
        try:
            msg = s.recv(4096)
            full_msg = full_msg + msg
        except socket.timeout, e:
            #print "[!] socket timed out!"
            #sys.exit(1)
            return full_msg
            
        except socket.error, e:
            print "[!] unknown socket error!"
            sys.exit(1)
        else:
            if len(msg) == 0: return full_msg
            else: ALERT(msg)


def snooze(delay,jitter):
    s = randint(delay-(delay*jitter),delay+(delay*jitter))
    if args['debug']: ALERT("Snoozing for %sms" % s, ALERT.INFO)
    time.sleep(s/1000)

def print_time():
    ALERT(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

class ALERT(object):
    
    def __init__(self, message, level=0, spacing=0, ansi=True):

        # default to ansi alerting, if it's detected as windows platform then disable
        if platform.system() is "Windows": ansi = False

        good = '[+]'
        bad = '[-]'
        normal = '[*]'
        severe = '[!]'
        info = '[>]'
        space = ''

        for i in range(spacing):
            space += '  '
        
        if ansi == True:
            if level == ALERT.GOOD: print("%s%s%s%s" % ('\033[1;32m',good,"\033[0;0m",space)),
            elif level == ALERT.BAD: print("%s%s%s%s" % ('\033[1;31m',bad,"\033[0;0m",space)),
            elif level == ALERT.SEVERE: print("%s%s%s%s" % ('\033[1;31m',severe,"\033[0;0m",space)),
            elif level == ALERT.INFO: print("%s%s%s%s" % ('\033[1;33m',info,"\033[0;0m",space)),
            else: print("%s%s%s%s" % ('\033[1;34m',normal,"\033[0;0m",space)),
            
        else:
            if level == ALERT.GOOD: print('%s%s' % good,space),
            elif level == ALERT.BAD: print('%s%s' % bad,space),
            elif level == ALERT.SEVERE: print('%s%s' % (severe,space)),
            elif level == ALERT.INFO: print('%s%s' % (info,space)),
            else: print('%s%s' % normal,space),
            
        print message
    
    @staticmethod
    @property
    def BAD(self): return -1
        
    @staticmethod
    @property
    def NORMAL(self): return 0
        
    @staticmethod
    @property
    def GOOD(self): return 1

    @staticmethod
    @property
    def SEVERE(self): return -2

    @staticmethod
    @property
    def INFO(self): return 2

if __name__ == '__main__':
    print hello_msg
    main()


