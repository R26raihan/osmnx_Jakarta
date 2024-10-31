import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
from flask import Flask, render_template, request
from io import BytesIO
import base64
from math import radians, cos, sin, sqrt, atan2
from haversine import haversine
from functools import lru_cache

# Fungsi untuk menghitung jarak haversine antara dua titik koordinat (lat, lon)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius bumi dalam kilometer
    phi1, phi2 = radians(lat1), radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)
    
    a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c  # Jarak dalam kilometer

# Fungsi untuk meng-cache pengambilan jaringan jalan
@lru_cache(maxsize=None)
def get_graph():
    # Ambil jaringan jalan dari Jakarta
    return ox.graph_from_place("Jakarta, Indonesia", network_type="drive")

# Fungsi untuk menghasilkan gambar rute dan mengambil nama jalan
@lru_cache(maxsize=None)
def generate_route_image(origin, destination):
    G = get_graph()  # Ambil jaringan jalan dari cache

    # Geocode untuk mendapatkan koordinat asal dan tujuan
    origin_coord = ox.geocode(origin)
    destination_coord = ox.geocode(destination)

    # Dapatkan node terdekat dari titik awal dan akhir
    orig_node = ox.distance.nearest_nodes(G, origin_coord[1], origin_coord[0])
    dest_node = ox.distance.nearest_nodes(G, destination_coord[1], destination_coord[0])

    # Hitung rute tercepat dengan A* menggunakan haversine sebagai heuristik
    route = nx.astar_path(G, orig_node, dest_node, heuristic=lambda u, v: haversine(G.nodes[u]['y'], G.nodes[u]['x'], G.nodes[v]['y'], G.nodes[v]['x']), weight="length")

    # Mendapatkan nama jalan yang dilewati dan hanya simpan nama unik
    route_streets = []
    seen_streets = set()  # Menggunakan set untuk menyimpan nama jalan yang sudah ditambahkan
    for u, v in zip(route[:-1], route[1:]):
        # Ambil data tepi antara dua node, periksa apakah ada beberapa segmen
        edge_data = G.get_edge_data(u, v)
        if edge_data:
            for key, data in edge_data.items():
                street_name = data.get('name', 'Unnamed road')
                if isinstance(street_name, str) and street_name not in seen_streets:
                    route_streets.append(street_name)
                    seen_streets.add(street_name)

    # Plot jaringan dan rute
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Mengatur warna latar belakang peta menjadi putih
    ax.set_facecolor('black')  # Ganti 'black' dengan 'white'
    
    gdf_edges = ox.graph_to_gdfs(G, nodes=False, edges=True)
    gdf_edges.plot(ax=ax, linewidth=0.5, edgecolor="black")  # Warna jalan biasa
    gdf_edges.loc[route].plot(ax=ax, linewidth=3, edgecolor="green")  # Warna rute
    plt.title(f"Rute Tercepat dari {origin} ke {destination}", fontsize=15)
    plt.axis("off")

    # Simpan gambar ke dalam objek BytesIO
    img = BytesIO()
    plt.savefig(img, format="png", bbox_inches="tight")
    img.seek(0)
    plt.close(fig)
    
    # Encode gambar ke string Base64
    img_base64 = base64.b64encode(img.read()).decode("utf-8")
    
    return img_base64, route_streets

# Inisialisasi Flask
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    img_base64 = None
    route_streets = None

    if request.method == "POST":
        # Ambil input lokasi awal dan tujuan dari pengguna
        origin = request.form.get("origin")
        destination = request.form.get("destination")

        # Generate gambar rute dan daftar nama jalan
        img_base64, route_streets = generate_route_image(origin, destination)

    return render_template("index.html", img_data=img_base64, route_streets=route_streets)

if __name__ == "__main__":
    app.run(debug=True)
