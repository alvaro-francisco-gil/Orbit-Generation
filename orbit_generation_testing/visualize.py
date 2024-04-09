# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_visualization.ipynb.

# %% auto 0
__all__ = ['visualize_static_orbits', 'export_dynamic_orbits_html']

# %% ../nbs/02_visualization.ipynb 2
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from pytest import raises

# %% ../nbs/02_visualization.ipynb 7
def visualize_static_orbits(data, time_instants=None, orbit_indices=None, show_legend=False, point_dict=None):
    """
    Visualizes orbits and highlights specified time instants for every orbit in orbit_indices with data shape (num_orbits, 6, num_time_points).

    :param data: numpy.ndarray, shape (num_orbits, 6, num_time_points), containing orbit data.
    :param time_instants: Optional[list[int]], time instants to highlight across selected orbits. If None or empty, no highlights are made.
    :param orbit_indices: Optional[list], indices of the orbits to visualize and highlight. If None, uses all orbits.
    :param show_legend: Optional[bool], indicates whether to show the legend.
    :param point_dict: Optional[dict], dictionary where keys are point names and values are the 3D coordinates of the points.
    """
    
    if time_instants is None:
        time_instants = []  # Ensure time_instants is a list if None is provided
    
    # Validate time instants before plotting
    max_time_instants = data.shape[2]
    for time_instant in time_instants:
        if time_instant < 0 or time_instant >= max_time_instants:
            raise ValueError(f"Time instant {time_instant} is out of range.")
    
    # Validate orbit indices before plotting
    num_orbits = data.shape[0]
    if orbit_indices is None:
        orbit_indices = range(num_orbits)  # Default to all orbits
    else:
        for index in orbit_indices:
            if index < 0 or index >= num_orbits:
                raise ValueError(f"Orbit index {index} is out of range.")
    
    # Proceed with plotting after successful validation
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    for index in orbit_indices:
        X = data[index, 0, :]  # X coordinates
        Y = data[index, 1, :]  # Y coordinates
        Z = data[index, 2, :]  # Z coordinates
        ax.plot(X, Y, Z, label=f'Orbit {index}', alpha=0.5)  # Plot orbits with reduced alpha to emphasize highlights

        # Highlight the specified time instants for each orbit, if any
        if time_instants:
            for time_instant in time_instants:
                posx, posy, posz = data[index, 0:3, time_instant]
                ax.scatter(posx, posy, posz, color='red', s=100, zorder=5)
    
    # Plot additional points if point_dict is provided
    if point_dict:
        for point_name, coords in point_dict.items():
            ax.scatter(*coords, label=point_name, s=100, depthshade=True)
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.title('3D Orbits Static Visualization')

    if show_legend:
        ax.legend()

    plt.show()

# %% ../nbs/02_visualization.ipynb 11
def export_dynamic_orbits_html(data, time_instants=None, orbit_indices=None, point_dict=None, filename='orbits.html'):
    """
    Visualize orbits in 3D and save as an interactive HTML file with a clickable legend, for data organized as (num_orbits, 6, num_time_points).
    Includes the option to add named points to the visualization and highlights the positions of each orbit at given time_instants.

    :param data: Numpy array of shape (num_orbits, 6, num_time_points)
    :param time_instants: Optional[List of int], the time instants to highlight across all orbits. If None or empty, no highlights are made.
    :param orbit_indices: Optional; List of indices of the orbits to visualize
    :param filename: String, name of the file to save the HTML plot
    :param point_dict: Optional; Dictionary where keys are point names and values are the 3D coordinates of the points
    """
    if time_instants is None:
        time_instants = []  # Ensure time_instants is a list if None is provided

    num_orbits = data.shape[0]  # Adjusted for the new data shape
    if orbit_indices is None:
        orbit_indices = range(num_orbits)  # Default to all orbits

    fig = go.Figure()

    # Plot each orbit
    for index in orbit_indices:
        if index < 0 or index >= num_orbits:
            raise ValueError(f"Orbit index {index} is out of range.")
        
        # Extract coordinates
        X = data[index, 0, :]  # X coordinates
        Y = data[index, 1, :]  # Y coordinates
        Z = data[index, 2, :]  # Z coordinates

        fig.add_trace(go.Scatter3d(x=X, y=Y, z=Z, mode='lines',
                                   name=f'Orbit {index}',
                                   legendgroup=f'orbit{index}',
                                   showlegend=True))

        # Highlight the positions at the given time_instants, if any
        if time_instants:
            for timestamp in time_instants:
                if timestamp < 0 or timestamp >= data.shape[2]:
                    raise ValueError(f"The provided timestamp {timestamp} is out of range.")
                highlight_x = [data[index, 0, timestamp]]
                highlight_y = [data[index, 1, timestamp]]
                highlight_z = [data[index, 2, timestamp]]
                fig.add_trace(go.Scatter3d(x=highlight_x, y=highlight_y, z=highlight_z, mode='markers',
                                           marker=dict(size=5, color='red'),
                                           name=f'Highlight {index} @ {timestamp}',
                                           legendgroup=f'orbit{index}',
                                           showlegend=False))

    # Add points from the point_dict if provided
    if point_dict is not None:
        for point_name, coords in point_dict.items():
            fig.add_trace(go.Scatter3d(x=[coords[0]], y=[coords[1]], z=[coords[2]], mode='markers',
                                       marker=dict(size=5),
                                       name=point_name))

    fig.update_layout(title='3D Orbits Visualization',
                      scene=dict(xaxis_title='X',
                                 yaxis_title='Y',
                                 zaxis_title='Z'),
                      width=800, height=600,
                      legend_title="Orbits Legend",
                      clickmode='event+select')

    fig.write_html(filename)
    print(f"Visualization saved to {filename}")


