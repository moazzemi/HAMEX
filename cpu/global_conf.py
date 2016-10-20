#!/usr/bin/python

import gem5_conf
import os

"""
Output directories
"""
output_dir = "output"

"""
Gem5 environment
"""
env_gem5_src = "/home/drg/work/parallel/gem5"
env_gem5_bin = env_gem5_src + "/build/ARM/gem5.opt"
kernel_image = env_gem5_src + "/full-system/src/linux-arm-gem5/vmlinux"
disk_image = env_gem5_src + "/full-system/disks/aarch32-ubuntu-natty-headless.img"

# support only GEM5_FS_HT
sim_type = confs.GEM5_FS_HT

# memory size
mem_size="2048MB"

# system clock
sys_clock="600MHz"

#
# Configuration for CPU architectures
#
g_num_cores = [2, 2]
g_base_core_conf = [confs.CORE_EXYNOS_A07, confs.CORE_EXYNOS_A15]
g_base_cache_conf = [confs.CACHE_EXYNOS_A07, confs.CACHE_EXYNOS_A15]
g_freq_list = [(confs.FREQ_1300MHz, confs.FREQ_0700MHz), (confs.FREQ_1800MHz, confs.FREQ_0600MHz)]



rcS_dir = os.path.join(output_dir, "rcS")

