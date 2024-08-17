import angr
import logging
import os
from fuzz import fuzzer


logging.getLogger('angr').setLevel(logging.CRITICAL)

def find_avoid_addresses(binary_path):
    avoid_addrs = []
    project = angr.Project(binary_path, auto_load_libs=False)
    cfg = project.analyses.CFGFast() 
    for function in cfg.functions.values():
        if any("exit" in block.disassembly_string for block in function.blocks):
            avoid_addrs.append(function.addr)
    
    return avoid_addrs

def identify_target_addresses(binary_path):
    find_addrs = []
    project = angr.Project(binary_path, auto_load_libs=False)
    cfg = project.analyses.CFGFast()
    for function in cfg.functions.values():
        if any(keyword in function.name for keyword in ["strcpy", "memcpy", "strcat", "gets"]):
            find_addrs.append(function.addr)
    
    return find_addrs

def symbolic_execution(binary_path, avoid_addrs=[], find_addrs=[]):
    project = angr.Project(binary_path, auto_load_libs=False)
    state = project.factory.entry_state()
    simgr = project.factory.simgr(state)

    for find_addr in find_addrs:
        simgr.explore(find=find_addr, avoid=avoid_addrs)

    return simgr.found

def fuzzing_input_generation(symbolic_paths, output_dir, fuzzer):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i, path in enumerate(symbolic_paths):
        input_data = path.posix.dumps(0)
        input_file = os.path.join(output_dir, f'input_{i}.bin')
        with open(input_file, 'wb') as f:
            f.write(input_data)

        print(f"Generated input {i} saved to {input_file}")
        fuzzer(input_file)

def main():
    binary_path = './bin/binary.bin'
    avoid_addrs = find_avoid_addresses(binary_path)
    find_addrs = identify_target_addresses(binary_path)

    if not find_addrs:
        print("No potential target addresses found.")
        return
    
    symbolic_paths = symbolic_execution(binary_path, avoid_addrs=avoid_addrs, find_addrs=find_addrs)

    if symbolic_paths:
        print(f"Found {len(symbolic_paths)} paths to target addresses.")
        fuzzing_input_generation(symbolic_paths, './fuzz_inputs', fuzzer)
    else:
        print("No paths found to the target addresses.")

if __name__ == "__main__":
    main()
