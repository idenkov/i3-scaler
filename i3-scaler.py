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

def update_config_file(config_path, settings_dict):
    """Update specific settings in a config file, preserving other settings."""
    config_lines = []
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            config_lines = file.readlines()

    updated_lines = []
    for line in config_lines:
        for key, value in settings_dict.items():
            if line.strip().startswith(key):
                line = f"{key} = {value}\n"
        updated_lines.append(line)

    for key, value in settings_dict.items():
        if not any(line.strip().startswith(key) for line in updated_lines):
            updated_lines.append(f"{key} = {value}\n")

    with open(config_path, 'w') as file:
        file.writelines(updated_lines)

    print(f"Updated {config_path} with settings: {settings_dict}")

def set_xresources_dpi(dpi, user_home):
    xresources_path = os.path.join(user_home, ".Xresources")
    settings = {"Xft.dpi": dpi}
    update_config_file(xresources_path, settings)
    subprocess.run(["xrdb", "-merge", xresources_path])
    print(f"Set Xft DPI to {dpi} in {xresources_path}.")

def set_i3_font_size(font_size, user_home):
    i3_config_path = os.path.join(user_home, ".config/i3/config")
    legacy_i3_config_path = os.path.join(user_home, ".i3/config")
    
    if not os.path.exists(i3_config_path) and os.path.exists(legacy_i3_config_path):
        i3_config_path = legacy_i3_config_path

    config_lines = []
    with open(i3_config_path, 'r') as file:
        config_lines = file.readlines()

    with open(i3_config_path, 'w') as file:
        for line in config_lines:
            if line.strip().startswith("font"):
                line = f"font pango:monospace {font_size}\n"
            file.write(line)

    print(f"Set i3 font size to {font_size} in {i3_config_path}.")

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

def set_qt_scaling(dpi, scale_factor, user_home):
    profile_path = os.path.join(user_home, ".profile")
    with open(profile_path, 'a+') as profile:
        profile.write(f"\nexport QT_SCALE_FACTOR={scale_factor}\n")
        profile.write(f"export QT_FONT_DPI={dpi}\n")
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
        set_i3_font_size(font_size, user_home)
        set_gtk_scaling(dpi, font_size, user_home)
        set_qt_scaling(dpi, scale_factor, user_home)

        print("Configuration changes applied successfully. Restarting i3wm...")
        restart_i3wm()

    except ValueError as e:
        print(f"Invalid input: {e}")

if __name__ == "__main__":
    main()

