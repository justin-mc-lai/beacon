"""
Integration example: Using ExitDetector and CircuitBreaker together.

This example demonstrates how to combine both detectors in a Ralph-style loop.
"""

from beacon.utils.circuit_breaker import CircuitBreaker
from beacon.utils.exit_detector import ExitDetector


def ralph_loop_example():
    """Example of a Ralph-style loop with dual detection."""
    # Initialize detectors
    exit_detector = ExitDetector(completion_threshold=2)
    circuit_breaker = CircuitBreaker(
        no_progress_threshold=3,
        same_error_threshold=3,
        output_decline_threshold=3,
    )

    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"\n=== Iteration {iteration}/{max_iterations} ===")

        # Simulate work (replace with actual implementation)
        result = simulate_work(iteration)

        # Check circuit breaker first (safety check)
        is_stuck, stuck_reason = circuit_breaker.detect_stuck(iteration, result)
        if is_stuck:
            print(f"❌ Circuit breaker triggered: {stuck_reason}")
            print("Loop terminated to prevent infinite iteration")
            break

        # Check exit conditions (completion check)
        should_exit, exit_reason = exit_detector.check_exit(result)
        if should_exit:
            print(f"✅ Exit conditions met: {exit_reason}")
            print("Task completed successfully")
            break

        print(f"Continue: {exit_reason}")

    if iteration >= max_iterations:
        print(f"\n⚠️  Reached max iterations ({max_iterations})")


def simulate_work(iteration: int) -> dict:
    """
    Simulate work for demonstration.

    In real usage, this would be replaced with actual implementation logic.
    """
    # Simulate different scenarios
    if iteration == 1:
        return {
            "output": "Starting implementation...",
            "EXIT_SIGNAL": False,
        }
    elif iteration == 2:
        return {
            "output": "Implementation in progress. All tasks are done.",
            "EXIT_SIGNAL": False,
        }
    elif iteration == 3:
        return {
            "output": "Project complete. All tasks are done. Ready for review.",
            "EXIT_SIGNAL": True,
        }
    else:
        return {
            "output": "Continuing work...",
            "EXIT_SIGNAL": False,
        }


if __name__ == "__main__":
    ralph_loop_example()
