# Phase-1 SPEC for:LeetCode Note Skill

## Expected skill args
/leetcode-note [problem-url1] [problem-url2] ... [template]
- `problem-url`: (Required) The URLs of the LeetCode problem that the user wants to create a note for. This will be used to fetch the problem details and generate a structured note.
- Can be a single URL or multiple URLs if the user wants to create notes for multiple problems at once. The skill should be able to handle both cases gracefully. But it is better to limit the number of URLs to a reasonable number (e.g., 5) to avoid overwhelming the user and the system. Also it is important to be discuss the same kind of set of problems (e.g., binary search as url1, search in rotated sorted array as url2, koko eating bananas as url3, as these problems are all related to binary search, it will be easier for the user to compare and contrast the different variations of binary search and learn from them).
- It will gather the following infromation based on the previous LLM discussion with the user:
  - Problem ID and Name
  - Key Takeaways from the discussion
  - Interview Feedback (if applicable)
  - Open Items for future review
- `template`: (Optional argument)This is another mode, this will not simply write a takeaway for per-problem, but will generate a hollistic note for the user basede on the discussion in a set of problems. (e.g. user gives a bunch of binary search problems, the template will generate a note that summarizes the key patterns and variations of binary search, and how to approach them in different scenarios. This will be more like a study guide for the user to review and learn from, rather than just a note for each individual problem).
- Default is to discuss in per-problem mode, not the template mode.

## Context
After solved a problem and with some discussion with AI using the `/leetcode-discuss` skill, users may want to summarize the problem and the key takeaways in a structured way. This skill will help users to create a note for the problem they solved, which can be used for future reference and review.

## Target
1. User can have per-problem notes that summarize the key takeaways from the discussion for each problem they solved. With detailed information in the Exaple Walkthrough section below, the user can have a clear and concise note for each problem, which can help them to review and reinforce their learning.
2. User can also have a holistic note that summarizes the key patterns and variations of a set of problems, which can be used as a study guide for future review and learning. This will help users to see the bigger picture and understand how different problems are related to each other, and how to approach them in different scenarios.

## Example walkthrough

### The per-problem note
I am discussing binary search with AI, here is our chat log, you can see we finally reach a point where I have a good understanding of binary search and its variations, and I want to create a note for this topic. I can use the `/leetcode-note` skill to create a note for the problems we discussed, and also a holistic note that summarizes the key patterns and variations of binary search.

========== BEGIN CHAT LOG EXAMPLE ==========
```log
 > /leetcode-discuss

╭─────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ✓  Activate Skill "leetcode-discuss": Interactive discussion and interview simulation for LeetCode… │
│                                                                                                     │
│ Skill leetcode-discuss activated. Resources loaded from                                             │
│ /Users/alfonshwu/.gemini/skills/leetcode-discuss:                                                   │
│                                                                                                     │
│ Showing up to 200 items (files + folders).                                                          │
│                                                                                                     │
│ /Users/alfonshwu/.gemini/skills/leetcode-discuss/                                                   │
│ ├───SKILL.md                                                                                        │
│ └───SPCE.md                                                                                         │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────╯

✦ I'm ready to dive into some LeetCode problems with you. To get started, please let me know:

   1. Mode: Would you like to do a Practice session (Socratic tutoring) or an Interview simulation (Mock
      interview)?
   2. Problem: Which problem are we looking at? (URL or ID)
   3. Status: If you've already attempted it, was your solution Accepted or Rejected? (Or are we starting
      from scratch?)
 > 1. Mode: Practice
   1. Search in the roated sorted array
   2. AC, here is my analysis

   class Solution {
   public:
       int search(vector<int>& nums, int target) {
           int l = 0, r = nums.size(); // Half-open interval: [l, r)

           while (l < r) {
               int m = l + (r - l) / 2;

               if (nums[m] == target) return m;

               // Safe right-bound assessment using r - 1
               if (nums[m] <= nums[r - 1]) {
                   if (target > nums[m] && target <= nums[r - 1]) {
                       l = m + 1;
                   } else {
                       r = m; // Exclusive right update
                   }
               }
               else {
                   if (target >= nums[l] && target < nums[m]) {
                       r = m;
                   } else {
                       l = m + 1;
                   }
               }
           }
           return -1;
       }
   };


   /*
   i Think I got it!

   Use he half-open interval [ )

   if right is sorted -> need to include the middle point to avoid missing
       search the right side, how do we search ?
           keep search in this side -> nums[r - 1] >= target > nums[m], l = m + 1
           (note no equal because if target == nums[m], then we "shoudl have" already return the answer)
           switch to the other side -> r = m
           (note not r = m - 1 because we use the half open interval)
   else
       serach the left side, how do we search ?
           keep seatch in this side -> nums[l] <= target < nums[m], r = m
           (note no equal because if target == nums[m], then we "shoudl have" already return the answer)
           switch to other side -> l = m + 1
           (note not l = m because we use the half open inteval)


   This prevents the egde case
       [3, 1] and search 3, initally, l = 0 , m = 1, r = 2
       [3, 1] -> actually the ride side is arleady sorted, so if we use nums[m] < nums[r - 1], then we
   misunderstandingly
       think R side is not sorted, but actually not. nums[1] <= num[2 - 1] so actually sortd, we just
   "CHEATED" ourself

       When we use <
           right side unsorted
           go else, target = 3, nums[l] = 3 nums[m] = 1 nums[r - 1] = 1 -> target NOT in this interval ,
   should search the r side
           l = m + 1
           l = 2, r = 2 terminated, return -1



       When we use <=
           right side sorted
           dont go else, target = 3, nums[l] = 3 nums[m] = 1 nums[r - 1] = 1 -> target is NOT in this
   inteval , should search the l side
           r = m
           l = 0, r = 0 , m = 0, FOUND!

   */
✦ Nice work! Using the half-open interval [l, r) can be tricky with rotated arrays, but your logic for
  identifying the sorted half using nums[m] <= nums[r - 1] is solid. You correctly identified that in a
  two-element array like [3, 1], nums[m] and nums[r-1] point to the same element, making the = check
  essential.

  Holistic Review
   * Correctness: Your implementation correctly handles the rotation by identifying which half is
     monotonically increasing and then checking if the target falls within that range.
   * Complexity:
       * Time: O(log n) because you're discarding half of the search space in each iteration.
       * Space: $O(1)$ as you're only using a few pointers.
   * Consistency: Your management of the [l, r) boundaries is consistent throughout (e.g., r = m and l = m
     + 1).

  ---

  Follow-up Questions

   1. Contextual Follow-up: You anchored your sorted-half check on the right side (nums[m] <= nums[r - 1]).
      If you had chosen to check the left side first (nums[l] <= nums[m]), how would the logic change?
      Specifically, does the [l, r) interval make one anchor "safer" or more intuitive than the other?

   2. Standard Follow-up: Suppose the input array nums is not guaranteed to have unique elements (i.e., it
      can contain duplicates). How does this affect your ability to determine which side is sorted? Can we
      still achieve O(log n) in the worst case?
 > 1.
   if (nums[m] == target) return m;

               // Safe right-bound assessment using r - 1
               if (nums[m] >= nums[l]) {
                   if (target >= nums[l] && target <= nums[r - 1]) {
                       r = m;  // in this half
                   } else {
                       l = m + 1; // in the other half
                   }
               }
               else {
                   if (target > nums[m] && target <= nums[r - 1]) {
                       l = m + 1; // in this half
                   } else {
                       r = m;  // in other half
                   }
               }


   I think half open interval is safer bcz it naturally fits the array iteration bejhaviour
   2. nums[left] == nums[mid] and nums[right] == nums[mid], it is impossible to know which half of the
   array is sorted. Simply increment the left pointer and decrement the right pointer to skip the
   identical elements
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
✦ That's a great attempt at reframing the logic using the left-side anchor! However, there's a small logic
  slip in the boundaries you just wrote.

  1. Analyzing your Left-Side logic
  If the left side is sorted (nums[m] >= nums[l]), you want to check if the target resides in that specific
  sorted range to decide whether to narrow your search to that half.

  In your snippet:

   1 if (nums[m] >= nums[l]) { // Left is sorted
   2     if (target >= nums[l] && target <= nums[r - 1]) { // <--- Check this condition
   3         r = m;
   4     }
   5 }
  If the left is sorted, you should check if target is between nums[l] and nums[m]. Checking target <=
  nums[r - 1] (the far right end) doesn't help you isolate the left half.

  The corrected logic for a left-anchor would be:

   1 if (nums[m] >= nums[l]) {
   2     if (target >= nums[l] && target < nums[m]) { // Is it in the sorted left?
   3         r = m;
   4     } else {
   5         l = m + 1;
   6     }
   7 }

  Regarding [l, r) safety: You're right that it's idiomatic in C++, but notice that in this specific
  problem, you had to use nums[r - 1] to check the right bound. In a standard [l, r] (closed) interval, you
  would just use nums[r]. The "danger" of [l, r) here is that if the range becomes empty (l == r),
  accessing nums[r-1] would be out of bounds if not careful (though your while (l < r) loop protects you).

  2. Handling Duplicates
  Spot on! If nums[l] == nums[m] == nums[r-1], we are "blind" and must prune the edges: l++ and r--.
   * Worst case: If the array is all 1s except for one 0, we end up checking every element, which leads to
     $O(n)$ time complexity. Binary search's logarithmic guarantee is broken by duplicates in a rotated
     array.

  ---

  Great session! Would you like to summarize our takeaways for this problem, or is there another pattern
  you'd like to explore?
```
========== END CHAT LOG EXAMPLE ==========

2. Then this skill asks user to provide the notebook path
    - if it is a notion link, then it will use the MCP with requiement below
    - if local file path, then it will save the note in local file system
3. The notion format for each of the problem, should be a markdown like the following (note the problem name and id should be included in the note, so that it can be easily searched and referenced in the future):
======== BEGIN EXAMPLE FOR PER-PROBLEM NOTE ==========
```md
# 853. Car Fleet
- **Intuition and Approach**:
    - **Intuition**: Cars closest to the target dictate the pace. A car farther back will form a fleet with a car ahead if it can reach the target faster than or at the same time as the car ahead. Since cars cannot pass each other, the faster car behind is forced to slow down and match the slower lead car's speed.
    - **Approach**:
        1. Pair each car's `position` with its `speed` and push them into a Max-Heap (`priority_queue`). This automatically sorts the cars by their starting position, letting us process them from **closest to the target to farthest**.
        2. Keep track of the current fleet's arrival time using a variable `cur` (initialized to `0`).
        3. Pop cars one by one:
            - Calculate the time this car needs to reach the target: $\text{timeNeeded} = \frac{\text{target} - \text{position}}{\text{speed}}$.
            - If `timeNeeded <= cur`, this car catches up to the existing fleet ahead. It becomes part of that fleet $\rightarrow$ **skip it** (`continue`).
            - If `timeNeeded > cur`, this car can never catch up to the cars ahead. It forms a **new fleet** $\rightarrow$ increment `res` and update `cur = timeNeeded` as the new pace time to beat.
- **Complexity**:
    - **Time**: $O(NlogN)$— Due to pushing N elements into the priority queue (sorting step). The evaluation loop itself is linear O(N).
    - **Space**: $O(N)$ — To store the position-speed pairs in the queue.
- **Additional Notes**
- **Code**:
```cpp
class Solution {
public:
    int carFleet(int target, vector<int>& position, vector<int>& speed){
        int res = 0;
        double cur = 0; // Tracks the time of the current slowest lead fleet

        // Max-heap to sort cars by position descending (closest to target first)
        priority_queue<pair<int, int>> q;
        for (int i = 0; i < position.size(); ++i) {
            q.push({position[i], speed[i]});
        }

        while (!q.empty()) {
            auto t = q.top();
            q.pop();

            // Time = Distance / Speed
            double timeNeeded = (double)(target - t.first) / t.second;

            // If it takes less/equal time, it joins the fleet ahead
            if (timeNeeded <= cur) continue;

            // Otherwise, it starts a brand new fleet
            cur = timeNeeded;
            ++res;
        }
        return res;
    }
};
``` 
```
========== END EXAMPLE FOR PER-PROBLEM NOTE ==========
4. Above is the full example of a per-problem note. Simply speaking it should include the problem name and id, the key takeaways (including intuition, approach, complexity analysis, and any additional notes), and the code. The note should be concise and clear, so that it can be easily reviewed in the future. 
5. The code is from my self-coding, and you can add some comment inside it to make it more clear, but you should not change ANY of logic of the code, as it is already correct and accepted. The key takeaways should be based on the discussion we had in the chat log, and should highlight the important points and insights that we discussed. The note should be structured in a way that is easy to read and understand, with clear headings and sections for each part of the note.

### The hollistic, paattern-wise note
1. After we have created the per-problem notes for a set of problems, we can use the `/leetcode-note template` mode to generate a holistic note that summarizes the key patterns and variations of the problems we discussed. This note will be more like a study guide for the user to review and learn from, rather than just a note for each individual problem. It will help users to see the bigger picture and understand how different problems are related to each other, and how to approach them in different scenarios. The note should include the common patterns, variations, and strategies that we discussed in the chat log, and should be structured in a way that is easy to read and understand.
2. Example output like this after discussing a set of binary search problems:

========= BEGIN EXAMPLE FOR PATTERN-WISE NOTE =========
```md
# Binary Search

# Binary Search: The Half-Open Manual [L, R) 📖

Following the philosophy of *Edsger Dijkstra*, this manual strictly utilizes the **half-open interval [left, right)**. This approach eliminates infinite loops and aligns cleanly with zero-indexed array boundaries.

## 💡 Why Half-Open Intervals?

- **Intuitive Range Size:** Size = `right - left`. No extra offsets.
- **Clear Empty Ranges:** An empty range is naturally represented by `left == right`.
- **Simple Invariants:** Loop condition is always `while (left < right)`. At termination, `left == right`.
- **Clean Midpoint Updates:** Lower half: `right = mid`; Upper half: `left = mid + 1`.

## 🛠️ Pattern 1: Exact Match (Find Target)

```cpp
int search(vector<int>& nums, int target) {
    int l = 0, r = nums.size();
    while (l < r) {
        int m = l + (r - l) / 2;
        if (nums[m] == target) return m;
        if (nums[m] < target) l = m + 1;
        else r = m;
    }
    return -1;
}
```

## 🛠️ Pattern 2: Lower Bound (First ≥ Target)

```cpp
int lower_bound(vector<int>& nums, int target) {
    int l = 0, r = nums.size();
    while (l < r) {
        int m = l + (r - l) / 2;
        if (nums[m] >= target) r = m; // Contract right
        else l = m + 1; // Expand left
    }
    return l; // (or r, they are equal)
}
```

## 🛠️ Pattern 3: Upper Bound (First > Target)

```cpp
int upper_bound(vector<int>& nums, int target) {
    int l = 0, r = nums.size();
    while (l < r) {
        int m = l + (r - l) / 2;
        if (nums[m] > target) r = m;
        else l = m + 1;
    }
    return l;
}
```

## 🛠️ Pattern 4: Rotated & Complex Search

When no target exists, compare against the boundaries. In [L, R), the safe right-hand comparison is always `nums[r - 1]`.

```cpp
// Example: Find Min in Rotated Sorted Array
while (l < r) {
    int m = l + (r - l) / 2;
    if (nums[m] <= nums[r - 1]) r = m; // Sorted side is right, min is at m or left
    else l = m + 1; // Sorted side is left, pivot is on the right
}
```

## ⚠️ Common Pitfalls

1. **Final Index Check:** If returning `l` in a search for an exact match, verify if `nums[l] == target` to handle 'not found' cases.
2. **Small Arrays [3, 1]:** When comparing `nums[m] < nums[r - 1]`, the equality check `<=` is mandatory. For an array of size 2, m and r-1 point to the same index. Using strictly less-than will fail to identify the sorted side.
```
========== END EXAMPLE FOR PATTERN-WISE NOTE ==========

3. Above is just a simple example of the binary search. In actual world, there are more groups and patterns. (e.g. in graph we will have matrix graph and node-based graph.) be sure to ask user for input if you find unable to classify the problems into specific patterns, and also ask user for confirmation if you are not sure about the classification. The goal is to help user to see the bigger picture and understand how different problems are related to each other, and how to approach them in different scenarios, or spot the common patterns and variations in a set of problems, so that they can apply the right strategy when they encounter similar problems in the future.
    - Basically, here is all of the groups: https://neetcode.io/practice/practice/neetcode250 
    - Or in my notion, here are the groups: (1) Array (2) Binary search (3) Tree (4) Graph matrix, (5) Graph general (6) Dynamic programming (7) Backtracking (8) Trie... others might not listed yet, it does not mean they are not important, just means I have not organized them yet, you can ask user for more input if you find the problems we discussed do not fit into these groups, or if you find some problems can fit into multiple groups, then you can ask user for confirmation on how to classify them, and also ask user for more input on the key patterns and variations in each group, so that you can generate a more comprehensive and accurate note for the user to review and learn from.
4. For both mode, ask user to first provide notion link for both method
    -  The link to per-problem note should be used to fetch the problem details and generate a structured note for each problem.
    -  The link to the template note should be used to generate a holistic note that summarizes the key patterns and variations of the problems we discussed.

## Enhancement

# Phase-2 SPEC