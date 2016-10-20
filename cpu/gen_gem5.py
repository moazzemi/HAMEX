#!/usr/bin/python

from __future__ import print_function
from os import listdir, makedirs
from os.path import isfile, join, basename, splitext, dirname
from shutil import copytree, copyfile
from global_conf import *
import gem5_conf
import stat

gem5_confs = []
gem5_confs_names = []

script_jobs = []
dest_dir = os.path.join(output_dir, "run_scripts")
gem5_script_name = "run_gem5"

def get_cpt_name(arch_dir):
	return "cpt-" + arch_dir

def make_conf_multi_core(core_types, cache_types, freqs, num_cores):
    if len(core_types) != len(num_cores):
        raise ValueError("core_types and num_cores don't match")
    return ("_".join([confs.get_core(core)[0] for core in core_types])+"Core_"+"_".join([confs.get_cache(cache_type)[0] for cache_type in cache_types])+"Cache_"+"_".join([confs.get_freq(freq)[0] for freq in freqs]),
            confs.build_conf(sim_type, env_gem5_bin, env_gem5_src, core_types, cache_types, num_cores, freqs, kernel_image,disk_image,mem_size, sys_clock))

def append_conf(c):
    gem5_confs_names.append(c[0])
    gem5_confs.append(c[1])

    """
        FIXME: We don't support creation of checkpoint of each configuration automatically
        Hence, we do a sanity check here to see if the checkpoint exsits.
    """
    if os.path.isdir(get_cpt_name(c[0])) == False:
        raise ValueError("Checkpoint dir doesn't exist for " + c[0])


# Generate configs middle and corner cases first
def gen_conf_files(con_list):
    config_path = con_list[0]
    config_file = con_list[1]
    gem5_script = con_list[2]
    rcs_src = con_list[3]
    rcs_dest = con_list[4]

    benchname = basename(rcs_dest).split(".")[0]
    arch_dir = basename(dirname(rcs_dest))
    sh_dest = os.path.splitext(rcs_dest)[0]+'.sh'
    output_path = join(output_dir, arch_dir)

    with open(config_file, "w+") as text_file:
        text_file.write(gem5_script)
    st = os.stat(config_file)
    os.chmod(config_file, st.st_mode | stat.S_IEXEC)

    copyfile(rcs_src, rcs_dest)

    # Create necessary directories

    # copy checkpoint dir for current benchmark with current arch
    cpt_dir = get_cpt_name(arch_dir)
    cpt_dir_dest = join(output_path, cpt_dir + "-" + benchname)
    try:
        copytree(cpt_dir, cpt_dir_dest)
    except:
        pass

    with open(sh_dest, "w+") as job_sh:
        job_sh.write("export M5_SRC=" + env_gem5_src + "\n")
    	#echo -e 'export M5_PATH='$M5_PATH >>  $RCS_JOB_SCRIPT
        #M5_PATH=$M5_SRC/full-system
    	job_sh.write("export GEM5_ARM=" + env_gem5_bin + "\n")
    	job_sh.write("\n")
        job_sh.write("{run_gem5} {rcs} {cpt_dir} 1>>{rcs_stdout} 2>>{rcs_stderr}".format(
            run_gem5 = config_file,
            rcs = rcs_dest,
            cpt_dir = cpt_dir_dest,
            rcs_stdout = join(config_path, benchname + ".out"),
            rcs_stderr = join(config_path, benchname + ".err")
            ));
    	job_sh.write("\n")
    script_jobs.append(sh_dest)

def build_script_gem5():
    #
    # Add all combinations of CPU architectures
    #
    for f1, f2 in zip(g_freq_list[0], g_freq_list[1]):
        append_conf(make_conf_multi_core(g_base_core_conf, g_base_cache_conf, [f1, f2], g_num_cores))

    config_list_multi = []

    for conf in range(0,len(gem5_confs)):
        config_path = join(dest_dir, gem5_confs_names[conf])
        config_file = join(config_path, gem5_script_name)
        gem5_script = gem5_confs[conf]

        rcs_list = []
        rcs_list_orig = []

        tmp_list = [f for f in listdir(rcS_dir) if isfile(join(rcS_dir,f))];

        try:
            print("create", config_path)
            makedirs(config_path)
        except: pass

        try:
            print("create", join(output_dir, gem5_confs_names[conf]))
            makedirs(join(output_dir, gem5_confs_names[conf]))
        except: pass

        for rcs in tmp_list:
            rcs_dest = join(config_path, rcs)
            rcs_src =join(rcS_dir, rcs)
            config_list_multi.append([config_path, config_file, gem5_script, rcs_src, rcs_dest])

    for con in config_list_multi:
        gen_conf_files(con)

def get_jobs():
    return script_jobs

def clear_jobs():
    script_jobs = []

if __name__ == "__main__":
    build_script_gem5()

