"""Custom build hook to map src/ packages to wizelit_sdk namespace."""

from pathlib import Path
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    """Build hook that maps all packages under src/ to wizelit_sdk namespace."""

    def initialize(self, version, build_data):
        """
        Initialize the build hook.
        
        Maps all packages from src/<module> to wizelit_sdk/<module>
        so users can import as: from wizelit_sdk.<module> import ...
        """
        src_path = Path(self.root) / "src"
        
        if not src_path.exists():
            return
        
        # Use force_include to map source paths to target paths in the wheel
        force_include = build_data.setdefault("force_include", {})
        
        # Get relative path from project root for source files
        root_path = Path(self.root)
        
        # Map src/__init__.py to wizelit_sdk/__init__.py
        init_file = src_path / "__init__.py"
        if init_file.exists():
            rel_init = init_file.relative_to(root_path)
            force_include[str(rel_init).replace("\\", "/")] = "wizelit_sdk/__init__.py"
        
        # Map standalone .py files from src/<module>.py to wizelit_sdk/<module>.py
        for item in src_path.iterdir():
            if item.is_file() and item.suffix == ".py" and item.name != "__init__.py":
                # Get relative path from project root
                rel_path = item.relative_to(root_path)
                source_path = str(rel_path).replace("\\", "/")
                target_path = f"wizelit_sdk/{item.name}"
                force_include[source_path] = target_path
        
        # Map each package from src/<module> to wizelit_sdk/<module>
        for item in src_path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                module_name = item.name
                target_base = Path("wizelit_sdk") / module_name
                
                # Recursively map all files in the package
                for py_file in item.rglob("*"):
                    if py_file.is_file():
                        # Get relative path from project root
                        rel_path = py_file.relative_to(root_path)
                        source_path = str(rel_path).replace("\\", "/")
                        # Get relative path within the package for target
                        target_rel = py_file.relative_to(item)
                        target_path = str(target_base / target_rel).replace("\\", "/")
                        force_include[source_path] = target_path

