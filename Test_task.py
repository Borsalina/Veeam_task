import os
import shutil
import time
import argparse

def sync_folders(source_folder, replica_folder, log_file):
    # Creating replica folder if it does not exist
    if not os.path.exists(replica_folder):
        os.makedirs(replica_folder)

    # Synchronizing source folder with replica folder
    for root, dirs, files in os.walk(source_folder):
        # Creating replica subfolder if it does not exist
        relative_path = os.path.relpath(root, source_folder)
        replica_path = os.path.join(replica_folder, relative_path)

        if not os.path.exists(replica_path):
            os.makedirs(replica_path)

        # Copying new and modified files
        for file in files:
            source_file_path = os.path.join(root, file)
            replica_file_path = os.path.join(replica_path, file)

            # If file is new or modified in source folder, copy it to replica folder
            if not os.path.exists(replica_file_path) or os.stat(source_file_path).st_mtime - os.stat(replica_file_path).st_mtime > 1:
                shutil.copy2(source_file_path, replica_file_path)
                log_file.write("Copied {} to {}\n".format(source_file_path, replica_file_path))
                print("Copied {} to {}".format(source_file_path, replica_file_path))

        # Removing deleted files
        for replica_file in os.listdir(replica_path):
            source_file_path = os.path.join(root, replica_file)
            replica_file_path = os.path.join(replica_path, replica_file)

            # If file is deleted in source folder, delete it from replica folder
            if not os.path.exists(source_file_path):
                os.remove(replica_file_path)
                log_file.write("Deleted {}\n".format(replica_file_path))
                print("Deleted {}".format(replica_file_path))

if __name__ == '__main__':
    # Setting up command line arguments
    parser = argparse.ArgumentParser(description="Sync two folders")
    parser.add_argument("source_folder", help="path to source folder")
    parser.add_argument("replica_folder", help="path to replica folder")
    parser.add_argument("log_file", help="path to log file")
    parser.add_argument("-t", "--time_interval", type=int, default=60, help="time interval between syncs in seconds (default=60)")
    args = parser.parse_args()

    # Starting synchronization loop
    with open(args.log_file, 'a') as log_file:
        while True:
            sync_folders(args.source_folder, args.replica_folder, log_file)
            time.sleep(args.time_interval))