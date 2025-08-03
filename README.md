# V2Ray Config Collector

A comprehensive Python application for collecting, processing, and validating V2Ray proxy configurations from multiple sources. This tool automates the entire workflow from fetching configurations to testing their connectivity.

## 🚀 Features

- **Multi-source Collection**: Fetches configurations from 50+ GitHub repositories and sources
- **Multi-protocol Support**: Supports VMess, VLess, Trojan, ShadowSocks, SSR, TUIC, and Hysteria2 protocols
- **Intelligent Processing**: Handles Base64, JSON, and plain text formats automatically
- **Duplicate Removal**: Advanced hash-based deduplication algorithm
- **Connectivity Testing**: TCP connection validation for all configurations
- **Organized Output**: Protocol-specific file organization and multiple output formats
- **Progress Tracking**: Real-time progress bars and detailed statistics
- **Error Handling**: Comprehensive error handling with retry mechanisms

## 📁 Project Structure

```
v2ray_config_collector/
├── main.py                     # Main entry point
├── core/                       # Core processing modules
│   ├── fetcher.py              # Configuration source collector
│   ├── parser.py               # Format converter
│   ├── deduplicator.py         # Duplicate remover
│   └── validator.py            # Connectivity tester
└── data/                       # Configuration and output files
    ├── sources/
    │   └── proxy_sources.txt    # Input: Source URLs list
    ├── raw/                     # Output: Raw collected configs
    │   ├── raw_configs.txt
    │   ├── raw_json.json
    │   └── raw_base64.txt
    ├── processed/               # Output: JSON formatted configs
    │   └── normalized_configs.json
    ├── unique/                  # Output: Deduplicated configs
    │   ├── deduplicated.json
    │   ├── deduplicated.txt
    │   └── protocols/           # Protocol-specific files
    └── validated/               # Output: Validated configs
        └── working_configs/     # TCP-tested valid configs
```

## 🔄 Workflow Overview

The application follows a 4-stage pipeline:

```
URLs → Source Collector → Format Converter → Deduplicator → Connectivity Validator
```

Each stage processes the output from the previous stage, creating a refined dataset at each step.

## 📋 Module Details

### 1. Source Collector (`fetcher.py`)

**Purpose**: Fetches proxy configurations from multiple online sources

**Input File**: 
- `data/sources/proxy_sources.txt` - Contains 50+ URLs pointing to configuration sources

**Processing**:
- **Phase 1**: Parallel processing of URLs using ThreadPoolExecutor (10 workers)
- **Phase 2**: Sequential retry for failed URLs
- Supports multiple content formats:
  - Plain text configurations
  - Base64 encoded content
  - JSON structured data
- Handles various protocols: VMess, VLess, Trojan, ShadowSocks, SSR, TUIC, Hysteria2

**Output Files**:
- `data/raw/raw_configs.txt` - Direct proxy configuration URLs
- `data/raw/raw_json.json` - JSON formatted content
- `data/raw/raw_base64.txt` - Base64 encoded content

**Key Features**:
- Multi-threaded fetching with configurable worker count
- Automatic retry mechanism (3 attempts per URL)
- Content type detection and parsing
- Progress tracking with detailed statistics
- Comprehensive error handling and reporting

### 2. Format Converter (`parser.py`)

**Purpose**: Converts all configuration formats into standardized JSON structure

**Input Files**:
- `data/raw/raw_configs.txt`
- `data/raw/raw_base64.txt`
- `data/raw/raw_json.json`

**Processing**:
- Parses each protocol with dedicated parsing functions
- Validates server addresses and port numbers
- Extracts all configuration parameters (server, port, encryption, network settings)
- Filters invalid configurations automatically
- Adds metadata (timestamps, line numbers, parsing info)

**Output File**:
- `data/processed/normalized_configs.json` - Standardized JSON format with metadata

**Supported Protocols & Parsing**
- **VMess**
- **VLess**
- **Trojan**
- **ShadowSocks**
- **SSR**
- **TUIC**
- **Hysteria2**

### 3. Deduplicator (`deduplicator.py`)

**Purpose**: Eliminates duplicate configurations using advanced hashing algorithms

**Input File**:
- `data/processed/normalized_configs.json`

**Processing**:
- **Phase 1**: Hash generation based on core parameters (server, port, UUID, protocol)
- **Phase 2**: Duplicate group identification and best configuration selection
- Uses MD5 hashing of key configuration parameters
- Smart selection algorithm: prefers configs with more complete information
- Maintains original configuration integrity

**Output Files**:
- `data/unique/deduplicated.json` - Complete deduplicated dataset
- `data/unique/deduplicated.txt` - Plain text configuration URLs
- `data/unique/protocols/` - Protocol-specific files:
  - `vmess_configs.json` & `vmess_configs.txt`
  - `vless_configs.json` & `vless_configs.txt`
  - `trojan_configs.json` & `trojan_configs.txt`
  - `shadowsocks_configs.json` & `shadowsocks_configs.txt`
  - `ssr_configs.json` & `ssr_configs.txt`
  - `tuic_configs.json` & `tuic_configs.txt`
  - `hysteria2_configs.json` & `hysteria2_configs.txt`

**URL Reconstruction**: 
- Rebuilds original URL format from JSON structure
- Maintains compatibility with V2Ray clients
- Preserves all protocol-specific parameters

### 4. Connectivity Validator (`validator.py`)

**Purpose**: Validates proxy server connectivity through TCP connection testing

**Input File**:
- `data/unique/deduplicated.txt`

**Processing**:
- **Multi-threaded Testing**: 100 concurrent workers for fast processing
- **Connection Validation**: TCP socket connection to each server:port
- **Timeout Management**: 5-second timeout per connection
- **Protocol-aware Parsing**: Extracts server and port from each protocol format
- **Real-time Progress**: Updates every 10 seconds with statistics

**Output Files**:
- `data/validated/working_configs/all_valid.txt` - All validated configurations
- `data/validated/working_configs/{protocol}_valid.txt` - Protocol-specific valid configs

**Error Categories**:
- Timeout errors
- Connection refused
- DNS resolution failures
- Parse errors
- General connection errors

## 🚀 Usage

### Prerequisites

- **Python 3.7 or higher** - Check your version with `python --version`
- **Git** (for cloning the repository)
- **Internet connection** (for fetching configurations)
- **Operating System**: Windows, macOS, or Linux

### Installation Methods

#### Method 1: Install from PyPI (Recommended)

```bash
# Install the package
pip install v2ray-config-collector

# Run the application
v2ray-config-collector
```

#### Method 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/Delta-Kronecker/v2ray-config-collector.git
cd v2ray-config-collector

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .

# Run the application
python v2ray_config_collector/main.py
```

#### Method 3: Direct Execution (Development)

```bash
# Clone the repository
git clone https://github.com/Delta-Kronecker/v2ray-config-collector.git
cd v2ray-config-collector

# Install dependencies
pip install requests>=2.28.0 tqdm>=4.64.0

# Run directly
cd config_collector
python main.py
```

### Setup Configuration Sources

Before running the application, you need to prepare the input file with configuration sources:

1. **Create or edit the source URLs file**:
   ```bash
   # The file should be located at: v2ray_config_collector/data/sources/proxy_sources.txt
   # Add your V2Ray configuration source URLs, one per line
   ```

2. **Example proxy_sources.txt content**:
   ```
   https://example1.com/configs
   https://example2.com/v2ray-configs
   https://github.com/user/repo/raw/main/configs.txt
   ```

### Running the Application

#### Complete Pipeline (Recommended)

```bash
# Run all stages sequentially
v2ray-config-collector

# Or if installed from source:
python v2ray_config_collector/main.py
```

This will execute all 4 stages:
1. **Collection** → Fetch configs from sources
2. **JSON Conversion** → Standardize format
3. **Deduplication** → Remove duplicates  
4. **TCP Testing** → Validate connectivity

#### Individual Module Execution

You can run each stage independently using the installed console commands:

```bash
# Stage 1: Collect configurations from sources
v2ray-fetch
# Output: data/raw/

# Stage 2: Convert all formats to JSON
v2ray-parse  
# Output: data/processed/normalized_configs.json

# Stage 3: Remove duplicate configurations
v2ray-dedup
# Output: data/unique/

# Stage 4: Test TCP connectivity
v2ray-test
# Output: data/validated/working_configs/
```

#### Alternative Module Execution (Development)

```bash
# From the v2ray_config_collector directory:
python -m core.fetcher
python -m core.parser
python -m core.deduplicator
python -m core.validator
```

### Understanding Output Files

After successful execution, you'll find organized output files:

```
v2ray_config_collector/data/
├── sources/
│   └── proxy_sources.txt               # INPUT: Your source URLs
├── raw/                                # Stage 1 Output
│   ├── raw_configs.txt                # Raw proxy URLs
│   ├── raw_json.json                  # JSON content
│   └── raw_base64.txt                 # Base64 content
├── processed/                          # Stage 2 Output  
│   └── normalized_configs.json        # Unified JSON format
├── unique/                            # Stage 3 Output
│   ├── deduplicated.json              # Deduplicated JSON
│   ├── deduplicated.txt               # Deduplicated URLs
│   └── protocols/                     # Per-protocol files
│       ├── vmess_configs.txt
│       ├── vless_configs.txt
│       ├── trojan_configs.txt
│       ├── shadowsocks_configs.txt
│       ├── ssr_configs.txt
│       ├── tuic_configs.txt
│       └── hysteria2_configs.txt
└── validated/                         # Stage 4 Output
    └── working_configs/               # TCP-validated configs
        ├── all_valid.txt              # All working configs
        ├── vmess_valid.txt           # Working VMess configs
        ├── vless_valid.txt           # Working VLess configs
        ├── trojan_valid.txt          # Working Trojan configs
        ├── shadowsocks_valid.txt     # Working SS configs
        ├── ssr_valid.txt             # Working SSR configs
        ├── tuic_valid.txt            # Working TUIC configs
        └── hysteria2_valid.txt       # Working Hysteria2 configs
```

### Configuration Options

The application uses sensible defaults, but you can modify behavior by editing the source files:

- **Thread count**: Modify `max_workers` in fetcher.py (default: 10 for collection, 100 for testing)
- **Timeout settings**: Adjust connection timeout in validator.py (default: 5 seconds)
- **Retry attempts**: Configure retry logic in fetcher.py (default: 3 attempts)

### Example Workflow

```bash
# 1. Install the application
pip install v2ray-config-collector

# 2. Prepare your source URLs (create/edit the file)
mkdir -p data/sources
echo "https://your-source1.com/configs" > data/sources/proxy_sources.txt
echo "https://your-source2.com/configs" >> data/sources/proxy_sources.txt

# 3. Run the complete pipeline
v2ray-config-collector

# 4. Use the validated configurations
# The working configs will be in: data/validated/working_configs/
```

### Troubleshooting

**Common Issues:**

1. **Python version error**: Ensure Python 3.7+ is installed
   ```bash
   python --version  # Should show 3.7 or higher
   ```

2. **Permission denied**: Use appropriate permissions for file operations
   ```bash
   # On Linux/macOS, you might need:
   sudo pip install v2ray-config-collector
   ```

3. **Network timeouts**: Check your internet connection and firewall settings

4. **Empty results**: Verify your source URLs in `proxy_sources.txt` are accessible

5. **Import errors**: Ensure all dependencies are installed
   ```bash
   pip install requests tqdm
   ```

**Getting Help:**
- Check the [Issues page](https://github.com/Delta-Kronecker/config-collector/issues) for known problems
- Review the console output for detailed error messages and statistics


## 📈 Output Statistics

Each module provides detailed statistics:

### Collector Statistics
- Total links processed
- Success/failure rates
- Content type breakdown (JSON/Base64/Plain)
- Retry attempts and recovery rates
- Processing speed metrics

### JSON Converter Statistics
- Total configurations processed
- Success/failure conversion rates
- Protocol distribution
- Validation results
- Filter reasons and error categories

### Duplicate Remover Statistics
- Original vs unique configuration counts
- Duplicate removal efficiency
- Protocol-wise distribution
- Hash collision analysis
- Processing performance metrics

### TCP Tester Statistics
- Connection success rates
- Protocol-wise validity
- Error categorization
- Processing speed
- Geographic/provider analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## ⚠️ Disclaimer

This tool is for educational and research purposes. Users are responsible for complying with their local laws and the terms of service of the proxy providers. The authors are not responsible for any misuse of this tool.

