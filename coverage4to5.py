#!/usr/bin/env python3

import os
import re
import sys
import json
import warnings

from coverage.sqldata import CoverageData


def main():
    if len(sys.argv) != 2:
        raise ValueError("Must be passed single parameter: coverage data path")
    input_path = sys.argv[1]
    if not os.path.isfile(input_path):
        raise ValueError(f"No such file or it is a directory: {input_path}")
    output_path = f"{input_path}.output"
    if os.path.exists(output_path):
        os.remove(output_path)
    with open(input_path, 'rt') as input_file:
        try:
            input_data = input_file.read()
            input_data = re.sub(r'^![^!]+!', '', input_data, count=1)
            input_data = json.loads(input_data)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            return
    output_data = CoverageData(basename=output_path)
    arcs_data = input_data.get('arcs', {})
    if not arcs_data:
        warnings.warn(f"Empty arcs: {input_path}", category=RuntimeWarning, stacklevel=2)
    output_data.add_arcs(arcs_data)

    os.remove(input_path)
    os.rename(output_path, input_path)
    print(f'Coverage is converted: {input_path}')

if __name__ == '__main__':
    main()
