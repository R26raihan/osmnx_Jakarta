![Untitled](https://github.com/user-attachments/assets/195e6d6e-0c48-4dbb-bfe1-b7062a4245d0)

🚀 Exploring Routes with Flask, OSMnx, and NetworkX! 🗺️
Welcome to our route-planning application! This Python code snippet combines the power of Flask, OSMnx, and NetworkX to help users find the fastest driving route in Jakarta, Indonesia. Let’s break down the magic step-by-step! ✨

1. Importing Libraries 📚
python
Salin kode
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
from flask import Flask, render_template, request
from io import BytesIO
import base64
from math import radians, cos, sin, sqrt, atan2
from functools import lru_cache
We start by importing essential libraries:

OSMnx for downloading and modeling street networks from OpenStreetMap.
NetworkX to work with graph data structures.
Matplotlib to visualize the routes.
Flask to create our web application.
BytesIO and Base64 for handling image data.
Some math functions to calculate distances.
2. Haversine Function 🌐
python
Salin kode
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in kilometers
    phi1, phi2 = radians(lat1), radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)
    
    a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c  # Distance in kilometers
Here, we define the Haversine formula to calculate the distance between two geographic points. This formula is essential for determining how far apart our origin and destination are! 🌍

3. Caching the Graph 🗄️
python
Salin kode
@lru_cache(maxsize=None)
def get_graph():
    return ox.graph_from_place("Jakarta, Indonesia", network_type="drive")
Using LRU cache, we store the street network graph of Jakarta. This means if we request the graph multiple times, we won’t have to fetch it from scratch each time—saving us some valuable processing time! ⏱️

4. Generating Route Image 🎨
python
Salin kode
@lru_cache(maxsize=None)
def generate_route_image(origin, destination):
    G = get_graph()  # Fetch the street network from cache

    # Geocode to get coordinates for origin and destination
    origin_coord = ox.geocode(origin)
    destination_coord = ox.geocode(destination)

    # Find the nearest nodes in the graph
    orig_node = ox.distance.nearest_nodes(G, origin_coord[1], origin_coord[0])
    dest_node = ox.distance.nearest_nodes(G, destination_coord[1], destination_coord[0])

    # Calculate the fastest route using A* algorithm
    route = nx.astar_path(G, orig_node, dest_node, heuristic=lambda u, v: haversine(G.nodes[u]['y'], G.nodes[u]['x'], G.nodes[v]['y'], G.nodes[v]['x']), weight="length")

    # Gather unique street names along the route
    route_streets = []
    seen_streets = set()
    for u, v in zip(route[:-1], route[1:]):
        edge_data = G.get_edge_data(u, v)
        if edge_data:
            for key, data in edge_data.items():
                street_name = data.get('name', 'Unnamed road')
                if isinstance(street_name, str) and street_name not in seen_streets:
                    route_streets.append(street_name)
                    seen_streets.add(street_name)

    # Plot the route on the map
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_facecolor('black')
    gdf_edges = ox.graph_to_gdfs(G, nodes=False, edges=True)
    gdf_edges.plot(ax=ax, linewidth=0.5, edgecolor="black")  # Normal road color
    gdf_edges.loc[route].plot(ax=ax, linewidth=3, edgecolor="green")  # Route color
    plt.title(f"Fastest Route from {origin} to {destination}", fontsize=15)
    plt.axis("off")

    # Save the image to BytesIO
    img = BytesIO()
    plt.savefig(img, format="png", bbox_inches="tight")
    img.seek(0)
    plt.close(fig)
    
    # Encode the image to Base64
    img_base64 = base64.b64encode(img.read()).decode("utf-8")
    
    return img_base64, route_streets
In this function, we:

Fetch the street graph and geocode the origin and destination.
Find the nearest nodes in the graph and calculate the fastest route using the A* algorithm.
Collect unique street names along the route.
Generate a beautiful plot of the route on a map and save it as a Base64 string, so it can be easily rendered in the web app! 🖼️
5. Setting Up Flask 🏗️
python
Salin kode
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    img_base64 = None
    route_streets = None

    if request.method == "POST":
        origin = request.form.get("origin")
        destination = request.form.get("destination")

        # Generate route image and street names
        img_base64, route_streets = generate_route_image(origin, destination)

    return render_template("index.html", img_data=img_base64, route_streets=route_streets)

if __name__ == "__main__":
    app.run(debug=True)
Finally, we set up our Flask application:

Define a route (/) to handle GET and POST requests.
On a POST request, we retrieve the origin and destination from the user, generate the route image and street names, and then render them on an HTML page.
When run, the app starts in debug mode, making it easier to see any errors as they occur! 🚦
Conclusion 🎉
This code structure is a fantastic example of how to combine several powerful libraries to create a user-friendly application that visualizes the fastest route in a bustling city like Jakarta. With its caching for performance and the beautiful visuals, this app is a great tool for urban explorers and drivers alike! 🏙️

Feel free to explore, modify, and make it even better! Happy coding! 💻✨
