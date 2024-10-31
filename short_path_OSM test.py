import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
from flask import Flask, render_template, request
from io import BytesIO
import base64
from math import radians, cos, sin, sqrt, atan2

# Fungsi untuk menghitung jarak haversine antara dua titik koordinat (lat, lon)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius bumi dalam kilometer
    phi1, phi2 = radians(lat1), radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)
    
    a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c  # Jarak dalam kilometer

# Fungsi untuk menghasilkan gambar rute dan mengambil nama jalan
def generate_route_image(origin_input, destination_input):
    # Ambil jaringan jalan dari Jakarta
    place_name = "Jakarta, Indonesia"
    G = ox.graph_from_place(place_name, network_type="drive")

    # Tentukan titik awal dan akhir berdasarkan input pengguna
    origin = ox.geocode(origin_input)  # Ambil koordinat dari input
    destination = ox.geocode(destination_input)  # Ambil koordinat dari input

    # Dapatkan node terdekat dari titik awal dan akhir
    orig_node = ox.distance.nearest_nodes(G, origin[1], origin[0])
    dest_node = ox.distance.nearest_nodes(G, destination[1], destination[0])

    # Hitung rute tercepat dengan A* menggunakan haversine sebagai heuristik
    route = nx.astar_path(G, orig_node, dest_node, heuristic=lambda u, v: haversine(G.nodes[u]['y'], G.nodes[u]['x'], G.nodes[v]['y'], G.nodes[v]['x']), weight="length")

    # Konversi jaringan menjadi GeoDataFrame untuk plotting
    gdf_edges = ox.graph_to_gdfs(G, nodes=False, edges=True)
    route_edges = gdf_edges.loc[route]

    # Mendapatkan nama jalan yang dilewati
    route_streets = []
    seen_streets = set()  # Set untuk menyimpan nama jalan yang sudah ditambahkan
    for u, v in zip(route[:-1], route[1:]):
        edge_data = G.get_edge_data(u, v)
        street_name = edge_data[0].get('name', 'Unnamed road')  # Nama jalan atau 'Unnamed road'
        # Pastikan street_name adalah string dan belum ada di set
        if street_name not in seen_streets:
            seen_streets.add(street_name)
            route_streets.append(street_name)

    # Plot jaringan dan rute
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf_edges.plot(ax=ax, linewidth=0.5, edgecolor="black")
    route_edges.plot(ax=ax, linewidth=3, edgecolor="red")

    plt.title("Rute Tercepat dari {} ke {}".format(origin_input, destination_input))
    plt.axis("off")

    # Simpan gambar ke dalam objek BytesIO, lalu kirim sebagai respons
    img = BytesIO()
    plt.savefig(img, format="png", bbox_inches="tight")
    img.seek(0)  # Set posisi kembali ke awal
    plt.close(fig)
    
    # Encode gambar ke string Base64
    img_base64 = base64.b64encode(img.read()).decode("utf-8")
    
    return img_base64, route_streets

# Inisialisasi Flask
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    img_base64 = None
    route_streets = []
    
    if request.method == "POST":
        # Ambil input lokasi dari form
        origin_input = request.form['origin']
        destination_input = request.form['destination']
        
        # Generate gambar rute dan daftar nama jalan
        img_base64, route_streets = generate_route_image(origin_input, destination_input)
    
    return render_template("index.html", route_streets=route_streets, img_data=img_base64)

if __name__ == "__main__":
    app.run(debug=True)
