#!/usr/bin/python

import gem5_conf
import os

"""
1. Output directories
"""
output_dir = "output"

"""
2. Benchmark configs
"""
#
# benchmark format: (name, category, running core #, #threads)
#
benchmarks_configs=[("parsec", "small", 1, 1)]

sim_parsec_dir = "/your_sim_directory_for_parsec"

"""
3. Gem5 environment
"""
env_gem5_src = "/home/your_working_directory/parallel/gem5"
env_gem5_bin = env_gem5_src + "/build/ARM/gem5.opt"
kernel_image = env_gem5_src + "/full-system/src/linux-arm-gem5/vmlinux"
disk_image = env_gem5_src + "/full-system/disks/aarch32-ubuntu-natty-headless.img"

# support only GEM5_FS_HT
sim_type = gem5_conf.GEM5_FS_HT

# memory size
mem_size="2048MB"

# system clock
sys_clock="600MHz"

#
# Configuration for CPU architectures
#
g_num_cores = [2, 2]
g_base_core_conf = [gem5_conf.CORE_EXYNOS_A07, gem5_conf.CORE_EXYNOS_A15]
g_base_cache_conf = [gem5_conf.CACHE_EXYNOS_A07, gem5_conf.CACHE_EXYNOS_A15]

#
# Frequency for the two type of cores
# e.g.
#   g_freq_list = [(gem5_conf.FREQ_1300MHz, gem5_conf.FREQ_0700MHz),
#                  (gem5_conf.FREQ_1800MHz, gem5_conf.FREQ_0600MHz)]
#
g_freq_list = [(gem5_conf.FREQ_1300MHz,), (gem5_conf.FREQ_1800MHz,)]

"""
4. Internal use only
"""
rcS_dir = os.path.join(output_dir, "rcS")

