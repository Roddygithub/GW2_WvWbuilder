#!/usr/bin/env python3
"""
Backend Monitoring Script
Checks health, uptime, and basic metrics
"""

import asyncio
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, Any

import httpx
import psutil


class BackendMonitor:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.start_time = datetime.now()
    
    async def check_health(self) -> Dict[str, Any]:
        """Check if backend is responding"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/v1/health")
                return {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "status_code": response.status_code,
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }
    
    async def check_api_endpoints(self) -> Dict[str, Any]:
        """Test key API endpoints"""
        endpoints = [
            "/api/v1/health",
            "/docs",
        ]
        
        results = {}
        async with httpx.AsyncClient(timeout=5.0) as client:
            for endpoint in endpoints:
                try:
                    response = await client.get(f"{self.base_url}{endpoint}")
                    results[endpoint] = {
                        "status_code": response.status_code,
                        "ok": response.status_code < 400,
                    }
                except Exception as e:
                    results[endpoint] = {
                        "status_code": 0,
                        "ok": False,
                        "error": str(e),
                    }
        
        return results
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system resource usage"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "load_average": psutil.getloadavg(),
        }
    
    def get_process_metrics(self) -> Dict[str, Any]:
        """Get metrics for backend process"""
        try:
            # Find uvicorn process
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any('uvicorn' in str(cmd) for cmd in cmdline):
                    process = psutil.Process(proc.info['pid'])
                    return {
                        "pid": process.pid,
                        "cpu_percent": process.cpu_percent(interval=1),
                        "memory_mb": process.memory_info().rss / 1024 / 1024,
                        "threads": process.num_threads(),
                        "uptime_seconds": (datetime.now() - datetime.fromtimestamp(process.create_time())).total_seconds(),
                    }
        except Exception as e:
            return {"error": str(e)}
        
        return {"status": "not_found"}
    
    async def run_health_check(self) -> Dict[str, Any]:
        """Run complete health check"""
        health = await self.check_health()
        endpoints = await self.check_api_endpoints()
        system = self.get_system_metrics()
        process = self.get_process_metrics()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "health": health,
            "endpoints": endpoints,
            "system": system,
            "process": process,
        }
    
    def format_report(self, data: Dict[str, Any]) -> str:
        """Format monitoring report"""
        lines = [
            "=" * 60,
            f"GW2 WvW Builder - Backend Monitoring Report",
            f"Time: {data['timestamp']}",
            "=" * 60,
            "",
            "🏥 Health Status:",
            f"  Status: {data['health']['status']}",
        ]
        
        if 'response_time_ms' in data['health']:
            lines.append(f"  Response Time: {data['health']['response_time_ms']:.2f}ms")
        
        lines.extend([
            "",
            "📊 API Endpoints:",
        ])
        
        for endpoint, info in data['endpoints'].items():
            status = "✅" if info['ok'] else "❌"
            lines.append(f"  {status} {endpoint}: HTTP {info['status_code']}")
        
        lines.extend([
            "",
            "💻 System Metrics:",
            f"  CPU: {data['system']['cpu_percent']}%",
            f"  Memory: {data['system']['memory_percent']}%",
            f"  Disk: {data['system']['disk_percent']}%",
            f"  Load Average: {data['system']['load_average']}",
        ])
        
        if 'pid' in data['process']:
            uptime = timedelta(seconds=int(data['process']['uptime_seconds']))
            lines.extend([
                "",
                "🔧 Backend Process:",
                f"  PID: {data['process']['pid']}",
                f"  CPU: {data['process']['cpu_percent']}%",
                f"  Memory: {data['process']['memory_mb']:.1f} MB",
                f"  Threads: {data['process']['threads']}",
                f"  Uptime: {uptime}",
            ])
        elif 'error' in data['process']:
            lines.append(f"  ⚠️  Process: {data['process']['error']}")
        else:
            lines.append("  ⚠️  Backend process not found")
        
        lines.extend([
            "",
            "=" * 60,
        ])
        
        return "\n".join(lines)


async def main():
    monitor = BackendMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--watch":
        # Watch mode: continuous monitoring
        print("Starting continuous monitoring (Ctrl+C to stop)...")
        try:
            while True:
                data = await monitor.run_health_check()
                print("\033[2J\033[H")  # Clear screen
                print(monitor.format_report(data))
                await asyncio.sleep(5)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
    else:
        # Single check
        data = await monitor.run_health_check()
        print(monitor.format_report(data))
        
        # Exit code based on health
        if data['health']['status'] != "healthy":
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
