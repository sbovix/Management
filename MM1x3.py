# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 09:56:47 2018

@author: silvia bova
"""

import simpy
import random
import numpy
from matplotlib import pyplot
import scipy
import math

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# CONSTANTS
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
RANDOM_SEED = 7

NUM = 50

ARRIVAL_RATE = 1.0
SERVICE_RATE = numpy.linspace(1.0, 10.0, num = NUM)

#max number of server
n=3

NUM_SERVER = 1
SIM_TIME = 10000

#Buffer capacity 
B = [1,3,6,20]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# WEB SERVER Class
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
class WebServer(object):

    def __init__(self, environ, numserver, service_time,b):

        # define the number of servers in parallel
        self.servers = simpy.Resource(environ, numserver)

        # holds samples of request-processing time
        self.s_time = [[],[],[]]

        self.service_time = service_time
        self.env = environ
        self.instant_qsize = b
        self.qsize = [0,0,0]
        

    def service_process(self, i):

        self.qsize[i] += 1

        # make a server request
        if(self.qsize[i] <= self.instant_qsize):
            with self.servers.request() as request:
                yield request
                #print ("Customers of queue %d has received the resource at %.2f" %(i,self.env.now))
    
                # once the servers is free, wait until service is finished
                s_time = random.expovariate(lambd=1.0/self.service_time)
                # yield an event to the simulator
                yield self.env.timeout(s_time)
                self.s_time[i].append(self.env.now)
                self.qsize[i] -= 1

            #print ("Customers %d satisfied at %.2f" %(i,self.env.now))
            
        #else:
            #print ("Customers lost by queue %d" %i)
            

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# REQUEST Class
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
class RequestArrival(object):

    # constructor
    def __init__(self, environ, interarrival_time):

        # holds samples of inter-arrival time
        self.inter_arrival = [[],[],[]]

        self.interarrival_time = interarrival_time
        self.env = environ

    # execute the process
    def arrival_process(self, web_service):
        while True:
            for i in range(0,3):
                # sample the time to next arrival
                inter_arrival = random.expovariate(lambd=1.0/(n*self.interarrival_time))
    
                # yield an event to the simulator
                yield self.env.timeout(inter_arrival)
                self.inter_arrival[i].append(self.env.now)    # sample time of arrival
    
                # a request has arrived - request the service to the server
                #print ("Customers of queue %d has arrived at %.2f" % (i,self.env.now))
                self.env.process(web_service.service_process(i))

#----------------------------------------------------------------------------------------------#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# MAIN
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

if __name__ == '__main__':

    print("Starting the simulation... ")

    txt=open("result_simulation.txt","w+")
    txt.truncate()

    mean_response_time = numpy.zeros((len(B),NUM))
    lost = numpy.zeros((len(B),NUM))
    arrivalrate = ARRIVAL_RATE
    

    th_RT = numpy.zeros((len(B),NUM))

    x = 0
    for b in range(0,len(B)):
        y = 0
        for servicerate in SERVICE_RATE:

            random.seed(RANDOM_SEED)

            env = simpy.Environment()

            # arrival
            request = RequestArrival(env, 1/arrivalrate)

            # web service
            webserver = WebServer(env, NUM_SERVER, 1/servicerate,B[b])

            # starts the arrival process
            env.process(request.arrival_process(webserver))

            # simulate until SIM_TIME
            env.run(until= SIM_TIME)
            

            # Statistics
            txt.write("Buffer capacity %d \n" %B[b])
            txt.write("Arrival rate [lambda]: %f - Service rate [u]: %f \n" %(arrivalrate, servicerate))
            txt.write("0-Number of requests: %d \t" %len(request.inter_arrival[0]))
            txt.write("0-Number of requests satisfied: %d \n" %len(webserver.s_time[0]))
            txt.write("0-Number of requests not satisfied: %d \n" % (len(request.inter_arrival[0]) - len(webserver.s_time[0])))
            txt.write("\n\n")
            txt.write("1-Number of requests: %d \t" %len(request.inter_arrival[1]))
            txt.write("1-Number of requests satisfied: %d \n" %len(webserver.s_time[1]))
            txt.write("1-Number of requests not satisfied: %d \n" % (len(request.inter_arrival[1]) - len(webserver.s_time[1])))
            txt.write("\n\n")
            txt.write("2-Number of requests: %d \t" %len(request.inter_arrival[2]))
            txt.write("2-Number of requests satisfied: %d \n" %len(webserver.s_time[2]))
            txt.write("2-Number of requests not satisfied: %d \n" % (len(request.inter_arrival[2]) - len(webserver.s_time[2])))
            
            # Calculate the number of lost customers as a function of B and mu
            lost[x,y] = ((len(request.inter_arrival[0]) - len(webserver.s_time[0]))+(len(request.inter_arrival[1]) - len(webserver.s_time[1]))+(len(request.inter_arrival[2]) - len(webserver.s_time[2])))
            
            # truncate inter_arrival list when not all are satisfied
            del request.inter_arrival[(len(webserver.s_time)):]

            # Calculate Vector of responsqe time
            response_time0 = [i[0] - i[1] for i in zip(webserver.s_time[0], request.inter_arrival[0])]
            response_time1 = [i[0] - i[1] for i in zip(webserver.s_time[1], request.inter_arrival[1])]
            response_time2 = [i[0] - i[1] for i in zip(webserver.s_time[2], request.inter_arrival[2])]
            mean_response_time[x,y] = (numpy.mean(response_time0)+numpy.mean(response_time1)+numpy.mean(response_time2))/3
#
            ro = arrivalrate/servicerate
            #th_RT[x,y] = (((ro*(1-scipy.math.pow(ro,b)))/(1-ro))-(b*scipy.math.pow(ro,b+1)))*(1/arrivalrate*(1-scipy.math.pow(ro,b+1)))
            
            txt.write("\n\n")
            txt.write("Average RESPONSE TIME for requests: %f" %mean_response_time[x,y])
            txt.write("\n\n")
#            
            
           
            y += 1
        x += 1
        
#########################################################################################
################### FIRST GRAPH: AVERAGE RESPONSE TIME ##################################
#########################################################################################
    
    #Theoretical response time
    #th_RT = 1/(SERVICE_RATE-(ARRIVAL_RATE/n))
   
   #plot mean number of customers in queueing line   
    pyplot.figure(0)    
    pyplot.plot(SERVICE_RATE, mean_response_time[0,:], label='Empirical')
    pyplot.title("Mean response time with B=1")
    pyplot.xlabel("mu")
    pyplot.ylabel("Mean Response Time")
    pyplot.grid();
    #pyplot.plot(SERVICE_RATE,th_RT[0,:], label='Theoretical')
    
   
    pyplot.figure(1)
    pyplot.plot(SERVICE_RATE, mean_response_time[1,:], label='Empirical')
    pyplot.title("Mean response time with B=3")
    pyplot.xlabel("mu")
    pyplot.ylabel("Mean Response Time")
    pyplot.grid();
    #pyplot.plot(SERVICE_RATE,th_RT[1,:], label='Theoretical')
    
    pyplot.figure(2)    
    pyplot.plot(SERVICE_RATE, mean_response_time[2,:], label='Empirical')
    pyplot.title("Mean response time with B=6")
    pyplot.xlabel("mu")
    pyplot.ylabel("Mean Response Time")
    pyplot.grid();
    #pyplot.plot(SERVICE_RATE,th_RT[2,:], label='Theoretical')
    
    pyplot.figure(3)
    pyplot.plot(SERVICE_RATE, mean_response_time[3,:], label='Empirical')
    pyplot.title("Mean response time with B=10")
    pyplot.xlabel("mu")
    pyplot.ylabel("Mean Response Time")
    pyplot.grid();
    #pyplot.plot(SERVICE_RATE,th_RT[3,:], label='Theoretical')
    
    pyplot.show();

#########################################################################################
################### SECOND GRAPH: AVERAGE RESPONSE TIME ##################################
#########################################################################################
    
   
   #plot number of request rejected 
    pyplot.figure(4)    
    pyplot.plot(SERVICE_RATE, lost[0,:],'ro')
    pyplot.title("Rejected request with B=1")
    pyplot.xlabel("mu")
    pyplot.ylabel("Rejected request")
    pyplot.grid();
    
   
    pyplot.figure(5)
    pyplot.plot(SERVICE_RATE, lost[1,:],'ro')
    pyplot.title("Rejected request with B=3")
    pyplot.xlabel("mu")
    pyplot.ylabel("Rejected request")
    pyplot.grid();
    
    pyplot.figure(6)    
    pyplot.plot(SERVICE_RATE, lost[2,:],'ro')
    pyplot.title("Rejected request with B=6")
    pyplot.xlabel("mu")
    pyplot.ylabel("Rejected request")
    pyplot.grid();
    
    pyplot.figure(7)
    pyplot.plot(SERVICE_RATE, lost[3,:],'ro')
    pyplot.title("Rejected request with B=10")
    pyplot.xlabel("mu")
    pyplot.ylabel("Rejected request")
    pyplot.grid();
    
    pyplot.show();


