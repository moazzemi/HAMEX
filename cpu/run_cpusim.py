#!/usr/bin/python

from __future__ import print_function
from global_conf import *
from multiprocessing.pool import ThreadPool, Pool
from subprocess import Popen, PIPE
import multiprocessing
import gen_rcS
import gen_gem5
import os.path

def run(job):
    p = Popen(["sh", job]);
    p.wait()

def run_jobs():
    jobs = gen_gem5.get_jobs()

    pool = ThreadPool(multiprocessing.cpu_count())
    for job in jobs:
        pool.apply_async(run, (job,))
    pool.close()
    pool.join()

benchmarks_configs=[("parsec", "small", 1, 1)]
def main():
    gen_gem5.clear_jobs()
    try:
        os.mkdir(output_dir)
    except:
        print("Error:", output_dir, "exists")
        raise

    print("Generating benchmark scripts...", end="")
    gen_rcS.build_script(benchmarks_configs)
    print("DONE")

    print("Generating gem5 scripts...", end="")
    gen_gem5.build_script_gem5()
    print("DONE")

    run_jobs()

if __name__ == "__main__":
    main()

