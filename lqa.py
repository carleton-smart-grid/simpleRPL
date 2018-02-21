# Jason Van Kerkhoven
# 20-02-2018

# Arguments:
#   -v OR --verbose         Toggle verbosity on
#   -c OR --count           Number of broadcast pings to send
#   -t OR --threshold       Minimum acceptable LQR (link quality rating)
#   -i OR --interval        Time between broadcasts (period)

# generic imports
import re
import sys
from subprocess import Popen, PIPE, STDOUT


# global variables (forgive my sin)
verbose = False


# verbose print
def printv(string):
    if verbose:
        print(string)


# run on execution
if __name__ == "__main__":
    # declaring program constants
    BROADCAST = 'ff02::1'
    IFACE = 'wlp3s0'
    FILE_NAME = 'passinglinks.cfg'


    # declaring program defaults
    threshold = 0.5
    count = 5
    interval = 1.0

    # parse arguments
    flags = sys.argv
    flags.pop(0)
    while (len(flags) > 0):
        flag = flags.pop(0)
        # toggle verbosity
        if (flag == '-v' or flag == '--verbose'):
            verbose = True
        # set threshold
        elif (flag == '-t' or flag == '--threshold'):
            threshold = float(flags.pop(0))
        # set count
        elif (flag == '-c' or flag == '--count'):
            count = int(flags.pop(0))
        # set interval
        elif (flag == '-i' or flag == '--interval'):
            interval = float(flags.pop(0))
        # error
        else:
            print('Unknown flag! Exiting...')
            sys.exit()


    # broadcast ping in shell, pipe output to program
    printv('Broadcasting...')
    cmd = 'sudo ping6 ' + BROADCAST + ' -I ' + IFACE + ' -c ' + str(count) + ' -i ' + str(interval)
    pipe = Popen([cmd], shell=True, stdout=PIPE, stderr=PIPE)
    shellOut, stderr = pipe.communicate()
    printv('Broadcast complete!')

    # split and parse into just MACs who responded
    shellOut = shellOut.decode('utf-8')
    echos = re.compile('fe80+::\S+')
    echos = echos.findall(shellOut)

    # tally the number of responses per MAC
    tally = {}
    if (len(echos) > 0):
        for mac in echos:
            if (mac in tally):
                tally[mac] += 1
            else:
                tally[mac] = 1

    # compute link quality rating for each echo-responder, save those over threshold
    file = open(FILE_NAME, 'w')
    printv('-------------------------------------')
    for key,value in tally.items():
        p = value/count
        if (p >= threshold):
            printv('\u001b[32m[ACCEPT]\u001b[0m   ' + str(key) + ' w/ ' + format(p*100, '.2f') + '% LQR')
            file.write(str(key) + '\n')
        else:
            printv('\u001b[31m[REJECT]\u001b[0m   ' + str(key) + ' w/ ' + format(p*100, '.2f') + '% LQR')
    printv('-------------------------------------')
