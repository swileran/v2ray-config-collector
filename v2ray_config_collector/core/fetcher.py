import requests
import base64
import time
import re
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from tqdm import tqdm
class SourceCollector:
    def __init__(self, input_file=None, output_file=None):
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if input_file is None:
            input_file = os.path.join(package_dir, 'data', 'sources', 'proxy_sources.txt')
        if output_file is None:
            output_file = os.path.join(package_dir, 'data', 'raw', 'raw_configs.txt')
        self.input_file = input_file
        self.output_file = output_file
        self.json_output_file = os.path.join(os.path.dirname(output_file), 'raw_json.json')
        self.base64_output_file = os.path.join(os.path.dirname(output_file), 'raw_base64.txt')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.stats = {
            'total_links': 0,
            'successful_links': 0,
            'failed_links': 0,
            'total_configs': 0,
            'json_content_count': 0,
            'base64_content_count': 0,
            'empty_responses': 0,
            'retry_attempts': 0
        }
        self.failed_urls = []
        self.successful_urls = []
        self.json_contents = []
        self.base64_contents = []
        self.stats_lock = threading.Lock()
        self.print_lock = threading.Lock()

    def safe_print(self, message):
        with self.print_lock:
            print(message)
    def read_links(self):
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                links = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            self.stats['total_links'] = len(links)
            print(f"Number of links read: {len(links)}")
            return links
        except FileNotFoundError:
            print(f"File {self.input_file} not found!")
            return []
    def is_base64_encoded(self, text):
        try:
            text = re.sub(r'\s', '', text)
            if len(text) % 4 != 0:
                return False
            base64.b64decode(text, validate=True)
            return True
        except:
            return False
    def is_json_content(self, content):
        try:
            json.loads(content)
            return True
        except:
            return False
    def decode_if_base64(self, content):
        if self.is_base64_encoded(content):
            try:
                decoded = base64.b64decode(content).decode('utf-8')
                return decoded
            except:
                return content
        return content
    def extract_configs(self, content):
        if not content:
            return []
        content = self.decode_if_base64(content)
        patterns = [
            r'vmess://[A-Za-z0-9+/=]+',
            r'vless://[^\s\n]+',
            r'trojan://[^\s\n]+',
            r'ss://[A-Za-z0-9+/=]+@[^\s\n]+',
            r'ssr://[A-Za-z0-9+/=]+',
            r'tuic://[^\s\n]+',
            r'hysteria2://[^\s\n]+',
            r'hy2://[^\s\n]+',
        ]
        configs = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            configs.extend(matches)
        configs = list(set(configs))
        return configs

    def fetch_url_with_retry(self, url, max_retries=3, show_fetching=True, silent=False):
        for attempt in range(max_retries):
            try:
                if show_fetching and attempt == 0 and not silent:
                    self.safe_print(f"Fetching: {url}")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                content = response.text.strip()
                original_content = response.text
                if not content:
                    if original_content and self.is_base64_encoded(original_content.replace('\n', '').replace('\r', '').replace(' ', '')):
                        return original_content
                    config_patterns = [
                        r'vmess://[A-Za-z0-9+/=]+',
                        r'vless://[^\s\n]+',
                        r'trojan://[^\s\n]+',
                        r'ss://[A-Za-z0-9+/=]+@[^\s\n]+',
                        r'ssr://[A-Za-z0-9+/=]+',
                        r'tuic://[^\s\n]+',
                        r'hysteria2://[^\s\n]+',
                        r'hy2://[^\s\n]+',
                    ]
                    has_configs = False
                    for pattern in config_patterns:
                        if re.search(pattern, original_content, re.IGNORECASE):
                            has_configs = True
                            break
                    if has_configs:
                        return original_content
                    with self.stats_lock:
                        self.stats['empty_responses'] += 1
                    if attempt < max_retries - 1:
                        if not silent:
                            self.safe_print(f"    Empty response")
                            self.safe_print(f"    Retrying ({attempt + 2}/{max_retries})...")
                        with self.stats_lock:
                            self.stats['retry_attempts'] += 1
                        time.sleep(2)
                        continue
                    return None
                return content
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    if not silent:
                        error_type = str(e).split(':')[0] if ':' in str(e) else str(e)[:30]
                        self.safe_print(f"    {error_type} - Retry {attempt + 2}/{max_retries}")
                    with self.stats_lock:
                        self.stats['retry_attempts'] += 1
                    time.sleep(3)
                else:
                    return None
            except Exception as e:
                if not silent:
                    self.safe_print(f"Unexpected error: {str(e)[:100]}")
                return None
        return None
    def fetch_single_url(self, url_data, pbar=None):
        i, url = url_data
        content = self.fetch_url_with_retry(url, show_fetching=False, silent=True)
        if content:
            if self.is_json_content(content):
                with self.stats_lock:
                    self.stats['successful_links'] += 1
                    self.stats['json_content_count'] += 1
                    self.successful_urls.append(url)
                    self.json_contents.append(content)
                if pbar:
                    pbar.set_postfix({"JSON": f"{self.stats['json_content_count']:,}", "Base64": f"{self.stats['base64_content_count']:,}", "Configs": f"{self.stats['total_configs']:,}"})
                return []
            elif self.is_base64_encoded(content):
                with self.stats_lock:
                    self.stats['successful_links'] += 1
                    self.stats['base64_content_count'] += 1
                    self.successful_urls.append(url)
                    self.base64_contents.append(content)
                if pbar:
                    pbar.set_postfix({"JSON": f"{self.stats['json_content_count']:,}", "Base64": f"{self.stats['base64_content_count']:,}", "Configs": f"{self.stats['total_configs']:,}"})
                return []
            else:
                configs = self.extract_configs(content)
                if configs:
                    with self.stats_lock:
                        self.stats['successful_links'] += 1
                        self.stats['total_configs'] += len(configs)
                        self.successful_urls.append(url)
                    if pbar:
                        pbar.set_postfix({"JSON": f"{self.stats['json_content_count']:,}", "Base64": f"{self.stats['base64_content_count']:,}", "Configs": f"{self.stats['total_configs']:,}"})
                    return configs
                else:
                    with self.stats_lock:
                        self.stats['failed_links'] += 1
                        self.failed_urls.append(url)
                    return []
        else:
            with self.stats_lock:
                self.stats['failed_links'] += 1
                self.failed_urls.append(url)
            return []

    def fetch_all_configs(self, max_workers=10):
        links = self.read_links()
        if not links:
            return
        all_configs = []
        print(f"\nPhase 1: Parallel processing of {len(links)} links using {max_workers} threads...")
        phase1_failed = []
        phase1_successful = 0
        url_data = [(i+1, url) for i, url in enumerate(links)]
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            with tqdm(total=len(links), desc="Phase 1 - Parallel", unit="url", 
                     bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} {postfix}') as pbar:
                future_to_url = {executor.submit(self.fetch_single_url, data, pbar): data for data in url_data}
                for future in as_completed(future_to_url):
                    try:
                        configs = future.result()
                        if configs:
                            all_configs.extend(configs)
                            phase1_successful += 1
                        else:
                            url_data_item = future_to_url[future]
                            phase1_failed.append(url_data_item[1])
                    except Exception as e:
                        url_data_item = future_to_url[future]
                        phase1_failed.append(url_data_item[1])
                    finally:
                        pbar.update(1)
        print(f"Phase 1 completed: {phase1_successful} successful, {len(phase1_failed)} failed")
        if phase1_failed:
            print(f"\nPhase 2: Sequential retry of {len(phase1_failed)} failed links...")
            phase2_recovered = 0
            phase2_final_failed = []
            time.sleep(0.1)
            with tqdm(total=len(phase1_failed), desc="Phase 2 - Sequential", unit="url") as pbar:
                for url in phase1_failed:
                    content = self.fetch_url_with_retry(url, show_fetching=False, silent=True)
                    if content:
                        if self.is_json_content(content):
                            phase2_recovered += 1
                            with self.stats_lock:
                                self.stats['successful_links'] += 1
                                self.stats['json_content_count'] += 1
                                if url not in self.successful_urls:
                                    self.successful_urls.append(url)
                                if url in self.failed_urls:
                                    self.failed_urls.remove(url)
                                self.json_contents.append(content)
                        elif self.is_base64_encoded(content):
                            phase2_recovered += 1
                            with self.stats_lock:
                                self.stats['successful_links'] += 1
                                self.stats['base64_content_count'] += 1
                                if url not in self.successful_urls:
                                    self.successful_urls.append(url)
                                if url in self.failed_urls:
                                    self.failed_urls.remove(url)
                                self.base64_contents.append(content)
                        else:
                            configs = self.extract_configs(content)
                            if configs:
                                all_configs.extend(configs)
                                phase2_recovered += 1
                                with self.stats_lock:
                                    self.stats['successful_links'] += 1
                                    self.stats['total_configs'] += len(configs)
                                    if url not in self.successful_urls:
                                        self.successful_urls.append(url)
                                    if url in self.failed_urls:
                                        self.failed_urls.remove(url)
                            else:
                                phase2_final_failed.append(url)
                    else:
                        phase2_final_failed.append(url)
                    pbar.update(1)
            print(f"Phase 2 completed: {phase2_recovered} recovered, {len(phase2_final_failed)} permanently failed")
            self.failed_urls = phase2_final_failed
        self.save_configs(all_configs)
        self.save_json_content()
        self.save_base64_content()
        self.print_detailed_summary(all_configs, phase1_successful, len(phase1_failed), 
                                   phase2_recovered if phase1_failed else 0, 
                                   len(phase2_final_failed) if phase1_failed else 0)

    def save_configs(self, configs):
        if not configs:
            print("No configs found to save!")
        else:
            try:
                output_dir = os.path.dirname(self.output_file)
                os.makedirs(output_dir, exist_ok=True)
                with open(self.output_file, 'w', encoding='utf-8') as f:
                    for config in configs:
                        f.write(config + '\n')
                print(f"{len(configs)} configs saved to file {self.output_file}")
            except Exception as e:
                print(f"Error saving configs file: {e}")
    def save_json_content(self):
        if not self.json_contents:
            print("No JSON content found to save!")
        else:
            try:
                output_dir = os.path.dirname(self.json_output_file)
                os.makedirs(output_dir, exist_ok=True)
                parsed_contents = []
                for content in self.json_contents:
                    try:
                        parsed_json = json.loads(content)
                        parsed_contents.append(parsed_json)
                    except json.JSONDecodeError:
                        continue
                with open(self.json_output_file, 'w', encoding='utf-8') as f:
                    json.dump(parsed_contents, f, indent=2, ensure_ascii=False)
                print(f"{len(parsed_contents)} JSON contents saved to file {self.json_output_file}")
            except Exception as e:
                print(f"Error saving JSON file: {e}")
    def save_base64_content(self):
        if not self.base64_contents:
            print("No base64 content found to save!")
        else:
            try:
                output_dir = os.path.dirname(self.base64_output_file)
                os.makedirs(output_dir, exist_ok=True)
                with open(self.base64_output_file, 'w', encoding='utf-8') as f:
                    for content in self.base64_contents:
                        f.write(content + '\n')
                print(f"{len(self.base64_contents)} base64 contents saved to file {self.base64_output_file}")
            except Exception as e:
                print(f"Error saving base64 file: {e}")

    def print_detailed_summary(self, configs, phase1_successful, phase1_failed, phase2_recovered, phase2_final_failed):
        title = "DETAILED RESULTS SUMMARY"
        print(f"\n{title}")
        print("=" * len(title))
        total_successful = phase1_successful + phase2_recovered
        total_failed = phase2_final_failed
        success_rate = (total_successful / self.stats['total_links']) * 100 if self.stats['total_links'] > 0 else 0
        print(f"Total links processed: {self.stats['total_links']}")
        print(f"Total successful: {total_successful}")
        print(f"Total failed: {total_failed}")
        print(f"Overall success rate: {success_rate:.1f}%")
        print(f"Total configs collected: {len(configs):,}")
        print(f"JSON content found: {self.stats['json_content_count']:,}")
        print(f"Base64 content found: {self.stats['base64_content_count']:,}")
        title = "PHASE BREAKDOWN:"
        print(f"\n{title}")
        print("-" * len(title))
        phase1_rate = (phase1_successful / self.stats['total_links']) * 100 if self.stats['total_links'] > 0 else 0
        print(f"Phase 1 (Parallel Processing):")
        print(f"   Successful: {phase1_successful}")
        print(f"   Failed: {phase1_failed}")
        print(f"   Success rate: {phase1_rate:.1f}%")
        if phase1_failed > 0:
            recovery_rate = (phase2_recovered / phase1_failed) * 100 if phase1_failed > 0 else 0
            print(f"\nPhase 2 (Sequential Retry):")
            print(f"   Attempted: {phase1_failed}")
            print(f"   Recovered: {phase2_recovered}")
            print(f"   Permanently failed: {phase2_final_failed}")
            print(f"   Recovery rate: {recovery_rate:.1f}%")
        title = "TECHNICAL DETAILS:"
        print(f"\n{title}")
        print("-" * len(title))
        print(f"Retry attempts: {self.stats['retry_attempts']}")
        print(f"Empty responses: {self.stats['empty_responses']}")
        if self.failed_urls:
            print(f"\nPERMANENTLY FAILED LINKS ({len(self.failed_urls)}):")
            for i, url in enumerate(self.failed_urls, 1):
                print(f"   {i:2d}. {url}")
        if self.stats['empty_responses'] > 0:
            print(f"\nEMPTY RESPONSE LINKS ({self.stats['empty_responses']}):")
            empty_count = 0
            for url in self.successful_urls + self.failed_urls:
                if empty_count < self.stats['empty_responses']:
                    print(f"   {empty_count + 1:2d}. {url} (had empty responses during retries)")
                    empty_count += 1
        print(f"\nOUTPUT FILES:")
        print(f"   Configs file: {self.output_file}")
        if os.path.exists(self.output_file):
            file_size_kb = os.path.getsize(self.output_file) / 1024
            print(f"   Size: {file_size_kb:,.1f} KB")
        print(f"   JSON file: {self.json_output_file}")
        if os.path.exists(self.json_output_file):
            file_size_kb = os.path.getsize(self.json_output_file) / 1024
            print(f"   Size: {file_size_kb:,.1f} KB")
        print(f"   Base64 file: {self.base64_output_file}")
        if os.path.exists(self.base64_output_file):
            file_size_kb = os.path.getsize(self.base64_output_file) / 1024
            print(f"   Size: {file_size_kb:,.1f} KB")
        print("=" * len("Convert proxy configurations to JSON format"))
def main():
    title = "V2Ray Config Collector"
    print(title)
    print("=" * len(title))
    collector = SourceCollector()
    collector.fetch_all_configs()
if __name__ == "__main__":
    main()