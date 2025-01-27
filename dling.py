from docling.document_converter import DocumentConverter
from time import perf_counter
from datetime import datetime
import os
import numpy as np
from typing import List, Dict


def scrape_docling(url: str, output_dir: str = "docling_output") -> tuple[float, str]:
    """Scrape content using Docling and save to markdown file."""
    os.makedirs(output_dir, exist_ok=True)

    converter = DocumentConverter()

    start_time = perf_counter()
    result = converter.convert(url)
    end_time = perf_counter()
    execution_time = end_time - start_time

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"docling_scrape_{timestamp}.md")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result.document.export_to_markdown())

    return execution_time, output_file


def run_statistical_test(url: str, iterations: int = 5) -> Dict[str, float]:
    """Run multiple iterations of scraping and calculate statistics."""
    times = []
    last_output = ""

    for _ in range(iterations):
        execution_time, output_file = scrape_docling(url)
        times.append(execution_time)
        last_output = output_file

    return {
        "mean": np.mean(times),
        "std": np.std(times),
        "ci_95": 1.96 * np.std(times) / np.sqrt(iterations),  # 95% confidence interval
        "min": np.min(times),
        "max": np.max(times),
        "last_output": last_output,
    }


if __name__ == "__main__":
    test_urls = {
        "Wikipedia (Reference)": "https://en.wikipedia.org/wiki/Formula_One",
        "JS Rendered": "https://quotes.toscrape.com/js",
        "Table Layout": "https://quotes.toscrape.com/tableful",
        "Pagination": "https://quotes.toscrape.com",
        "Infinite Scroll": "https://quotes.toscrape.com/scroll",
    }

    results = []
    total_mean_time = 0
    iterations = 5  # Number of iterations per URL

    for site_name, url in test_urls.items():
        try:
            stats = run_statistical_test(url, iterations)
            results.append(
                {"site": site_name, "stats": stats, "file": stats["last_output"]}
            )
            total_mean_time += stats["mean"]
            print(f"Scraped {site_name}:")
            print(f"  Mean time: {stats['mean']:.4f} ± {stats['ci_95']:.4f} seconds")
            print(f"  Range: {stats['min']:.4f} - {stats['max']:.4f} seconds")
            print(f"Output saved to: {stats['last_output']}")
        except Exception as e:
            print(f"Error scraping {site_name}: {str(e)}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join("docling_output", f"scraping_results_{timestamp}.md")

    with open(results_file, "w", encoding="utf-8") as f:
        f.write("# Docling Scraping Test Results\n\n")
        f.write("| Site | Mean Time (s) | 95% CI | Min-Max (s) |\n")
        f.write("|------|---------------|---------|-------------|\n")
        for result in results:
            stats = result["stats"]
            f.write(
                f"| {result['site']} | {stats['mean']:.4f} | ±{stats['ci_95']:.4f} | "
                f"{stats['min']:.4f}-{stats['max']:.4f} |\n"
            )
        f.write("|------|---------------|---------|-------------|\n")
        f.write(f"| **Total Mean** | **{total_mean_time:.4f}** | | |\n\n")

        f.write("## Details\n")
        f.write(f"Number of iterations per URL: {iterations}\n\n")
        for result in results:
            f.write(f"* {result['site']}: Final output saved to `{result['file']}`\n")

    print(f"\nResults summary saved to: {results_file}")
