# Types of Trees in Data Structures

## Binary Tree
- **Structure**: Each node has at most two children (left and right)
- **How it works**: Simple hierarchical structure with a root node and subtrees
- **Example**: 
  ```
      10
     /  \
    5    15
   / \     \
  3   7     20
  ```

## Binary Search Tree (BST)
- **Structure**: Specialized binary tree where left child < parent < right child
- **How it works**: Maintains sorted order; enables efficient search, insert, delete
- **Example**:
  ```
      8
     / \
    3   10
   / \    \
  1   6    14
     / \   /
    4   7 13
  ```

## AVL Tree
- **Structure**: Self-balancing BST where height difference between left and right subtrees ≤ 1
- **How it works**: Performs rotations after insertions/deletions to maintain balance
- **Example**:
  ```
      8
     / \
    4   12
   / \  / \
  2  6  10 14
  ```

## Red-Black Tree
- **Structure**: Self-balancing BST with nodes colored red or black
- **How it works**: Maintains balance using color properties and rotations
- **Example** (B=black, R=red):
  ```
      8B
     /  \
    3R   10R
   / \     \
  1B  6B    14B
  ```

## B-Tree
- **Structure**: Multi-way search tree with variable number of children per node
- **How it works**: Designed for block storage systems; minimizes disk I/O
- **Example** (order 3):
  ```
      [10, 20]
      /   |   \
  [5,8] [15] [30,40]
  ```

## B+ Tree
- **Structure**: Variant of B-tree with all data in leaf nodes; leaves linked in sequence
- **How it works**: Optimized for range queries and systems where data is on disk
- **Example**:
  ```
        [15]
       /    \
    [5,10]  [20,30] 
    (Leaves connected with pointers →)
  ```

## Trie (Prefix Tree)
- **Structure**: Nodes represent characters; paths from root form words/prefixes
- **How it works**: Efficiently stores and searches strings with shared prefixes
- **Example** (storing "cat", "car", "dog"):
  ```
       (root)
       /    \
      c      d
     /        \
    a          o
   / \          \
  t   r          g
  ```

## Heap
- **Structure**: Complete binary tree with heap property (min-heap: parent ≤ children)
- **How it works**: Used for priority queues and efficient access to min/max element
- **Example** (min-heap):
  ```
        1
       / \
      3   2
     / \  /
    17 19 7
  ```

## Segment Tree
- **Structure**: Binary tree for storing intervals or segments
- **How it works**: Allows querying ranges of elements, often with lazy propagation
- **Example** (sum of array [5,8,6,3,2,7,2,6]):
  ```
        39
       /  \
     22    17
    /  \   / \
   13   9  9  8
  ```

## Splay Tree
- **Structure**: Self-adjusting BST that moves recently accessed elements to root
- **How it works**: Uses rotations to keep frequently accessed elements near the root
- **Example** (after accessing 14):
  ```
       14
       / \
      8  20
     / \
    3  10
  ```

## Quadtree
- **Structure**: Each node has exactly four children or none
- **How it works**: Recursively divides 2D space into quadrants; used for spatial data
- **Example** (representing a region with points):
  ```
    (root: entire area)
    /    |    |    \
  NW    NE    SW   SE
  ```

## Octree
- **Structure**: 3D version of quadtree; each node has eight children or none
- **How it works**: Divides 3D space into octants; used for 3D spatial data, graphics
- **Example**: Similar to quadtree but with 8 branches at each level

## R-Tree
- **Structure**: Height-balanced tree for spatial data with overlapping rectangles
- **How it works**: Groups nearby objects with minimum bounding rectangles
- **Example**: Each node represents a bounding box containing child nodes/objects

## Fenwick Tree (Binary Indexed Tree)
- **Structure**: Array-based tree structure
- **How it works**: Efficiently updates elements and calculates prefix sums
- **Example** (for array [3,2,5,4,1,3,7]):  
  Binary representation handles cumulative sums at various positions

## Huffman Tree
- **Structure**: Full binary tree used for lossless data compression
- **How it works**: Assigns shorter codes to more frequent characters
- **Example** (for text with frequencies a:45, b:13, c:12, d:16, e:9, f:5):
  ```
         (100)
         /   \
       (55)  (45:a)
       /  \
     (30) (25)
     / \   / \
   (16:d)(14)(13:b)(12:c)
        / \
      (9:e)(5:f)
  ```

Each tree structure serves specific purposes, with various trade-offs in terms of complexity, memory usage, and operational efficiency for different types of operations.
