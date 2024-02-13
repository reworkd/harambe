import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List

from harambe.meta import url_to_netloc


class DataTracker(ABC):
    @abstractmethod
    async def save_data(self, new_data: List[Dict]):
        """Append data for a domain and stage to a JSON file"""
        raise NotImplementedError()

    @abstractmethod
    def load_data(self, url: str, stage: str) -> List[Dict]:
        """Load data for a domain and stage from a JSON file"""
        raise NotImplementedError()

    @abstractmethod
    def visit(self, url: str):
        """Mark the url as visited and save to the domain file"""
        raise NotImplementedError()

    @abstractmethod
    def has_been_visited(self, url: str) -> bool:
        """Check if the url has been visited"""
        raise NotImplementedError()


class StubTracker(DataTracker):
    async def save_data(self, new_data: List[Dict]):
        pass

    def load_data(self, url: str, stage: str) -> List[Dict]:
        return []

    def visit(self, url: str):
        pass

    def has_been_visited(self, url: str) -> bool:
        return False


class FileDataTracker(DataTracker):
    def __init__(self, domain: str, stage: str):
        # Define the storage directory as 'data' one level up from the current script
        self.storage_dir = Path(__file__).resolve().parent.parent / "data"
        # Ensure the storage directory exists
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.visited_urls = {}
        self.domain = url_to_netloc(domain)
        self.stage = stage

    def get_storage_filepath(self, data_type: str) -> Path:
        """Generate the filename for the given domain and data type"""
        return self.storage_dir / f"{self.domain}_{data_type}.json"

    def _load_visited_urls(self, domain: str) -> set:
        """Load visited urls for a domain from a JSON file"""
        domain_file = self.get_storage_filepath("urls")
        if domain_file.exists():
            with domain_file.open("r") as file:
                return set(json.load(file))
        return set()

    def _save_visited_urls(self, domain: str):
        """Save visited urls for a domain to a JSON file"""
        domain_file = self.get_storage_filepath("urls")
        with domain_file.open("w") as file:
            json.dump(list(self.visited_urls.get(domain, set())), file, indent=4)

    def save_data(self, *new_data: Dict):
        """Append data for a domain and stage to a JSON file"""
        domain_file = self.get_storage_filepath(self.stage)

        # Load existing data if file exists
        if domain_file.exists():
            with domain_file.open("r") as file:
                data = json.load(file)
        else:
            data = []

        # Append new data
        data.extend(new_data)

        # Save the updated data back to the JSON file
        with domain_file.open("w") as file:
            json.dump(data, file, indent=4)

    def load_data(self, url: str, stage: str) -> List[Dict]:
        """Load data for a domain and stage from a JSON file"""
        domain_file = self.get_storage_filepath(stage)
        if domain_file.exists():
            with domain_file.open("r") as file:
                return json.load(file)
        return []

    def visit(self, url: str):
        """Mark the url as visited and save to the domain file"""
        domain = self.domain
        if domain not in self.visited_urls:
            self.visited_urls[domain] = self._load_visited_urls(domain)
        self.visited_urls[domain].add(url)
        self._save_visited_urls(domain)

    def has_been_visited(self, url: str) -> bool:
        """Check if the url has been visited"""
        domain = url_to_netloc(url)
        if domain not in self.visited_urls:
            self.visited_urls[domain] = self._load_visited_urls(domain)
        return url in self.visited_urls[domain]
