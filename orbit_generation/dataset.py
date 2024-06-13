# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/05_dataset.ipynb.

# %% auto 0
__all__ = ['get_orbit_data_from_hdf5', 'get_orbit_features_from_hdf5', 'get_orbit_features_from_folder',
           'substitute_values_from_df', 'get_orbit_classes', 'get_periods_of_orbit_dict',
           'get_first_period_of_fixed_period_dataset', 'get_full_fixed_step_dataset',
           'get_first_period_fixed_step_dataset']

# %% ../nbs/05_dataset.ipynb 2
import os
import h5py
import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Any

from .processing import pad_and_convert_to_3d, segment_and_convert_to_3d, add_time_vector_to_orbits
from .constants import ORBIT_CLASS_DF

# %% ../nbs/05_dataset.ipynb 4
def get_orbit_data_from_hdf5(file_path: str                   # Path to the HDF5 file.
                            ) -> Tuple[Dict[int, np.ndarray], # Dictionary of orbits with numerical keys.
                                    pd.DataFrame,             # DataFrame containing orbit features.
                                    Dict[str, float]]:        # Dictionary containing system features.
    """
    Load orbit data from an HDF5 file.
    """
    with h5py.File(file_path, 'r') as file:
        # Extract not_propagated_orbits and store in a list of integers
        not_propagated_orbits = [index - 1 for index in file['not_propagated_orbits'][0].tolist()]
        
        # Extract system features and labels
        system_features = file['system_features'][:]
        system_labels = file['system_labels'][:].astype(str)
        
        # Create a dictionary for system
        system_dict = {label: feature[0] for label, feature in zip(system_labels.flatten().tolist(), system_features)}
        
        # Extract orbit features and labels
        orbit_features = file['orbit_features'][:]
        orbit_labels = file['orbit_labels'][:].astype(str)
        
        # Create a dataframe for orbits
        orbit_df = pd.DataFrame(orbit_features.T, columns=orbit_labels.flatten().tolist())
        
        # Remove rows in orbit_df based on not_propagated_orbits
        orbit_df = orbit_df.drop(not_propagated_orbits).reset_index(drop=True)
        
        # Extract numpy arrays with numerical keys
        orbits = {int(key): file[key][:] for key in file.keys() if key.isdigit()}
        
        # Reset the index of the dictionary to start on 0
        orbits = {i: orbits[key] for i, key in enumerate(sorted(orbits.keys()))}
                
    return orbits, orbit_df, system_dict

# %% ../nbs/05_dataset.ipynb 7
def get_orbit_features_from_hdf5(file_path: str          # Path to the HDF5 file.
                                ) -> pd.DataFrame:       # DataFrame containing orbit features.
    """
    Load orbit DataFrame from an HDF5 file.
    """
    with h5py.File(file_path, 'r') as file:
        # Extract not_propagated_orbits and store in a list of integers
        not_propagated_orbits = [index - 1 for index in file['not_propagated_orbits'][0].tolist()]
        
        # Extract orbit features and labels
        orbit_features = file['orbit_features'][:]
        orbit_labels = file['orbit_labels'][:].astype(str)
        
        # Create a dataframe for orbits
        orbit_df = pd.DataFrame(orbit_features.T, columns=orbit_labels.flatten().tolist())
        
        # Remove rows in orbit_df based on not_propagated_orbits
        orbit_df = orbit_df.drop(not_propagated_orbits).reset_index(drop=True)
                
    return orbit_df

# %% ../nbs/05_dataset.ipynb 8
def get_orbit_features_from_folder(folder_path: str    # Path to the folder
                                  ) -> pd.DataFrame:   # DataFrame containing concatenated orbit features.
    """
    Concatenate orbit DataFrames from all HDF5 files in a folder, preserving original index and adding system column.
    """
    all_dfs = []  # List to store individual DataFrames

    # Iterate over all files in the folder
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        # Check if the file is an HDF5 file
        if file_name.endswith('.h5') or file_name.endswith('.hdf5'):
            # Get the orbit DataFrame from the HDF5 file
            orbit_df = get_orbit_features_from_hdf5(file_path)
            
            # Preserve the original index as a new column
            orbit_df['original_index'] = orbit_df.index
            
            # Add a new column called 'system' with the name of the file (without extension)
            orbit_df['system'] = os.path.splitext(file_name)[0].split('_')[0]
            
            # Append the DataFrame to the list
            all_dfs.append(orbit_df)

    # Concatenate all DataFrames
    concatenated_df = pd.concat(all_dfs, ignore_index=True)
    
    return concatenated_df

# %% ../nbs/05_dataset.ipynb 13
def substitute_values_from_df(values: List[Any],         # List of values to be substituted.
                              df: pd.DataFrame,          # DataFrame containing the mapping.
                              goal_column: str,          # Column in the DataFrame to get the substitution values from.
                              id_column: str = 'Id'      # Column in the DataFrame to match the values with. Default is 'Id'.
                             ) -> List[Any]:
    """
    Substitute values in the given list based on the mapping from a DataFrame's id column to goal column.

    Parameters:
    values (List[Any]): List of values to be substituted.
    df (pd.DataFrame): DataFrame containing the mapping from id_column to goal_column.
    goal_column (str): Column in the DataFrame to get the substitution values from.
    id_column (str, optional): Column in the DataFrame to match the values with. Default is 'Id'.

    Returns:
    List[Any]: A list with substituted values from the DataFrame's goal_column.
    """
    # Create a dictionary for substitution from the DataFrame
    substitution_dict = df.set_index(id_column)[goal_column].to_dict()

    # Substitute the values in the list using the dictionary
    substituted_values = [substitution_dict.get(value, value) for value in values]

    return substituted_values

# %% ../nbs/05_dataset.ipynb 14
def get_orbit_classes(values: List[Any]) -> Tuple[List[Any], List[Any], List[Any], List[Any]]:
    """
    Get orbit classes based on the given values and DataFrame. Returns four lists corresponding
    to 'Label', 'Type', 'Subtype', and 'Direction' columns.

    Parameters:
    values (List[Any]): List of values to be substituted.

    Returns:
    Tuple[List[Any], List[Any], List[Any], List[Any]]: Four lists with substituted values from 'Label', 'Type', 'Subtype', and 'Direction' columns.
    """
    labels = substitute_values_from_df(values, ORBIT_CLASS_DF, 'Label')
    types = substitute_values_from_df(values, ORBIT_CLASS_DF, 'Type')
    subtypes = substitute_values_from_df(values, ORBIT_CLASS_DF, 'Subtype')
    directions = substitute_values_from_df(values, ORBIT_CLASS_DF, 'Direction')

    return labels, types, subtypes, directions

# %% ../nbs/05_dataset.ipynb 17
def get_periods_of_orbit_dict(orbits: Dict[int, np.ndarray],         # Dictionary of orbits with numerical keys.
                              propagated_periods: Dict[int, int],    # Dictionary of propagated periods for each orbit.
                              desired_periods: int                   # Desired number of periods.
                             ) -> Dict[int, np.ndarray]:             # Processed dictionary of orbits.
    """
    Process the orbits to extract the desired periods and print the percentage of the dataset returned.
    """
    processed_orbits = {}
    total_length_before = 0
    total_length_after = 0
    
    for key, orbit in orbits.items():
        total_length_before += orbit.shape[1]
        if key in propagated_periods:
            num_propagated = propagated_periods[key]
            if num_propagated >= desired_periods:
                # Calculate the length to take
                length_per_period = orbit.shape[1] // num_propagated
                length_to_take = length_per_period * desired_periods
                # Take the desired periods from the beginning
                processed_orbits[key] = orbit[:, :int(length_to_take) + 1]
                total_length_after += length_to_take + 1
            else:
                # Raise an error if the number of propagated periods is less than desired
                raise ValueError(f"The number of propagated periods ({num_propagated}) for orbit {key} is less than the desired periods ({desired_periods}).")
        else:
            # Raise an error if the key is not in propagated_periods
            raise KeyError(f"Key {key} is not found in propagated_periods.")
    
    # Calculate and print the percentage of the dataset returned
    percentage_returned = (total_length_after / total_length_before) * 100
    print(f"Percentage of the dataset returned: {percentage_returned:.2f}%")
    
    return processed_orbits


# %% ../nbs/05_dataset.ipynb 19
def get_first_period_of_fixed_period_dataset(file_path: str              # Path to the HDF5 file.
                                            ) -> Tuple[np.ndarray,       # 3D numpy array of padded orbits.
                                                    pd.DataFrame,        # DataFrame containing orbit features.
                                                    Dict[str, float]]:   # Dictionary containing system features.
    """
    Load and process orbit data from an HDF5 file for the first period.
    """
    # Load the orbit data, features dataframe, and system dictionary from the HDF5 file
    orbits, orbit_df, system_dict = get_orbit_data_from_hdf5(file_path)

    # Extract propagated periods and periods from the DataFrame
    propagated_periods = orbit_df['propagated_periods'].tolist()
    periods = orbit_df['period'].tolist()

    # Remove the file type and extract parts of the file name to determine processing steps
    file_name = os.path.basename(file_path).split('.')[0]
    file_parts = file_name.split('_')

    # Check if the second part of the file name is 'N'
    if file_parts[1] == 'N':
        # Add time vectors to the orbits
        orbits = add_time_vector_to_orbits(orbits, propagated_periods, periods)
        # Pad and convert the orbits to a 3D array using the fourth part of the file name as timesteps
        orbits = pad_and_convert_to_3d(orbits, int(file_parts[3]))

    return orbits, orbit_df, system_dict


# %% ../nbs/05_dataset.ipynb 21
def get_full_fixed_step_dataset(file_path: str,                   # Path to the HDF5 file.
                                segment_length: int               # Desired length of each segment.
                                ) -> Tuple[np.ndarray,            # 3D numpy array of segmented orbits.
                                        pd.DataFrame,             # DataFrame containing orbit features.
                                        List[int],                # List of IDs representing each new segment.
                                        Dict[str, float]]:        # Dictionary containing system features.
    """
    Load and process orbit data from an HDF5 file, segmenting each orbit into specified length.
    """
    # Load the orbit data, features dataframe, and system dictionary from the HDF5 file
    orbits, orbit_df, system_dict = get_orbit_data_from_hdf5(file_path)

    # Check if the second part of the file name is 'dt'
    if os.path.basename(file_path).split('_')[1] == 'dt':
        # Segment the orbits and get the corresponding segment IDs
        orbits, orbits_ids = segment_and_convert_to_3d(orbits, segment_length)

    return orbits, orbit_df, orbits_ids, system_dict

# %% ../nbs/05_dataset.ipynb 22
def get_first_period_fixed_step_dataset(file_path: str,                  # Path to the HDF5 file.
                                        segment_length: int              # Desired length of each segment.
                                       ) -> Tuple[np.ndarray,            # 3D numpy array of segmented orbits.
                                               pd.DataFrame,             # DataFrame containing orbit features.
                                               List[int],                # List of IDs representing each new segment.
                                               Dict[str, float]]:        # Dictionary containing system features.
    """
    Load and process orbit data from an HDF5 file, segmenting each orbit into specified length.
    """
    # Load the orbit data, features dataframe, and system dictionary from the HDF5 file
    orbits, orbit_df, system_dict = get_orbit_data_from_hdf5(file_path)

    # Get the propagated periods from the orbit_df
    propagated_periods = orbit_df['propagated_periods'].to_dict()

    # Process orbits to extract the first desired period
    orbits = get_periods_of_orbit_dict(orbits, propagated_periods, desired_periods=1)
    
    # Check if the second part of the file name is 'dt'
    if os.path.basename(file_path).split('_')[1] == 'dt':
        # Segment the orbits and get the corresponding segment IDs
        orbits, orbits_ids = segment_and_convert_to_3d(orbits, segment_length)

    return orbits, orbit_df, orbits_ids, system_dict
