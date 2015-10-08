#!/usr/bin/env ganga
import os,sys
import subprocess
runcarddir = '/mt/home/morgan/NNLOJET/driver/grid'


try:
    prodwarm = sys.argv[1]
except IndexError:
    prodwarm = 'production'

prodwarm = 'production'
mode = 'Dirac'

if prodwarm == 'warmup':
    multithread=True
    print "SETTING TO MULTITHREADED RUNNING"
    nruns = 1
else:
    multithread=False
    print "ASSUMING THIS IS A PRODUCTION RUN"
    print "SETTING TO SINGLE THREADED RUNNING"
    nruns = 100

if multithread and mode != 'ARC':
    print "Error: multithreading is not supported for backends other than ARC"
    exit()


seedList = [str(i) for i in range(nruns,2*nruns+1)]


argList = []

runcards = os.listdir(runcarddir)

cmd = ['lfc-ls','output']

output = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]


for seed in seedList:
    for r in runcards:
        if '~' not in r:
            arg = ' -run '+r+' -iseed '+seed
            checkarg = r+'-'+seed
            if checkarg not in output:
                argList.append([arg,r,seed,multithread])


print "Number of jobs: ", len(argList)

argSplit = ArgSplitter(args = argList)

j0 = Job()
j0.application = Executable(exe=File('/mt/home/morgan/working/ganga.py'))

if mode == 'ARC':
    j0.backend=ARC()
    j0.backend.CE='ce2.dur.scotgrid.ac.uk'
elif mode == 'Dirac':
    j0.backend=Dirac()
    j0.backend.settings['BannedSites']=["LCG.UKI-NORTHGRID-MAN-HEP.uk","LCG.UKI-LT2-IC-HEP.uk","LCG.EFDA-JET.xx"]
else:
    print "Invalid backend: ", mode
    exit()

if multithread:
    j0.backend.requirements.other = ['(count=16)','(countpernode=16)']

j0.splitter=argSplit
j0.submit()
