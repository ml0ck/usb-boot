import os
import subprocess
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def display_header():
    header = f"""
    {Fore.CYAN}
    ▄• ▄▌.▄▄ · ▄▄▄▄·             ▄▄▄▄▄
    █▪██▌▐█ ▀. ▐█ ▀█▪▪     ▪     •██
    █▌▐█▌▄▀▀▀█▄▐█▀▀█▄ ▄█▀▄  ▄█▀▄  ▐█.▪
    ▐█▄█▌▐█▄▪▐███▄▪▐█▐█▌.▐▌▐█▌.▐▌ ▐█▌·
     ▀▀▀  ▀▀▀▀ ·▀▀▀▀  ▀█▄▀▪ ▀█▄▀▪ ▀▀▀
    {Style.RESET_ALL}
    """
    print(header)

def list_disks():
    print(f"{Fore.YELLOW}Listing available disks:{Style.RESET_ALL}")
    result = subprocess.run(["lsblk", "-o", "NAME,SIZE,TYPE,MOUNTPOINT"], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    disks = [line for line in lines if "disk" in line]
    for i, disk in enumerate(disks, start=1):
        print(f"{i}) {disk}")
    return disks

def select_disk(disks):
    while True:
        try:
            choice = int(input(f"{Fore.GREEN}Enter the number corresponding to the disk: {Style.RESET_ALL}"))
            if 1 <= choice <= len(disks):
                selected_disk = disks[choice - 1].split()[0]
                return f"/dev/{selected_disk}"
            else:
                print(f"{Fore.RED}Invalid choice. Please enter a number from the list.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a number.{Style.RESET_ALL}")

def select_iso_path():
    iso_path = input(f"{Fore.GREEN}Enter the path to the ISO file: {Style.RESET_ALL}")
    if not os.path.isfile(iso_path):
        print(f"{Fore.RED}ISO file not found. Please enter a valid path.{Style.RESET_ALL}")
        return select_iso_path()
    return iso_path

def is_mounted(device):
    result = subprocess.run(["mountpoint", "-q", device], capture_output=True)
    return result.returncode == 0

def unmount_partitions(disk):
    print(f"{Fore.BLUE}Unmounting partitions on {disk}...{Style.RESET_ALL}")
    try:
        # Unmount all partitions on the disk
        partitions = subprocess.run(["lsblk", "-nr", "-o", "NAME", f"{disk}"], capture_output=True, text=True).stdout.splitlines()
        for partition in partitions:
            partition_path = f"/dev/{partition.strip()}"
            if is_mounted(partition_path):
                subprocess.run(["sudo", "umount", partition_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}An error occurred while unmounting: {e}{Style.RESET_ALL}")

def delete_partitions(disk):
    print(f"{Fore.BLUE}Deleting partitions on {disk}...{Style.RESET_ALL}")
    try:
        # Delete all partitions on the disk
        subprocess.run(["sudo", "sgdisk", "--zap-all", disk], check=True)
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}An error occurred while deleting partitions: {e}{Style.RESET_ALL}")

def format_disk(disk):
    print(f"{Fore.BLUE}Formatting {disk}...{Style.RESET_ALL}")
    try:
        unmount_partitions(disk)
        delete_partitions(disk)

        # Format the disk
        subprocess.run(["sudo", "mkfs.vfat", "-F", "32", f"{disk}"], check=True)

        print(f"{Fore.GREEN}Disk formatted successfully.{Style.RESET_ALL}")
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")

def format_and_write_iso(disk, iso_path):
    print(f"{Fore.BLUE}Formatting {disk} and writing {iso_path}...{Style.RESET_ALL}")
    try:
        unmount_partitions(disk)
        delete_partitions(disk)

        # Format the disk
        subprocess.run(["sudo", "dd", "if=/dev/zero", f"of={disk}", "bs=512", "count=1"], check=True)

        # Write the ISO to the disk
        subprocess.run(["sudo", "dd", f"if={iso_path}", f"of={disk}", "bs=4M", "status=progress"], check=True)

        print(f"{Fore.GREEN}Operation completed successfully.{Style.RESET_ALL}")
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")

def main():
    display_header()
    print(f"{Fore.MAGENTA}ASCII User-Friendly USB Bootable Creator{Style.RESET_ALL}")

    while True:
        print("\nMenu:")
        print(f"{Fore.CYAN}1.{Style.RESET_ALL} List available disks")
        print(f"{Fore.CYAN}2.{Style.RESET_ALL} Format USB drive")
        print(f"{Fore.CYAN}3.{Style.RESET_ALL} Create bootable USB with ISO")
        print(f"{Fore.CYAN}4.{Style.RESET_ALL} Exit")

        choice = input(f"{Fore.GREEN}Choose an option (1-4): {Style.RESET_ALL}")

        if choice == '1':
            disks = list_disks()
        elif choice == '2':
            disks = list_disks()
            disk = select_disk(disks)
            format_disk(disk)
        elif choice == '3':
            disks = list_disks()
            disk = select_disk(disks)
            iso_path = select_iso_path()
            format_and_write_iso(disk, iso_path)
        elif choice == '4':
            print(f"{Fore.YELLOW}Exiting the program.{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}Invalid choice. Please select a valid option.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
