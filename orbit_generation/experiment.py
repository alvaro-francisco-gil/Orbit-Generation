# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/08_experiment.ipynb.

# %% auto 0
__all__ = ['setup_new_experiment']

# %% ../nbs/08_experiment.ipynb 2
import os
import csv
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple

from .constants import ORBIT_CLASS_DF

# %% ../nbs/08_experiment.ipynb 3
def setup_new_experiment(params: Dict[str, Any],              # Dictionary of parameters for the new experiment.
                         experiments_folder: str,             # Path to the folder containing all experiments.
                         csv_file: Optional[str] = None       # Optional path to the CSV file tracking experiment parameters.
                        ) -> str:                             # The path to the newly created experiment folder.
    """
    Sets up a new experiment by creating a new folder and updating the CSV file with experiment parameters.

    Parameters:
    params (Dict[str, Any]): A dictionary of parameters for the new experiment.
    experiments_folder (str): Path to the folder containing all experiments.
    csv_file (Optional[str]): Optional path to the CSV file tracking experiment parameters. Default is None, which sets the file to 'experiments.csv' in the experiments_folder.

    Returns:
    str: The path to the newly created experiment folder.
    """
    # Ensure the experiments folder exists
    if not os.path.exists(experiments_folder):
        os.makedirs(experiments_folder)

    # Default CSV file to 'experiments.csv' in the experiments_folder if not provided
    if csv_file is None:
        csv_file = os.path.join(experiments_folder, 'experiments.csv')

    # Determine the next experiment number
    experiment_folders = [d for d in os.listdir(experiments_folder) if os.path.isdir(os.path.join(experiments_folder, d))]
    experiment_numbers = [int(folder.split(' ')[-1]) for folder in experiment_folders if folder.startswith('experiment')]
    next_experiment_number = max(experiment_numbers, default=0) + 1

    # Create a new folder for the next experiment
    new_experiment_folder = os.path.join(experiments_folder, f'experiment {next_experiment_number}')
    os.makedirs(new_experiment_folder)

    # Update the CSV file with the new experiment's parameters
    csv_exists = os.path.isfile(csv_file)
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        # Write header if the CSV does not exist
        if not csv_exists:
            header = ['id'] + list(params.keys())
            writer.writerow(header)
        # Write the experiment parameters
        row = [next_experiment_number] + list(params.values())
        writer.writerow(row)

    print(f'New experiment setup complete: {new_experiment_folder}')
    print(f'Parameters saved to {csv_file}.')

    return new_experiment_folder