# Random Package
The random package can be helpful many scenarios from creating fake data, load testing APIs, to laod balancing [(List of Use Cases)](#List-of-Use-Cases). Its handy to know what is in the package when the time to use it inevitably comes.
The cheatsheet includes a reference table of all major functions followed by practical code examples organized by use case.

The examples cover everything from basic random number generation to advanced techniques like Monte Carlo simulation and different sampling methods. Each code block demonstrates real-world applications you might encounter in data analysis, game development, testing, or scientific computing.

The cheatsheet also includes important tips at the end, like using the `secrets` module for cryptographic applications and understanding the differences between similar functions like `choice()` vs `choices()`.

# Python Random Package Cheatsheet

## Function Reference Table

| Function | Description | Example Usage |
|----------|-------------|---------------|
| `random()` | Random float between 0.0 and 1.0 | `random.random()` |
| `randint(a, b)` | Random integer between a and b (inclusive) | `random.randint(1, 10)` |
| `randrange(start, stop, step)` | Random integer from range | `random.randrange(0, 100, 2)` |
| `uniform(a, b)` | Random float between a and b | `random.uniform(1.5, 10.5)` |
| `choice(seq)` | Random element from sequence | `random.choice(['a', 'b', 'c'])` |
| `choices(seq, k=1)` | Random elements with replacement | `random.choices([1, 2, 3], k=3)` |
| `sample(seq, k)` | Random elements without replacement | `random.sample([1, 2, 3, 4], 2)` |
| `shuffle(seq)` | Shuffle sequence in-place | `random.shuffle(my_list)` |
| `gauss(mu, sigma)` | Gaussian/normal distribution | `random.gauss(0, 1)` |
| `normalvariate(mu, sigma)` | Normal distribution (thread-safe) | `random.normalvariate(0, 1)` |
| `expovariate(lambd)` | Exponential distribution | `random.expovariate(1.5)` |
| `seed(x)` | Initialize random number generator | `random.seed(42)` |
| `getstate()` | Get generator state | `random.getstate()` |
| `setstate(state)` | Set generator state | `random.setstate(state)` |

## Code Examples

### Basic Random Numbers

```python
import random

# Random float between 0.0 and 1.0
print(random.random())  # 0.8394077505647799

# Random integer (inclusive range)
print(random.randint(1, 6))  # 4

# Random integer from range with step
print(random.randrange(0, 100, 5))  # 35

# Random float in specified range
print(random.uniform(1.0, 10.0))  # 7.123456789
```

### Working with Sequences

```python
import random

# Choose random element
fruits = ['apple', 'banana', 'cherry', 'date']
print(random.choice(fruits))  # 'banana'

# Choose multiple elements with replacement
print(random.choices(fruits, k=3))  # ['apple', 'apple', 'cherry']

# Choose multiple elements without replacement
print(random.sample(fruits, 2))  # ['cherry', 'apple']

# Shuffle list in-place
numbers = [1, 2, 3, 4, 5]
random.shuffle(numbers)
print(numbers)  # [3, 1, 5, 2, 4]
```

### Weighted Random Selection

```python
import random

# Weighted choices
items = ['red', 'green', 'blue']
weights = [10, 5, 1]  # red is 10x more likely than blue

result = random.choices(items, weights=weights, k=5)
print(result)  # ['red', 'red', 'green', 'red', 'red']

# Using cumulative weights
cum_weights = [10, 15, 16]  # equivalent to weights above
result = random.choices(items, cum_weights=cum_weights, k=3)
print(result)
```

### Statistical Distributions

```python
import random

# Normal/Gaussian distribution
mean, std_dev = 100, 15
iq_score = random.gauss(mean, std_dev)
print(f"IQ Score: {iq_score:.1f}")

# Generate multiple normal values
iq_scores = [random.gauss(100, 15) for _ in range(5)]
print(iq_scores)

# Exponential distribution (useful for modeling wait times)
avg_wait_time = 2.5
wait_time = random.expovariate(1/avg_wait_time)
print(f"Wait time: {wait_time:.2f} minutes")

# Other distributions
print(f"Beta: {random.betavariate(2, 5)}")
print(f"Gamma: {random.gammavariate(2, 1)}")
print(f"Log normal: {random.lognormvariate(0, 1)}")
```

### Reproducible Random Numbers

```python
import random

# Set seed for reproducible results
random.seed(42)
print(random.random())  # Always: 0.6394267984578837
print(random.randint(1, 100))  # Always: 81

# Reset with same seed
random.seed(42)
print(random.random())  # Same as first call: 0.6394267984578837

# Save and restore state
state = random.getstate()
print(random.random())  # 0.025010755222666936

random.setstate(state)
print(random.random())  # Same: 0.025010755222666936
```

### Practical Examples

```python
import random
import string

# Generate random password
def generate_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choices(chars, k=length))

print(generate_password(16))

# Simulate dice rolls
def roll_dice(num_dice=2, num_sides=6):
    return [random.randint(1, num_sides) for _ in range(num_dice)]

print(f"Dice roll: {roll_dice()}")
print(f"D20 roll: {roll_dice(1, 20)}")

# Random color generator
def random_hex_color():
    return f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"

print(f"Random color: {random_hex_color()}")

# Monte Carlo simulation example
def estimate_pi(num_points=100000):
    inside_circle = 0
    for _ in range(num_points):
        x, y = random.uniform(-1, 1), random.uniform(-1, 1)
        if x*x + y*y <= 1:
            inside_circle += 1
    return 4 * inside_circle / num_points

print(f"Pi estimate: {estimate_pi()}")
```

### Random Sampling Patterns

```python
import random

# Reservoir sampling (useful for large datasets)
def reservoir_sample(stream, k):
    reservoir = []
    for i, item in enumerate(stream):
        if i < k:
            reservoir.append(item)
        else:
            j = random.randint(0, i)
            if j < k:
                reservoir[j] = item
    return reservoir

# Bootstrap sampling
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
bootstrap_sample = random.choices(data, k=len(data))
print(f"Bootstrap sample: {bootstrap_sample}")

# Stratified sampling
def stratified_sample(groups, sample_size):
    samples = []
    per_group = sample_size // len(groups)
    for group in groups:
        samples.extend(random.sample(group, min(per_group, len(group))))
    return samples

group_a = [1, 2, 3, 4, 5]
group_b = [6, 7, 8, 9, 10]
result = stratified_sample([group_a, group_b], 4)
print(f"Stratified sample: {result}")
```

## Quick Tips

- Use `random.seed()` for reproducible results in testing
- `random.choice()` for single selection, `random.sample()` for multiple without replacement
- `random.choices()` supports weights and allows replacement
- `random.shuffle()` modifies the original list
- For cryptographic purposes, use the `secrets` module instead
- `random.gauss()` is faster than `random.normalvariate()` but not thread-safe

---
# List of Use Cases
The Python `random` package has numerous practical applications across different domains. Here are the main use cases:

## Data Science & Statistics

**Data Sampling and Analysis**
- Creating random samples from large datasets for analysis
- Bootstrap sampling for statistical inference
- Cross-validation by randomly splitting data into train/test sets
- Generating synthetic datasets for testing algorithms
- Monte Carlo simulations for risk analysis and probability modeling

**A/B Testing**
- Randomly assigning users to control/experimental groups
- Ensuring unbiased distribution of test subjects
- Creating randomized controlled experiments

## Game Development

**Core Game Mechanics**
- Dice rolls, card shuffling, and random events
- Procedural generation of game worlds, dungeons, or levels
- Random enemy spawning and loot drops
- AI decision-making with probabilistic behaviors
- Random number generation for game physics (particle effects, etc.)

## Machine Learning & AI

**Model Training**
- Randomly initializing neural network weights
- Creating random train/validation/test splits
- Data augmentation through random transformations
- Stochastic gradient descent with random batch selection
- Hyperparameter tuning with random search

**Reinforcement Learning**
- Epsilon-greedy exploration strategies
- Random action selection during training
- Environment randomization for robust learning

## Security & Cryptography

**Authentication Systems**
- Generating random session tokens and API keys
- Creating temporary passwords and verification codes
- Salt generation for password hashing
- Random challenge generation for security protocols

*Note: For cryptographic purposes, use the `secrets` module instead of `random` for security-critical applications.*

## Software Testing & Quality Assurance

**Test Data Generation**
- Creating random test inputs for fuzzing
- Generating edge cases and boundary conditions
- Property-based testing with random inputs
- Load testing with randomized user behaviors
- Database seeding with realistic random data

## Scientific Computing & Research

**Simulation and Modeling**
- Weather pattern simulation
- Population dynamics modeling
- Physics simulations with random perturbations
- Economic modeling with stochastic processes
- Biological system modeling (genetic algorithms, evolution)

## Web Development & Applications

**User Experience**
- Randomizing content display (featured products, testimonials)
- Creating random user avatars or profile colors
- Shuffling playlist orders or recommendation feeds
- Random quote or tip generators
- Captcha generation

**System Operations**
- Load balancing with random server selection
- Cache eviction with random replacement policies
- Random delays to prevent thundering herd problems
- Feature flag randomization for gradual rollouts

## Educational & Training

**Learning Applications**
- Random question selection for quizzes
- Flashcard shuffling for spaced repetition
- Random practice problem generation
- Simulation exercises for training scenarios

## Art & Creative Applications

**Generative Art**
- Random color palette generation
- Procedural texture and pattern creation
- Music composition with random elements
- Creative writing prompt generation
- Random layout and design variations

## Business & Operations

**Decision Making**
- Random sampling for surveys and market research
- Employee scheduling with fairness constraints
- Random auditing and quality control checks
- Lottery systems and prize draws
- Random customer selection for promotions

## Performance & Optimization

**Algorithm Testing**
- Benchmarking with random datasets
- Stress testing with random workloads
- Cache performance testing with random access patterns
- Database query optimization with random data distributions

The `random` package is particularly valuable because it provides a simple, consistent interface for introducing controlled randomness into applications. This randomness is essential for creating realistic simulations, ensuring fair distributions, testing edge cases, and building engaging user experiences. However, remember that the randomness is pseudorandom and deterministic when seeded, making it perfect for reproducible research and debugging.
