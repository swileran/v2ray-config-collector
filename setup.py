from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="v2ray-config-collector",
    version="1.0.0",
    author="V2Ray Config Collector",
    author_email="",
    description="A comprehensive Python application for collecting, processing, and validating V2Ray proxy configurations from multiple sources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Delta-Kronecker/v2ray-config-collector",
    project_urls={
        "Bug Tracker": "https://github.com/Delta-Kronecker/v2ray-config-collector/issues",
        "Documentation": "https://github.com/Delta-Kronecker/v2ray-config-collector#readme",
        "Source Code": "https://github.com/Delta-Kronecker/v2ray-config-collector",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: System :: Networking",
        "Topic :: Utilities",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
            "isort>=5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "v2ray-config-collector=v2ray_config_collector.main:main",
            "v2ray-fetch=v2ray_config_collector.core.fetcher:main",
            "v2ray-parse=v2ray_config_collector.core.parser:main",
            "v2ray-dedup=v2ray_config_collector.core.deduplicator:main",
            "v2ray-test=v2ray_config_collector.core.validator:main",
        ],
    },
    include_package_data=True,
    package_data={
        "v2ray_config_collector": [
            "data/sources/*.txt",
        ],
    },
    keywords=[
        "v2ray",
        "proxy",
        "vpn",
        "vmess",
        "vless",
        "trojan",
        "shadowsocks",
        "ssr",
        "tuic",
        "hysteria2",
        "config",
        "collector",
        "networking",
    ],
    zip_safe=False,
)