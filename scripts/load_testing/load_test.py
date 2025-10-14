#!/usr/bin/env python3
"""
GW2 WvW Builder - Load Testing Script
Version: 1.0.0
Purpose: Performance and load testing for backend API
"""

import asyncio
import time
from typing import Dict, List
import statistics
import httpx
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# Configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_USER_EMAIL = "frontend@user.com"
TEST_USER_PASSWORD = "Frontend123!"

class LoadTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results: Dict[str, List[float]] = {}
        self.token = None
    
    async def get_token(self) -> str:
        """Authenticate and get JWT token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/login",
                data={
                    "username": TEST_USER_EMAIL,
                    "password": TEST_USER_PASSWORD
                }
            )
            if response.status_code == 200:
                data = response.json()
                return data["access_token"]
            else:
                raise Exception(f"Authentication failed: {response.status_code}")
    
    async def test_endpoint(
        self,
        name: str,
        method: str,
        endpoint: str,
        iterations: int = 100,
        concurrent: int = 10,
        use_auth: bool = False
    ) -> Dict:
        """Test an endpoint with concurrent requests"""
        
        console.print(f"\n[cyan]Testing {name}...[/cyan]")
        console.print(f"  Iterations: {iterations}, Concurrent: {concurrent}")
        
        response_times = []
        status_codes = []
        errors = 0
        
        headers = {}
        if use_auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        async def make_request():
            start = time.time()
            try:
                async with httpx.AsyncClient() as client:
                    if method == "GET":
                        response = await client.get(
                            f"{self.base_url}{endpoint}",
                            headers=headers,
                            timeout=10.0
                        )
                    elif method == "POST":
                        response = await client.post(
                            f"{self.base_url}{endpoint}",
                            headers=headers,
                            timeout=10.0
                        )
                    
                    elapsed = time.time() - start
                    return elapsed, response.status_code, None
            except Exception as e:
                elapsed = time.time() - start
                return elapsed, 0, str(e)
        
        # Run requests in batches
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Running {name}...", total=iterations)
            
            for i in range(0, iterations, concurrent):
                batch_size = min(concurrent, iterations - i)
                tasks = [make_request() for _ in range(batch_size)]
                results = await asyncio.gather(*tasks)
                
                for elapsed, status, error in results:
                    response_times.append(elapsed)
                    status_codes.append(status)
                    if error or status == 0:
                        errors += 1
                
                progress.update(task, advance=batch_size)
        
        # Calculate statistics
        if response_times:
            stats = {
                "name": name,
                "total": iterations,
                "errors": errors,
                "success_rate": ((iterations - errors) / iterations) * 100,
                "avg_time": statistics.mean(response_times),
                "min_time": min(response_times),
                "max_time": max(response_times),
                "median_time": statistics.median(response_times),
                "p95_time": sorted(response_times)[int(len(response_times) * 0.95)] if len(response_times) > 20 else max(response_times),
                "requests_per_sec": iterations / sum(response_times) if sum(response_times) > 0 else 0
            }
        else:
            stats = {
                "name": name,
                "total": iterations,
                "errors": iterations,
                "success_rate": 0,
                "avg_time": 0,
                "min_time": 0,
                "max_time": 0,
                "median_time": 0,
                "p95_time": 0,
                "requests_per_sec": 0
            }
        
        self.results[name] = stats
        return stats
    
    def print_results(self):
        """Print formatted results table"""
        
        console.print("\n[bold green]═══════════════════════════════════════════════════════════[/bold green]")
        console.print("[bold green]                  LOAD TEST RESULTS                        [/bold green]")
        console.print("[bold green]═══════════════════════════════════════════════════════════[/bold green]\n")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Endpoint", style="cyan", width=30)
        table.add_column("Total", justify="right")
        table.add_column("Errors", justify="right")
        table.add_column("Success %", justify="right")
        table.add_column("Avg (ms)", justify="right")
        table.add_column("Min (ms)", justify="right")
        table.add_column("Max (ms)", justify="right")
        table.add_column("P95 (ms)", justify="right")
        table.add_column("Req/s", justify="right")
        
        for name, stats in self.results.items():
            success_style = "green" if stats["success_rate"] > 95 else "yellow" if stats["success_rate"] > 90 else "red"
            
            table.add_row(
                name,
                str(stats["total"]),
                str(stats["errors"]),
                f"[{success_style}]{stats['success_rate']:.1f}%[/{success_style}]",
                f"{stats['avg_time']*1000:.2f}",
                f"{stats['min_time']*1000:.2f}",
                f"{stats['max_time']*1000:.2f}",
                f"{stats['p95_time']*1000:.2f}",
                f"{stats['requests_per_sec']:.1f}"
            )
        
        console.print(table)
        
        # Overall summary
        total_requests = sum(s["total"] for s in self.results.values())
        total_errors = sum(s["errors"] for s in self.results.values())
        overall_success = ((total_requests - total_errors) / total_requests * 100) if total_requests > 0 else 0
        
        console.print(f"\n[bold]Overall Statistics:[/bold]")
        console.print(f"  Total Requests: {total_requests}")
        console.print(f"  Total Errors: {total_errors}")
        console.print(f"  Overall Success Rate: {overall_success:.2f}%")
        
        if overall_success >= 95:
            console.print("\n[bold green]✅ LOAD TEST PASSED[/bold green]")
        elif overall_success >= 90:
            console.print("\n[bold yellow]⚠️  LOAD TEST WARNING[/bold yellow]")
        else:
            console.print("\n[bold red]❌ LOAD TEST FAILED[/bold red]")

async def main():
    """Run load tests"""
    
    console.print("\n[bold blue]GW2 WvW Builder - Load Testing[/bold blue]")
    console.print("="*60)
    
    tester = LoadTester()
    
    # Get authentication token
    console.print("\n[yellow]Authenticating...[/yellow]")
    try:
        tester.token = await tester.get_token()
        console.print("[green]✓ Authentication successful[/green]")
    except Exception as e:
        console.print(f"[red]✗ Authentication failed: {e}[/red]")
        return
    
    # Define tests
    tests = [
        {
            "name": "Health Check",
            "method": "GET",
            "endpoint": "/api/v1/health",
            "iterations": 100,
            "concurrent": 20,
            "use_auth": False
        },
        {
            "name": "Dashboard Stats",
            "method": "GET",
            "endpoint": "/api/v1/dashboard/stats",
            "iterations": 50,
            "concurrent": 10,
            "use_auth": True
        },
        {
            "name": "Recent Activities",
            "method": "GET",
            "endpoint": "/api/v1/dashboard/activities?limit=10",
            "iterations": 50,
            "concurrent": 10,
            "use_auth": True
        },
        {
            "name": "User Profile",
            "method": "GET",
            "endpoint": "/api/v1/users/me",
            "iterations": 50,
            "concurrent": 10,
            "use_auth": True
        }
    ]
    
    # Run tests
    for test in tests:
        await tester.test_endpoint(**test)
        await asyncio.sleep(1)  # Brief pause between tests
    
    # Print results
    tester.print_results()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Load test interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
