# ===================================================================
# Copyright 2025 National Oceanography Centre
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.
# ===================================================================

"""
Entry for the project.

@author: Mr. Srikanth Nagella
"""

import cProfile
import getopt
import logging
import sys
import time

from . import profiler

# Logging set to info
logging.basicConfig(level=logging.INFO)


def main():
    """
    Run main function.

    Checks the command line parameters and passes them to the profile module for processing.
    """
    setup_file = ""
    mask_gui = False
    try:
        opts, dummy_args = getopt.getopt(
            sys.argv[1:], "hs:g", ["help", "setup=", "mask_gui"]
        )
    except getopt.GetoptError:
        print("usage: pybdy -g -s <namelist.bdy> ")
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print("usage: pybdy [-g] -s <namelist.bdy> ")
            print(
                "       -g (optional) will open settings editor before extracting the data"
            )
            print("       -s <bdy filename> file to use")
            sys.exit()
        elif opt in ("-s", "--setup"):
            setup_file = arg
        elif opt in ("-g", "--mask_gui"):
            mask_gui = True

    if setup_file == "":
        print("usage: pybdy [-g] -s <namelist.bdy> ")
        sys.exit(2)

    # Logger
    # logger = logging.getLogger(__name__)
    t0 = time.time()
    cProfile.runctx(
        "f(x, y)",
        {"f": profiler.process_bdy, "x": setup_file, "y": mask_gui},
        {},
        "pybdy_stats",
    )
    t1 = time.time()
    print("Execution Time: %s" % (t1 - t0))


if __name__ == "__main__":
    main()
