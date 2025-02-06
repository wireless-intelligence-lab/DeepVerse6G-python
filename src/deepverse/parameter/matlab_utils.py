import re
import numpy as np

# TODO: Matrix input is not supported - may be required for modes such as random selection or different arrays

####################################### LOADING Functions ##########################################
def matlab_load(file):
    """
    Loads the parameters from a MATLAB (.m) file.

    Returns:
        dict: The parameters loaded from the MATLAB file.
    """
    params = {}
    content = file.read()
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith('%'):  # Ignore empty lines and comments
            match = re.match(r'dv\.(\w+(\.\w+)*)\s*=\s*(.+);', line)
            if match:
                key = match.group(1)
                value = match.group(3).replace('true', 'True').replace('false', 'False')
                value = convert_matlab_range_to_list(value)
                try:
                    parsed_value = eval(value)  # Convert value from string to its actual type
                    assign_nested_value(params, key.split('.'), parsed_value)
                except Exception as e:
                    print(f"Error evaluating value for {key}: {value}. Error: {e}")
    return params

def convert_matlab_range_to_list(value):
    """
    Converts MATLAB range syntax (e.g., 1:8, 1:2:8) to a Python list representation.

    Args:
        value (str): The MATLAB range string.

    Returns:
        str: The Python list string representation.
    """
    range_pattern = re.compile(r'\[(\d+)(?::(\d+))?(?::(\d+))?\]')
    match = range_pattern.match(value)
    if match:
        start = int(match.group(1))
        if match.group(2):
            end = int(match.group(2))
        else:
            end = start
            
        if match.group(3):
            step = int(match.group(3))
        else:
            step = 1
        return str(list(np.arange(start, end + 1, step)))
    return value

def assign_nested_value(d, keys, value):
    """
    Assigns a value to a nested dictionary given a list of keys.

    Args:
        d (dict): The dictionary to assign the value in.
        keys (list): A list of keys representing the nested structure.
        value: The value to assign.
    """
    for key in keys[:-1]:
        d = d.setdefault(key, {})
    d[keys[-1]] = value
    
###################### WRITING FUNCTIONS ##############################
def matlab_dump(params, file):
    file.write("%% Automatically generated MATLAB file\n\n")
    for key, value in params.items():
        write_nested_value(file, f"dv.{key}", value)
        
def write_nested_value(file, key, value):
    """
    Writes a nested value to a file in MATLAB syntax.

    Args:
        file: The file object to write to.
        key (str): The key representing the nested structure.
        value: The value to write.
    """
    if isinstance(value, dict):
        for sub_key, sub_value in value.items():
            write_nested_value(file, f"{key}.{sub_key}", sub_value)
    else:
        matlab_value = convert_to_matlab_syntax(value)
        file.write(f"{key} = {matlab_value};\n")

def convert_to_matlab_syntax(value):
    """
    Converts a Python value to its MATLAB syntax representation.

    Args:
        value: The Python value to convert.

    Returns:
        str: The MATLAB syntax representation of the value.
    """
    if isinstance(value, str):
        return f"'{value}'"
    elif isinstance(value, bool):
        return 'true' if value else 'false'
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, float):
        return convert_float_to_matlab_scientific(value)
    elif isinstance(value, list):
        return convert_list_to_matlab_range(value)
    elif isinstance(value, np.ndarray):
        return convert_list_to_matlab_range(value.tolist())
    elif isinstance(value, dict):
        return f"{{ {', '.join(f'{k}: {convert_to_matlab_syntax(v)}' for k, v in value.items())} }}"
    elif isinstance(value, np.ndarray):
        return list(value)
    else:
        raise ValueError(f"Unsupported value type: {type(value)}")


def convert_list_to_matlab_range(value):
    """
    Converts a Python list to MATLAB range syntax if possible.

    Args:
        value (list): The Python list to convert.

    Returns:
        str: The MATLAB range string or None if not a valid range.
    """
    if len(value) < 8:
        return f"[{', '.join(map(convert_to_matlab_syntax, value))}]"
    
    diff = value[1] - value[0]
    for i in range(1, len(value) - 1):
        if value[i + 1] - value[i] != diff:
            return f"[{', '.join(map(convert_to_matlab_syntax, value))}]"
    
    if diff == 1:
        return f"[{value[0]}:{value[-1]}]"
    else:
        return f"[{value[0]}:{diff}:{value[-1]}]"
    
def convert_float_to_matlab_scientific(value):
    """
    Converts a Python float to MATLAB scientific notation with e6, e9, e12, etc.

    Args:
        value (float): The Python float to convert.

    Returns:
        str: The MATLAB scientific notation string.
    """
    if abs(value) >= 1e12:
        return f"{value / 1e12:g}e12"
    elif abs(value) >= 1e9:
        return f"{value / 1e9:g}e9"
    elif abs(value) >= 1e6:
        return f"{value / 1e6:g}e6"
    else:
        return f"{value}"
    
    