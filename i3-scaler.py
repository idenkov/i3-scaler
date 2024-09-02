#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path
import getpass

def get_user_home():
    """Get the home directory of the user running the script."""
    user_home = str(Path.home())
    print(f"Detected user home directory: {user_home}")
    return user_home

def update_or_append_line(file_path, key, value, command=False):
    """Update a line in the file if the key exists, otherwise append it."""
    lines = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()

    updated = False
    for i, line in enumerate(lines):
        if command and key in line:
            lines[i] = f"{key} {value}\n"
            updated = True
        elif line.strip().startswith(key):
            lines[i] = f"{key}: {value}\n" if file_path.endswith('.Xresources') else f"{key}={value}\n"
            updated = True

    if not updated:
        if command:
            lines.append(f"{key} {value}\n")
        else:
            lines.append(f"{key}: {value}\n" if file_path.endswith('.Xresources') else f"{key}={value}\n")

    with open(file_path, 'w') as file:
        file.writelines(lines)

def update_config_file(config_path, settings_dict):
    """Update the configuration file with the provided settings."""
    if not os.path.exists(config_path):
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        open(config_path, 'w').close()

    with open(config_path, 'r') as file:
        lines = file.readlines()

    updated_lines = []
    for line in lines:
        updated = False
        for key, value in settings_dict.items():
            if line.strip().startswith(key):
                updated_lines.append(f"{key}={value}\n" if config_path.endswith(".ini") else f"{key} = {value}\n")
                updated = True
                break
        if not updated:
            updated_lines.append(line)

    for key, value in settings_dict.items():
        if not any(line.strip().startswith(key) for line in updated_lines):
            updated_lines.append(f"{key}={value}\n" if config_path.endswith(".ini") else f"{key} = {value}\n")

    with open(config_path, 'w') as file:
        file.writelines(updated_lines)

def set_xresources_dpi(dpi, user_home):
    xresources_path = os.path.join(user_home, ".Xresources")
    update_or_append_line(xresources_path, "Xft.dpi", dpi)
    subprocess.run(["xrdb", "-merge", xresources_path])
    print(f"Set Xft DPI to {dpi} in {xresources_path}.")

def set_i3_font_size(font_size, dpi, user_home):
    i3_config_path = os.path.join(user_home, ".config/i3/config")
    legacy_i3_config_path = os.path.join(user_home, ".i3/config")
    
    if not os.path.exists(i3_config_path) and os.path.exists(legacy_i3_config_path):
        i3_config_path = legacy_i3_config_path

    with open(i3_config_path, 'r') as file:
        config_lines = file.readlines()

    with open(i3_config_path, 'w') as file:
        xrandr_command = f"exec xrandr --dpi {dpi}"
        xrandr_found = False

        for line in config_lines:
            if line.strip().startswith("font"):
                line = f"font pango:monospace {font_size}\n"
            elif line.strip().startswith("exec xrandr --dpi"):
                if not xrandr_found:
                    line = f"{xrandr_command}\n"
                    xrandr_found = True
                else:
                    continue  # Skip any duplicate lines
            file.write(line)

        # If the xrandr command was not found, append it
        if not xrandr_found:
            file.write(f"{xrandr_command}\n")
            print(f"Added '{xrandr_command}' to {i3_config_path}.")
        else:
            print(f"'{xrandr_command}' was already present and updated if needed in {i3_config_path}.")

def set_gtk_scaling(dpi, font_size, user_home):
    gtk3_config_path = os.path.join(user_home, ".config/gtk-3.0/settings.ini")
    gtk2_config_path = os.path.join(user_home, ".gtkrc-2.0")
    gtk4_config_path = os.path.join(user_home, ".config/gtk-4.0/settings.ini")

    gtk3_settings = {
        "gtk-font-name": f"Sans {font_size}",
        "gtk-dpi": dpi,
        "gtk-xft-dpi": dpi * 1000
    }
    update_config_file(gtk3_config_path, gtk3_settings)

    gtk2_settings = {
        "gtk-font-name": f"Sans {font_size}",
        "gtk-xft-dpi": dpi * 1000
    }
    update_config_file(gtk2_config_path, gtk2_settings)

    gtk4_settings = {
        "gtk-font-name": f"Sans {font_size}",
        "gtk-xft-dpi": dpi * 1000
    }
    update_config_file(gtk4_config_path, gtk4_settings)

def update_or_append_env_var(file_path, key, value):
    """Update or append environment variable in the file."""
    lines = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()

    updated = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f"export {key}="):
            if line.strip().split("=")[-1] != str(value):
                lines[i] = f"export {key}={value}\n"
            updated = True

    if not updated:
        lines.append(f"export {key}={value}\n")

    with open(file_path, 'w') as file:
        file.writelines(lines)

def set_qt_scaling(dpi, scale_factor, user_home):
    profile_path = os.path.join(user_home, ".profile")
    update_or_append_env_var(profile_path, "QT_SCALE_FACTOR", scale_factor)
    update_or_append_env_var(profile_path, "QT_FONT_DPI", dpi)
    print(f"Set QT scaling in {profile_path}.")

def restart_i3wm():
    subprocess.run(["i3-msg", "restart"])
    print("Restarted i3wm to apply changes.")

def main():
    try:
        current_user = getpass.getuser()
        print(f"Script is running as user: {current_user}")

        user_home = get_user_home()

        dpi = int(input("Enter desired DPI (e.g., 96, 120, 144): "))
        font_size = int(input("Enter desired font size for i3 and GTK apps (e.g., 12, 14): "))
        scale_factor = dpi / 96

        set_xresources_dpi(dpi, user_home)
        set_i3_font_size(font_size, dpi, user_home)
        set_gtk_scaling(dpi, font_size, user_home)
        set_qt_scaling(dpi, scale_factor, user_home)

        print("Configuration changes applied successfully. Restarting i3wm...")
        restart_i3wm()

    except ValueError as e:
        print(f"Invalid input: {e}")

if __name__ == "__main__":
    main()

