
def build_header():
    return (
    "#!/bin/bash\n"
    "\n"
    )

GEM5_SE = 0
GEM5_SE_HT = 1
GEM5_FS = 2
GEM5_FS_HT = 3

def build_gem5(sim_type, env_gem5_bin, env_gem5_src):
    if sim_type == GEM5_FS_HT:
        return (
        ""+env_gem5_bin+" \\\n"
        " --outdir=$2 \\\n"
        " --debug-flags=DRAM \\\n"
        " --debug-file=traces.out.gz \\\n"
        " "+env_gem5_src+"/configs/example/fsHT.py \\\n"
        " --script=$1 \\\n"
        )
    else:
        raise Exception("Invalid config")


def listnize(the_list,func,idx):
    aux = ""
    for x in the_list:
        aux = aux + func(x)[idx] + ";"
    return aux[:-1]

def get_nums(num_type):
    return (str(num_type),None)

def build_cpu_cache_conf_privL2(core_type_list, num_cores_per_type):
    return(
    " --tech-node=28 \\\n"
    " --cpu-type arm_detailed \\\n"
    " --num-cpus-types "+str(len(core_type_list))+" \\\n"
    " --num-cpus-eachtype \""+listnize(num_cores_per_type,get_nums,0)+"\" \\\n"
    " --caches \\\n"
    " --num-l2caches \""+listnize(num_cores_per_type,get_nums,0)+"\" \\\n"
    )

def build_cpu_cache_conf_sharedL2(core_type_list, num_cores_per_type):
    return(
    " --tech-node=28 \\\n"
    " --cpu-type arm_detailed \\\n"
    " --num-cpus-types "+str(len(core_type_list))+" \\\n"
    " --num-cpus-eachtype \""+listnize(num_cores_per_type,get_nums,0)+"\" \\\n"
    " --caches \\\n"
    " --num-l2caches \""+";".join("1" for x in core_type_list)+"\" \\\n"
    )

FREQ_3000MHz = 0
FREQ_2000MHz = 1
FREQ_1900MHz = 2
FREQ_1800MHz = 3
FREQ_1700MHz = 4
FREQ_1600MHz = 5
FREQ_1500MHz = 6
FREQ_1400MHz = 7
FREQ_1300MHz = 8
FREQ_1200MHz = 9
FREQ_1100MHz = 10
FREQ_1000MHz = 11
FREQ_0900MHz = 12
FREQ_0800MHz = 13
FREQ_0700MHz = 14
FREQ_0600MHz = 15
FREQ_0500MHz = 16

def get_freq(freq):
    if freq == FREQ_3000MHz:
        return ("3000MHz","1.3V")
    elif freq == FREQ_2000MHz:
        return ("2000MHz","1.0V")
    elif freq == FREQ_1900MHz:
        return ("1900MHz","1.0V")
    elif freq == FREQ_1800MHz:
        return ("1800MHz","0.9V")
    elif freq == FREQ_1700MHz:
        return ("1700MHz","0.9V")
    elif freq == FREQ_1600MHz:
        return ("1600MHz","0.8V")
    elif freq == FREQ_1500MHz:
        return ("1500MHz","0.8V")
    elif freq == FREQ_1400MHz:
        return ("1400MHz","0.75V")
    elif freq == FREQ_1300MHz:
        return ("1300MHz","0.75V")
    elif freq == FREQ_1200MHz:
        return ("1200MHz","0.75V")
    elif freq == FREQ_1100MHz:
        return ("1100MHz","0.7V")
    elif freq == FREQ_1000MHz:
        return ("1000MHz","0.7V")
    elif freq == FREQ_0900MHz:
        return ("0900MHz","0.7V")
    elif freq == FREQ_0800MHz:
        return ("0800MHz","0.65V")
    elif freq == FREQ_0700MHz:
        return ("0700MHz","0.65V")
    elif freq == FREQ_0600MHz:
        return ("0600MHz","0.6V")
    elif freq == FREQ_0500MHz:
        return ("0500MHz","0.6V")
    else:
        raise Exception("Invalid frequency")

def build_freqs(freq_list):
    return (
    " --cpu-clock \""+listnize(freq_list,get_freq,0)+"\" \\\n"
    " --cpu-voltage \""+listnize(freq_list,get_freq,1)+"\" \\\n"
    )


CORE_HUGE = 0
CORE_BIG = 1
CORE_MEDIUM = 2
CORE_LITTLE = 3
CORE_EXYNOS_A15 = 4
CORE_EXYNOS_A07 = 5

def get_core(core_type):
    if core_type == CORE_HUGE:
        return ("huge","8","32","32","64","192","256","256","2048","8192","8192","4096","16","64kB", "2", "arm_detailed")
    elif core_type == CORE_BIG:
        return ("big","4","16","16","32","128","128","128","1024","4096","4096","2048","16","32kB", "2", "arm_detailed")
    elif core_type == CORE_MEDIUM:
        return ("medium","2","8","8","16","64","64","64","512","2048","2048","1024","16","16kB", "2", "arm_detailed")
    elif core_type == CORE_LITTLE:
        return ("little","1","8","8","16","64","64","64","512","2048","2048","1024","16","8kB", "1", "arm_detailed")
    elif core_type == CORE_EXYNOS_A15:
        return ("exynosA15","4","16","16","48","60","90","256","1024","4096","4096","4096","48","32kB", "2", "arm_detailed")
    elif core_type == CORE_EXYNOS_A07:
        return ("exynosA07","1", "8", "8","16", "0", "0",  "0",   "0", "256", "256", "256", "8","32kB", "2", "MinorCPU")
    else:
        raise Exception("Invalid core type:", core_type)

def build_cores(core_type_list):
    return (
    " --cpus-type-names \""+listnize(core_type_list,get_core,-1)+"\" \\\n"
    " --cpu-pipeline-width \""+listnize(core_type_list,get_core,1)+"\" \\\n"
    " --cpu-LQentries \""+listnize(core_type_list,get_core,2)+"\" \\\n"
    " --cpu-SQentries \""+listnize(core_type_list,get_core,3)+"\" \\\n"
    " --cpu-IQentries \""+listnize(core_type_list,get_core,4)+"\" \\\n"
    " --cpu-ROBentries \""+listnize(core_type_list,get_core,5)+"\" \\\n"
    " --cpu-numPhysIntRegs \""+listnize(core_type_list,get_core,6)+"\" \\\n"
    " --cpu-numPhysFloatRegs \""+listnize(core_type_list,get_core,7)+"\" \\\n"
    " --cpu-localPredictorSize \""+listnize(core_type_list,get_core,8)+"\" \\\n"
    " --cpu-globalPredictorSize \""+listnize(core_type_list,get_core,9)+"\" \\\n"
    " --cpu-choicePredictorSize \""+listnize(core_type_list,get_core,10)+"\" \\\n"
    " --cpu-BTBEntries \""+listnize(core_type_list,get_core,11)+"\" \\\n"
    " --cpu-RASSize \""+listnize(core_type_list,get_core,12)+"\" \\\n"
    " --l1i-size \""+listnize(core_type_list,get_core,13)+"\" \\\n"
    " --l1i-assoc \""+listnize(core_type_list,get_core,14)+"\" \\\n"
    )


CACHE_HUGE = 0
CACHE_BIG = 1
CACHE_MEDIUM = 2
CACHE_LITTLE = 3
CACHE_EXYNOS_A15 = 4
CACHE_EXYNOS_A07 = 5

def get_cache(cache_type):
    if cache_type == CACHE_HUGE:
        return ("huge","64kB","2","1024kB","8")
    elif cache_type == CACHE_BIG:
        return ("big","32kB","2","512kB","8")
    elif cache_type == CACHE_MEDIUM:
        return ("medium","16kB","2","256kB","4")
    elif cache_type == CACHE_LITTLE:
        return ("little","8kB","1","64kB","4")
    elif cache_type == CACHE_EXYNOS_A15:
        return ("exynosA15","32kB","2","2048kB","16")
    elif cache_type == CACHE_EXYNOS_A07:
        return ("exynosA07","32kB","4","512kB","8")
    else:
        raise Exception("Invalid cache type")

def build_caches(cache_type_list):
    return (
    " --l1d-size \""+listnize(cache_type_list,get_cache,1)+"\" \\\n"
    " --l1d-assoc \""+listnize(cache_type_list,get_cache,2)+"\" \\\n"
    " --l2-size \""+listnize(cache_type_list,get_cache,3)+"\" \\\n"
    " --l2-assoc \""+listnize(cache_type_list,get_cache,4)+"\" \\\n"
    )


def build_kernel(kernel_image,disk_image):
    return (
    " --kernel="+kernel_image+" \\\n"
    " --disk-image="+disk_image+" \\\n"
    )

def build_mems_final(mem_size, mem_freq):
    return (
    " --mem-size={} \\\n".format(mem_size) +
    " --sys-clock={} \\\n".format(mem_freq)
    )
def build_tail():
    return (" -r 1 --restore-with-cpu arm_detailed")


def build_conf(sim_type, env_gem5_bin, env_gem5_src, core_type_list, cache_type_list, num_cores_per_type,freq_list,kernel_image,disk_image,mem_size, mem_freq):
    return build_header() + build_gem5(sim_type, env_gem5_bin, env_gem5_src) + build_cpu_cache_conf_sharedL2(core_type_list, num_cores_per_type) + build_freqs(freq_list) + build_cores(core_type_list) + build_caches(cache_type_list) + build_kernel(kernel_image,disk_image) + build_mems_final(mem_size, mem_freq)+build_tail()






