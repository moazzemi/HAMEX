#!/usr/bin/python

from __future__ import print_function
from collections import defaultdict
from global_conf import *
import os
import parsec_conf


parsec_dir = "/home/gem5/benchmarks/parsec"

# helper functions to build script for each parsec benchmark
def build_blackscholes(core, nr_threads, input_file, output_file):
	name = "blackscholes"
	exe = "./bin/" + name
	template = "{exe} {nr_threads} {input_file} {output_file} &"
	return (name, core, template.format(exe = exe, nr_threads = nr_threads, input_file = input_file,
			output_file = output_file))

def build_bodytrack(core, nr_threads, dataset_path, nr_cameras, nr_frames, nr_particles, nr_layers, thread_model):
	name = "bodytrack"
	exe = "./bin/" + name
	template = "{exe} {dataset_path} {nr_cameras} {nr_frames} {nr_particles} {nr_layers} {thread_model} {nr_threads}&"
	return (name, core, template.format(exe = exe, nr_threads = nr_threads, dataset_path = dataset_path, nr_cameras = nr_cameras, nr_frames = nr_frames, nr_particles = nr_particles, nr_layers = nr_layers, thread_model = thread_model))

def build_canneal(core, nr_threads, nr_swaps, temp, netlist):
	name = "canneal"
	exe = "./bin/" + name
	template = "{exe} {nr_threads} {nr_swaps} {temp} {netlist} &"
	return (name, core, template.format(exe = exe, nr_threads = nr_threads, nr_swaps = nr_swaps, temp = temp, netlist = netlist))

def build_dedup(core, nr_threads, infile, outfile, flags):
	name = "dedup"
	exe = "./bin/" + name
	template = "{exe} {flags} -t {nr_threads} -i {infile} -o {outfile} &"
	return (name, core, template.format(exe = exe, flags = flags, nr_threads = nr_threads, infile = infile, outfile = outfile))

def build_ferret(core, nr_threads, database, table, query_dir, top_k, depth, outfile):
	name = "ferret"
	exe = "./bin/" + name
	template = "{exe} {database} {table} {query_dir} {top_k} {depth} {nr_threads} {outfile} &"
	return (name, core, template.format(exe = exe, nr_threads = nr_threads, database = database, table = table, query_dir = query_dir, top_k = top_k, depth = depth, outfile = outfile))

def build_fluidanimate(core, nr_threads, nr_frames, infile, outfile):
	name = "fluidanimate"
	exe = "./bin/" + name
	template = "{exe} {nr_threads} {nr_frames} {infile} {outfile} &"
	return (name, core, template.format(exe = exe, nr_threads = nr_threads, nr_frames = nr_frames, infile = infile, outfile = outfile))

def build_streamcluster(core, nr_threads, k1, k2, d, n, chunksize, clustersize, infile, outfile):
	name = "streamcluster"
	exe = "./bin/" + name
	template = "{} {} {} {} {} {} {} {} {} {} &"
	return (name, core, template.format(exe, k1, k2, d, n, chunksize, clustersize, infile, outfile, nr_threads))

def build_x264(core, nr_threads, nr_frames, infile, outfile, flags):
	name = "x264"
	exe = "./bin/" + name + "_mod"
	template = "{exe} {flags} --ref {nr_frames} --threads {nr_threads} -o {outfile} {infile} &"
	return (name, core, template.format(exe = exe, nr_threads = nr_threads, flags = flags, nr_frames = nr_frames, outfile = outfile, infile = infile))


def gen_script_set(category, core, num_thread):
	if category == "small":
		return [
		build_blackscholes(core, num_thread, "./input_simsmall/in_4K.txt", "/dev/null"),
		build_bodytrack(core, num_thread, "./input_simsmall/sequenceB_1/", 4, 1, 1000, 5, 0),
		build_canneal(core, num_thread, 10000, 2000, "input_simsmall/100000.nets"),
		build_dedup(core, num_thread, "./input_simsmall/media.dat", "./output.dat.ddp", "-c -p -v"),
		build_ferret(core, num_thread, "./input_simsmall/corel", "lsh", "./input_simsmall/queries", 10, 20, "./output.txt"),
		build_fluidanimate(core, num_thread, 5, "./input_simsmall/in_35K.fluid", "./out.fluid"),
		build_streamcluster(core, num_thread, 10, 20, 32, 4096, 4096, 1000, "none", "./output.txt"),
		build_x264(core, num_thread, 5, "input_simsmall/eledream_640x360_8.y4m", "./output.x264_mod", "--quiet --qp 20 --partitions b8x8,i4x4 --direct auto --weightb --mixed-refs --no-fast-pskip --me umh --subme 7 --analyse b8x8,i4x4"),
		]
	elif category == "medium":
		return [
		build_blackscholes(core, num_thread, "./input_simsmall/in_4K.txt", "/dev/null"),
		build_bodytrack(core, num_thread, "./input_simmedium/sequenceB_2/", 4, 2, 2000, 5, 0),
		build_canneal(core, num_thread, 15000, 2000, "input_simmedium/200000.nets"),
		build_dedup(core, num_thread, "./input_simmedium/media.dat", "./output.dat.ddp", "-c -p"),
		build_ferret(core, num_thread, "./input_simmedium/corel", "lsh", "./input_simmedium/queries", 10, 20, "./output.txt"),
		build_fluidanimate(core, num_thread, 5, "./input_simmedium/in_100K.fluid", "./out.fluid"),
		build_streamcluster(core, num_thread, 10, 20, 64, 8192, 8192, 1000, "none", "./output.txt"),
		build_x264(core, num_thread, 5, "input_simmedium/eledream_640x360_32.y4m", "./output.x264_mod", "--quiet --qp 20 --partitions b8x8,i4x4 --direct auto --weightb --mixed-refs --no-fast-pskip --me umh --subme 7 --analyse b8x8,i4x4"),
		]
	else:
		raise ValueError("Need \"small\" or \"medium\"")
	return []

def gen_script(benchmark):
	s = """#!/bin/bash

# Auto-generated file
# command-line: {cmd}

/sbin/m5 dumpresetstats
cd {parsec_dir}/{name}
time taskset -c {core} {cmd}

wait
/sbin/m5 exit
/sbin/m5 exit

""".format(parsec_dir = parsec_dir, name = benchmark[0], core = benchmark[1], cmd = benchmark[2])
	return s

def _gen_filename(benchmark, tag):
	return "{}-{}-{}.rcS".format(benchmark[0], benchmark[1], tag)


def build_script(configs):
	# Create directories
	os.mkdir(rcS_dir)


	benchmarks = defaultdict(lambda : defaultdict(list))
	for config in configs:
		if config[0] == "parsec":
			benchmarks[config[0]][config[1]].append(parsec_conf.gen_config(config[1], config[2], config[3]))
		else:
			raise ValueError(config[0] + " is not supported.")

    # parsec
	for bname in benchmarks:
        # small, medium
		for btype in benchmarks[bname]:
            # benchmark set of this type
			for bset in benchmarks[bname][btype]:
				for b in bset:
					fname = _gen_filename(b, btype)
					fpath = rcS_dir + "/" + fname
					if os.access(fpath, os.R_OK):
						print("File", fname, "exists.")
						continue

					f = open(fpath, 'w')
					f.write(gen_script(b))
					f.close()

