import re
import subprocess
import os
import sys
import time
import itertools
import argparse



ssdict={"adsp":"75,37,3,48,0,0,0","mss":"75,37,3,0,0,0,0","slpi":"75,37,03,64,00,0,0","cdsp":"75,37,03,96,01,0,0","wpss":"75,37,03,160,0,0,0,0","spss":"not_applicable"}
    

def wait_and_root():
    os.system('adb wait-for-device')
    os.system('adb wait-for-device')
    os.system('adb root')
    os.system('adb wait-for-device')
    os.system('adb wait-for-device')
    print('Rooted')
    output=subprocess.check_output('adb remount')
    out=''.join(map(chr, output))    
    if 'remount succeeded' not in out:
        os.system('adb reboot')
        time.sleep(150)
        os.system('adb root')
        os.system('adb wait-for-device')
        os.system('adb wait-for-device')
  

    
def check_subsys_state():
    
    rp_subsys_names = subprocess.check_output('adb shell cat /sys/class/remoteproc/remoteproc*/name')
    rp_subsys_names = list(rp_subsys_names.decode("utf-8").split('\r\n'))
    
    
    for rproc_name in rp_subsys_names:
        for ss in subsystems:
            if rproc_name.find(ss) != -1:
               
                subsystem_crashed = False
                X=rp_subsys_names.index(rproc_name)
                cmd="adb shell cat /sys/class/remoteproc/remoteproc" + str(X) + "/state"
                
                
                print(cmd)
                os.system(cmd)
                
                state = subprocess.check_output(cmd)
                print(state)
                
                if state.find(b"running") == -1:
                    
                    subsystem_crashed = True
                         
                    
                if subsystem_crashed:
                    print("TEST FAIL")
                    timestr = time.strftime("%Y%m%d-%H%M%S")
                    filename = "dmesg1_"+timestr+".txt"
                    f = open(filename, "w")
                    subprocess.call(["adb", "shell",  "dmesg"], stdout=f)
                    os.system('adb shell \"echo c > /proc/sysrq-trigger\"')
                    os.system("adb reboot")
                    exit()
                
                else:
                    print("TEST PASS") 
                   
    if mode=="enabled" or mode=="inline" or setprop==True:
        print("Hello")
          
        output=subprocess.check_output("adb shell ls /data/vendor/ramdump/")
        out=''.join(map(chr, output))
        output=list(output.decode("utf-8").split('\r\n'))
                      
                            
        print(out)
        if "elf" in out:
            print("Dump collection successful")
                               
                            
        os.system('adb shell rm /data/vendor/ramdump/*.elf')
        subprocess.check_output("adb shell ls /data/vendor/ramdump/")
                               
    
    
def enable_coredump(mode):
    
    rp_subsys_names = subprocess.check_output('adb shell cat /sys/class/remoteproc/remoteproc*/name')
    rp_subsys_names = list(rp_subsys_names.decode("utf-8").split('\r\n'))
    if setprop == True:
        cmd = "adb shell setprop persist.vendor.ssr.enable_ramdumps 1"
        os.system(cmd)
        print(cmd)
        
        
        for rproc_name in rp_subsys_names:
            for ss in subsystems:
               
                    
                if rproc_name.find(ss) != -1:
                    
                    X = rp_subsys_names.index(rproc_name)
                    
                   
                    cmd = "adb shell \"echo enabled  > /sys/class/remoteproc/remoteproc" + str(X) + "/coredump\""
                    os.system(cmd)
                        
                    cmd = "adb shell cat /sys/class/remoteproc/remoteproc" + str(X) + "/coredump"
                        
                    os.system(cmd)
                    coredump = subprocess.check_output(cmd)
                    print("coredump = ",coredump)
       
    else:
        cmd='adb shell "echo 1 > /sys/module/qcom_ramdump/parameters/enable_dump_collection"'
        os.system(cmd)
        print(cmd)
        cmd="adb shell /vendor/bin/subsystem_ramdump &"
        output = subprocess.Popen(cmd, shell=False)
        
        


        for rproc_name in rp_subsys_names:
            for ss in subsystems:
         
                    
                if rproc_name.find(ss) != -1:
                    
                    X = rp_subsys_names.index(rproc_name)
                    
                    if mode=='enabled':
                        cmd = "adb shell \"echo enabled  > /sys/class/remoteproc/remoteproc" + str(X) + "/coredump\""
                        os.system(cmd)
                        print(cmd)
                        cmd = "adb shell cat /sys/class/remoteproc/remoteproc" + str(X) + "/coredump"
                        
                        os.system(cmd)
                        coredump = subprocess.check_output(cmd)
                        print("coredump = ",coredump)
                        if coredump.find(b"enabled") == -1:
                            print("coredump is not set to enabled, error in setting enabled")   
                            
                    if mode=='inline':
                        cmd = "adb shell \"echo inline  > /sys/class/remoteproc/remoteproc" + str(X) + "/coredump\""
                        os.system(cmd)
                        print(cmd)
                        cmd = "adb shell cat /sys/class/remoteproc/remoteproc" + str(X) + "/coredump"
                        
                        os.system(cmd)
                        coredump = subprocess.check_output(cmd)
                        print("coredump = ",coredump)
                        if coredump.find(b"inline") == -1:
                            print("coredump is not set to inline, error in setting inline")
                    
                    if mode=='disabled':
                        cmd = "adb shell \"echo disabled  > /sys/class/remoteproc/remoteproc" + str(X) + "/coredump\""
                        os.system(cmd)
                        print(cmd)
                        cmd = "adb shell cat /sys/class/remoteproc/remoteproc" + str(X) + "/coredump"
                        
                        os.system(cmd)
                        coredump = subprocess.check_output(cmd)
                        print("coredump = ",coredump)
                        if coredump.find(b"disabled") == -1:
                            print("coredump is not set to disabled, error in setting disabled")


def enable_recovery():
    
    if setprop == True:
        cmd = "adb shell setprop persist.vendor.ssr.restart_level ALL_ENABLE";
        output = subprocess.check_output(cmd)
        rp_subsys_names = subprocess.check_output('adb shell cat /sys/class/remoteproc/remoteproc*/name')
        rp_subsys_names = list(rp_subsys_names.decode("utf-8").split('\r\n'))
        
        
        for rproc_name in rp_subsys_names:
            for ss in subsystems:
         
                    
                if rproc_name.find(ss) != -1:
                    
                    X = rp_subsys_names.index(rproc_name)
                    
                    cmd = "adb shell cat /sys/class/remoteproc/remoteproc" + str(X) + "/recovery"
                   
                    os.system(cmd)
                    recovery = subprocess.check_output(cmd)
                    print("recovery = ",recovery)
                    
        
    else:
        
        
        rp_subsys_names = subprocess.check_output('adb shell cat /sys/class/remoteproc/remoteproc*/name')
        rp_subsys_names = list(rp_subsys_names.decode("utf-8").split('\r\n'))
        
        
        for rproc_name in rp_subsys_names:
            for ss in subsystems:
         
                    
                if rproc_name.find(ss) != -1:
                    
                    X = rp_subsys_names.index(rproc_name)
                    cmd="adb shell chmod 777 /sys/class/remoteproc/remoteproc" + str(X) + "/recovery"
                    
                    os.system(cmd)
                    cmd = "adb shell \"echo enabled  > /sys/class/remoteproc/remoteproc" + str(X) + "/recovery\""
                    print(cmd)
                    os.system(cmd)
                    cmd = "adb shell cat /sys/class/remoteproc/remoteproc" + str(X) + "/recovery"
                   
                    os.system(cmd)
                    recovery = subprocess.check_output(cmd)
                    print("recovery = ",recovery)
                    if recovery.find(b"enabled") == -1:
                        print("recovery is not set to enabled, error in setting enabled")
        

def perform_spss_ssr():
    os.system('adb shell /vendor/bin/spcom_smoke_test -t ssr')
    time.sleep(30)
    check_subsys_state()



def execute_pairwise_ssrs():
    
    sscommands_applicable=[]
    rp_subsys_names = subprocess.check_output('adb shell cat /sys/class/remoteproc/remoteproc*/name')
    rp_subsys_names = list(rp_subsys_names.decode("utf-8").split('\r\n'))
    for rproc_name in rp_subsys_names:
        for ss in subsystems:
            if rproc_name.find(ss) != -1:
                #sscommands_applicable.append(sscommands[rp_subsys_names.index(rproc_name)]) 
                sscommands_applicable.append(ssdict[ss])
    print(sscommands_applicable)         
    if "not_applicable" in sscommands_applicable:
        sscommands_applicable.remove("not_applicable")
        
    print(sscommands_applicable) 
    commands_list=[]
    
    for i in range(1,len(sscommands_applicable)+1):
        combinations=itertools.combinations(sscommands_applicable,i)
        commands_list+=combinations
        print(commands_list)   
        
    for i in commands_list:
        
        command='\" \" '.join(list(i))
        print(command)
        
           
        
        #os.system('adb shell export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/vendor/lib64/')
       
        cmd='adb shell /data/local/tmp/diag_callback_client ' + '\"' + command + '\"'
        
        print(cmd)
        
        print("executing pairwise ssrs")
        
        output = subprocess.check_output(cmd)
        
        time.sleep(40)
        check_subsys_state()
        
        
    
   
stability = False
functional = False

def main1():
    
    global iters        
    
    wait_and_root()

    failed_iterations = 0
    passed_iterations = 0
    
    target = subprocess.check_output('adb shell cat /sys/devices/soc0/machine')
    target = target.decode('utf-8').strip()
    print(target)
    
    
    
    sscommands_applicable=[]
    rp_subsys_names = subprocess.check_output('adb shell cat /sys/class/remoteproc/remoteproc*/name')
    rp_subsys_names = list(rp_subsys_names.decode("utf-8").split('\r\n'))
    
    for rproc_name in rp_subsys_names:
        for ss in subsystems:
            if rproc_name.find(ss) != -1:
                 
                sscommands_applicable.append(ssdict[ss])
    print(sscommands_applicable)   
    if "not_applicable" in sscommands_applicable:
        sscommands_applicable.remove("not_applicable")
    
    enable_recovery()
    enable_coredump(mode)
    
    
      
    os.system('adb push \\\\cube\\kernel1\\hari\\remoteproc\\diag_callback_client /data/local/tmp')
    os.system('adb shell chmod +x /data/local/tmp/diag_callback_client')
    

      
    if test_type=='functional':
        
        if "spss" in subsystems:
                perform_spss_ssr()
        
        for i in sscommands_applicable:
            
            cmd='adb shell /data/local/tmp/diag_callback_client \"' + i + "\""
            print(cmd)
            output = subprocess.check_output(cmd)
            
            time.sleep(30)
            check_subsys_state()
   
    if test_type=='stability':
        
            
        if(iters==0):
            iters=2
         
        
        for i in range(1,iters+1):
            if "spss" in subsystems:
                perform_spss_ssr()
            # os.system('adb shell /vendor/bin/spcom_smoke_test -t ssr')
            time.sleep(10)
            

            execute_pairwise_ssrs()
            check_subsys_state()
            print("iteration: ",i)

    if test_type=='reboot':
        
        if(iters==0):
            iters=100
            
        for i in range(1,iters+1):
            os.system('adb reboot')
            time.sleep(150)
            wait_and_root()
            check_subsys_state()

          
if __name__ == "__main__":
    
    
    parser = argparse.ArgumentParser(description='remoteproc')
    parser.add_argument('--test_type', dest='test_type', type=str, help='type_of_test',default='functional')
    parser.add_argument('--subsystems', dest='subsystems', type=str, help='list_of_subsystems',default='adsp')
    parser.add_argument('--mode', dest='mode', type=str, help='coredump mode',default='disabled')
    parser.add_argument('--iterations', dest='iterations', type=int, help='iterations',default=0)
    parser.add_argument('--setprop', dest='setprop', type=bool, help='setprop enabling',default=False)
    args = parser.parse_args()
    test_type=args.test_type
    subsystems=args.subsystems
    setprop=args.setprop
    mode=args.mode
    iters=args.iterations
    
    subsystems=subsystems.split(',')    
    
    print(test_type)
    print(subsystems)
    print(mode)   
    
    main1()
    
