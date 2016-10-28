# Copyright (c) 2012-2013, 2015 ARM Limited
# All rights reserved
#
# The license below extends only to copyright in the software and shall
# not be construed as granting a license to any other intellectual
# property including but not limited to intellectual property relating
# to a hardware implementation of the functionality of the software
# licensed hereunder.  You may use the software subject to the license
# terms below provided that you ensure that this notice is replicated
# unmodified and in its entirety in all distributions of the software,
# modified or unmodified, in source code or in binary form.
#
# Copyright (c) 2010 Advanced Micro Devices, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Lisa Hsu

# Configure the M5 cache hierarchy config in one place
#

import m5
from m5.objects import *
from Caches import *
from collections import namedtuple

def config_ht_cache(system, options, cpu_type_idx, cpus):
    '''
    if options.external_memory_system and (options.caches or options.l2cache):
        print "External caches and internal caches are exclusive options.\n"
        sys.exit(1)

    if options.external_memory_system:
        ExternalCache = ExternalCacheFactory(options.external_memory_system)

    if options.cpu_type == "arm_detailed":
        try:
            from O3_ARM_v7a import *
        except:
            print "arm_detailed is unavailable. Did you compile the O3 model?"
            sys.exit(1)

        dcache_class, icache_class, l2_cache_class = \
            O3_ARM_v7a_DCache, O3_ARM_v7a_ICache, O3_ARM_v7aL2
    else:
        dcache_class, icache_class, l2_cache_class = \
            L1_DCache, L1_ICache, L2Cache
    '''
    if options.cpus_type_names[cpu_type_idx] == "arm_detailed":
        try:
            from O3_ARM_v7a import *
        except:
            print "arm_detailed is unavailable. Did you compile the O3 model?"
            sys.exit(1)

        dcache_class, icache_class, l2_cache_class = \
            O3_ARM_v7a_DCache, O3_ARM_v7a_ICache, O3_ARM_v7aL2
    else:
        dcache_class, icache_class, l2_cache_class = cache_ht_cls[cpu_type_idx].dcache_cls, \
                                cache_ht_cls[cpu_type_idx].icache_cls, cache_ht_cls[cpu_type_idx].l2_cache_cls, 

    for i in xrange(int(options.num_cpus_eachtype[cpu_type_idx])):
        icache = icache_class(size=options.l1i_size[cpu_type_idx],
                                  assoc=int(options.l1i_assoc[cpu_type_idx]))
        dcache = dcache_class(size=options.l1d_size[cpu_type_idx],
                                  assoc=int(options.l1d_assoc[cpu_type_idx]))

        if options.memchecker:
            dcache_mon = MemCheckerMonitor(warn_only=True)
            dcache_real = dcache

            # Do not pass the memchecker into the constructor of
            # MemCheckerMonitor, as it would create a copy; we require
            # exactly one MemChecker instance.
            dcache_mon.memchecker = system.memchecker

            # Connect monitor
            dcache_mon.mem_side = dcache.cpu_side

            # Let CPU connect to monitors
            dcache = dcache_mon

        # When connecting the caches, the clock is also inherited
        # from the CPU in question
        cpus[i].addPrivateSplitL1Caches(icache, dcache)

        if options.memchecker:
            # The mem_side ports of the caches haven't been connected yet.
            # Make sure connectAllPorts connects the right objects.
            system.cpu[i].dcache = dcache_real
            system.cpu[i].dcache_mon = dcache_mon

        cpus[i].createInterruptController()

        cpus[i].connectAllPorts(system.tol2bus, system.membus)


def config_cache_singlel2(options, system):

    # Set the cache line size of the system
    system.cache_line_size = options.cacheline_size


    #Since multiple L2 coherency is only implemented at Ruby,
    #we force the use of a single L2 here

    # If there is only one cpu type we use that clock domain
    # otherwise we use the system clock domain
    assert(options.num_cpus_types >= 1)
    if options.num_cpus_types == 1:
        l2ClockDomain = system.cpu_clk_domain[0]
    else:
        l2ClockDomain = system.clk_domain

    system.l2 = L2Cache(clk_domain=l2ClockDomain,
                               size=options.l2_size[0],
                               assoc=int(options.l2_assoc[0]))
    system.tol2bus = L2XBar(clk_domain = l2ClockDomain)
    system.l2.cpu_side = system.tol2bus.master
    system.l2.mem_side = system.membus.slave

    if options.memchecker:
        system.memchecker = MemChecker()

    cpu_idx =  0
    for type_idx in xrange(options.num_cpus_types):
        cpus = []
        for x in xrange(int(options.num_cpus_eachtype[type_idx])):
            cpus.append(system.cpu[cpu_idx])
            cpu_idx += 1
        config_ht_cache(system,options,type_idx,cpus)

	'''
    # If elastic trace generation is enabled, make sure the memory system is
    # minimal so that compute delays do not include memory access latencies.
    # Configure the compulsory L1 caches for the O3CPU, do not configure
    # any more caches.
    if options.l2cache and options.elastic_trace_en:
        fatal("When elastic trace is enabled, do not configure L2 caches.")

    if options.l2cache:
        # Provide a clock for the L2 and the L1-to-L2 bus here as they
        # are not connected using addTwoLevelCacheHierarchy. Use the
        # same clock as the CPUs.
        system.l2 = l2_cache_class(clk_domain=system.cpu_clk_domain,
                                   size=options.l2_size,
                                   assoc=options.l2_assoc)

        system.tol2bus = L2XBar(clk_domain = system.cpu_clk_domain)
        system.l2.cpu_side = system.tol2bus.master
        system.l2.mem_side = system.membus.slave

    if options.memchecker:
        system.memchecker = MemChecker()

    for i in xrange(options.num_cpus):
        if options.caches:
            icache = icache_class(size=options.l1i_size,
                                  assoc=options.l1i_assoc)
            dcache = dcache_class(size=options.l1d_size,
                                  assoc=options.l1d_assoc)

            if options.memchecker:
                dcache_mon = MemCheckerMonitor(warn_only=True)
                dcache_real = dcache

                # Do not pass the memchecker into the constructor of
                # MemCheckerMonitor, as it would create a copy; we require
                # exactly one MemChecker instance.
                dcache_mon.memchecker = system.memchecker

                # Connect monitor
                dcache_mon.mem_side = dcache.cpu_side

                # Let CPU connect to monitors
                dcache = dcache_mon

            # When connecting the caches, the clock is also inherited
            # from the CPU in question
            if buildEnv['TARGET_ISA'] == 'x86':
                system.cpu[i].addPrivateSplitL1Caches(icache, dcache,
                                                      PageTableWalkerCache(),
                                                      PageTableWalkerCache())
            else:
                system.cpu[i].addPrivateSplitL1Caches(icache, dcache)

            if options.memchecker:
                # The mem_side ports of the caches haven't been connected yet.
                # Make sure connectAllPorts connects the right objects.
                system.cpu[i].dcache = dcache_real
                system.cpu[i].dcache_mon = dcache_mon

        elif options.external_memory_system:
            # These port names are presented to whatever 'external' system
            # gem5 is connecting to.  Its configuration will likely depend
            # on these names.  For simplicity, we would advise configuring
            # it to use this naming scheme; if this isn't possible, change
            # the names below.
            if buildEnv['TARGET_ISA'] in ['x86', 'arm']:
                system.cpu[i].addPrivateSplitL1Caches(
                        ExternalCache("cpu%d.icache" % i),
                        ExternalCache("cpu%d.dcache" % i),
                        ExternalCache("cpu%d.itb_walker_cache" % i),
                        ExternalCache("cpu%d.dtb_walker_cache" % i))
            else:
                system.cpu[i].addPrivateSplitL1Caches(
                        ExternalCache("cpu%d.icache" % i),
                        ExternalCache("cpu%d.dcache" % i))

        system.cpu[i].createInterruptController()
        if options.l2cache:
            system.cpu[i].connectAllPorts(system.tol2bus, system.membus)
        elif options.external_memory_system:
            system.cpu[i].connectUncachedPorts(system.membus)
        else:
            system.cpu[i].connectAllPorts(system.membus)
	'''
    return system


def config_cache_privatel2_aux(options, system, cpu_type_idx, cpu_idx):
    system.l2[cpu_idx].size = options.l2_size[cpu_type_idx]
    system.l2[cpu_idx].assoc = int(options.l2_assoc[cpu_type_idx])

    system.l2[cpu_idx].cpu_side = system.tol2bus[cpu_idx].master
    system.l2[cpu_idx].mem_side = system.membus.slave

    icache = cache_ht_cls[cpu_type_idx].icache_cls(size=options.l1i_size[cpu_type_idx],
                                  assoc=int(options.l1i_assoc[cpu_type_idx]))
    dcache = cache_ht_cls[cpu_type_idx].dcache_cls(size=options.l1d_size[cpu_type_idx],
                                  assoc=int(options.l1d_assoc[cpu_type_idx]))

    if options.memchecker:
        dcache_mon = MemCheckerMonitor(warn_only=True)
        dcache_real = dcache

        # Do not pass the memchecker into the constructor of
        # MemCheckerMonitor, as it would create a copy; we require
        # exactly one MemChecker instance.
        dcache_mon.memchecker = system.memchecker

        # Connect monitor
        dcache_mon.mem_side = dcache.cpu_side

        # Let CPU connect to monitors
        dcache = dcache_mon

        # When connecting the caches, the clock is also inherited
        # from the CPU in question
    system.cpu[cpu_idx].addPrivateSplitL1Caches(icache, dcache)

    if options.memchecker:
        # The mem_side ports of the caches haven't been connected yet.
        # Make sure connectAllPorts connects the right objects.
        system.cpu[cpu_idx].dcache = dcache_real
        system.cpu[cpu_idx].dcache_mon = dcache_mon

    system.cpu[cpu_idx].createInterruptController()

    system.cpu[cpu_idx].connectAllPorts(system.tol2bus[cpu_idx], system.membus)

def config_cache_privatel2(options, system):
    if options.memchecker:
        system.memchecker = MemChecker()

    # Set the cache line size of the system
    system.cache_line_size = options.cacheline_size
    
    system.l2 = [cache_ht_cls[cpu_idx].l2_cache_cls(clk_domain=system.cpu_clk_domain[cpu_idx],
                               size=options.l2_size[0],
                               assoc=int(options.l2_assoc[0])) 
                     for cpu_idx in xrange(options.num_cpus)]
#     system.l2 = [L2Cache(clk_domain=system.cpu_clk_domain[cpu_idx],
#                                size=options.l2_size[0],
#                                assoc=int(options.l2_assoc[0]))
#                   for cpu_idx in xrange(options.num_cpus)]
    system.tol2bus = [L2XBar(clk_domain = system.cpu_clk_domain[cpu_idx])
                        for cpu_idx in xrange(options.num_cpus)]

    cpu_idx =  0
    for type_idx in xrange(options.num_cpus_types):
        for x in xrange(int(options.num_cpus_eachtype[type_idx])):
            config_cache_privatel2_aux(options, system, type_idx, cpu_idx)
            cpu_idx += 1


    return system

cache_ht_cls = []
def config_cache(options, system):
    CacheClasses = namedtuple('CacheClasses', ['dcache_cls', 'icache_cls', 'l2_cache_cls'])

    for cpu_type in options.cpus_type_names:
        if cpu_type == "arm_detailed":
            try:
                from O3_ARM_v7a import *
            except:
                print "arm_detailed is unavailable. Did you compile the O3 model?"
                sys.exit(1)
    
            dcache_class, icache_class, l2_cache_class = \
                O3_ARM_v7a_DCache, O3_ARM_v7a_ICache, O3_ARM_v7aL2
        else:
            dcache_class, icache_class, l2_cache_class = L1_DCache, L1_ICache, L2Cache
    
        cache_ht_cls.append(CacheClasses(dcache_cls = dcache_class, icache_cls = icache_class, l2_cache_cls = l2_cache_class))

    if options.num_cpus == options.total_l2_cache:
        return config_cache_privatel2(options, system)
    else:
        return config_cache_singlel2(options, system)

# ExternalSlave provides a "port", but when that port connects to a cache,
# the connecting CPU SimObject wants to refer to its "cpu_side".
# The 'ExternalCache' class provides this adaptation by rewriting the name,
# eliminating distracting changes elsewhere in the config code.
class ExternalCache(ExternalSlave):
    def __getattr__(cls, attr):
        if (attr == "cpu_side"):
            attr = "port"
        return super(ExternalSlave, cls).__getattr__(attr)

    def __setattr__(cls, attr, value):
        if (attr == "cpu_side"):
            attr = "port"
        return super(ExternalSlave, cls).__setattr__(attr, value)

def ExternalCacheFactory(port_type):
    def make(name):
        return ExternalCache(port_data=name, port_type=port_type,
                             addr_ranges=[AllMemory])
    return make
