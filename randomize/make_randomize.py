# Randomizes the co-occurrence matrix with the required randomize-mode. Useful if we want to make control measures

import randomize.modes as rand
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Randomizes the co-occurrence matrix with the required randomize-mode.")
    parser.add_argument("in_file", help="location of the original co-occurrence matrix")
    parser.add_argument("out_file", help="location of the randomized co-occurrence matrix")
    parser.add_argument("mode", help="The way of randomize")
    args = parser.parse_args()
    rand.randomize(args.in_file, getattr(rand, args.mode), args.out_file)
