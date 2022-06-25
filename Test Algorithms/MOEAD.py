from pymoo.algorithms.moo.moead import MOEAD
from pymoo.factory import get_problem, get_reference_directions
from time import sleep
from pythonosc import udp_client
import numpy as np
import matplotlib.pyplot as plt
from pymoo.factory import get_performance_indicator
from pymoo.visualization.scatter import Scatter
from sklearn.preprocessing import MinMaxScaler


problem = get_problem("zdt1")

ref_dirs = get_reference_directions("das-dennis", 2, n_partitions=99)
algorithm = MOEAD(ref_dirs, n_neighbors=15, prob_neighbor_mating=0.7)

hv = get_performance_indicator("hv", ref_point=np.array([1.2,1.2]))

# prepare the algorithm to solve the specific problem (same arguments as for the minimize function)
algorithm.setup(problem, ('n_gen', 250), seed=1)
sleep(0)

# until the algorithm has no terminated
while algorithm.has_next():
    
    # do the next iteration
    algorithm.next()

    # do same more things, printing, logging, storing or even modifying the algorithm object
    #print(algorithm.n_gen, algorithm.evaluator.n_eval)
    
    approximation_set = algorithm.result().F
    
    #sort the approximation set so that left->right means min(x)->max(x) and max(y)->min(y)
    approximation_set = approximation_set[approximation_set[:,0].argsort()] 
    
    #calculate the hypervolume index
    #first scale the approximation set so it fits the 0, 1 range
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_set = scaler.fit(approximation_set)
    scaled_set = scaler.transform(approximation_set)
    hypervolume = hv.do(scaled_set)
    
    #reset the hypervolume contributions
    hypervolume_contributions_list = []
    
    #calculate the hypervolume contributions
    for index in range(len(scaled_set)):
        new_set = np.delete(scaled_set, index, 0) 
        hypervolume_of_new_set = hv.do(new_set)
        hypervolume_contribution = hypervolume - hypervolume_of_new_set
        hypervolume_contributions_list = np.array(hypervolume_contributions_list, dtype=np.float)
        hypervolume_contributions_list = np.append(hypervolume_contributions_list, hypervolume_contribution)
        
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
    
res = approximation_set
csfont = {'fontname':'Adobe Garamond pro'}
plt.figure(figsize=(7, 5), linewidth=20)
plt.scatter(res[:, 0], res[:, 1], s=50, facecolors='black', edgecolors='red', linewidths=2)
plt.title("Objective Space", fontsize=20, **csfont)
plt.show()
