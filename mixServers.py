# -*- coding: utf-8 -*-
"""
Created on Sat Apr 28 13:12:20 2018

@author: silvia
"""

import simpy
import random
import numpy
from matplotlib import pyplot
from scipy.stats import t
import math

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# CONSTANTS
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
RANDOM_SEED = 7

#SERVICE_RATE = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
#ARRIVAL_RATE = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
NUM = 50

# = 10.0 # it is the inverse of the service rate (speed)
ARRIVAL_TIME = 10.0
SERVICE_TIME = numpy.linspace(1.0, 10.0, num = NUM)
#ARRIVAL_TIME = numpy.linspace(1.0, 10.0, num = NUM)

#max number of server
n=4

CONF_LEVEL = 0.9
NUM_BEANS = 10

NUM_SERVER = 1
SIM_TIME = 100000

#Buffer capacity 
B = [1,3,6,10]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# WEB SERVER Class
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
class WebServer(object):

    def __init__(self, environ, numserver, service_rate,b):

        # define the number of servers in parallel
        self.servers = simpy.Resource(environ, numserver)

        # holds samples of request-processing time
        self.service_time = [[],[],[],[]]

        self.service_rate = service_rate
        self.env = environ
        self.instant_qsize = b
        self.qsize = [0,0,0,0]
        

    def service_process(self, i):

        self.qsize[i] += 1

        # make a server request
        if(self.qsize[i] <= self.instant_qsize):
            with self.servers.request() as request:
                yield request
                #print ("Customers of queue %d has received the resource at %.2f" %(i,self.env.now))
                if(i!=3):
                    # once the servers is free, wait until service is finished
                    service_time = random.expovariate(lambd=1.0/self.service_rate)
                else:
                    service_time = random.expovariate(lambd=n/self.service_rate)
                # yield an event to the simulator
                yield self.env.timeout(service_time)
                self.service_time[i].append(self.env.now)
                self.qsize[i] -= 1

            #print ("Customers %d satisfied at %.2f" %(i,self.env.now))
            
        #else:
            #print ("Customers lost by queue %d" %i)
            

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# REQUEST Class
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
class RequestArrival(object):

    # constructor
    def __init__(self, environ, arrival_rate):

        # holds samples of inter-arrival time
        self.inter_arrival = [[],[],[],[]]

        self.arrival_rate = arrival_rate
        self.env = environ

    # execute the process
    def arrival_process(self, web_service):
        while True:
            for i in range(0,n):
                # sample the time to next arrival
                inter_arrival = random.expovariate(lambd=1.0/self.arrival_rate)
    
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
    arrivalrate = ARRIVAL_TIME


    ro = numpy.zeros((len(B),NUM))

    x = 0
    for b in range(0,len(B)):
        y = 0
        for servicerate in SERVICE_TIME:

            random.seed(RANDOM_SEED)

            env = simpy.Environment()

            # arrival
            request = RequestArrival(env, arrivalrate)

            # web service
            webserver = WebServer(env, NUM_SERVER, servicerate,B[b])

            # starts the arrival process
            env.process(request.arrival_process(webserver))

            # simulate until SIM_TIME
            env.run(until= SIM_TIME)
            

            # Statistics
            txt.write("Buffer capacity %d \n" %B[b])
            txt.write("Arrival rate [lambda]: %f - Service rate [u]: %f \n" %(arrivalrate, servicerate))
            txt.write("0-Number of requests: %d \t" %len(request.inter_arrival[0]))
            txt.write("0-Number of requests satisfied: %d \n" %len(webserver.service_time[0]))
            txt.write("0-Number of requests not satisfied: %d \n" % (len(request.inter_arrival[0]) - len(webserver.service_time[0])))
            txt.write("\n\n")
            txt.write("1-Number of requests: %d \t" %len(request.inter_arrival[1]))
            txt.write("1-Number of requests satisfied: %d \n" %len(webserver.service_time[1]))
            txt.write("1-Number of requests not satisfied: %d \n" % (len(request.inter_arrival[1]) - len(webserver.service_time[1])))
            txt.write("\n\n")
            txt.write("2-Number of requests: %d \t" %len(request.inter_arrival[2]))
            txt.write("2-Number of requests satisfied: %d \n" %len(webserver.service_time[2]))
            txt.write("3-Number of requests not satisfied: %d \n" % (len(request.inter_arrival[2]) - len(webserver.service_time[2])))
            txt.write("\n\n")
            txt.write("3-Number of requests: %d \t" %len(request.inter_arrival[3]))
            txt.write("3-Number of requests satisfied: %d \n" %len(webserver.service_time[3]))
            txt.write("3-Number of requests not satisfied: %d \n" % (len(request.inter_arrival[3]) - len(webserver.service_time[3])))
                        
            
            # Calculate the number of lost customers as a function of B and mu 
            lost[x,y] = ((len(request.inter_arrival[0]) - len(webserver.service_time[0]))+(len(request.inter_arrival[1]) - len(webserver.service_time[1]))+(len(request.inter_arrival[2]) - len(webserver.service_time[2]))+(len(request.inter_arrival[3]) - len(webserver.service_time[3])) )
                    
            # truncate inter_arrival list when not all are satisfied
            del request.inter_arrival[(len(webserver.service_time)):]

            # Calculate Vector of responsqe time
            response_time0 = [i[0] - i[1] for i in zip(webserver.service_time[0], request.inter_arrival[0])]
            response_time1 = [i[0] - i[1] for i in zip(webserver.service_time[1], request.inter_arrival[1])]
            response_time2 = [i[0] - i[1] for i in zip(webserver.service_time[2], request.inter_arrival[2])]
            response_time3 = [i[0] - i[1] for i in zip(webserver.service_time[3], request.inter_arrival[3])]            
            mean_response_time[x,y] = (numpy.mean(response_time0)+numpy.mean(response_time1)+numpy.mean(response_time2)+numpy.mean(response_time3))/4
#
#            ro[x,y] = servicerate/arrivalrate
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
#    th_RT = (n*SERVICE_TIME*ARRIVAL_TIME)/((n*ARRIVAL_TIME)-SERVICE_TIME)
   
   #plot mean number of customers in queueing line   
    pyplot.figure(0)    
    pyplot.plot(1/SERVICE_TIME, mean_response_time[0,:], label='Empirical')
    pyplot.title("Mean response time with B=1")
    pyplot.xlabel("mu")
    pyplot.ylabel("Mean Response Time")
    pyplot.grid();
#    pyplot.plot(1/SERVICE_TIME,th_RT, label='Theoretical')
    
   
    pyplot.figure(1)
    pyplot.plot(1/SERVICE_TIME, mean_response_time[1,:], label='Empirical')
    pyplot.title("Mean response time with B=3")
    pyplot.xlabel("lambda")
    pyplot.ylabel("Mean Response Time")
    pyplot.grid();
#    pyplot.plot(1/SERVICE_TIME,th_RT, label='Theoretical')
    
    pyplot.figure(2)    
    pyplot.plot(1/SERVICE_TIME, mean_response_time[2,:], label='Empirical')
    pyplot.title("Mean response time with B=6")
    pyplot.xlabel("mu")
    pyplot.ylabel("Mean Response Time")
    pyplot.grid();
#    pyplot.plot(1/SERVICE_TIME,th_RT, label='Theoretical')
   
    pyplot.figure(3)
    pyplot.plot(1/SERVICE_TIME, mean_response_time[3,:], label='Empirical')
    pyplot.title("Mean response time with B=10")
    pyplot.xlabel("mu")
    pyplot.ylabel("Mean Response Time")
    pyplot.grid();
#    pyplot.plot(1/SERVICE_TIME,th_RT, label='Theoretical')
    
    pyplot.show();

#########################################################################################
################### SECOND GRAPH: AVERAGE RESPONSE TIME ##################################
#########################################################################################
    
   
   #plot number of request rejected 
    pyplot.figure(4)    
    pyplot.plot(1/SERVICE_TIME, lost[0,:])
    pyplot.title("Rejected request with B=1")
    pyplot.xlabel("mu")
    pyplot.ylabel("Rejected request")
    pyplot.grid();
    
   
    pyplot.figure(5)
    pyplot.plot(1/SERVICE_TIME, lost[1,:])
    pyplot.title("Rejected request with B=3")
    pyplot.xlabel("mu")
    pyplot.ylabel("Rejected request")
    pyplot.grid();
    
    pyplot.figure(6)    
    pyplot.plot(1/SERVICE_TIME, lost[2,:])
    pyplot.title("Rejected request with B=6")
    pyplot.xlabel("mu")
    pyplot.ylabel("Rejected request")
    pyplot.grid();
    
    pyplot.figure(7)
    pyplot.plot(1/SERVICE_TIME, lost[3,:])
    pyplot.title("Rejected request with B=10")
    pyplot.xlabel("mu")
    pyplot.ylabel("Rejected request")
    pyplot.grid();
    
    pyplot.show();