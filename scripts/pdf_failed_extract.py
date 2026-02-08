import os
import re
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime


def log_timestamp(message: str) -> None:
    """Print message with timestamp prefix."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")


def split_into_batches(items, batch_size=25):
    """Split list into batches of specified size."""
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]


if __name__ == "__main__":
    log_timestamp("Starting failed batch reprocessing...")

    # Setup
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    client = OpenAI(api_key=api_key)
    directory = Path(__file__).parent.parent / "batch"
    batch_filename_pattern = re.compile(r"^batch_(\d+)_image_requests\.jsonl$")

    # Find all request files without matching result files
    failed_batches = []
    for name in os.listdir(directory):
        m = batch_filename_pattern.match(name)
        if m:
            batch_num = m.group(1)
            results_file = directory / f"batch_{batch_num}_results.jsonl"

            # Only add if results file doesn't exist
            if not results_file.exists():
                failed_batches.append((int(batch_num), name))

    if not failed_batches:
        log_timestamp("No failed batches found. Exiting.")
        exit(0)

    log_timestamp(
        f"Found {len(failed_batches)} unprocessed batches: {[b[0] for b in failed_batches]}")

    # Parse all requests from failed batches into master list
    all_requests = []
    for batch_num, filename in failed_batches:
        filepath = directory / filename

        with open(filepath, "r", encoding="utf-8") as f:
            # JSONL format: each line is a separate JSON object
            for line in f:
                line = line.strip()
                if line:  # Skip empty lines
                    req = json.loads(line)
                    all_requests.append(req)

    log_timestamp(f"Total requests to reprocess: {len(all_requests)}")

    # Split into batches of 25
    BATCH_SIZE = 25
    request_batches = split_into_batches(all_requests, BATCH_SIZE)
    total_batches = len(request_batches)

    log_timestamp(
        f"Split into {total_batches} batches of up to {BATCH_SIZE} requests each\n")

    # Create and submit new batch files
    all_batch_jobs = []

    for batch_idx, request_batch in enumerate(request_batches, start=1):
        log_timestamp(
            f"=== Processing Retry Batch {batch_idx}/{total_batches} ({len(request_batch)} requests) ===")

        # Create new JSONL file for this batch
        retry_batch_file = directory / \
            f"retry_batch_{batch_idx}_image_requests.jsonl"

        with open(retry_batch_file, 'w', encoding='utf-8') as f:
            for request in request_batch:
                f.write(json.dumps(request) + '\n')

        log_timestamp(f"Created JSONL file: {retry_batch_file.name}")

        # Upload batch file
        log_timestamp("Uploading batch file...")
        batch_file = client.files.create(
            file=open(retry_batch_file, "rb"),
            purpose="batch"
        )
        log_timestamp(f"Batch file uploaded: {batch_file.id}")

        # Create batch job
        batch_job = client.batches.create(
            input_file_id=batch_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h"
        )

        all_batch_jobs.append({
            'batch_number': batch_idx,
            'job_id': batch_job.id,
            'request_count': len(request_batch),
            'status': batch_job.status,
            'retry_batch_file': retry_batch_file.name
        })

        log_timestamp(f"Batch job created: {batch_job.id}")
        log_timestamp(f"Status: {batch_job.status}\n")

    # Monitor all batch jobs
    log_timestamp(f"All {total_batches} retry batch jobs submitted!")
    log_timestamp("Monitoring progress (checking every 60 seconds)...\n")

    completed_batches = set()
    last_status_update = {}

    while len(completed_batches) < total_batches:
        for batch_info in all_batch_jobs:
            batch_num = batch_info['batch_number']

            # Skip if already completed
            if batch_num in completed_batches:
                continue

            batch_job = client.batches.retrieve(batch_info['job_id'])

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
                        f"Retry Batch {batch_num}/{total_batches}: {completed}/{total} ({progress_pct:.1f}%) | Failed: {failed} | Status: {batch_job.status}")
                    last_status_update[batch_num] = completed

            # Check if batch is done
            if batch_job.status in ["completed", "failed", "expired", "cancelled"]:
                if batch_num not in completed_batches:
                    log_timestamp(
                        f"Retry Batch {batch_num}/{total_batches} finished with status: {batch_job.status}")
                    completed_batches.add(batch_num)
                    batch_info['final_status'] = batch_job.status
                    batch_info['output_file_id'] = batch_job.output_file_id if hasattr(
                        batch_job, 'output_file_id') else None

        if len(completed_batches) < total_batches:
            time.sleep(60)

    # Download and extract results
    log_timestamp("\nAll retry batches completed")
    log_timestamp("Downloading results...\n")

    new_extraction_data = []
    successful_batches = 0
    failed_batches_count = 0

    for batch_info in all_batch_jobs:
        batch_num = batch_info['batch_number']

        if batch_info['final_status'] == "completed" and batch_info['output_file_id']:
            log_timestamp(
                f"Downloading results for Retry Batch {batch_num}...")

            result_file_id = batch_info['output_file_id']
            result = client.files.content(result_file_id).content
            result = result.decode('utf-8')

            # Save raw results for this retry batch
            output_results_path = directory / \
                f"retry_batch_{batch_num}_results.jsonl"
            with open(output_results_path, 'w', encoding='utf-8') as f:
                f.write(result)

            # Extract content
            result_entries = result.strip().split("\n")
            for r in result_entries:
                res = json.loads(r)
                if 'response' in res and 'body' in res['response']:
                    content = res['response']['body']['choices'][0]['message']['content']
                    new_extraction_data.append({
                        'batch_number': f"retry_{batch_num}",
                        'custom_id': res['custom_id'],
                        'content': content
                    })

            successful_batches += 1
            log_timestamp(
                f"Retry Batch {batch_num} downloaded ({len(result_entries)} results)")
        else:
            failed_batches_count += 1
            log_timestamp(
                f"Retry Batch {batch_num} FAILED with status: {batch_info['final_status']}")

    # Append to existing all_extracted_results.json
    if new_extraction_data:
        extracted_output_path = directory / "all_extracted_results.json"

        # Load existing data
        existing_data = []
        if extracted_output_path.exists():
            with open(extracted_output_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            log_timestamp(f"Loaded {len(existing_data)} existing extractions")

        # Append new data
        combined_data = existing_data + new_extraction_data

        # Save combined data
        with open(extracted_output_path, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)

        log_timestamp(f"\nAppended {len(new_extraction_data)} new extractions")
        log_timestamp(f"Total extractions now: {len(combined_data)}")
        log_timestamp(f"Saved to: {extracted_output_path}")

    # Final summary
    log_timestamp("\n=== Final Summary ===")
    log_timestamp(f"Total retry batches processed: {total_batches}")
    log_timestamp(f"Successful batches: {successful_batches}")
    log_timestamp(f"Failed batches: {failed_batches_count}")
    log_timestamp(f"New extractions added: {len(new_extraction_data)}")
    log_timestamp(f"Total requests reprocessed: {len(all_requests)}")
    log_timestamp("\nReprocessing completed")
