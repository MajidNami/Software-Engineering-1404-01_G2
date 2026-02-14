# 🗺️ Integrated Map Service (Team 9 Sub-module)

This directory contains the **Integrated Map Service**, a core component of the `Software-Engineering-1404-01_G2` project. This module provides a high-performance, interactive geographical dashboard for visualizing Iran's tourism potential at both provincial and county levels.

## 🌟 Overview

Inspired by the design of [Japan-Guide](https://www.japan-guide.com/), our service offers a seamless way to explore regional data through a dynamic heatmap system. Users can filter by interest, and the map instantly updates its scoring and color-coding to reflect the best destinations.

### Key Features

* **Hierarchical Drill-down:** Navigate from a national overview to specific Provinces, and further into detailed County (Shahrestan) views.
* **Dynamic Tourism Scoring:** Instant map recoloring based on four main categories:
    * 🍔 **Food:** Restaurants, cafes, and local gastronomy.
    * 🏛️ **Attractions:** Historical landmarks and museums.
    * 🎭 **Culture:** Heritage sites and cultural points of interest.
    * 🌲 **Nature:** National parks, mountains, and scenic landscapes.


* **POI Discovery:** When viewing at the county level, the system fetches real-time facility markers (hotels, restaurants, etc.) via internal API integration.
* **Optimized Performance:** Uses a deterministic hashing algorithm for consistent regional scoring and client-side filtering for smooth performance.

## 🛠️ Tech Stack

* **Map Engine:** Leaflet.js
* **Base Maps:** CartoDB (Light-All style) via OpenStreetMap
* **Backend:** Django (Python)
* **Data Format:** GeoJSON for administrative boundaries
* **Typography:** Vazirmatn (RTL optimized)

## 📊 Data Sources & Credits

We utilize reliable open-source data to power our mapping engine:

* **Administrative Boundaries:** GeoJSON files for Iran's borders are sourced from [Humdata - GeoBoundaries for Iran](https://data.humdata.org/dataset/geoboundaries-admin-boundaries-for-iran-islamic-republic-of).
* **Conceptual Design:** The regional filtering and user experience flow are inspired by the UX of [Japan-Guide.com](https://www.japan-guide.com/).

## 🚀 Getting Started

Since this module is part of a microservice architecture, it can be executed within the main project environment.

### 1. Running with Docker

From the project's root directory:

```bash
docker-compose up --build

pwsh ./up-all.ps1
```

### 2. Manual Development Setup

1. Navigate to the project root.
2. Install requirements: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Start server: `python manage.py runserver`
5. Access the module at: `http://localhost:8000/team9/`

## 🤝 Contributing

This module is maintained by **Team 9**. For any feature requests or bug reports regarding the map service, please open an issue or submit a pull request within the main repository.

---

**Developed with ❤️ by Team 9**
*Part of the Software Engineering Course - Winter 1404*

👨‍💻 [@mr-mobasheri](https://github.com/mr-mobasheri)

👨‍💻 [@alinourbakhsh2020](https://github.com/alinourbakhsh2020)

👨‍💻 [@Amyr-333](https://github.com/Amyr-333)

👨‍💻 [@M-Rafi-Hd](https://github.com/M-Rafi-Hd)

