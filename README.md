# Email-Validator
Uses time-based delays in responses and RCPT to identify valid emails on an SMTP server. Particularly created for a certain email appliance.
## Usage
```
$ python email-validator.py -h
usage: email-validator.py [-h] -H HOST [-p PORT] [-f FROM] -r RECIPIENT
                          [-i INDEX] [-b BANNER] [-D DOMAIN] [-t THRESHOLD]
                          [-d DELAY] [-j JITTER] [-c CSV] [-v] [-vv]

Work in progress...email-validator.py --host TARGETHOST -p 25 -f
doesnotexist@gmail.com -r recipients.txt -D target.com -vv --delay 2000

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  The host to target for enumeration (hostname or IP)
  -p PORT, --port PORT  The default SMTP service port (default 25)
  -f FROM, --from FROM  MAIL FROM address (include the @domain.com)
  -r RECIPIENT, --recipient RECIPIENT
                        RCPT TO address to validate (include the @domain.com),
                        or the filename of addresses
  -i INDEX, --index INDEX
                        Start from this count (index). Good for fast-
                        forwarding through a file
  -b BANNER, --banner BANNER
                        The HELO command to send (typically banner)
  -D DOMAIN, --domain DOMAIN
                        Domain to append on recipients (ex: gmail.com)
  -t THRESHOLD, --threshold THRESHOLD
                        The timeout threshold for a valid user account
                        (default 500ms)
  -d DELAY, --delay DELAY
                        The delay between attempts (default 5000ms)
  -j JITTER, --jitter JITTER
                        The delay jitter between attempts. Multiplied by sleep
                        delay (default 0.3)
  -c CSV, --csv CSV     The CSV file to save the found accounts at
  -v, --verbose         Verbose output
  -vv, --debug          Less tool output, only shows good/bad/info error
                        messages.
```
