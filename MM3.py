# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 09:49:48 2018

@author: silvia
"""

import simpy
import random
import numpy
from matplotlib import pyplot
import scipy

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# CONSTANTS
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
RANDOM_SEED = 7

NUM = 50

ARRIVAL_RATE = 1.0
SERVICE_RATE = numpy.linspace(1.1, 10.0, num = NUM)

#max number of server
n=1

NUM_SERVER = 3
SIM_TIME = 10000

#Buffer capacity 
B = [2,4,6,10]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# WEB SERVER Class
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
class WebServer(object):

    def __init__(self, environ, numserver, service_time,b):

        # define the number of servers in parallel
        self.servers = simpy.Resource(environ, numserver)

        # holds samples of request-processing time
        self.s_time = []

        self.service_time = service_time
        self.env = environ
        self.instant_qsize = b
        self.qsize = 0

    def service_process(self):

        self.qsize += 1

        # make a server request
        if(self.qsize <= self.instant_qsize):
            with self.servers.request() as request:
                yield request
            #    print ("Customers has received the resource at ", self.env.now)
    
                # once the servers is free, wait until service is finished
                s_time = random.expovariate(lambd=n/self.service_time)
                # yield an event to the simulator
                yield self.env.timeout(s_time)
                self.s_time.append(self.env.now)
                self.qsize -= 1

          #  print ("Customers satisfied at ", self.env.now)
            
        #else:
           # print ("Customers lost")
            

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# REQUEST Class
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
class RequestArrival(object):

    # constructor
    def __init__(self, environ, interarrival_time):

        # holds samples of inter-arrival time
        self.inter_arrival = []

        self.interarrival_time = interarrival_time
        self.env = environ

    # execute the process
    def arrival_process(self, web_service):
        while True:

            # sample the time to next arrival
            inter_arrival = random.expovariate(lambd=1.0/self.interarrival_time)

            # yield an event to the simulator
            yield self.env.timeout(inter_arrival)
            self.inter_arrival.append(self.env.now)    # sample time of arrival

            # a request has arrived - request the service to the server
           # print ("Customers has arrived at ", self.env.now)
            self.env.process(web_service.service_process())

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
    th_RT = numpy.zeros((len(B),NUM))
    P0 = numpy.zeros((len(B),NUM))
    arrivalrate = ARRIVAL_RATE

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
            txt.write("Arrival rate [lambda]: %f - Service rate [u]: %f \n" %(arrivalrate, servicerate))
            txt.write("Number of requests: %d \t" %len(request.inter_arrival))
            txt.write("Number of requests satisfied: %d \n" %len(webserver.s_time))
            txt.write("Number of requests not satisfied: %d \n" % (len(request.inter_arrival) - len(webserver.s_time)))

            # Calculate Vector of response time

            response_time = [i[0] - i[1] for i in zip(webserver.s_time, request.inter_arrival)]
            mean_response_time[x,y] = numpy.mean(response_time)

            ro = arrivalrate/(NUM_SERVER*servicerate)
            r = arrivalrate/servicerate 
            P0 = 
            th_RT[x,y] = scipy.math.factorial(NUM_SERVER)*ro*(((1-scipy.math.pow(ro,B[b]))*(1-scipy.math.pow(ro,B[b]+1)))-(B[b]*scipy.math.pow(ro,B[b]+1)*(1-ro)*(1-scipy.math.pow(ro,B[b]+1))))/(arrivalrate*(1-ro)*(1-scipy.math.pow(ro,B[b]+1)))
            
            txt.write("Average RESPONSE TIME for requests: %f" %mean_response_time[x,y])
            txt.write("\n\n")
            
            # Calculate the number of lost customers as a function of B and mu
            lost[x,y] = (len(request.inter_arrival) - len(webserver.s_time))
            
            y += 1
        x += 1
        
#########################################################################################
################### FIRST GRAPH: AVERAGE RESPONSE TIME ##################################
#########################################################################################
    
    #Theoretical response time
    #th_RT = 1/(n*(SERVICE_RATE-ARRIVAL_RATE))
   
   #plot mean number of customers in queueing line   
    pyplot.figure(0)    
    pyplot.plot(SERVICE_RATE, mean_response_time[0,:], label='Empirical')
    pyplot.xlabel("mu")
    pyplot.ylabel("Mean Response Time")
    pyplot.title("M/M/3/2")
    pyplot.grid();
    pyplot.plot(SERVICE_RATE,th_RT[0,:], label='Theoretical')
   
    pyplot.figure(1)
    pyplot.plot(SERVICE_RATE, mean_response_time[1,:], label='Empirical')
    pyplot.xlabel("mu")
    pyplot.ylabel("Mean Response Time")
    pyplot.title("M/M/3/4")
    pyplot.grid();
    pyplot.plot(SERVICE_RATE,th_RT[1,:], label='Theoretical')
    
    pyplot.figure(2)    
    pyplot.plot(SERVICE_RATE, mean_response_time[2,:], label='Empirical')
    pyplot.xlabel("mu")
    pyplot.ylabel("Mean Response Time")
    pyplot.title("M/M/3/6")
    pyplot.grid();
    pyplot.plot(SERVICE_RATE,th_RT[2,:], label='Theoretical')
    
    pyplot.figure(3)
    pyplot.plot(SERVICE_RATE, mean_response_time[3,:], label='Empirical')
    pyplot.xlabel("mu")
    pyplot.ylabel("Mean Response Time")
    pyplot.title("M/M/3/10")
    pyplot.grid();
    pyplot.plot(SERVICE_RATE,th_RT[3,:], label='Theoretical')
    
    pyplot.show();
    
    #########################################################################################
################### SECOND GRAPH: AVERAGE RESPONSE TIME ##################################
#########################################################################################
    
   
   #plot number of request rejected 
    pyplot.figure(4)    
    pyplot.plot(SERVICE_RATE, lost[0,:],'ro')
    pyplot.title("M/M/3/2")
    pyplot.xlabel("mu")
    pyplot.ylabel("Rejected request")
    pyplot.grid();
    
   
    pyplot.figure(5)
    pyplot.plot(SERVICE_RATE, lost[1,:],'ro')
    pyplot.title("M/M/3/4")
    pyplot.xlabel("mu")
    pyplot.ylabel("Rejected request")
    pyplot.grid();
    
    pyplot.figure(6)    
    pyplot.plot(SERVICE_RATE, lost[2,:],'ro')
    pyplot.title("M/M/3/6")
    pyplot.xlabel("mu")
    pyplot.ylabel("Rejected request")
    pyplot.grid();
    
    pyplot.figure(7)
    pyplot.plot(SERVICE_RATE, lost[3,:],'ro')
    pyplot.title("M/M/3/10")
    pyplot.xlabel("mu")
    pyplot.ylabel("Rejected request")
    pyplot.grid();
    
    pyplot.show();

