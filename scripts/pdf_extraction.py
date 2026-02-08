import os
import re
import math
import time
import json
import base64

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
from configparser import ConfigParser
from typing import Tuple, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from datetime import datetime


def log_timestamp(message: str) -> None:
    """Print message with timestamp prefix."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")


def split_into_batches(items: List[Any], batch_size: int = 500) -> List[List[Any]]:
    """Split list into batches of specified size."""
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]


def load_config(config_path: str) -> ConfigParser:
    """Load configuration from INI file."""
    config = ConfigParser()
    config_file = Path(__file__).parent.parent / config_path

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    config.read(config_file)
    return config


class DataFetcher:
    """Handles fetching and loading of PDF-to-image conversion data."""

    def __init__(self, config_path: str = "config.ini"):
        self.config = load_config(config_path)

    def _get_path(self, section: str, key: str) -> Path:
        """Get absolute path from config."""
        relative_path = self.config.get(section, key)
        return (Path(__file__).parent.parent / relative_path).resolve()

    def _load_png_files(self, directory: Path) -> List[str]:
        """Load all PNG file paths from directory."""
        if not directory.exists():
            print(f"Warning: Directory not found: {directory}")
            return []

        return [str(p) for p in directory.rglob("*.png")]

    def _load_requirements(self, file_path: Path) -> List[str]:
        """Load requirement strings from JSON file."""
        if not file_path.exists():
            print(f"Warning: Requirements file not found: {file_path}")
            return []

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [obj['requirement'] for obj in data]

    def _load_tests(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load test data from JSON file."""
        if not file_path.exists():
            print(f"Warning: Tests file not found: {file_path}")
            return []

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def fetch_all(self) -> Tuple[List[str], List[str], List[Dict[str, Any]]]:
        """
        Fetch all data: PDF-to-image paths, requirements, and tests.

        Returns:
            Tuple containing:
                - List of PNG file paths
                - List of requirement strings
                - List of test data dictionaries

        Note:
            All PDF-to-image conversion data is stored locally.
            Visit the Kaggle link in the repository to access this data.
        """
        pdf_to_image_dir = self._get_path("DATA", "pdf_to_image")
        requirements_file = self._get_path("DATA", "requirement")
        tests_file = self._get_path("DATA", "test")

        pdf_paths = self._load_png_files(pdf_to_image_dir)
        requirements = self._load_requirements(requirements_file)
        tests = self._load_tests(tests_file)

        return pdf_paths, requirements, tests


class OpenAIAPI:
    """Handles API calls to the OpenAI API with prompt management."""

    def __init__(self, api_key: str, config_path: str = "config.ini"):
        self.config = load_config(config_path)
        self.client = OpenAI(api_key=api_key)
        self._lock = Lock()  # Thread lock for thread-safe operations

    def request_chat(self, data: str):
        """
        Creates a chat POST request for the OpenAI API
        """
        return None

    def request_image(
        self,
        img_path: str,
        prompt: Dict[str, Any],
        detail: str = "low"
    ) -> Dict[str, Any]:
        """
        Creates an image POST request body for the OpenAI API.

        Args:
            img_path: Path to image file
            prompt: Dictionary with 'system' and 'user' keys
            detail: Image detail level ('low', or 'high')

        Returns:
            Request body dictionary
        """
        base64_image = self.encode_image(img_path)

        body: Dict[str, Any] = {
            "model": self.config.get("OpenAI", "model"),
            "messages": [
                {
                    "role": "system",
                    "content": prompt["system"]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt["user"]
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                                "detail": detail
                            }
                        }
                    ]
                }
            ]
        }

        return body

    def _process_single_image(
        self,
        img_path: str,
        index: int,
        prompt: Dict[str, Any],
        detail: str,
        temperature: float,
        top_p: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """
        Process a single image for batch request (thread worker function).

        Args:
            img_path: Path to image file
            index: Index for custom_id
            prompt: Prompt dictionary
            detail: Image detail level
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            max_tokens: Maximum tokens to generate

        Returns:
            Formatted batch request dictionary
        """
        try:
            # Get request body for this image
            body = self.request_image(img_path, prompt, detail)
            body["temperature"] = temperature
            body["top_p"] = top_p
            body["max_tokens"] = max_tokens

            # Create batch request format
            batch_request = {
                "custom_id": f"request-{index}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": body
            }

            return batch_request

        except Exception as e:
            return {
                "custom_id": f"request-{index}",
                "error": str(e),
                "img_path": img_path
            }

    def create_batch_img_jsonl(
        self,
        paths: List[str],
        prompt: Dict[str, Any],
        detail: str = "low",
        temperature: float = 1.0,
        top_p: float = 1.0,
        max_tokens: int = 2560,
        max_workers: int = 10
    ) -> Dict[str, Any]:
        """
        Create a JSONL file for batch image analysis requests using multithreading.

        Args:
            paths: List of image file paths
            prompt: Dictionary with 'system' and 'user' prompt keys
            output_path: Path to save the JSONL file
            detail: Image detail level ('low' or 'high')
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            max_tokens: Maximum tokens to generate
            max_workers: Number of threads to use

        Returns:
            Dictionary with results summary
        """
        if not paths:
            raise ValueError("Image paths list cannot be empty")

        if "system" not in prompt or "user" not in prompt:
            raise ValueError("Prompt must contain 'system' and 'user' keys")

        batch_requests = []
        errors = []

        output_path = (Path(__file__).parent.parent / "batch" /
                       "batch_image_requests.jsonl").resolve()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_index = {
                executor.submit(
                    self._process_single_image,
                    img_path,
                    idx,
                    prompt,
                    detail,
                    temperature,
                    top_p,
                    max_tokens
                ): (idx, img_path)
                for idx, img_path in enumerate(paths, start=1)
            }

            # Collect results as they complete
            for future in as_completed(future_to_index):
                idx, img_path = future_to_index[future]
                try:
                    result = future.result()

                    if "error" in result:
                        errors.append({
                            "index": idx,
                            "path": img_path,
                            "error": result["error"]
                        })
                    else:
                        batch_requests.append(result)

                except Exception as e:
                    errors.append({
                        "index": idx,
                        "path": img_path,
                        "error": str(e)
                    })

        # Sort batch_requests by custom_id to maintain order
        batch_requests.sort(key=lambda x: int(x["custom_id"].split("-")[1]))

        # Write to JSONL file
        output_file = Path(output_path)
        with open(output_file, 'w', encoding='utf-8') as f:
            for request in batch_requests:
                f.write(json.dumps(request) + '\n')

        # Return summary
        return {
            "success": True,
            "total_images": len(paths),
            "successful_requests": len(batch_requests),
            "failed_requests": len(errors),
            "output_file": str(output_file),
            "errors": errors if errors else None
        }

    def encode_image(self, img_path: str) -> str:
        """Encode image to base64 string."""

        if not Path(img_path).exists():
            raise FileNotFoundError(f"Image file not found: {img_path}")

        with open(img_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")


def fetch_data() -> Tuple[List[str], List[str], List[Dict[str, Any]]]:
    """
    Fetch PDF-to-image data, requirements, and tests.
    """
    fetcher = DataFetcher()
    return fetcher.fetch_all()


if __name__ == "__main__":
    log_timestamp("Starting batch processing...")

    pdf_to_images, requirements, tests = fetch_data()

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    openai_api = OpenAIAPI(api_key=api_key)
    config = load_config("config.ini")

    with open(Path(__file__).parent.parent / config.get("DATA", "prompt")) as f:
        prompts = json.load(f)

    # Process batches
    BATCH_SIZE = 50
    image_batches = split_into_batches(pdf_to_images, BATCH_SIZE)
    total_batches = len(image_batches)
    total_images = len(pdf_to_images)

    log_timestamp(f"Total images: {total_images}")
    log_timestamp(
        f"Split into {total_batches} batches of {BATCH_SIZE} images each\n")

    all_batch_jobs = []

    # Create all batch jobs
    for batch_idx, image_batch in enumerate(image_batches, start=1):
        log_timestamp(
            f"=== Processing Batch {batch_idx}/{total_batches} ({len(image_batch)} images) ===")

        # Create JSONL for this batch
        result = openai_api.create_batch_img_jsonl(
            paths=image_batch,
            prompt=prompts["pdf_to_image"],
            detail="high",
            max_tokens=4096
        )

        log_timestamp(
            f"JSONL created: {result['successful_requests']}/{result['total_images']} successful")

        if result['failed_requests'] > 0:
            log_timestamp(
                f"WARNING: {result['failed_requests']} requests failed during JSONL creation")

        # Rename the JSONL file to include batch number
        original_file = Path(result['output_file'])
        batch_file_path = original_file.parent / \
            f"batch_{batch_idx}_image_requests.jsonl"
        original_file.rename(batch_file_path)

        # Upload batch file
        log_timestamp("Uploading batch file...")
        batch_file = openai_api.client.files.create(
            file=open(batch_file_path, "rb"),
            purpose="batch"
        )
        log_timestamp(f"Batch file uploaded: {batch_file.id}")

        # Create batch job
        batch_job = openai_api.client.batches.create(
            input_file_id=batch_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h"
        )

        all_batch_jobs.append({
            'batch_number': batch_idx,
            'job_id': batch_job.id,
            'image_count': len(image_batch),
            'status': batch_job.status
        })

        log_timestamp(f"Batch job created: {batch_job.id}")
        log_timestamp(f"Status: {batch_job.status}\n")

    # Monitor all batch jobs
    log_timestamp(f"All {total_batches} batch jobs submitted!")
    log_timestamp("Monitoring progress (checking every 60 seconds)...\n")

    completed_batches = set()
    last_status_update = {}

    while len(completed_batches) < total_batches:
        for batch_info in all_batch_jobs:
            batch_num = batch_info['batch_number']

            # Skip if already completed
            if batch_num in completed_batches:
                continue

            batch_job = openai_api.client.batches.retrieve(
                batch_info['job_id'])

            # Check if request_counts is available
            if hasattr(batch_job, 'request_counts') and batch_job.request_counts:
                counts = batch_job.request_counts
                total = counts.total
                completed = counts.completed
                failed = counts.failed

                # Only print if there's progress
                last_completed = last_status_update.get(batch_num, 0)
                if completed != last_completed:
                    progress_pct = (completed / total *
                                    100) if total > 0 else 0
                    log_timestamp(
                        f"Batch {batch_num}/{total_batches}: {completed}/{total} ({progress_pct:.1f}%) | Failed: {failed} | Status: {batch_job.status}")
                    last_status_update[batch_num] = completed

            # Check if batch is done
            if batch_job.status in ["completed", "failed", "expired", "cancelled"]:
                if batch_num not in completed_batches:
                    log_timestamp(
                        f"Batch {batch_num}/{total_batches} finished with status: {batch_job.status}")
                    completed_batches.add(batch_num)
                    batch_info['final_status'] = batch_job.status
                    batch_info['output_file_id'] = batch_job.output_file_id if hasattr(
                        batch_job, 'output_file_id') else None

        if len(completed_batches) < total_batches:
            time.sleep(60)

    # Download and save results from all batches
    log_timestamp("\nAll batches completed")
    log_timestamp("Downloading and consolidating results...\n")

    all_extraction_data = []
    successful_batches = 0
    failed_batches = 0

    for batch_info in all_batch_jobs:
        batch_num = batch_info['batch_number']

        if batch_info['final_status'] == "completed" and batch_info['output_file_id']:
            log_timestamp(f"Downloading results for Batch {batch_num}...")

            result_file_id = batch_info['output_file_id']
            result = openai_api.client.files.content(result_file_id).content
            result = result.decode('utf-8')

            # Save raw results for this batch
            output_results_path = Path(
                __file__).parent.parent / "batch" / f"batch_{batch_num}_results.jsonl"
            with open(output_results_path, 'w', encoding='utf-8') as f:
                f.write(result)

            # Extract content
            result_entries = result.strip().split("\n")
            for r in result_entries:
                res = json.loads(r)
                if 'response' in res and 'body' in res['response']:
                    content = res['response']['body']['choices'][0]['message']['content']
                    all_extraction_data.append({
                        'batch_number': batch_num,
                        'custom_id': res['custom_id'],
                        'content': content
                    })

            successful_batches += 1
            log_timestamp(
                f"Batch {batch_num} downloaded ({len(result_entries)} results)")
        else:
            failed_batches += 1
            log_timestamp(
                f"Batch {batch_num} FAILED with status: {batch_info['final_status']}")

    # Save consolidated extracted content
    if all_extraction_data:
        extracted_output_path = Path(
            __file__).parent.parent / "batch" / "all_extracted_results.json"
        with open(extracted_output_path, 'w', encoding='utf-8') as f:
            json.dump(all_extraction_data, f, indent=2, ensure_ascii=False)

        log_timestamp(
            f"\nConsolidated results saved to: {extracted_output_path}")
        log_timestamp(f"Total extractions: {len(all_extraction_data)}")

    # Final summary
    log_timestamp("\n=== Final Summary ===")
    log_timestamp(f"Total batches: {total_batches}")
    log_timestamp(f"Successful batches: {successful_batches}")
    log_timestamp(f"Failed batches: {failed_batches}")
    log_timestamp(f"Total extractions: {len(all_extraction_data)}")
    log_timestamp("\nScript completed")
