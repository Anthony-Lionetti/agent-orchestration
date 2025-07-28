import os
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("filesystem")

@mcp.tool()
def read_file(path: str) -> str:
    """Read the contents of a file.
    
    Args:
        path: The path to the file to read
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Write content to a file.
    
    Args:
        path: The path to the file to write
        content: The content to write to the file
    """
    try:
        # Ensure directory exists
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@mcp.tool()
def list_directory(path: str) -> str:
    """List the contents of a directory.
    
    Args:
        path: The path to the directory to list
    """
    try:
        items = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                items.append(f"[DIR]  {item}/")
            else:
                size = os.path.getsize(item_path)
                items.append(f"[FILE] {item} ({size} bytes)")
        return "\n".join(items) if items else "Directory is empty"
    except Exception as e:
        return f"Error listing directory: {str(e)}"

@mcp.tool()
def create_directory(path: str) -> str:
    """Create a directory.
    
    Args:
        path: The path of the directory to create
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return f"Successfully created directory {path}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"

@mcp.tool()
def file_exists(path: str) -> str:
    """Check if a file or directory exists.
    
    Args:
        path: The path to check
    """
    if os.path.exists(path):
        if os.path.isdir(path):
            return f"Directory exists: {path}"
        else:
            return f"File exists: {path}"
    else:
        return f"Path does not exist: {path}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio') 