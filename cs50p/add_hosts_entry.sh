#!/bin/bash

# Define the host entry
HOSTS_ENTRY="127.0.0.1 to"
HOSTS_FILE="/etc/hosts"

echo "Attempting to add '$HOSTS_ENTRY' to $HOSTS_FILE"


# Check if the entry already exists
if grep -qF "$HOSTS_ENTRY" "$HOSTS_FILE"; then
    echo "Entry '$HOSTS_ENTRY' already exists in $HOSTS_FILE. No changes made."
else
    echo "Adding '$HOSTS_ENTRY' to $HOSTS_FILE..."
    # Use sudo to append the entry. The tee command is used because /etc/hosts
    # is typically not directly writable by unprivileged users.
    if echo "$HOSTS_ENTRY" | sudo tee -a "$HOSTS_FILE" > /dev/null; then
        echo "Successfully added '$HOSTS_ENTRY' to $HOSTS_FILE."
        echo "You might need to flush your DNS cache for the changes to take effect."
        # Provide OS-specific DNS flush commands
        case "$(uname -s)" in
            Darwin)
                echo "On macOS, run: sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder"
                ;;
            Linux)
                if command -v systemd-resolve &> /dev/null; then
                    echo "On Linux (systemd-resolved), run: sudo systemd-resolve --flush-caches"
                elif command -v resolvectl &> /dev/null; then
                    echo "On Linux (resolvectl), run: sudo resolvectl flush-caches"
                else
                    echo "On Linux, restarting NetworkManager might help: sudo service network-manager restart"
                    echo "Or try: sudo /etc/init.d/nscd restart"
                fi
                ;;
        esac
    else
        echo "Failed to add the entry. This might require administrator privileges."
        echo "Please run the script with sudo: sudo ./add_hosts_entry.sh"
    fi
fi
