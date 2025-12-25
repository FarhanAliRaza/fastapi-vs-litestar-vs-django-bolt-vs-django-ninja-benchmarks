#!/usr/bin/env python3
"""
Framework Benchmark Runner

Benchmarks 4 frameworks with 4 endpoints each using bombardier:
- FastAPI
- Litestar
- Django Ninja
- Django Bolt

Endpoints:
1. /json-1k  - ~1KB JSON response
2. /json-10k - ~10KB JSON response
3. /db       - 10 database reads
4. /slow     - 2 second mock delay

Best practices followed:
- Warmup requests before benchmarking
- Multiple runs for consistency
- Controlled concurrency
- Results saved to markdown
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


@dataclass
class BenchConfig:
    """Benchmark configuration."""

    connections: int = 100  # Concurrent connections
    duration: int = 10      # Duration in seconds
    warmup_requests: int = 1000  # Warmup requests
    runs: int = 3           # Number of runs per endpoint


@dataclass
class BenchResult:
    """Single benchmark result."""

    framework: str
    endpoint: str
    rps: float
    latency_avg_ms: float
    latency_p99_ms: float
    errors: int
    duration_s: float


FRAMEWORKS = {
    "fastapi": {"port": 8001, "prefix": ""},
    "litestar": {"port": 8002, "prefix": ""},
    "django-ninja": {"port": 8003, "prefix": "/ninja"},
    "django-bolt": {"port": 8004, "prefix": ""},
}

ENDPOINTS = [
    "/json-1k",
    "/json-10k",
    "/db",
    "/slow",
]


def run_bombardier(
    url: str,
    connections: int,
    duration: int,
) -> dict | None:
    """Run bombardier and return parsed results."""
    cmd = [
        "bombardier",
        "-c", str(connections),
        "-d", f"{duration}s",
        "--print", "r",
        "--format", "json",
        url,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=duration + 30,
        )
        if result.returncode != 0:
            print(f"  ERROR: bombardier failed: {result.stderr}")
            return None

        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        print(f"  ERROR: bombardier timed out")
        return None
    except json.JSONDecodeError as e:
        print(f"  ERROR: Failed to parse bombardier output: {e}")
        return None
    except FileNotFoundError:
        print("ERROR: bombardier not found. Install it first:")
        print("  go install github.com/codesenberg/bombardier@latest")
        sys.exit(1)


def warmup(url: str, requests: int) -> bool:
    """Send warmup requests using bombardier."""
    cmd = [
        "bombardier",
        "-c", "10",
        "-n", str(requests),
        "--print", "r",
        url,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, timeout=60)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_server(host: str, port: int, prefix: str) -> bool:
    """Check if server is responding."""
    import urllib.request
    import urllib.error

    url = f"http://{host}:{port}{prefix}/json-1k"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError):
        return False


def benchmark_framework(
    framework: str,
    host: str,
    port: int,
    prefix: str,
    config: BenchConfig,
) -> list[BenchResult]:
    """Benchmark a single framework."""
    results = []
    base_url = f"http://{host}:{port}{prefix}"

    print(f"\n{'='*60}")
    print(f"Benchmarking: {framework.upper()}")
    print(f"Base URL: {base_url}")
    print(f"{'='*60}")

    # Check server
    if not check_server(host, port, prefix):
        print(f"  ERROR: Server not responding at {base_url}")
        return results

    for endpoint in ENDPOINTS:
        url = f"{base_url}{endpoint}"
        print(f"\n  Endpoint: {endpoint}")

        # Warmup
        print(f"    Warming up ({config.warmup_requests} requests)...")
        if not warmup(url, config.warmup_requests):
            print(f"    WARNING: Warmup failed")

        # Multiple runs
        run_results = []
        for run in range(config.runs):
            print(f"    Run {run + 1}/{config.runs}...", end=" ", flush=True)

            data = run_bombardier(url, config.connections, config.duration)
            if data is None:
                print("FAILED")
                continue

            rps = data.get("result", {}).get("rps", {}).get("mean", 0)
            latency = data.get("result", {}).get("latency", {})
            latency_avg = latency.get("mean", 0) / 1_000_000  # ns to ms
            latency_p99 = latency.get("percentiles", {}).get("99", 0) / 1_000_000

            errors = 0
            for code, count in data.get("result", {}).get("statusCodeDistribution", {}).items():
                if not code.startswith("2"):
                    errors += count

            print(f"RPS: {rps:,.0f}, Latency: {latency_avg:.2f}ms (p99: {latency_p99:.2f}ms)")

            run_results.append({
                "rps": rps,
                "latency_avg": latency_avg,
                "latency_p99": latency_p99,
                "errors": errors,
            })

        if run_results:
            # Take the best RPS run
            best = max(run_results, key=lambda x: x["rps"])
            results.append(BenchResult(
                framework=framework,
                endpoint=endpoint,
                rps=best["rps"],
                latency_avg_ms=best["latency_avg"],
                latency_p99_ms=best["latency_p99"],
                errors=best["errors"],
                duration_s=config.duration,
            ))

    return results


def generate_markdown_report(results: list[BenchResult], config: BenchConfig) -> str:
    """Generate markdown benchmark report."""
    lines = [
        "# Framework Benchmark Results",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Configuration",
        "",
        f"- Connections: {config.connections}",
        f"- Duration: {config.duration}s per endpoint",
        f"- Warmup: {config.warmup_requests} requests",
        f"- Runs: {config.runs} (best result taken)",
        "",
        "## Endpoints",
        "",
        "| Endpoint | Description |",
        "|----------|-------------|",
        "| `/json-1k` | ~1KB JSON response |",
        "| `/json-10k` | ~10KB JSON response |",
        "| `/db` | 10 database reads |",
        "| `/slow` | 2 second mock delay |",
        "",
        "## Results",
        "",
    ]

    # Group by endpoint
    for endpoint in ENDPOINTS:
        endpoint_results = [r for r in results if r.endpoint == endpoint]
        if not endpoint_results:
            continue

        lines.append(f"### {endpoint}")
        lines.append("")
        lines.append("| Framework | RPS | Latency (avg) | Latency (p99) | Errors |")
        lines.append("|-----------|----:|-------------:|-------------:|-------:|")

        # Sort by RPS descending
        endpoint_results.sort(key=lambda x: x.rps, reverse=True)

        for r in endpoint_results:
            lines.append(
                f"| {r.framework} | {r.rps:,.0f} | {r.latency_avg_ms:.2f}ms | "
                f"{r.latency_p99_ms:.2f}ms | {r.errors} |"
            )

        lines.append("")

    # Summary table
    lines.append("## Summary (RPS by Endpoint)")
    lines.append("")

    header = "| Framework |"
    separator = "|-----------|"
    for endpoint in ENDPOINTS:
        header += f" {endpoint} |"
        separator += "--------:|"

    lines.append(header)
    lines.append(separator)

    frameworks_in_results = list(set(r.framework for r in results))
    for framework in frameworks_in_results:
        row = f"| {framework} |"
        for endpoint in ENDPOINTS:
            r = next((x for x in results if x.framework == framework and x.endpoint == endpoint), None)
            if r:
                row += f" {r.rps:,.0f} |"
            else:
                row += " - |"
        lines.append(row)

    lines.append("")

    return "\n".join(lines)


def generate_graph(results: list[BenchResult], endpoint: str, output_path: Path) -> None:
    """Generate a bar chart with rounded corners for a specific endpoint."""
    # Filter results for this endpoint
    endpoint_results = [r for r in results if r.endpoint == endpoint]
    if not endpoint_results:
        return

    # Sort by RPS ascending (lowest first, like the reference image)
    endpoint_results.sort(key=lambda x: x.rps)

    frameworks = [r.framework for r in endpoint_results]
    rps_values = [r.rps for r in endpoint_results]

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 7))

    # Colors - olive green like the reference image
    bar_color = "#8FBC8F"  # Dark sea green
    edge_color = "#6B8E6B"

    # Bar positions and width
    x_positions = range(len(frameworks))
    bar_width = 0.6

    # Draw rounded rectangle bars using FancyBboxPatch
    for i, (x, rps) in enumerate(zip(x_positions, rps_values)):
        # Create rounded rectangle
        fancy_box = FancyBboxPatch(
            (x - bar_width / 2, 0),  # (x, y) bottom-left corner
            bar_width,  # width
            rps,  # height
            boxstyle="round,pad=0,rounding_size=0.02",
            facecolor=bar_color,
            edgecolor=edge_color,
            linewidth=1,
            mutation_aspect=rps / bar_width * 0.01,  # Adjust rounding based on aspect
        )
        ax.add_patch(fancy_box)

        # Add value label above bar
        ax.text(
            x,
            rps + max(rps_values) * 0.02,
            f"{rps:,.0f}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    # Set axis limits
    ax.set_xlim(-0.5, len(frameworks) - 0.5)
    ax.set_ylim(0, max(rps_values) * 1.15)

    # Labels and ticks
    ax.set_xticks(list(x_positions))
    ax.set_xticklabels(frameworks, rotation=45, ha="right", fontsize=11)
    ax.set_ylabel("Requests per Second (RPS)", fontsize=12)

    # Title
    endpoint_name = endpoint.replace("/", "").replace("-", " ").title()
    ax.set_title(f"Framework Benchmark - {endpoint_name}", fontsize=14, fontweight="bold", pad=20)

    # Format y-axis with commas
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:,.0f}"))

    # Grid (only horizontal)
    ax.yaxis.grid(True, linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)

    # Remove top and right spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Tight layout
    plt.tight_layout()

    # Save
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()


def generate_combined_graph(results: list[BenchResult], output_path: Path) -> None:
    """Generate a single chart with all endpoints grouped by framework."""
    if not results:
        return

    # Get unique frameworks and endpoints
    frameworks = sorted(set(r.framework for r in results))
    endpoints = sorted(set(r.endpoint for r in results))

    # Sort frameworks by average RPS across all endpoints
    framework_avg_rps = {}
    for fw in frameworks:
        fw_results = [r.rps for r in results if r.framework == fw]
        framework_avg_rps[fw] = sum(fw_results) / len(fw_results) if fw_results else 0
    frameworks = sorted(frameworks, key=lambda f: framework_avg_rps[f])

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 8))

    # Colors for each endpoint
    colors = ["#8FBC8F", "#87CEEB", "#DDA0DD", "#F0E68C"]  # Green, Blue, Purple, Yellow
    edge_colors = ["#6B8E6B", "#5F9EA0", "#BA55D3", "#BDB76B"]

    # Bar settings
    n_frameworks = len(frameworks)
    n_endpoints = len(endpoints)
    bar_width = 0.8 / n_endpoints
    x_positions = range(n_frameworks)

    # Draw bars for each endpoint
    for i, endpoint in enumerate(endpoints):
        offset = (i - n_endpoints / 2 + 0.5) * bar_width
        rps_values = []

        for fw in frameworks:
            r = next((x for x in results if x.framework == fw and x.endpoint == endpoint), None)
            rps_values.append(r.rps if r else 0)

        # Draw rounded bars
        for j, (x, rps) in enumerate(zip(x_positions, rps_values)):
            if rps > 0:
                fancy_box = FancyBboxPatch(
                    (x + offset - bar_width / 2, 0),
                    bar_width * 0.9,
                    rps,
                    boxstyle="round,pad=0,rounding_size=0.015",
                    facecolor=colors[i % len(colors)],
                    edgecolor=edge_colors[i % len(edge_colors)],
                    linewidth=1,
                    mutation_aspect=rps / bar_width * 0.005,
                    label=endpoint if j == 0 else "",
                )
                ax.add_patch(fancy_box)

                # Add value label above bar
                ax.text(
                    x + offset,
                    rps + max(r.rps for r in results) * 0.01,
                    f"{rps:,.0f}",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                    fontweight="bold",
                    rotation=90,
                )

    # Set axis limits
    max_rps = max(r.rps for r in results)
    ax.set_xlim(-0.5, n_frameworks - 0.5)
    ax.set_ylim(0, max_rps * 1.25)

    # Labels and ticks
    ax.set_xticks(list(x_positions))
    ax.set_xticklabels(frameworks, rotation=45, ha="right", fontsize=11)
    ax.set_ylabel("Requests per Second (RPS)", fontsize=12)
    ax.set_title("Framework Benchmark - All Endpoints", fontsize=14, fontweight="bold", pad=20)

    # Format y-axis with commas
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:,.0f}"))

    # Grid
    ax.yaxis.grid(True, linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)

    # Remove top and right spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Legend
    legend_patches = [
        plt.Rectangle((0, 0), 1, 1, facecolor=colors[i % len(colors)], edgecolor=edge_colors[i % len(edge_colors)])
        for i in range(len(endpoints))
    ]
    ax.legend(legend_patches, endpoints, loc="upper left", fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()


def generate_all_graphs(results: list[BenchResult], output_dir: Path) -> list[Path]:
    """Generate graphs for all endpoints."""
    output_dir.mkdir(exist_ok=True)
    generated = []

    endpoints_in_results = list(set(r.endpoint for r in results))

    # Individual graphs for each endpoint
    for endpoint in endpoints_in_results:
        filename = f"benchmark_{endpoint.replace('/', '').replace('-', '_')}.png"
        output_path = output_dir / filename
        generate_graph(results, endpoint, output_path)
        generated.append(output_path)
        print(f"  Generated: {output_path}")

    # Combined graph with all endpoints
    combined_path = output_dir / "benchmark_combined.png"
    generate_combined_graph(results, combined_path)
    generated.append(combined_path)
    print(f"  Generated: {combined_path}")

    return generated


def main():
    parser = argparse.ArgumentParser(description="Framework Benchmark Runner")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("-c", "--connections", type=int, default=100, help="Concurrent connections")
    parser.add_argument("-d", "--duration", type=int, default=10, help="Duration per endpoint (seconds)")
    parser.add_argument("-w", "--warmup", type=int, default=1000, help="Warmup requests")
    parser.add_argument("-r", "--runs", type=int, default=3, help="Runs per endpoint")
    parser.add_argument("-o", "--output", default="BENCHMARK_RESULTS.md", help="Output file")
    parser.add_argument("--frameworks", nargs="+", choices=list(FRAMEWORKS.keys()),
                        default=list(FRAMEWORKS.keys()), help="Frameworks to benchmark")
    parser.add_argument("--skip-slow", action="store_true", help="Skip the /slow endpoint")

    args = parser.parse_args()

    # Filter endpoints based on --skip-slow
    global ENDPOINTS
    if args.skip_slow:
        ENDPOINTS = [e for e in ENDPOINTS if e != "/slow"]

    config = BenchConfig(
        connections=args.connections,
        duration=args.duration,
        warmup_requests=args.warmup,
        runs=args.runs,
    )

    print("Framework Benchmark")
    print("=" * 60)
    print(f"Host: {args.host}")
    print(f"Connections: {config.connections}")
    print(f"Duration: {config.duration}s")
    print(f"Warmup: {config.warmup_requests} requests")
    print(f"Runs: {config.runs}")
    print(f"Frameworks: {', '.join(args.frameworks)}")

    all_results = []

    for framework in args.frameworks:
        fw_config = FRAMEWORKS[framework]
        results = benchmark_framework(
            framework=framework,
            host=args.host,
            port=fw_config["port"],
            prefix=fw_config["prefix"],
            config=config,
        )
        all_results.extend(results)

    if all_results:
        report = generate_markdown_report(all_results, config)
        output_path = Path(args.output)
        output_path.write_text(report)
        print(f"\nResults saved to: {output_path}")
        print("\n" + report)

        # Generate graphs
        print("\nGenerating graphs...")
        graph_dir = Path("graphs")
        generate_all_graphs(all_results, graph_dir)
        print(f"Graphs saved to: {graph_dir}/")
    else:
        print("\nNo results collected!")


if __name__ == "__main__":
    main()
