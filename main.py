"""
# Abstract
This program takes in the paths of 2 log files, each representing the trajectory of the veichle.
Running the file will generate a series of comparison statistics between the trajectories.

Each log file is a csv file with the following columns:
x,y,heading,s,dst,angle,delta

# Example
```
python main.py <path/to/ideal_trajectory.csv> <path/to/real_trajectory.csv>
```
"""

import matplotlib.pyplot as plt
import os
import pandas as pd # type: ignore

import errors
from settings import Settings

# def draw_trajectory(plot, points: list)-> None:
#     pass

COLORED_OK= "\033[32m[ OK ]\033[0m"
COLORED_WARNING= "\033[33m[ WARNING ]\033[0m"

def get_trajectory_points(file_path: str, verbose: bool= False)-> list:
    try:
        dataframe= pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        raise errors.EmptyFileError(file_path, "File {filename} is empty.\nTo solve this issue, try passing a log file that has an x and a y parameter in its columns.")

    if dataframe.empty and verbose: print(f"{COLORED_WARNING} The file {file_path} does not contain any values.")

    ###                                        ###
    ### Checking wether required columns exist ###
    ###                                        ###

    if 'x' not in dataframe.columns:
        raise errors.UnexistentRequiredColumn('x', filename= file_path)
    if 'y' not in dataframe.columns:
        raise errors.UnexistentRequiredColumn('y', filename= file_path)

    return list(zip(dataframe.x, dataframe.y))

def check_file_opens(file_path: str)-> bool:
    try:
        with open(file_path, 'r'):
            return
    except IOError:
        raise errors.FileOpeningError(file_path)

def main(settings: Settings) -> None:
    VERBOSE= settings.get("general.verbose", False)

    OUTPUT_DIRECTORY= settings.get("files.output_directory", "output")
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)

        if VERBOSE:
            print(f"{COLORED_OK} Directory '{OUTPUT_DIRECTORY}' created.")

    ###                        ###
    ### Checking if files open ###
    ###                        ###

    expected_trajectory_file= settings.get("files.expected_trajectory_log_file", "undefined_file")
    real_trajectory_file= settings.get("files.real_trajectory_log_file", "undefined_file")
    check_file_opens(expected_trajectory_file)
    check_file_opens(real_trajectory_file)

    ###                                ###
    ### Initializing trajectories plot ###
    ###                                ###

    expected_trajectory_points= get_trajectory_points(expected_trajectory_file, VERBOSE)
    real_trajectory_points=     get_trajectory_points(real_trajectory_file, VERBOSE)

    if VERBOSE: print(f"{COLORED_OK} Succesfully extracted trajectory points.")

    ###                                        ###
    ### Calculating the dimensions of the plot ###
    ###                                        ###

    coordinate_bounds={
        "top": max(max(expected_trajectory_points, key= lambda x: x[1])[1], max(real_trajectory_points, key= lambda x: x[1])[1]),
        "right": max(max(expected_trajectory_points, key= lambda x: x[0])[0], max(real_trajectory_points, key= lambda x: x[0])[0]),
        "bottom": min(min(expected_trajectory_points, key= lambda x: x[1])[1], min(real_trajectory_points, key= lambda x: x[1])[1]),
        "left": min(min(expected_trajectory_points, key= lambda x: x[0])[0], min(real_trajectory_points, key= lambda x: x[0])[0])
    }

    TITLE= settings.get("trajectories_comparisons_plot.title", "Trajectories Comparisons")
    BACKGROUND_COLOR= settings.get("trajectories_comparisons_plot.background_color", "#FFFFFF")
    fig, ax = plt.subplots()
    ax.set_title(TITLE)
    ax.set_facecolor(BACKGROUND_COLOR)
    ax.set_xlim(coordinate_bounds["left"], coordinate_bounds["right"])
    ax.set_ylim(coordinate_bounds["bottom"], coordinate_bounds["top"])

    ###                          ###
    ### Drawing the trajectories ###
    ###                          ###

    ###                 ###
    ### Saving the plot ###
    ###                 ###

    trajectories_comparison_output_path= os.path.join(OUTPUT_DIRECTORY, settings.get("trajectories_comparisons_plot.filename", "trajectories_comparison.png"))
    plt.savefig(trajectories_comparison_output_path)

    if VERBOSE:
        print(f"{COLORED_OK} Succesfully saved plot to {trajectories_comparison_output_path}")


if __name__ == "__main__":
    ###                     ###
    ### Extracting settings ###
    ###                     ###

    settings= Settings("settings.json")

    main(settings)