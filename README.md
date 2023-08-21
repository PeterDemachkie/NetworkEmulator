# Network Emulator Documentation

Welcome to the Network Emulator documentation. This guide will walk you through the steps to use the Network Emulator program developed by Peter Demachkie. The Network Emulator simulates a basic network environment with routers, hosts, and switches, allowing you to interact with the simulated network.

## Table of Contents

1. [Installation](#installation)
2. [Getting Started](#getting-started)
3. [Main Menu](#main-menu)
4. [Interacting with the Network](#interacting-with-the-network)
5. [Editing the Topology](#editing-the-topology)
6. [Saving and Loading Topology](#saving-and-loading-topology)
7. [Exiting the Program](#exiting-the-program)

## Installation

To use the Network Emulator, you need to have Python installed on your system. You can download Python from the official website: [Python Downloads](https://www.python.org/downloads/).

Once you have Python installed, follow these steps to set up the Network Emulator:

1. Clone the GitHub repository
   ```bash
   $ git clone https://github.com/PeterDemachkie/NetworkEmulator.git
   $ cd NetworkEmulator

## Getting Started

When you run the `userinterface.py` script, the Network Emulator will present you with a main menu that provides various options for interacting with the simulated network.

## Main Menu

The main menu provides the following options:

- **View Network Details**: View details about the entire network.
- **View Subnet Details**: View details about a specific subnet.
- **Interact With Network**: Send packets within the network.
- **Edit Network Topology**: Edit routers, hosts, or switches in the network.
- **Save Topology**: Save the current topology to a JSON file.
- **Load Topology**: Load a topology from a JSON file.
- **Quit**: Exit the Network Emulator.

## Interacting with the Network

When you choose the "Interact With Network" option, you can send packets within the simulated network. You'll need to provide the following information:

- Packet type (UDP or ICMP).
- Source and destination hosts.
- Data for UDP packets (optional).

## Editing the Topology

The "Edit Network Topology" option allows you to modify the network topology. You can add, edit, or remove routers, hosts, and switches. Follow the prompts to make changes to the topology.

### Oops...

If you accidentally enter a part of the topology editor you didn't mean to, type !BACK to go back to the previous menu.

## Saving and Loading Topology

You can save the current network topology to a JSON file using the "Save Topology" option. Similarly, you can load a previously saved topology from a JSON file using the "Load Topology" option.

## Exiting the Program

To exit the Network Emulator, select the "Quit" option from the main menu.

## Need Help?

If you encounter any issues, have questions, or want to contribute to the project, you can reach out to me, the project owner, at peterdemachkie101@gmail.com.
