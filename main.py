"""
# Abstract
This script compares two trajectories by plotting them on a graph using matplotlib.
It reads trajectory data from CSV files, processes the data, and generates a plot
that visually compares the expected and real trajectories.

# Usage
Run this script as the main module to generate a plot comparing the expected and real trajectories.
Play with the settings in the settings.json file.
"""

import matplotlib # type: ignore
import matplotlib.pyplot as plt # type: ignore
import os
import pandas as pd # type: ignore

import errors
from settings import Settings

matplotlib.use("Agg")

COLORED_OK= "\033[32m[ OK ]\033[0m"
COLORED_WARNING= "\033[33m[ WARNING ]\033[0m"
ROWS= 2
COLUMNS= 3

CM2INCH= 0.393701
RADIANS2DEGREES= 57.29577951308232

def angle_timeline_comparison_template(plot: plt.Axes, first_path_args: dict, second_path_args: dict, background_color: str= None, title_args: dict= None, axes_args: dict= dict(), grid_args: dict= dict(), legend_args: dict= dict())-> None:
    DEFAULT_BACKGROUND_COLOR= "#FFFFFF"
    DEFAULT_TEXT_COLOR= "#000000"
    DEFAULT_FIRST_TRAJECTORY_COLOR= "#FF0000"
    DEFAULT_SECOND_TRAJECTORY_COLOR= "#00FF00"

    ###                    ###
    ### Handling the title ###
    ###                    ###

    if title_args is not None:
        plot.set_title(
            label= title_args.get("text", "TITLE"),
            loc= title_args.get("loc", "left"),
            color= title_args.get("color", DEFAULT_TEXT_COLOR)
        )

    ###                               ###
    ### Handling the background color ###
    ###                               ###

    plot.set_facecolor((background_color if (background_color is not None) else DEFAULT_BACKGROUND_COLOR))

    ###               ###
    ### Handling axes ###
    ###               ###

    if axes_args.get("show", True):
        plot.spines["top"].set_color("none")
        plot.spines["right"].set_color("none")
        plot.spines["bottom"].set_color(axes_args.get("color", DEFAULT_TEXT_COLOR))
        plot.spines["left"].set_color(axes_args.get("color", DEFAULT_TEXT_COLOR))


        plot.spines["bottom"].set_position("zero") # Fix x-axis to 0 of y-axis
        plot.tick_params(axis="both", colors=axes_args.get("color", DEFAULT_TEXT_COLOR)) # Show ticks
        plot.plot(1, 0, ">", color=axes_args.get("color", DEFAULT_TEXT_COLOR), transform=plot.get_yaxis_transform(), clip_on=False)

    else:
        for spine in plot.spines.values():
            spine.set_visible(False)

        plot.xaxis.set_ticks_position("none")
        plot.yaxis.set_ticks_position("none")

    ###               ###
    ### Handling grid ###
    ###               ###

    if grid_args.get("show", True):
        plot.grid(
            True,
            which="major",
            axis="y",
            color=grid_args.get("color", DEFAULT_TEXT_COLOR),
            linestyle="--",
            linewidth=0.5
        )

    ###                  ###
    ### Handling drawing ###
    ###                  ###

    x_axis_upper_bound= max(first_path_args["data"]["x"]+second_path_args["data"]["x"])

    plot.set_xlim(xmin=0, xmax= x_axis_upper_bound)
    plot.set_ylim(ymin=180, ymax= -180)

    plot.plot(
        first_path_args["data"]["x"],
        [heading*RADIANS2DEGREES for heading in first_path_args["data"]["y"]],
        label=first_path_args.get("label", "Trajectory 1"),
        color=first_path_args.get("color", DEFAULT_FIRST_TRAJECTORY_COLOR)
    )
    plot.plot(
        second_path_args["data"]["x"],
        [heading*RADIANS2DEGREES for heading in second_path_args["data"]["y"]],
        label=second_path_args.get("label", "Trajectory 2"),
        color=second_path_args.get("color", DEFAULT_SECOND_TRAJECTORY_COLOR)
    )

    ###                 ###
    ### Handling Legend ###
    ###                 ###

    if legend_args.get("show", True):
        plt.legend(facecolor= legend_args.get("background_color", DEFAULT_TEXT_COLOR), labelcolor= legend_args.get("text_color", DEFAULT_BACKGROUND_COLOR), framealpha= 1, loc="lower right")

def read_trajectory(file_path: str, verbose: bool= False)-> pd.DataFrame:
    try:
        dataframe= pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        raise errors.EmptyFileError(file_path, "File {filename} is empty.\nTo solve this issue, try passing a log file that has an x and a y parameter in its columns.")

    if dataframe.empty and verbose: print(f"{COLORED_WARNING} The file {file_path} does not contain any values.")

    return dataframe

def get_column(column_name: str, file_path: str, verbose: bool= False)-> list:
    dataframe= read_trajectory(file_path, verbose)

    ###                                        ###
    ### Checking wether required columns exist ###
    ###                                        ###

    if column_name not in dataframe.columns:
        raise errors.UnexistentRequiredColumn(column_name, filename= file_path)

    return list(dataframe[column_name])

def draw_trajectory(points: list, label: str, color: str, thickness: int= 1, alpha: float= 0.75)-> None:
    x, y= zip(*points)
    plt.plot(x, y, label= label, color= color, linewidth= thickness, alpha= alpha)

def get_trajectory_points(file_path: str, verbose: bool= False)-> list:
    dataframe= read_trajectory(file_path, verbose)

    ###                                        ###
    ### Checking wether required columns exist ###
    ###                                        ###

    if "x" not in dataframe.columns:
        raise errors.UnexistentRequiredColumn("x", filename= file_path)
    if "y" not in dataframe.columns:
        raise errors.UnexistentRequiredColumn("y", filename= file_path)

    return list(zip(dataframe.x, dataframe.y))

def check_file_opens(file_path: str)-> bool:
    try:
        with open(file_path, "r"):
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

    ###                       ###
    ### Initializing the plot ###
    ###                       ###

    background_color= settings.get("general_styling.background_color", "#FFFFFF")
    text_color= settings.get("general_styling.text_color", "#000000")
    plt.figure(
        figsize=(
            float(settings.get("general.width_cm", 32)) * CM2INCH,
            float(settings.get("general.height_cm", 48)) * CM2INCH
        ),
        facecolor= background_color
    )

    trajectories_plot= plt.subplot(ROWS, COLUMNS, (1, 1))
    trajectories_plot.set_title(
        settings.get("trajectories_comparisons_plot.title", "Trajectories Comparison"),
        loc= settings.get("trajectories_comparisons_plot.title_location", "left"),
        color= text_color
    )
    trajectories_plot.set_facecolor(background_color)

    if settings.get("trajectories_comparisons_plot.show_axes", False):
        trajectories_plot.spines["bottom"].set_color(
            settings.get("trajectories_comparisons_plot.axes_color", "#FFFFFF")
        )
        trajectories_plot.spines["left"].set_color(
            settings.get("trajectories_comparisons_plot.axes_color", "#FFFFFF")
        )
    else:
        for spine in trajectories_plot.spines.values():
            spine.set_visible(False)

        trajectories_plot.xaxis.set_ticks_position("none")
        trajectories_plot.yaxis.set_ticks_position("none")

    plt.subplots_adjust(left=0.05, right=.95, bottom=0.05, top=0.92)

    if settings.get("trajectories_comparisons_plot.show_grid", True):
        trajectories_plot.grid(
            True,
            which="major",
            axis="both",
            color=settings.get("trajectories_comparisons_plot.grid_color", "#000000"),
            linestyle="--",
            linewidth=0.5
        )

    plt.tick_params(
        axis="both",
        labelcolor=text_color
    )

    ###                     ###
    ### Setting plot bounds ###
    ###                     ###

    top_bound= max(max(expected_trajectory_points, key= lambda x: x[1])[1], max(real_trajectory_points, key= lambda x: x[1])[1])
    right_bound= max(max(expected_trajectory_points, key= lambda x: x[0])[0], max(real_trajectory_points, key= lambda x: x[0])[0])
    bottom_bound= min(min(expected_trajectory_points, key= lambda x: x[1])[1], min(real_trajectory_points, key= lambda x: x[1])[1])
    left_bound= min(min(expected_trajectory_points, key= lambda x: x[0])[0], min(real_trajectory_points, key= lambda x: x[0])[0])
    internal_padding= 10/100
    width= right_bound - left_bound
    height= top_bound - bottom_bound

    coordinate_bounds={
        "top": top_bound + (internal_padding * height),
        "right": right_bound + (internal_padding * width),
        "bottom": bottom_bound - (internal_padding * height),
        "left": left_bound - (internal_padding * width)
    }

    del top_bound, right_bound, bottom_bound, left_bound, internal_padding, width, height

    trajectories_plot.set_xlim(coordinate_bounds["left"], coordinate_bounds["right"])
    trajectories_plot.set_ylim(coordinate_bounds["bottom"], coordinate_bounds["top"])

    ###                          ###
    ### Drawing the trajectories ###
    ###                          ###

    draw_trajectory(
        expected_trajectory_points,
        settings.get("expected_trajectory.label", "Expected Trajectory"),
        settings.get("expected_trajectory.color", "#FF0000"),
        settings.get("expected_trajectory.line_width", 2),
        settings.get("expected_trajectory.alpha", 0.75)
    )
    draw_trajectory(
        real_trajectory_points,
        settings.get("real_trajectory.label", "Real Trajectory"),
        settings.get("real_trajectory.color", "#00FF00"),
        settings.get("real_trajectory.line_width", 2),
        settings.get("real_trajectory.alpha", .75)
    )

    if settings.get("trajectories_comparisons_plot.show_legend", True):
        plt.legend(facecolor= text_color, labelcolor= background_color, framealpha= 1, loc="lower right")

    ###                                        ###
    ### Initializing the heading-timeline plot ###
    ###                                        ###

    heading_timeline_plot= plt.subplot(ROWS, COLUMNS, (4, 4))

    angle_timeline_comparison_template(
        heading_timeline_plot,
        first_path_args= {
            "data": {
                "x": get_column("s", expected_trajectory_file, VERBOSE),
                "y": get_column("heading", expected_trajectory_file, VERBOSE)
            },
            "label": settings.get("expected_trajectory.label", "Expected Heading"),
            "color": settings.get("expected_trajectory.color", "#FF0000")
        },
        second_path_args= {
            "data": {
                "x": get_column("s", real_trajectory_file, VERBOSE),
                "y": get_column("heading", real_trajectory_file, VERBOSE)
            },
            "label": settings.get("real_trajectory.label", "Real Heading"),
            "color": settings.get("real_trajectory.color", "#00FF00")
        },
        background_color= background_color,
        title_args= {
            "text": settings.get("heading_timeline_plot.title", "Heading Timeline"),
            "loc": settings.get("heading_timeline_plot.title_location", "left"),
            "color": text_color
        },
        axes_args= {
            "show": settings.get("heading_timeline_plot.show_axes", True),
            "color": settings.get("heading_timeline_plot.axes_color", "#000000")
        },
        grid_args= {
            "show": settings.get("heading_timeline_plot.show_grid", True),
            "color": settings.get("heading_timeline_plot.grid_color", "#000000")
        },
        legend_args= {
            "show": settings.get("heading_timeline_plot.show_legend", True),
            "background_color": text_color,
            "text_color": background_color,
        }
    )

    ###                                      ###
    ### Initializing the angle-timeline plot ###
    ###                                      ###

    angle_timepline_plot= plt.subplot(ROWS, COLUMNS, (5, 5))

    angle_timeline_comparison_template(
        angle_timepline_plot,
        first_path_args= {
            "data": {
                "x": get_column("s", expected_trajectory_file, VERBOSE),
                "y": get_column("angle", expected_trajectory_file, VERBOSE)
            },
            "label": settings.get("expected_trajectory.label", "Expected Angle"),
            "color": settings.get("expected_trajectory.color", "#FF0000")
        },
        second_path_args= {
            "data": {
                "x": get_column("s", real_trajectory_file, VERBOSE),
                "y": get_column("angle", real_trajectory_file, VERBOSE)
            },
            "label": settings.get("real_trajectory.label", "Real Angle"),
            "color": settings.get("real_trajectory.color", "#00FF00")
        },
        background_color= background_color,
        title_args= {
            "text": settings.get("angle_timeline_plot.title", "Angle Timeline"),
            "loc": settings.get("angle_timeline_plot.title_location", "left"),
            "color": text_color
        },
        axes_args= {
            "show": settings.get("angle_timeline_plot.show_axes", True),
            "color": settings.get("angle_timeline_plot.axes_color", "#000000")
        },
        grid_args= {
            "show": settings.get("angle_timeline_plot.show_grid", True),
            "color": settings.get("angle_timeline_plot.grid_color", "#000000")
        },
        legend_args= {
            "show": settings.get("angle_timeline_plot.show_legend", True),
            "background_color": text_color,
            "text_color": background_color,
        }
    )

    ###                                      ###
    ### Initializing the delta-timeline plot ###
    ###                                      ###

    delta_timeline_plot= plt.subplot(ROWS, COLUMNS, (6, 6))

    angle_timeline_comparison_template(
        delta_timeline_plot,
        first_path_args= {
            "data": {
                "x": get_column("s", expected_trajectory_file, VERBOSE),
                "y": get_column("delta", expected_trajectory_file, VERBOSE)
            },
            "label": settings.get("expected_trajectory.label", "Expected Delta"),
            "color": settings.get("expected_trajectory.color", "#FF0000")
        },
        second_path_args= {
            "data": {
                "x": get_column("s", real_trajectory_file, VERBOSE),
                "y": get_column("delta", real_trajectory_file, VERBOSE)
            },
            "label": settings.get("real_trajectory.label", "Real Delta"),
            "color": settings.get("real_trajectory.color", "#00FF00")
        },
        background_color= background_color,
        title_args= {
            "text": settings.get("delta_timeline_plot.title", "Delta Timeline"),
            "loc": settings.get("delta_timeline_plot.title_location", "left"),
            "color": text_color
        },
        axes_args= {
            "show": settings.get("delta_timeline_plot.show_axes", True),
            "color": settings.get("delta_timeline_plot.axes_color", "#000000")
        },
        grid_args= {
            "show": settings.get("delta_timeline_plot.show_grid", True),
            "color": settings.get("delta_timeline_plot.grid_color", "#000000")
        },
        legend_args= {
            "show": settings.get("delta_timeline_plot.show_legend", True),
            "background_color": text_color,
            "text_color": background_color,
        }
    )

    ###                 ###
    ### Saving the plot ###
    ###                 ###

    trajectories_comparison_output_path= os.path.join(OUTPUT_DIRECTORY, settings.get("files.filename", "trajectories_comparison.png"))
    plt.savefig(trajectories_comparison_output_path)

    if VERBOSE: print(f"{COLORED_OK} Succesfully saved the plot at '{trajectories_comparison_output_path}'.")

    ###                  ###
    ### Showing the plot ###
    ###                  ###

    plt.show()


if __name__ == "__main__":
    ###                     ###
    ### Extracting settings ###
    ###                     ###

    settings= Settings("settings.json")

    main(settings)