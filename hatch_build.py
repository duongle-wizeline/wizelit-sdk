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
        
        # Map src/__init__.py to wizelit_sdk/__init__.py
        force_include["src/__init__.py"] = "wizelit_sdk/__init__.py"
        
        # Map standalone .py files from src/<module>.py to wizelit_sdk/<module>.py
        for item in src_path.iterdir():
            if item.is_file() and item.suffix == ".py" and item.name != "__init__.py":
                force_include[f"src/{item.name}"] = f"wizelit_sdk/{item.name}"
        
        # Map each package from src/<module> to wizelit_sdk/<module>
        for item in src_path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                module_name = item.name
                source_base = Path("src") / module_name
                target_base = Path("wizelit_sdk") / module_name
                
                # Recursively map all files in the package
                for py_file in item.rglob("*"):
                    if py_file.is_file():
                        rel_path = py_file.relative_to(src_path / module_name)
                        source_path = source_base / rel_path
                        target_path = target_base / rel_path
                        # Map source to target (use forward slashes for wheel paths)
                        force_include[str(source_path).replace("\\", "/")] = str(target_path).replace("\\", "/")

