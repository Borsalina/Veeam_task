import os
import shutil
import time
import logging
import argparse
import hashlib

def setup_logging(log_file):
    # Set up logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s]: %(message)s",
        handlers=[
            logging.FileHandler(log_file),  # Log to a file
            logging.StreamHandler()          # Log to console
        ]
    )

def synchronize_folders(source_folder, replica_folder, interval_seconds, log_file):
    # Set up logging
    setup_logging(log_file)

    while True:
        try:
            # Check if both source and replica folders exist
            if not os.path.exists(source_folder):
                logging.error(f"Source folder '{source_folder}' does not exist.")
                raise FileNotFoundError(f"Source folder '{source_folder}' not found.")
            if not os.path.exists(replica_folder):
                os.makedirs(replica_folder)  # Create replica folder if it doesn't exist
                logging.info(f"Created replica folder: {replica_folder}")

            # Perform synchronization
            sync_folders(source_folder, replica_folder)

        except Exception as e:
            logging.exception(f"An error occurred: {e}")

        finally:
            # Wait for the specified interval before the next synchronization
            time.sleep(interval_seconds)

def sync_folders(source_folder, replica_folder):
    # Synchronize files from source folder to replica folder
    for root, dirs, files in os.walk(source_folder):
        for file_name in files:
            source_file = os.path.join(root, file_name)
            replica_file = os.path.join(replica_folder, os.path.relpath(source_file, source_folder))

            # Copy file if it doesn't exist in replica or if it differs
            if not os.path.exists(replica_file) or file_differs(source_file, replica_file):
                shutil.copy2(source_file, replica_file)
                logging.info(f"Copied: {source_file} to {replica_file}")

    # Remove files from replica folder that don't exist in source folder
    for root, dirs, files in os.walk(replica_folder):
        for file_name in files:
            replica_file = os.path.join(root, file_name)
            source_file = os.path.join(source_folder, os.path.relpath(replica_file, replica_folder))

            if not os.path.exists(source_file):
                os.remove(replica_file)
                logging.info(f"Removed file: {replica_file}")

def file_differs(file1, file2):
    # Compare files based on their contents using SHA-256 hashing
    block_size = 65536  # 64 KB
    hasher1 = hashlib.sha256()
    hasher2 = hashlib.sha256()

    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        while True:
            buf1 = f1.read(block_size)
            buf2 = f2.read(block_size)
            if buf1 == b'' and buf2 == b'':
                break
            hasher1.update(buf1)
            hasher2.update(buf2)

    return hasher1.hexdigest() != hasher2.hexdigest()

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Folder synchronization script.")
    parser.add_argument("source_folder", help="Path to the source folder")
    parser.add_argument("replica_folder", help="Path to the replica folder")
    parser.add_argument("interval_seconds", type=int, help="Synchronization interval in seconds")
    parser.add_argument("log_file", help="Path to the log file")
    args = parser.parse_args()

    # Start synchronization
    synchronize_folders(
        args.source_folder,
        args.replica_folder,
        args.interval_seconds,
        args.log_file
    )

if __name__ == "__main__":
    main()
