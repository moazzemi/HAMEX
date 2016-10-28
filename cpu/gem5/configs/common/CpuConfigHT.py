# Copyright (c) 2012 ARM Limited
# All rights reserved.
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
# Authors: Andreas Sandberg

from m5.objects import *


def cpu_count(options):
    count = 0
    for i in range(0,options.num_cpus_types):
        count += int(options.num_cpus_eachtype[i])
    return count
    
def l2_cache_count(options):
    count = 0
    for i in range(0,options.num_cpus_types):
        count += int(options.num_l2caches[i])
    return count

def set_cpu_names(system, options):
    cpu_idx =  0
    for type_idx in xrange(options.num_cpus_types):
        for x in xrange(int(options.num_cpus_eachtype[type_idx])):
            system.cpu[cpu_idx].name = '{0}_cpu{0}'.format(options.cpus_type_names[type_idx],system.cpu[cpu_idx].cpu_id)
            cpu_idx += 1
    

def set_cpu_clock_domains(system, options):
    if cpu_count(options) == l2_cache_count(options):
        set_cpu_clock_domains_private(system,options)
    else:
        set_cpu_clock_domains_clustered(system,options)
        

def set_cpu_clock_domains_clustered(system, options):
    cpu_idx =  0
    system.cpu_voltage_domain = [VoltageDomain(voltage = options.cpu_voltage[type_idx]) for type_idx in xrange(options.num_cpus_types)]
    system.cpu_clk_domain = [SrcClockDomain(clock = options.cpu_clock[type_idx],  voltage_domain = system.cpu_voltage_domain[type_idx]) for type_idx in xrange(options.num_cpus_types)]
    for type_idx in xrange(options.num_cpus_types):
        for x in xrange(int(options.num_cpus_eachtype[type_idx])):
            system.cpu[cpu_idx].clk_domain = system.cpu_clk_domain[type_idx]
            cpu_idx += 1

def set_cpu_clock_domains_private(system, options):
    cpuIDX =  0
    system.cpu_voltage_domain = [VoltageDomain(voltage = options.cpu_voltage[0]) for i in xrange(options.num_cpus)]
    system.cpu_clk_domain = [SrcClockDomain(clock = options.cpu_clock[0],  voltage_domain = system.cpu_voltage_domain[i]) for i in xrange(options.num_cpus)]
    for type_idx in xrange(options.num_cpus_types):
        for cpu in xrange(int(options.num_cpus_eachtype[type_idx])):
            system.cpu_voltage_domain[cpuIDX].voltage = options.cpu_voltage[type_idx]
            system.cpu_clk_domain[cpuIDX].clock = options.cpu_clock[type_idx]
            system.cpu[cpuIDX].clk_domain = system.cpu_clk_domain[cpuIDX]
            cpuIDX += 1    


def config_heterogeneous_cpus(system, options):
    if options.cpu_type != "detailed": return
    
    cpu_idx =  0
    for type_idx in xrange(options.num_cpus_types):
        for x in xrange(int(options.num_cpus_eachtype[type_idx])):
            
            if options.cpus_type_names[type_idx] == "arm_detailed":
                system.cpu[cpu_idx].technologyNode = options.tech_node
            
            pipeline_stages_width = int(options.cpu_pipeline_width[type_idx])
            #Timebuffer fails if wbWidth < 2
            pipeline_stated_wbWidth = 2 if (pipeline_stages_width < 2) else pipeline_stages_width
      
            system.cpu[cpu_idx].fetchWidth      =pipeline_stages_width
            system.cpu[cpu_idx].decodeWidth     =pipeline_stages_width
            system.cpu[cpu_idx].dispatchWidth   =pipeline_stages_width
            system.cpu[cpu_idx].renameWidth     =pipeline_stages_width
            system.cpu[cpu_idx].issueWidth      =pipeline_stages_width
            system.cpu[cpu_idx].squashWidth     =pipeline_stages_width
            system.cpu[cpu_idx].wbWidth         =pipeline_stated_wbWidth
            system.cpu[cpu_idx].commitWidth     =pipeline_stages_width

            system.cpu[cpu_idx].LQEntries       =int(options.cpu_LQentries[type_idx])
            system.cpu[cpu_idx].SQEntries       =int(options.cpu_SQentries[type_idx])
            system.cpu[cpu_idx].numIQEntries    =int(options.cpu_IQentries[type_idx])
            system.cpu[cpu_idx].numROBEntries   =int(options.cpu_ROBentries[type_idx])            

            system.cpu[cpu_idx].numPhysIntRegs = int(options.cpu_numPhysIntRegs[type_idx])
            system.cpu[cpu_idx].numPhysFloatRegs = int(options.cpu_numPhysFloatRegs[type_idx])
            
            system.cpu[cpu_idx].branchPred.localPredictorSize = int(options.cpu_localPredictorSize[type_idx])
            system.cpu[cpu_idx].branchPred.globalPredictorSize = int(options.cpu_globalPredictorSize[type_idx])
            system.cpu[cpu_idx].branchPred.choicePredictorSize = int(options.cpu_choicePredictorSize[type_idx])
            system.cpu[cpu_idx].branchPred.BTBEntries = int(options.cpu_BTBEntries[type_idx])
            system.cpu[cpu_idx].branchPred.RASSize = int(options.cpu_RASSize[type_idx])                                                                   
            
            cpu_idx += 1
    
    

