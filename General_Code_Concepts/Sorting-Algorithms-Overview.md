# Sorting Algorithm Cheatsheet

## Bubble Sort
- Works by repeatedly stepping through the list, comparing adjacent elements, and swapping them if they're in the wrong order
- After each pass, the largest unsorted element "bubbles" to its correct position
- Time Complexity: O(n²) average and worst case
- Space Complexity: O(1)
- Stable: Yes
- In-place: Yes
- Best for: Small datasets or nearly sorted data

## Selection Sort
- Divides the input into a sorted and unsorted region
- Repeatedly finds the minimum element from the unsorted region and moves it to the end of the sorted region
- Time Complexity: O(n²) in all cases
- Space Complexity: O(1)
- Stable: No (typical implementation)
- In-place: Yes
- Best for: Small datasets where memory usage is a concern

## Insertion Sort
- Works by building the final sorted array one item at a time
- Takes each element and inserts it into its correct position among the previously sorted elements
- Time Complexity: O(n²) average and worst case, O(n) best case (nearly sorted)
- Space Complexity: O(1)
- Stable: Yes
- In-place: Yes
- Best for: Small datasets, online algorithms (where data arrives sequentially)

## Merge Sort
- Divides the array into halves, sorts each half, then merges the sorted halves
- Uses the "divide and conquer" strategy
- Time Complexity: O(n log n) in all cases
- Space Complexity: O(n)
- Stable: Yes
- In-place: No
- Best for: Large datasets where stable sorting is required

## Quick Sort
- Picks a "pivot" element and partitions the array around it
- Elements less than pivot go left, greater elements go right
- Recursively sorts the sub-arrays
- Time Complexity: O(n log n) average, O(n²) worst case
- Space Complexity: O(log n) due to recursion
- Stable: No (typical implementation)
- In-place: Yes
- Best for: General purpose sorting when stability isn't required

## Heap Sort
- Builds a max heap from the data
- Repeatedly extracts the maximum element and rebuilds the heap
- Time Complexity: O(n log n) in all cases
- Space Complexity: O(1)
- Stable: No
- In-place: Yes
- Best for: When consistent performance is needed with O(1) space

## Radix Sort
- Non-comparative sorting algorithm
- Sorts numbers digit by digit, from least significant to most significant
- Time Complexity: O(nk) where k is the number of digits
- Space Complexity: O(n+k)
- Stable: Yes
- In-place: No
- Best for: Integers with fixed number of digits

## Counting Sort
- Works by counting occurrences of each element
- Calculates the position of each element in the output array
- Time Complexity: O(n+k) where k is the range of input
- Space Complexity: O(k)
- Stable: Yes
- In-place: No
- Best for: Small range of integer keys

## Bucket Sort
- Distributes elements into buckets, sorts each bucket, then concatenates
- Time Complexity: O(n+k) average, O(n²) worst case
- Space Complexity: O(n+k)
- Stable: Yes (if using a stable sort within buckets)
- In-place: No
- Best for: Uniformly distributed data over a range

## Tim Sort
- Hybrid of merge sort and insertion sort
- Breaks array into small pieces, sorts them with insertion sort, then merges
- Time Complexity: O(n log n)
- Space Complexity: O(n)
- Stable: Yes
- In-place: No
- Best for: Real-world data with some pre-existing order

## Shell Sort
- Variation of insertion sort that allows exchange of far elements
- Uses decreasing gap sequence to sort elements
- Time Complexity: Depends on gap sequence, around O(n log² n)
- Space Complexity: O(1)
- Stable: No
- In-place: Yes
- Best for: Medium-sized datasets
