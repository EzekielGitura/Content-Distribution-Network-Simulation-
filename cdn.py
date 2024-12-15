import socket
import threading
import hashlib
import time
import random
import json
import logging
import uuid
import queue
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import yaml

# Enhanced geolocation and server management
@dataclass
class ServerInfo:
    server_id: str
    host: str
    port: int
    location: Dict[str, float]
    health_score: float = 100.0
    last_health_check: float = 0
    total_requests: int = 0
    error_count: int = 0

class GeolocationService:
    """Advanced geolocation and distance calculation service"""
    @staticmethod
    def calculate_network_distance(loc1: Dict[str, float], loc2: Dict[str, float]) -> float:
        """
        Calculate network distance using Haversine formula
        
        :param loc1: First location coordinates
        :param loc2: Second location coordinates
        :return: Approximate network distance
        """
        from math import radians, sin, cos, sqrt, atan2

        R = 6371  # Earth radius in kilometers
        
        lat1, lon1 = radians(loc1['lat']), radians(loc1['lon'])
        lat2, lon2 = radians(loc2['lat']), radians(loc2['lon'])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c

class CDNManagementService:
    """Centralized management for CDN servers"""
    def __init__(self):
        self.servers: Dict[str, ServerInfo] = {}
        self.server_health_queue = queue.Queue()
        
    def register_server(self, server_info: ServerInfo):
        """
        Register a new server in the CDN
        
        :param server_info: Server information
        """
        self.servers[server_info.server_id] = server_info
        logging.info(f"Server {server_info.server_id} registered")
    
    def deregister_server(self, server_id: str):
        """
        Remove a server from the CDN
        
        :param server_id: Server identifier
        """
        if server_id in self.servers:
            del self.servers[server_id]
            logging.warning(f"Server {server_id} deregistered")
    
    def select_optimal_server(self, client_location: Dict[str, float]) -> Optional[ServerInfo]:
        """
        Select the most appropriate server based on location and health
        
        :param client_location: Client's geographical location
        :return: Optimal server for content delivery
        """
        healthy_servers = [
            server for server in self.servers.values() 
            if server.health_score > 50
        ]
        
        if not healthy_servers:
            return None
        
        return min(
            healthy_servers, 
            key=lambda s: (
                GeolocationService.calculate_network_distance(client_location, s.location),
                100 - s.health_score
            )
        )
    
    def perform_health_check(self):
        """
        Periodically check server health and update metrics
        """
        async def health_check():
            while True:
                for server in list(self.servers.values()):
                    try:
                        # Simulate health check
                        current_time = time.time()
                        if current_time - server.last_health_check > 30:
                            # Simulated health check logic
                            server.health_score = max(0, server.health_score - (server.error_count * 10))
                            server.last_health_check = current_time
                    except Exception as e:
                        logging.error(f"Health check failed for {server.server_id}: {e}")
                
                await asyncio.sleep(30)  # Check every 30 seconds
        
        asyncio.create_task(health_check())

class ContentServer:
    """
    Enhanced content server with advanced routing and error handling
    """
    def __init__(
        self, 
        management_service: CDNManagementService, 
        server_id: str, 
        location: Dict[str, float]
    ):
        # Previous implementation with added robustness
        # ... (keep existing implementation)
        
        # Add registration to management service
        server_info = ServerInfo(
            server_id=server_id,
            host=self.host,
            port=self.port,
            location=location,
            health_score=100.0
        )
        management_service.register_server(server_info)

class CDNMetricsExporter:
    """
    Prometheus-compatible metrics exporter
    """
    def __init__(self, management_service: CDNManagementService):
        self.management_service = management_service
    
    def generate_metrics(self) -> str:
        """
        Generate Prometheus-compatible metrics
        
        :return: Metrics in text format
        """
        metrics = []
        for server_id, server in self.management_service.servers.items():
            metrics.extend([
                f'cdn_server_health{{server_id="{server_id}"}} {server.health_score}',
                f'cdn_server_requests{{server_id="{server_id}"}} {server.total_requests}',
                f'cdn_server_errors{{server_id="{server_id}"}} {server.error_count}'
            ])
        
        return '\n'.join(metrics)

def load_configuration(config_path: str = 'config.yaml') -> Dict[str, Any]:
    """
    Load CDN configuration from YAML file
    
    :param config_path: Path to configuration file
    :return: Configuration dictionary
    """
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def main():
    """
    Enhanced CDN simulation main function
    """
    # Load configuration
    config = load_configuration()
    
    # Initialize management service
    management_service = CDNManagementService()
    
    # Start health monitoring
    management_service.perform_health_check()
    
    # Initialize metrics exporter
    metrics_exporter = CDNMetricsExporter(management_service)
    
    # Create servers with predefined locations
    server_locations = [
        {"lat": 40.7128, "lon": -74.0060},  # New York
        {"lat": 34.0522, "lon": -118.2437}, # Los Angeles
        {"lat": 37.7749, "lon": -122.4194}, # San Francisco
        # Add more locations
    ]
    
    # Simulation logic (similar to previous implementation)
    # Add more robust error handling and routing

if __name__ == "__main__":
    main()
