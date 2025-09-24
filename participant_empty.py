#!/bin/env python3

import json
import os
import argparse


def to_empty(cell):
    code_cell = cell['cell_type'] in ('code', 'raw')
    to_empty = 'empty' in cell['metadata'].get('tags', [])
    return code_cell and to_empty


def create_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("FILES", nargs='+', type=argparse.FileType('r'))
    parser.add_argument("-v", "--verbose", action="store_true", help="Be verbose about action")

    output_group = parser.add_argument_group('output')
    parser.add_mutually_exclusive_group()._group_actions.extend([
        output_group.add_argument("-o", "--outputdir", help='Write stripped files to output directory'),
        output_group.add_argument("-i", "--inplace", action='store_true', help='Work in-place, modifying current file')
    ])
    parser.add_argument("-k", "--keep-comments", action='store_true', help='Keep comments in the code cells')

    return parser


def main(args=create_parser().parse_args()):
    for file in args.FILES:
        if args.verbose:
            print(f'Processing: {file.name}')
        content = json.load(file)

        for cell in filter(to_empty, content['cells']):
            if args.keep_comments:
                cell['source'] = [line for line in cell['source'] if line.startswith('#') and not line.startswith('##')]
            else:
                cell['source'] = []

        if args.inplace:
            outname = file.name
        elif args.outputdir:
            outname = os.path.join(args.outputdir, os.path.basename(file.name))
        else:  # fallback to avoid erasing files in case we are in the directory
            outname = f"{os.path.basename(file.name)}.new"

        with open(outname, 'w', encoding="UTF-8") as out:
            if args.verbose:
                print(f'Writting to {outname}')
            json.dump(content, out, indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main(create_parser().parse_args())
