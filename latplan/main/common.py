import os
import os.path
import glob
import sys
import hashlib
import numpy as np
import latplan.model
import latplan.util.stacktrace
from latplan.util.tuning import simple_genetic_search, parameters, nn_task, reproduce, load_history, loadsNetWithWeights
from latplan.util        import curry
#from ../util import ensure_list, NpEncoder, gpu_info
import matplotlib.pyplot as plt
#np.set_printoptions(threshold=sys.maxsize)

################################################################
# globals

args     = None
sae_path = None

################################################################
# command line parsing

import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)


# 
# RawDescriptionHelpFormatter
# ArgumentDefaultsHelpFormatter


parser.add_argument(
    "mode",
    help=(
        "A string which contains mode substrings."
        "\nRecognized modes are:"
        "\n" 
        "\n   learn     : perform the training with a hyperparameter tuner. Results are stored in samples/[experiment]/logs/[hyperparameter]."
        "\n               If 'learn' is not specified, it attempts to load the stored weights."
        "\n   plot      : produce visualizations"
        "\n   dump      : dump the csv files necessary for producing the PDDL models"
        "\n   summary   : perform extensive performance evaluations and collect the statistics, store the result in performance.json"
        "\n   debug     : debug training limited to epoch=2, batch_size=100. dataset is truncated to 200 samples"
        "\n   reproduce : train the best hyperparameter so far three times with different random seeds. store the best results."
        "\n   iterate   : iterate plot/dump/summary commands above over all hyperparmeters that are already trained and stored in logs/ directory."
        "\n"
        "\nFor example, learn_plot_dump contains 'learn', 'plot', 'dump' mode."
        "\nThe separater does not matter because its presense is tested by python's `in` directive, i.e., `if 'learn' in mode:` ."
        "\nTherefore, learnplotdump also works."))


subparsers = parser.add_subparsers(
    title="subcommand",
    metavar="subcommand",
    required=True,
    description=(
        "\nA string which matches the name of one of the dataset functions in latplan.main module."
        "\n"
        "\nEach task has a different set of parameters, e.g.,"
        "\n'puzzle' has 'type', 'width', 'height' where 'type' should be one of 'mnist', 'spider', 'mandrill', 'lenna',"
        "\nwhile 'lightsout' has 'type' being either 'digital' and 'twisted', and 'size' being an integer."
        "\nSee subcommand help."))

def add_common_arguments(subparser,task,objs=False):
    subparser.set_defaults(task=task)
    subparser.add_argument(
        "num_examples",
        default=5000,
        type=int,
        help=(
            "\nNumber of data points to use. 90%% of this number is used for training, and 5%% each for validation and testing."
            "\nIt is assumed that the user has already generated a dataset archive in latplan/puzzles/,"
            "\nwhich contains a larger number of data points using the setup-dataset script provided in the root of the repository."))
    subparser.add_argument(
        "aeclass",
        help=
        "A string which matches the name of the model class available in latplan.model module.\n"+
        "It must be one of:\n"+
        "\n".join([ " "*4+name for name, cls in vars(latplan.model).items()
                    if type(cls) is type and \
                    issubclass(cls, latplan.network.Network) and \
                    cls is not latplan.network.Network
                ])
    )
    if objs:
        subparser.add_argument("location_representation",
                               nargs='?',
                               choices=["bbox","coord","binary","sinusoidal","anchor"],
                               default="coord",
                               help="A string which specifies how to convert/encode the location in the dataset. See documentations for normalize_transitions_objects")
        subparser.add_argument("randomize_location",
                               nargs='?',
                               type=bool,
                               default=False,
                               help="A boolean which specifies whether we randomly translate the environment globally. See documentations for normalize_transitions_objects")
    subparser.add_argument("comment",
                           nargs='?',
                           default="",
                           help="A string which is appended to the directory name to label each experiment.")
    return



def main(parameters={}):
    print("22")
    import latplan.util.tuning
    latplan.util.tuning.parameters.update(parameters)
    print("33")
    import sys
    global args, sae_path
    args = parser.parse_args()
    print("44")
    task = args.task
    delattr(args,"task")
    latplan.util.tuning.parameters.update(vars(args))
    print("55")
    sae_path = "_".join(sys.argv[2:])
    try:
        task(args)
    except:
        latplan.util.stacktrace.format()


################################################################
# procedures for each mode

def plot_autoencoding_image(ae,transitions,label):
    if 'plot' not in args.mode:
        return

    if hasattr(ae, "plot_transitions"):
        transitions = transitions[:6]
        ae.plot_transitions(transitions, ae.local(f"transitions_{label}"),verbose=True)
    else:
        transitions = transitions[:3]
        states = transitions.reshape((-1,*transitions.shape[2:]))
        ae.plot(states, ae.local(f"states_{label}"),verbose=True)

    return




def plot_autoencoding_imageBIS(ae,transitions,label): # Aymeric [16/06/2022]

    print("ae.local(transitions_")
    print(ae.local(f"transitions_{label}"))

    ae.plot_transitionsBis(transitions, ae.local(f"transitions_{label}"),verbose=True)
  
    return




def testCatVars(ae,transitions,label): # Aymeric [16/06/2022]

    print("ae.local(transitions_")
    print(ae.local(f"transitions_{label}"))

    ae.testCat_vars(transitions, ae.local(f"transitions_{label}"),verbose=True)
  
    return



# BACK UP
# def plot_autoencoding_imageBIS(ae,transitions,label): # Aymeric [14/06/2022]

#     print("ae.local(transitions_")
#     print(ae.local(f"transitions_{label}"))

#     if hasattr(ae, "plot_transitions"):
#         transitions = transitions[:6]
#         ae.plot_transitions(transitions, ae.local(f"transitions_{label}"),verbose=True)
#     else:
#         transitions = transitions[:3]
#         states = transitions.reshape((-1,*transitions.shape[2:]))
#         ae.plot(states, ae.local(f"states_{label}"),verbose=True)

#     return



def dump_all_actions(ae,configs,trans_fn,name = "all_actions.csv",repeat=1):
    if 'dump' not in args.mode:
        return
    l     = len(configs)
    batch = 5000
    loop  = (l // batch) + 1
    print(ae.local(name))
    with open(ae.local(name), 'wb') as f:
        for i in range(repeat):
            for begin in range(0,loop*batch,batch):
                end = begin + batch
                print((begin,end,len(configs)))
                transitions = trans_fn(configs[begin:end])
                pre, suc    = transitions[0], transitions[1]
                pre_b       = ae.encode(pre,batch_size=1000).round().astype(int)
                suc_b       = ae.encode(suc,batch_size=1000).round().astype(int)
                actions     = np.concatenate((pre_b,suc_b), axis=1)
                np.savetxt(f,actions,"%d")


def dump_actions(ae,transitions,name = "actions.csv",repeat=1):
    if 'dump' not in args.mode:
        return
    print(ae.local(name))
    ae.dump_actions(transitions,batch_size = 1000)


def dump_actionsBIS(ae,transitions,name = "actions.csv",repeat=1):
    print(ae.local(name))
    ae.dump_actions(transitions,batch_size = 1000)


def dump_all_states(ae,configs,states_fn,name = "all_states.csv",repeat=1):
    if 'dump' not in args.mode:
        return
    l     = len(configs)
    batch = 5000
    loop  = (l // batch) + 1
    print(ae.local(name))
    with open(ae.local(name), 'wb') as f:
        for i in range(repeat):
            for begin in range(0,loop*batch,batch):
                end = begin + batch
                print((begin,end,len(configs)))
                states   = states_fn(configs[begin:end])
                states_b = ae.encode(states,batch_size=1000).round().astype(int)
                np.savetxt(f,states_b,"%d")


def dump_states(ae,states,name = "states.csv",repeat=1):
    if 'dump' not in args.mode:
        return
    print(ae.local(name))
    with open(ae.local(name), 'wb') as f:
        for i in range(repeat):
            np.savetxt(f,ae.encode(states,batch_size = 1000).round().astype(int),"%d")


def dump_code_unused():
    # This code is not used. Left here for copy-pasting in the future.
    if False:
        dump_states      (ae,all_states,"all_states.csv")
        dump_all_actions (ae,all_transitions_idx,
                          lambda idx: all_states[idx.flatten()].reshape((len(idx),2,num_objs,-1)).transpose((1,0,2,3)))


def train_val_test_split(x):
    train = x[:int(len(x)*0.9)]
    val   = x[int(len(x)*0.9):int(len(x)*0.95)]
    test  = x[int(len(x)*0.95):]
    return train, val, test

keys_to_ignore = ["time_start","time_duration","time_end","HOSTNAME","LSB_JOBID","gpu","mean","std","hash"]


def _key(config):
    def tuplize(x):
        if isinstance(x,list):
            return tuple([tuplize(y) for y in x])
        else:
            return x
    return tuple( tuplize(v) for k, v in sorted(config.items())
                  if k not in keys_to_ignore)

def _add_misc_info(config):
    for key in ["HOSTNAME", "LSB_JOBID"]:
        try:
            config[key] = os.environ[key]
        except KeyError:
            pass
    # try:
    #     config["gpu"] = gpu_info()[0]["name"]
    # except:
    #     # not very important
    #     pass


    config["hash"] = hashlib.md5(bytes(str(_key(config)),"utf-8")).hexdigest()

    print("config[hash]")
    print(config["hash"])

    return


def run(path,transitions,extra=None):
    train, val, test = train_val_test_split(transitions)

    def postprocess(ae):
        show_summary(ae, train, test)
        plot_autoencoding_image(ae,train,"train")
        plot_autoencoding_image(ae,test,"test")
        dump_actions(ae,transitions)
        return ae

    def report(net,eval):
        try:
            postprocess(net)
            if extra:
                extra(net)
        except:
            latplan.util.stacktrace.format()
        return


    if 'learn' in args.mode:



        parameters['batch_size'] = 400
        parameters['N'] = 300
        parameters['beta_d'] = 10
        parameters['beta_z'] = 10
        parameters['aae_depth'] = 2 # see Tble 9.1, PAS SUR DE LA SIGNIFICATION l?? !!!
        parameters['aae_activation'] = 'relu' # see 9.2

        parameters['aae_width'] = 1000 # not sure, see 9.1 fc(1000) and fc(6000)

        parameters['max_temperature'] = 5.0

        parameters['conv_depth'] = 3 # dans 9.1, encode ET decode ont chacun 3 Conv

        parameters['conv_pooling'] = 1 # = train_common.py

        parameters['conv_kernel'] = 5 # = train_common.py

        parameters['conv_per_pooling']  = 1

        parameters['conv_channel']  = 32
        parameters['conv_channel_increment'] = 1

        parameters['eff_regularizer'] = None

        parameters['A'] = 6000 # max # of actions

        # nn_task(network, path, train_in, train_out, val_in, val_out, parameters, resume=False) single iteration of NN training

        print(latplan.model.get(parameters["aeclass"]))
        exit()

        task = curry(nn_task, latplan.model.get(parameters["aeclass"]), path, train, train, val, val)

        _add_misc_info(parameters)

        task(parameters)


        exit()
        
        # simple_genetic_search(
        #     curry(nn_task, latplan.model.get(parameters["aeclass"]),
        #           path,
        #           train, train, val, val), # noise data is used for tuning metric
        #     parameters,
        #     path,
        #     limit              = 100,
        #     initial_population = 100,
        #     population         = 100,
        #     report             = report,
        # )



    if 'testing' in args.mode: # aymeric [13/06/2022]

        parameters['batch_size'] = 400
        parameters['N'] = 300
        parameters['beta_d'] = 10
        parameters['beta_z'] = 10
        parameters['aae_depth'] = 2 # see Tble 9.1, PAS SUR DE LA SIGNIFICATION l?? !!!
        parameters['aae_activation'] = 'relu' # see 9.2

        parameters['aae_width'] = 1000 # not sure, see 9.1 fc(1000) and fc(6000)

        parameters['max_temperature'] = 5.0

        parameters['conv_depth'] = 3 # dans 9.1, encode ET decode ont chacun 3 Conv

        parameters['conv_pooling'] = 1 # = train_common.py

        parameters['conv_kernel'] = 5 # = train_common.py

        parameters['conv_per_pooling']  = 1

        parameters['conv_channel']  = 32
        parameters['conv_channel_increment'] = 1

        parameters['eff_regularizer'] = None

        parameters['A'] = 6000 # max # of actions


        parameters["optimizer"] = "radam"


        #print(latplan.model.get(parameters["aeclass"]))
        #print(type(latplan.model.get(parameters["aeclass"])))


        # loadsNetWithWeights (renvoie net, error) dans tunning.py
        # qui appel loadsModelAndWeights de network.py
        task = curry(loadsNetWithWeights, latplan.model.get(parameters["aeclass"]), path, train, train, val, val)

        #print(type(train))
        #print(train.shape)
        #print(train[0].shape)
        #print(train[0][0]) # transition 0/36000, image 0/1

        _add_misc_info(parameters)


        # CHOIX DU NETWORK
        parameters['hash'] = "8dd53f4ca49f65444250447a16903f86"


        net, error = task(parameters)


        #print("ae !!!")
        #print(ae)

        # plt.figure(figsize=(6,6))
        # plt.imshow(train[0][0],interpolation='nearest',cmap='gray') # transition 0, image 0
        # plt.savefig("im1.png") #
        # plt.figure(figsize=(6,6))
        # plt.imshow(train[0][1],interpolation='nearest',cmap='gray') # transition 0, image 1
        # plt.savefig("im2.png") #

        print("THE SHAPE")
        print(train.shape)

        #Plot la 1ere transition de train (train[:1]) les plots sont dans samples/puzzle.../logs/8dd.....
        plot_autoencoding_imageBIS(net, train[:1], "train") #
        #testCatVars(net, train, "train")

        exit()


    if 'dump_actions' in args.mode: # Aymeric [28-06-22]


        # dump_actions 3 dans model.py

        # puis _dump_actions_prologue dans model.py

        # puis dump_preconditions 2

        # puis save_array dans network.py

        parameters['batch_size'] = 400
        parameters['N'] = 300
        parameters['beta_d'] = 10
        parameters['beta_z'] = 10
        parameters['aae_depth'] = 2 # see Tble 9.1, PAS SUR DE LA SIGNIFICATION l?? !!!
        parameters['aae_activation'] = 'relu' # see 9.2
        parameters['aae_width'] = 1000 # not sure, see 9.1 fc(1000) and fc(6000)
        parameters['max_temperature'] = 5.0
        parameters['conv_depth'] = 3 # dans 9.1, encode ET decode ont chacun 3 Conv
        parameters['conv_pooling'] = 1 # = train_common.py
        parameters['conv_kernel'] = 5 # = train_common.py
        parameters['conv_per_pooling']  = 1
        parameters['conv_channel']  = 32
        parameters['conv_channel_increment'] = 1
        parameters['eff_regularizer'] = None
        parameters['A'] = 6000 # max # of actions
        parameters["optimizer"] = "radam"
        task = curry(loadsNetWithWeights, latplan.model.get(parameters["aeclass"]), path, train, train, val, val)
        _add_misc_info(parameters)
        parameters['hash'] = "8dd53f4ca49f65444250447a16903f86"

        net, error = task(parameters)

        dump_actionsBIS(net,transitions)

        exit()

    if 'resume' in args.mode:
        simple_genetic_search(
            lambda parameters: nn_task(latplan.model.get(parameters["aeclass"]), path, train, train, val, val, parameters, resume=True),
            parameters,
            path,
            limit              = 100,
            initial_population = 100,
            population         = 100,
            report             = report,
        )

    if 'debug' in args.mode:
        print("debug run. removing past logs...")
        for _path in glob.glob(os.path.join(path,"*")):
            if os.path.isfile(_path):
                os.remove(_path)
        parameters["epoch"]=1
        parameters["batch_size"]=100
        train, val = train[:200], val[:200]
        simple_genetic_search(
            curry(nn_task, latplan.model.get(parameters["aeclass"]),
                  path,
                  train, train, val, val), # noise data is used for tuning metric
            parameters,
            path,
            limit              = 1,
            initial_population = 1,
            population         = 1,
            report             = report,
        )

    if 'reproduce' in args.mode:   # reproduce the best result from the grid search log
        reproduce(
            curry(nn_task, latplan.model.get(parameters["aeclass"]),
                  path,
                  train, train, val, val), # noise data is used for tuning metric
            path,
            report      = report,
        )

    if 'iterate' in args.mode:
        open_list, _ = load_history(path)
        topk = open_list[:10]
        topk_dirnames = [
            os.path.join(path,"logs",elem[1]["hash"])
            for elem in topk
        ]
        print(f"iterating mode {args.mode} for all weights stored under logs")
        for path in topk_dirnames:
            postprocess(latplan.model.load(path))



def show_summary(ae,train,test):
    if 'summary' in args.mode:
        ae.summary()
        ae.report(train, test_data = test, train_data_to=train, test_data_to=test)


