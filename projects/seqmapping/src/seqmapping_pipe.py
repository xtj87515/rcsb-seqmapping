#!/usr/bin/env python3
# Created by Tongji Xing 09/10/2024

import argparse
import os
from subprocess import run


def main():
    parser = argparse.ArgumentParser(description="Integrated SeqMapping Pipeline")
    parser.add_argument("--download", action="store_true", help="Download databases")
    parser.add_argument("--preprocess", action="store_true", help="Preprocess databases")
    parser.add_argument("--search", action="store_true", help="Run MMseqs2 search")
    parser.add_argument("--mongo", action="store_true", help="Load search results to MongoDB")
    args = parser.parse_args()

    # Get the working directory of the script location
    script_dir = os.path.dirname(os.path.realpath(__file__))

    if args.download:
        run(script_dir + "/" + "setup_mmseqs2.sh", check=False)

    if args.preprocess:
        run(script_dir + "/" + "prepocess_databases.sh", check=False)

    if args.search:
        run(script_dir + "/" + "run_mmseqs2_search.sh", check=False)

    if args.mongo:
        run(script_dir + "/" + "search_output_to_mongo.py", check=False)


if __name__ == "__main__":
    main()
