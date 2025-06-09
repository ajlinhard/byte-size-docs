Yes, there are several better architectural patterns for testing these anomaly detectors. Here are some improved approaches:This improved architecture provides several benefits:

## Key Improvements:

1. **Separation of Concerns**: Detectors are separate from exceptions, making them easier to test and more flexible.

2. **Non-throwing Detection**: The `detect()` method returns a result object instead of throwing, allowing for better testing and batch processing.

3. **Rich Result Objects**: `AnomalyResult` contains severity levels, context data, and structured information.

4. **Flexible Exception Handling**: You can choose whether to throw exceptions or collect results.

5. **Composite Pattern**: `AnomalyManager` can run multiple detectors and aggregate results.

## Testing Advantages:

```python
# Easy to test without exception handling
def test_speed_detector():
    detector = SpeedAnomalyDetector(0.1, 0.8)
    
    # Test normal case
    result = detector.detect(0.5, 1000)
    assert not result.is_anomaly
    
    # Test anomaly case
    result = detector.detect(2000, 1000)
    assert result.is_anomaly
    assert result.severity == "critical"
    assert "above_maximum" in result.context["violation_type"]

# Test exception behavior separately
def test_speed_detector_exceptions():
    detector = SpeedAnomalyDetector(0.1, 0.8)
    
    with pytest.raises(ImpossibleSpeedException) as exc_info:
        detector.check(2000, 1000)
    
    assert exc_info.value.velocity == 2.0
```

## Alternative Patterns:

- **Strategy Pattern**: Different detection algorithms for the same anomaly type
- **Observer Pattern**: Notify multiple handlers when anomalies are detected
- **Builder Pattern**: Construct complex anomaly detection pipelines
- **Factory Pattern**: Create detectors based on configuration

This architecture is much more testable, maintainable, and follows SOLID principles better than the original design.

# Code:
```python
from abc import ABC, abstractmethod
from typing import Any, List, Optional
from dataclasses import dataclass
from enum import Enum


# Option 1: Separate Detectors from Exceptions (Recommended)
class AnomalyException(Exception):
    """Base exception for anomalies"""
    def __init__(self, message: str, anomaly_type: str, **context):
        super().__init__(message)
        self.anomaly_type = anomaly_type
        self.context = context


class ImpossibleSpeedException(AnomalyException):
    """Specific exception for speed anomalies"""
    def __init__(self, message: str, velocity: float, min_threshold: float, max_threshold: float):
        super().__init__(
            message, 
            "impossible_speed", 
            velocity=velocity, 
            min_threshold=min_threshold, 
            max_threshold=max_threshold
        )
        self.velocity = velocity
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold


@dataclass
class AnomalyResult:
    """Result of an anomaly check"""
    is_anomaly: bool
    message: str = ""
    severity: str = "info"  # info, warning, error, critical
    context: dict = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}


class AnomalyDetector(ABC):
    """Base class for anomaly detectors"""
    
    @abstractmethod
    def detect(self, *args, **kwargs) -> AnomalyResult:
        """Detect anomaly and return result (non-throwing)"""
        pass
    
    def check(self, *args, **kwargs) -> bool:
        """Check for anomaly and raise exception if found"""
        result = self.detect(*args, **kwargs)
        if result.is_anomaly:
            self._raise_exception(result, *args, **kwargs)
        return True
    
    @abstractmethod
    def _raise_exception(self, result: AnomalyResult, *args, **kwargs):
        """Raise appropriate exception based on result"""
        pass


class SpeedAnomalyDetector(AnomalyDetector):
    """Detector for speed anomalies"""
    
    def __init__(self, min_threshold: float = 0.0, max_threshold: float = 1.0):
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
    
    def detect(self, distance: float, sample_rate_ms: float) -> AnomalyResult:
        """Non-throwing detection method"""
        velocity = distance / sample_rate_ms
        
        if velocity < self.min_threshold:
            return AnomalyResult(
                is_anomaly=True,
                message=f"Speed too low: {velocity:.4f} (min: {self.min_threshold})",
                severity="error",
                context={
                    "velocity": velocity,
                    "min_threshold": self.min_threshold,
                    "max_threshold": self.max_threshold,
                    "violation_type": "below_minimum"
                }
            )
        
        if velocity > self.max_threshold:
            return AnomalyResult(
                is_anomaly=True,
                message=f"Speed too high: {velocity:.4f} (max: {self.max_threshold})",
                severity="critical",
                context={
                    "velocity": velocity,
                    "min_threshold": self.min_threshold,
                    "max_threshold": self.max_threshold,
                    "violation_type": "above_maximum"
                }
            )
        
        return AnomalyResult(
            is_anomaly=False,
            message="Speed within normal range",
            context={"velocity": velocity}
        )
    
    def _raise_exception(self, result: AnomalyResult, distance: float, sample_rate_ms: float):
        velocity = result.context["velocity"]
        raise ImpossibleSpeedException(
            result.message,
            velocity,
            self.min_threshold,
            self.max_threshold
        )


# Option 2: Composite Anomaly Detector
class AnomalyManager:
    """Manages multiple anomaly detectors"""
    
    def __init__(self):
        self.detectors: List[AnomalyDetector] = []
    
    def add_detector(self, detector: AnomalyDetector):
        self.detectors.append(detector)
    
    def detect_all(self, data: dict) -> List[AnomalyResult]:
        """Run all detectors and return results"""
        results = []
        for detector in self.detectors:
            try:
                # Assume each detector knows which data it needs
                if isinstance(detector, SpeedAnomalyDetector):
                    result = detector.detect(data.get('distance', 0), data.get('sample_rate_ms', 1))
                    results.append(result)
            except Exception as e:
                results.append(AnomalyResult(
                    is_anomaly=True,
                    message=f"Detector error: {str(e)}",
                    severity="error"
                ))
        return results
    
    def check_all(self, data: dict, fail_fast: bool = True) -> List[AnomalyResult]:
        """Check all detectors, optionally stopping at first anomaly"""
        results = []
        for detector in self.detectors:
            try:
                if isinstance(detector, SpeedAnomalyDetector):
                    if fail_fast:
                        detector.check(data.get('distance', 0), data.get('sample_rate_ms', 1))
                    else:
                        result = detector.detect(data.get('distance', 0), data.get('sample_rate_ms', 1))
                        results.append(result)
                        if result.is_anomaly and fail_fast:
                            detector._raise_exception(result, data.get('distance', 0), data.get('sample_rate_ms', 1))
            except AnomalyException:
                if fail_fast:
                    raise
        return results


# Example usage and testing
if __name__ == "__main__":
    # Test individual detector
    speed_detector = SpeedAnomalyDetector(min_threshold=0.1, max_threshold=0.8)
    
    # Non-throwing detection
    result = speed_detector.detect(0.5, 1000)  # velocity = 0.0005
    print(f"Detection result: {result}")
    
    result = speed_detector.detect(2000, 1000)  # velocity = 2.0
    print(f"Detection result: {result}")
    
    # Exception-throwing check
    try:
        speed_detector.check(2000, 1000)
    except ImpossibleSpeedException as e:
        print(f"Caught: {e}")
        print(f"Velocity: {e.velocity}")
        print(f"Context: {e.context}")
    
    # Test composite manager
    manager = AnomalyManager()
    manager.add_detector(speed_detector)
    
    test_data = {"distance": 2000, "sample_rate_ms": 1000}
    results = manager.detect_all(test_data)
    print(f"Manager results: {results}")
    
    try:
        manager.check_all(test_data, fail_fast=True)
    except ImpossibleSpeedException as e:
        print(f"Manager caught: {e}")
```
