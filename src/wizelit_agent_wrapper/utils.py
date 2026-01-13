"""Utility functions for Wizelit Agent Wrapper."""


def greet(name: str = "World") -> str:
    """
    Generate a greeting message.
    
    Args:
        name: Name to greet. Defaults to "World".
        
    Returns:
        A greeting string.
        
    Example:
        >>> greet("Alice")
        'Hello, Alice!'
        >>> greet()
        'Hello, World!'
    """
    return f"Hello, {name}!"

