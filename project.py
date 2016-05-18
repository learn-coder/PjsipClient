# Importing all the required files
import sys
import pjsua as pj
import threading
from time import sleep


# Logging inside the callback class
def log_cb(level, str, len):
    print str,


# Created MyCallCallback class inorder to receive events from the Call being made
class MyCallCallback(pj.CallCallback):
    def __init__(self, call= None):
        pj.CallCallback.__init__(self, call)
    
    def on_state(self):
        print "Call is =", self.call.info().state_text,
        print "last code =", self.call.info().last_code, 
        print "(" + self.call.info().last_reason + ")"
        
    # Notify Client1 if media state of the call has been changed
    def on_media_state(self):
        global lib
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            # Connecting sound device with the call
            call_slot = self.call.info().conf_slot
            lib.conf_connect(call_slot, 0)
            lib.conf_connect(0, call_slot)
            print " CALL SUCCESSFUL!"
 

# Creating MyAccountCallback class 
class MyAccountCallback(pj.AccountCallback):
    def __init__(self, acc):
        pj.AccountCallback.__init__(self, acc)

         
# Check if command line argument are not properly given 
if len(sys.argv) != 2:
    print 'Please enter destination addr <dst-URI>'
    sys.exit(1)


# Try catch block to handle errors
try:
    # Creating an instance of library
    lib = pj.Lib()

    # Using the Init library having the default configurations
    lib.init(log_cfg = pj.LogConfig(level=3, callback=log_cb))

    # Creating an UDP transport that is listening to any available port
    trans_config = pj.TransportConfig()
    trans_config.port = 5060
    trans_config.bound_addr = "192.168.112.128"
    transport = lib.create_transport(pj.TransportType.UDP,trans_config)
    
    # Starting the library instance
    lib.start()
    lib.set_null_snd_dev()
    
    # Account configuration from Client1 in order to register with the Server
    acc_cfg = pj.AccountConfig(domain = '169.254.2.2', username = '2010', password = 'password', display = 'Ambarish', registrar = 'sip:169.254.2.2:5060', proxy = 'sip:169.254.2.2:5060')
    
    # Client1's ID and port number in order to create an account
    acc_cfg.id = "sip:2010"
    acc_cfg.reg_uri = "sip:169.254.2.2:5060"
    acc = lib.create_account(acc_cfg)
    
    # Printing the response from server about the registration process
    print '\n'
    print 'Registration complete, status=', acc.info().reg_status, \
         '(' + acc.info().reg_reason + ')'

    # Waiting for 5 seconds
    sleep(5)
    
    # Making a call to Client2 at 169.254.1.10:5060 using aruments from CLI
    call = acc.make_call(sys.argv[1], MyCallCallback())
    
    # Waiting for the response from the server side
    sleep(20)

    # Manual unregistration process
    print " If you want to unregister? Please press y/n and press ENTER "
    unreg= sys.stdin.readline().rstrip('\r\n')
    
    # Checking the response from Client1
    
    # If the response from the Client1 is YES
    if unreg=="Y" or unreg =="y":
        # Unregister the created account
        acc.set_registration(False)
    
    # Else exit from the code
    else:
        print "you chose not to unregister, so exiting the code without destroying the library"
        # Exiting the code without destroying the library
        sys.exit(1)
    

    # Reply from the Server side regarding un-registration
    print '\n'
    print 'Registration complete, status=', acc.info().reg_status, \
         '(' + acc.info().reg_reason + ')'

    
    # We are done with our part, shutdown the library
    lib.destroy()
    lib = None
    print "Destroyed the library and successfully unregistered"

# Except block
except pj.Error, e:
    print 'Exception: ' + str(e)
    lib.destroy()
    lib = None
    sys.exit(1)
