# Link State Routing Simulator

A dynamic network simulation tool built in Python that visualizes the Link State Routing protocol. This project demonstrates how routers discover network topology, synchronize databases using flooding, and calculate shortest paths using Dijkstra's Algorithm.

This tool is designed for students and network enthusiasts to understand the inner workings of protocols like OSPF in an interactive, visual environment.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Installation

This project requires **Python 3.x**. It relies on standard Python libraries (`tkinter`, `heapq`, `copy`, `math`), so no external package installation is necessary.

1. **Clone the repository**
   ```bash
   git clone [https://github.com/Nowshin-Rahman-2102014/Link_state_routing](https://github.com/Nowshin-Rahman-2102014/Link_state_routing)
   cd Link_state_routing
````

2.  **Verify Python Installation**
    Ensure you have Python installed by running:

    ```bash
    python --version
    ```

3.  **Run the Application**

    ```bash
    python Link_State_Routing.py
    ```

    *(Note: If your script is named something else, replace `main.py` with your filename).*

## Usage

Once the application launches, you will see a Graphical User Interface (GUI) representing a network of 5 routers (A, B, C, D, E).

### 1\. View Routing Tables

  - Click on any **Router Node (Pink Circle)** to view its internal Routing Table in the sidebar.
  - This shows the *Destination*, *Next Hop*, and *Total Cost*.

### 2\. Update Link Costs

  - In the **Control Panel** (Sidebar), locate the "Update Link Cost" section.
  - Enter the **Source** (e.g., `A`), **Destination** (e.g., `B`), and the new **Cost** (e.g., `50`).
  - Click **Update Link**.
  - *Result:* You will see the network "Flood" in the logs, and the routing tables will update automatically.

### 3\. Highlight Shortest Path

  - In the **Highlight Shortest Path** section.
  - Enter **From** (e.g., `A`) and **To** (e.g., `E`).
  - Click **Show Path**.
  - *Result:* The shortest path will be highlighted in **Bright Green** on the visual canvas.

## Features

  - **Interactive Topology:** Visual representation of nodes and weighted links using `tkinter`.
  - **Dijkstra's Algorithm:** Implements a binary heap priority queue for efficient shortest-path calculation (O(E log V)).
  - **Link State Flooding:** Simulates the broadcast of Link State Packets (LSPs) to synchronize the Link State Database (LSDB) across all routers.
  - **Dynamic Convergence:** The network automatically re-converges when link costs are modified.
  - **Path Visualization:** Graphically highlights the full route from source to destination.
  - **Event Logging:** A scrolling log window displays flooding events and convergence status in real-time.

## Project Structure

  - **Router Class:** Handles LSDB storage, LSP processing, and Dijkstra's logic.
  - **NetworkSimulator Class:** Manages the global state, triggers flooding, and acts as the simulation engine.
  - **NetworkGUI Class:** Handles the frontend visualization, user input, and canvas drawing.

## Contributing

Contributions are welcome to improve the visualization or add new algorithms (like Distance Vector)\!

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## License


## Contact

**Sadia Homayra Nowshin** Student ID: 2102014  
Course: CCE-314 (Computer Networks)

Project Link: [https://github.com/Nowshin-Rahman-2102014/Link_state_routing](https://github.com/Nowshin-Rahman-2102014/Link_state_routing)

```

```
