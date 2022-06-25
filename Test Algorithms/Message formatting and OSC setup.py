from time import sleep
from pythonosc import udp_client

######### format the approximation set and send it over to SonOpt via OSC #######
#convert the arrays into lists
#first the approximation set list
obj_one = ['{:f}'.format(item) for item in approximation_set[:, 0]]
obj_two = ['{:f}'.format(item) for item in approximation_set[:, 1]]
objs_combined = [obj_one, obj_two]
formatted_approximation_set = [' '.join(str(item) for item in column) for column in zip(*objs_combined)]
#then the hypervolume contributions list
formatted_hypervolume_contributions_list = ['{:f}'.format(item) for item in hypervolume_contributions_list]
      
#send the results to SonOpt
client_a = udp_client.SimpleUDPClient("127.0.0.1", 5002)
client_a.send_message("start", formatted_approximation_set)
client_a = udp_client.SimpleUDPClient("127.0.0.1", 5003)
client_a.send_message("start", formatted_hypervolume_contributions_list)
    
sleep(0.5)
