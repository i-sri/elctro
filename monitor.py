#!/usr/bin/python
from ABE_ADCDACPi import ADCDACPi
import time
from datetime import datetime
import signal, os

def handler(signum, frame):
    global running
    print 'Stopping', signum
    running = False
    
signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGQUIT, handler)
signal.signal(signal.SIGABRT, handler)
signal.signal(signal.SIGTERM, handler)


adcdac = ADCDACPi()
adcdac.set_adc_refvoltage(3.3)

deltaT =  0.001          # time between somples
vThreshold = -0.3        # min. voltage drop to take into account
maxPossiblePower = 20001 # max. possible power

# initialise a ring of size avgSize to store the last 
# voltage values

avgSize = 4
v = adcdac.read_adc_voltage(1)
vs = [v] * avgSize       # fill the ring 
vsum = v * avgSize
vsInsert = 1             # insert position == oldest item position

vpred = v
vnew = v

tpred = datetime.now()
tp = time.time()
fileDay = tpred.day

fname = "data-"+str(tpred)+".json"
print "Writing to : ", fname
of = open(fname,'w') 
of.write('[\n')
of.close()

firstLine = True
running = True

while running :

    # detect a descent on the smoothed voltage measures
    
    nticks = 0
    vinit = vnew
    while vnew <= vpred :
        vpred = vnew
        nticks = nticks + 1
        
        time.sleep(deltaT)  
        v = adcdac.read_adc_voltage(1)

        # compute new voltage as average of the last avgSize measured voltages
        
        vsum = vsum - vs[vsInsert]  # subtract first (oldest) item
        
        vs[vsInsert] = v            # insert last v in ring
        vsInsert = (vsInsert + 1) % avgSize
        
        vsum = vsum + v
        vnew = vsum / avgSize
        
    #end while
    
    if (vnew - vinit) < vThreshold:   # the descent is significant 
        tt = time.time()      
        tstamp = datetime.now() 
        powerInW =  3600.0/(tt-tp)
        print tstamp, ("%.6f" % (tt-tp)), ", W: ", 3600.0/(tt-tp), " delta V: ", vnew - vinit , " nti: ", nticks      

        today = tstamp.day
    
        if today != fileDay:
            # a new day --> create a new file
            of = open(fname,'a') 
            of.write("\n]")
        
            # create a new file
            fname = "data-"+str(tstamp)+".json"           
            print "Writing to : ", fname
            of = open(fname,'w') 
            of.write('[\n')
            of.close()
            firstLine = True
            fileDay = today
                  
        of = open(fname,'a') 
        if not firstLine :
            of.write(',\n')
        else:
            firstLine = False
        
        watts = str(3600.0/(tt-tp))
        of.write('{ "d": "'+str(tstamp)+'", "t": '+("%.6f" % tt)+', "dt": '+("%.6f" % (tt-tp))+', "w": '+watts+ ', "dv": ' + str(vnew - vinit)+"}")
        of.close()
        
        wf = open("watts.html",'w') 
        wf.write('<html><meta http-equiv="refresh" content="1"><body><p style="font-size: 60px;">' + watts + '</p></body></html>');
        wf.close()
        
        jf = open("watts.json", "w")
        jf.write("["+watts+"]\n")
        jf.close()

        tpred = tstamp
        tp = tt
        
    #end if
       
    vpred = vnew 

#end while

of = open(fname,'a') 
of.write('\n]')    
        



