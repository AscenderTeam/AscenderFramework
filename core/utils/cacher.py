from pathlib import Path
from settings import BASE_PATH

import json


class AscCacher:
    
    def __init__(self) -> None:
        self._cache_dir = f"{BASE_PATH}/.asc_cache"
        self.prefix = "asc_"
        
        # Create cache directory if not exists
        self.initiate_cache_dir()
    
    def initiate_cache_dir(self) -> None:
        """
        Initiate cache directory.
        """
        Path(self._cache_dir).mkdir(parents=True, exist_ok=True)

    def save_json_cache(self, data: dict, keyname: str, is_binary: bool = False) -> None:
        """
        Save json data to cache file.

        Args:
            data (dict): Data needs to be cached
            keyname (str): Keyname of the cache file to be found later
            is_binary (bool): If True, the data will be saved as binary file. Defaults to False.
        """
        if is_binary:
            open(f"{self._cache_dir}/{self.prefix}{keyname}.asch", "wb").write(json.dumps(data).encode("utf-8"))
            return
        
        open(f"{self._cache_dir}/{self.prefix}{keyname}.asch", "w").write(json.dumps(data))
    
    def load_json_cache(self, keyname: str, is_binary: bool = False) -> dict | None:
        """
        Load json data from cache file.

        Args:
            keyname (str): Keyname of the cache file to be found later
            is_binary (bool): If True, the data will be loaded as binary file. Defaults to False.

        Returns:
            dict: Data from cache file
        """
        if not self.is_cache_exists(keyname):
            return None
        
        if is_binary:
            return json.loads(open(f"{self._cache_dir}/{self.prefix}{keyname}.asch", "rb").read().decode("utf-8"))
        
        return json.loads(open(f"{self._cache_dir}/{self.prefix}{keyname}.asch", "r").read())
    
    def save_text_cache(self, data: str, keyname: str, is_binary: bool = False) -> None:
        """
        Save text data to cache file.

        Args:
            data (str): Data needs to be cached
            keyname (str): Keyname of the cache file to be found later
            is_binary (bool): If True, the data will be saved as binary file. Defaults to False.
        """
        if is_binary:
            open(f"{self._cache_dir}/{self.prefix}{keyname}.asch", "wb").write(data.encode("utf-8"))
            return
        
        open(f"{self._cache_dir}/{self.prefix}{keyname}.asch", "w").write(data)
    
    def load_text_cache(self, keyname: str, is_binary: bool = False) -> str | None:
        """
        Load text data from cache file.

        Args:
            keyname (str): Keyname of the cache file to be found later
            is_binary (bool): If True, the data will be loaded as binary file. Defaults to False.

        Returns:
            str: Data from cache file
        """
        if not self.is_cache_exists(keyname):
            return None
        
        if is_binary:
            return open(f"{self._cache_dir}/{self.prefix}{keyname}.asch", "rb").read().decode("utf-8")
        
        return open(f"{self._cache_dir}/{self.prefix}{keyname}.asch", "r").read()
    
    def is_cache_exists(self, keyname: str) -> bool:
        """
        Check if cache file exists.

        Args:
            keyname (str): Keyname of the cache file to be found later

        Returns:
            bool: True if cache file exists, otherwise False
        """
        return Path(f"{self._cache_dir}/{self.prefix}{keyname}.asch").exists()