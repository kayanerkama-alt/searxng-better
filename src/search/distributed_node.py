# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Distributed Node System for Atomic Search
Allows users to run search nodes and contribute to the network
"""

import time
import hashlib
import secrets
import json
import threading
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from enum import Enum
import requests


class NodeStatus(Enum):
    """Node status values"""
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"


@dataclass
class SearchNode:
    """A distributed search node"""
    node_id: str
    name: str
    ip_address: str
    location: str
    registered_at: int
    last_seen: int
    status: str
   贡献_count: int = 0
    avg_response_ms: float = 0.0
    uptime_hours: float = 0.0
    api_key_hash: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "id": self.node_id,
            "name": self.name,
            "location": self.location,
            "registered_at": self.registered_at,
            "last_seen": self.last_seen,
            "status": self.status,
            "contributions": self.贡献_count,
            "avg_response_ms": round(self.avg_response_ms, 2),
            "uptime_hours": round(self.uptime_hours, 1)
        }


@dataclass
class NodeTask:
    """A task assigned to a node"""
    task_id: str
    task_type: str
    data: Dict
    assigned_at: int
    expires_at: int
    status: str = "pending"
    result: Optional[Dict] = None


class DistributedNodeSystem:
    """
    Manages the distributed node network
    Users can become nodes by visiting /node-start
    """
    
    NODE_REWARD_PER_SEARCH = 1  # Points per search contribution
    MAX_CONCURRENT_TASKS = 10
    
    def __init__(self):
        self._lock = threading.RLock()
        self._nodes: Dict[str, SearchNode] = {}
        self._api_keys: Dict[str, str] = {}  # api_key -> node_id
        self._tasks: Dict[str, NodeTask] = {}
        self._node_history: Dict[str, List[Dict]] = {}
        self._rewards: Dict[str, int] = {}  # node_id -> points
        
        # Start maintenance thread
        self._running = True
        self._maintenance_thread = threading.Thread(target=self._maintenance, daemon=True)
        self._maintenance_thread.start()
    
    def generate_registration_url(self, base_url: str = "") -> str:
        """Generate a unique registration URL for a new node"""
        token = secrets.token_urlsafe(32)
        return f"{base_url}/node/register?token={token}"
    
    def register_node(
        self,
        name: str,
        ip_address: str,
        location: str = "Unknown",
        token: Optional[str] = None
    ) -> Dict:
        """
        Register a new node
        
        Returns:
            Node info including API key
        """
        with self._lock:
            node_id = f"node_{secrets.token_hex(8)}"
            api_key = secrets.token_urlsafe(48)
            api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            node = SearchNode(
                node_id=node_id,
                name=name or f"Node-{node_id[-6:]}",
                ip_address=ip_address,
                location=location,
                registered_at=int(time.time()),
                last_seen=int(time.time()),
                status=NodeStatus.ACTIVE.value,
                api_key_hash=api_key_hash
            )
            
            self._nodes[node_id] = node
            self._api_keys[api_key_hash] = node_id
            self._rewards[node_id] = 0
            
            return {
                "success": True,
                "node_id": node_id,
                "api_key": api_key,
                "api_endpoint": f"/api/node/submit",
                "instructions": self._get_setup_instructions(node)
            }
    
    def _get_setup_instructions(self, node: SearchNode) -> Dict:
        """Get setup instructions for a node"""
        return {
            "welcome": f"Welcome to Atomic Search Network, {node.name}!",
            "steps": [
                "1. Save your API key securely (shown above)",
                "2. Install the Atomic Node client: pip install atomic-search-node",
                "3. Configure your client with the API key",
                "4. Start your node: atomic-node start",
                "5. Monitor at /node/status"
            ],
            "rewards": "Earn rewards for every search you help process!",
            "docs_url": "/info/en/node-docs"
        }
    
    def verify_api_key(self, api_key: str) -> Optional[str]:
        """Verify an API key and return node_id"""
        with self._lock:
            api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            return self._api_keys.get(api_key_hash)
    
    def node_heartbeat(self, node_id: str) -> Dict:
        """Node heartbeat to stay active"""
        with self._lock:
            if node_id in self._nodes:
                node = self._nodes[node_id]
                node.last_seen = int(time.time())
                node.status = NodeStatus.ACTIVE.value
                
                # Calculate uptime
                node.uptime_hours = (node.last_seen - node.registered_at) / 3600
                
                return {
                    "success": True,
                    "status": "active",
                    "pending_tasks": self._get_pending_tasks(node_id),
                    "rewards": self._rewards.get(node_id, 0)
                }
            return {"success": False, "error": "Node not found"}
    
    def _get_pending_tasks(self, node_id: str) -> List[Dict]:
        """Get pending tasks for a node"""
        tasks = []
        for task in self._tasks.values():
            if task.status == "pending" and task.expires_at > int(time.time()):
                tasks.append({
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                    "data": task.data
                })
                if len(tasks) >= self.MAX_CONCURRENT_TASKS:
                    break
        return tasks
    
    def submit_task_result(
        self,
        node_id: str,
        task_id: str,
        result: Dict,
        processing_time_ms: float
    ) -> Dict:
        """Submit a task result"""
        with self._lock:
            if node_id not in self._nodes:
                return {"success": False, "error": "Node not found"}
            
            if task_id not in self._tasks:
                return {"success": False, "error": "Task not found"}
            
            task = self._tasks[task_id]
            task.status = "completed"
            task.result = result
            
            # Calculate rewards
            base_reward = self.NODE_REWARD_PER_SEARCH
            speed_bonus = max(0, 100 - processing_time_ms / 10)  # Faster = more reward
            reward = int(base_reward + speed_bonus)
            
            self._rewards[node_id] = self._rewards.get(node_id, 0) + reward
            
            # Update node stats
            node = self._nodes[node_id]
            node.贡献_count += 1
            
            # Running average
            if node.贡献_count > 0:
                node.avg_response_ms = (
                    (node.avg_response_ms * (node.贡献_count - 1) + processing_time_ms)
                    / node.贡献_count
                )
            
            return {
                "success": True,
                "reward": reward,
                "total_rewards": self._rewards[node_id]
            }
    
    def contribute_search(self, node_id: str, query: str, results: List[Dict]) -> Dict:
        """Node contributes search results"""
        with self._lock:
            if node_id not in self._nodes:
                return {"success": False, "error": "Node not found"}
            
            node = self._nodes[node_id]
            node.贡献_count += 1
            
            # Small reward for contributing
            reward = 1
            self._rewards[node_id] = self._rewards.get(node_id, 0) + reward
            
            # Store in history
            if node_id not in self._node_history:
                self._node_history[node_id] = []
            
            self._node_history[node_id].append({
                "query": query[:100],
                "results_count": len(results),
                "timestamp": int(time.time())
            })
            
            # Keep only last 100 entries
            if len(self._node_history[node_id]) > 100:
                self._node_history[node_id].pop(0)
            
            return {
                "success": True,
                "reward": reward,
                "total_contributions": node.贡献_count
            }
    
    def get_node_status(self, node_id: str, api_key: str) -> Optional[Dict]:
        """Get detailed node status"""
        verified_id = self.verify_api_key(api_key)
        if verified_id != node_id:
            return None
        
        with self._lock:
            if node_id not in self._nodes:
                return None
            
            node = self._nodes[node_id]
            
            return {
                **node.to_dict(),
                "rewards": self._rewards.get(node_id, 0),
                "recent_activity": self._node_history.get(node_id, [])[-10:],
                "network_stats": self._get_network_stats()
            }
    
    def _get_network_stats(self) -> Dict:
        """Get overall network statistics"""
        with self._lock:
            total_nodes = len(self._nodes)
            active_nodes = sum(1 for n in self._nodes.values() if n.status == "active")
            total_contributions = sum(n.贡献_count for n in self._nodes.values())
            
            return {
                "total_nodes": total_nodes,
                "active_nodes": active_nodes,
                "total_contributions": total_contributions,
                "network_health": round(active_nodes / total_nodes * 100, 1) if total_nodes else 0
            }
    
    def list_nodes(self, include_inactive: bool = False) -> List[Dict]:
        """List all nodes"""
        with self._lock:
            nodes = list(self._nodes.values())
            if not include_inactive:
                nodes = [n for n in nodes if n.status == "active"]
            return [n.to_dict() for n in nodes]
    
    def _maintenance(self):
        """Background maintenance"""
        while self._running:
            time.sleep(60)  # Every minute
            
            with self._lock:
                now = int(time.time())
                
                # Mark inactive nodes
                for node in self._nodes.values():
                    if now - node.last_seen > 300:  # 5 minutes
                        node.status = NodeStatus.INACTIVE.value
                
                # Clean expired tasks
                self._tasks = {
                    k: v for k, v in self._tasks.items()
                    if v.expires_at > now
                }
    
    def shutdown(self):
        """Shutdown the node system"""
        self._running = False


# Global instance
_node_system = DistributedNodeSystem()


def get_node_system() -> DistributedNodeSystem:
    """Get the node system"""
    return _node_system


def register_node(name: str, ip: str, location: str = "Unknown") -> Dict:
    """Register a new node"""
    return _node_system.register_node(name, ip, location)


def node_heartbeat(node_id: str) -> Dict:
    """Send node heartbeat"""
    return _node_system.node_heartbeat(node_id)


def get_node_status(node_id: str, api_key: str) -> Optional[Dict]:
    """Get node status"""
    return _node_system.get_node_status(node_id, api_key)


def list_all_nodes() -> List[Dict]:
    """List all nodes"""
    return _node_system.list_nodes()
