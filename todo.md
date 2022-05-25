- Add BSMT/address subtypes to the AC_Table merge op

- Transition the Rhino file to Python process using PyShape

- Use Struc to compare topology
- Use Struc to poll Sheet Number
- Rhino to Insert "SSS" Text
- Rhino to Insert Splice Text
- Rhino to Offset Curves
  - + Conduit Offset
  - + Conduit Lengths

---

- [x] Draw NetworkX in Cytoscape 
  - [ ] Using locations info from Rhino Points!
- [x] Draw a NetworkX graph in Cytoscape

- [x] Layout Selector with Callback
- [x] Proper Node and Edge Labels
  - [x] Printing to Terminal
  - [ ] Displayed in Cytoscape
- [x] Stacking Bar Graph
- [x] Appropriate colors
- [x] Filtering by Node

- [x] Node Data Table
  - [ ] Fix Filtering Issue
    - INFO: After a node is selected in the graph, the nodes can no longer be entirely removed. The previous node is added as a callback to the function. 
  - [ ] Edge Data Table
- [x] Layout improvement


- All On in Datasheet
- TODO: What is wrong with the NODE vs ID labels?

- Import functions from tree_cable_allocation
  - functionalize functions
  - re-implement with NetworkX
  - calculate Cumulative and Dead Ranges (out of product_fibre_ranges [24, 48, 72, 96, 144, 288, 432])
  - calculate Capacities based on Calculated Capacity from PPC Addresses -> Live Counts

- Additional Functions:
  - Total Civil Meters (Display in Green)
  - Total Hours spent designing FSA 
    - since start?
  - Designed by
  - Approved by
  - Phase PRE, CMR, DFD, OFC, OFX
  - File connected to:

- Figure out how to:
  - Change the class of a button / indicator based on conditions
    - Have a standard function wrapper / decorator that changes it based on codes:
      - RED Error / Exception
      - GREEN Expected Type
      - WARNING Value Errors (bad data or uncaught exceptions to the formulas)

- DRC Python app has callbacks from 
  - [x] Radio -> Dropdown (set/filter list of options)
  - Dropdown -> Numeric / Text Display
  - Dropdown -> Graphs (one callback per graph object)

- Display the allocated fibre beside the fibre capacity on graph, with Dead denoted and range info on hover
- Range info display
  - SB Y-axis
  - Drop range X-axis
  - Display ranges by
    - Index
    - Increasing on Fibre Number

- Cable Info Data

- How To Use Data
  - Overlay Circled Numbers
    - 1. Verify Order
    - 2. SSS
    - 3. Activity Numbers
      - Set Radio to All, highlight columnn on dataframe
    - 4. FCP#
      - Input#
    - 5. Ranges
      - Skipped Ranges Input
    - 6. Cumulative Range and Dead Count
      - Populate 
  - Exit when clicked?

- Edge Thicknesses in Graph