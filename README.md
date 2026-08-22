# Ghost DNS by Swir v6.0 APEX - JSON Database Edition 👻🌍

A powerful, modern, and user-friendly Windows desktop application built with Python and CustomTkinter. Ghost DNS allows users to quickly manage and switch their system's DNS servers to optimize internet speed, reduce gaming latency, enhance privacy, or block ads.

## ✨ Key Features

* **One-Click DNS Switching:** Instantly apply pre-configured DNS profiles categorized by their purpose:
  * 🎮 **Performance & Gaming:** Ultra-fast servers like Cloudflare and G-Core for lowest latency.
  * 🔒 **Privacy & Security:** Quad9 and Mullvad to block trackers and prevent data logging.
  * 🛡️ **Ad Control & Filtering:** AdGuard and OpenDNS for network-wide ad blocking and phishing protection.
  * 🔄 **System Default:** Easily revert to your router's default Automatic (DHCP) settings.
* **Live Ping Tester ⚡:** Automatically pings available DNS servers and displays real-time response times (ms) to help you choose the fastest connection.
* **JSON Database Integration:** Create, save, and apply your own custom DNS profiles. Your personalized servers are safely stored locally in a `custom_dns.json` file.
* **Smart Network Detection:** Automatically detects your active network adapter and displays your currently active DNS addresses.
* **Modern UI:** A sleek, fully responsive dark mode interface powered by CustomTkinter.

## 🛠️ Requirements

* **OS:** Windows 10 / Windows 11 (Requires Administrator privileges to modify system network settings using `netsh`).
* **Python:** Python 3.8 or higher.
pip install customtkinter
