# Basic Simics Concepts

## 1. Introduction

This document provides a brief technical overview of Simics concepts and principles.

## 2. Configurations

Simics is a discrete-event simulator that models transitions between fixed states, known as configurations. A configuration consists of configuration objects (instances of configuration classes), each with its own state, which can be saved as a checkpoint. The simulation evolves one configuration into another over simulated time.

### 2.1 Classes and Attributes

Each class represents a kind of things being simulated—typically, a model of some piece of hardware, such as a processor or a network chip.

- **Class Definition**: Includes class name, attributes, interfaces, and constructor/destructor methods.
- **Attributes**: Have a name, value type, and get/set methods. Types include numbers, strings, raw data, object references, lists, and NIL.
- **Checkpoint-Safe**: Classes must expose internal states as attributes for correct saving and restoration.

### 2.2 Interfaces
A class can implement an interface, similar to other programming language. A class can also call the methods defined by another class. This is how objects communicate.

Interfaces do not carry state and are not part of configurations.

- **Interfaces**: Collections of methods for querying or altering class instance states.
- **Port Interfaces**: Named interfaces allowing multiple implementations under different port names.

## 3. Time

Simulated by clocks, which advance time in a round-robin order by a time quantum. Clocks are loosely synchronized, and time is measured in simulated seconds or cycles.

Each clock's frequency defines the cycle length, even non-processor clock objects.

No single global time in the simulation; time always belongs to a clock. Different clocks can have different views of the time. This may cause time paradoxes if objects using different clocks interact or share mutable state.

### 3.1 Events

Objects can schedule methods to execute at future times, known as events. You need to have a clock to run events. Events can be canceled and are part of the configuration.

The expiration time can be specified in seconds or cycles.

### 3.2 Processor Time and Execution

- **Steps**: Execution of instructions or exceptions, typically one per cycle.
- **Determinism**: Simics is normally deterministic, ensuring consistent simulation results from the same starting configuration. However, you should take more care when writing random numbers, or having real-world interactions.

### 3.3 Distributed Simulation

Multiple simulations are possible to be linked to proceed in lock-step, with communication delays defined by minimum latency.

## 4. Program Organisation

Simics consists of a core and modules.

### 4.1 The Simics Core

The core, `simics-common`, handles command-line parsing and simulator functions. It includes the Simics API (a set of functions starting with `SIM_`) and fundamental classes.

### 4.2 Modules

Modules contain model-specific code, typically one configuration class per module. They are loaded automatically when needed and can be written in C, DML, or Python. Mainly in DML.

## 5. Simulation

### 5.1 Starting, Running, and Stopping

Simulation starts with `SIM_continue()` and stops via user input or `SIM_break_simulation()`.

### 5.2 Haps

Haps are callback points in the simulation, allowing functions to be executed when specific conditions are met.

### 5.3 Reverse Simulation

Simics can simulate backwards by saving micro-checkpoints. This requires deterministic and checkpoint-safe models.

### 5.4 Asynchronous Input

Simics interacts with the external world using asynchronous callbacks, including notifiers, real-time events, and thread-safe callbacks.