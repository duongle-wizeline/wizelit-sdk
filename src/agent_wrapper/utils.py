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

def greet_many(names: list[str]) -> list[str]:
    """
    Generate a greeting message for each name.
    
    Args:
        names: List of names to greet.
        
    Returns:
        A list of greeting strings.
    """
    return [f"Hello, {name}!" for name in names]