# Vocab Technical Concepts

Idempotency - the property of an operation where applying it multiple times yeilds the exact dame final effect as applying once.
Example:
- When loading in data incrementally based on new files that action is NOT idempotent since running the files once loads the new files then the same files would not be loaded if run again.
