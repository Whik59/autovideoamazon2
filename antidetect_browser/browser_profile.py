#!/usr/bin/env python3
"""
Browser Profile Management Module
Handles browser profiles with unique fingerprints and proxy configurations
"""

import json
import random
import hashlib
from pathlib import Path


class BrowserProfile:
    """Manages individual browser profiles with unique fingerprints"""
    
    def __init__(self, profile_name, proxy_config=None, target_country=None):
        self.profile_name = profile_name
        self.proxy_config = proxy_config
        self.target_country = target_country or "USA"  # Default to USA
        self.fingerprint = self.generate_fingerprint()
        
        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        self.profile_dir = script_dir / "profiles" / profile_name
        self.chrome_data_dir = self.profile_dir / "chrome_data"
        
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.chrome_data_dir.mkdir(exist_ok=True)
        
    def generate_fingerprint(self):
        """Generate a highly unique browser fingerprint for anti-detection"""
        
        # Country-specific configurations for your YouTube channels
        country_configs = {
            "Italy": {
                "timezones": ["Europe/Rome", "Europe/Vatican"],
                "languages": ["it-IT,it;q=0.9", "it-IT,it;q=0.9,en;q=0.8"],
                "os_preference": {"Windows": 0.6, "Mac": 0.25, "Linux": 0.15}
            },
            "France": {
                "timezones": ["Europe/Paris", "Europe/Monaco"],
                "languages": ["fr-FR,fr;q=0.9", "fr-FR,fr;q=0.9,en;q=0.8", "fr-CA,fr;q=0.9"],
                "os_preference": {"Windows": 0.55, "Mac": 0.3, "Linux": 0.15}
            },
            "Spain": {
                "timezones": ["Europe/Madrid", "Europe/Andorra"],
                "languages": ["es-ES,es;q=0.9", "es-ES,es;q=0.9,en;q=0.8", "es-ES,es;q=0.9,ca;q=0.8"],
                "os_preference": {"Windows": 0.65, "Mac": 0.25, "Linux": 0.1}
            },
            "Netherlands": {
                "timezones": ["Europe/Amsterdam"],
                "languages": ["nl-NL,nl;q=0.9", "nl-NL,nl;q=0.9,en;q=0.8", "en-US,en;q=0.9,nl;q=0.8"],
                "os_preference": {"Windows": 0.5, "Mac": 0.35, "Linux": 0.15}
            },
            "Poland": {
                "timezones": ["Europe/Warsaw"],
                "languages": ["pl-PL,pl;q=0.9", "pl-PL,pl;q=0.9,en;q=0.8"],
                "os_preference": {"Windows": 0.7, "Mac": 0.2, "Linux": 0.1}
            },
            "Sweden": {
                "timezones": ["Europe/Stockholm"],
                "languages": ["sv-SE,sv;q=0.9", "sv-SE,sv;q=0.9,en;q=0.8", "en-US,en;q=0.9,sv;q=0.8"],
                "os_preference": {"Windows": 0.45, "Mac": 0.4, "Linux": 0.15}
            },
            "Germany": {
                "timezones": ["Europe/Berlin", "Europe/Zurich"],
                "languages": ["de-DE,de;q=0.9", "de-DE,de;q=0.9,en;q=0.8", "de-AT,de;q=0.9"],
                "os_preference": {"Windows": 0.55, "Mac": 0.3, "Linux": 0.15}
            },
            "USA": {
                "timezones": ["America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles", 
                             "America/Phoenix", "America/Detroit", "America/Atlanta", "America/Miami", "America/Boston"],
                "languages": ["en-US,en;q=0.9", "en-US,en;q=0.9,es;q=0.8", "en-US,en;q=0.9,fr;q=0.7"],
                "os_preference": {"Windows": 0.6, "Mac": 0.35, "Linux": 0.05}
            }
        }
        
        # Get country-specific config
        country_config = country_configs.get(self.target_country, country_configs["USA"])
        
        # Expanded screen resolutions (50+ combinations)
        common_widths = [1024, 1280, 1366, 1440, 1536, 1600, 1680, 1920, 2048, 2560, 3440, 3840]
        common_heights = [600, 720, 768, 900, 864, 1024, 1050, 1080, 1200, 1440, 1440, 2160]
        resolutions = [(w, h) for w in common_widths for h in common_heights if w > h and (w/h) in [16/9, 16/10, 4/3, 21/9]]
        
        # Generate country-appropriate user agents based on OS preferences
        chrome_versions = [118, 119, 120, 121, 122]
        webkit_versions = ["537.36", "537.35", "537.34"]
        
        user_agents = []
        os_preference = country_config["os_preference"]
        
        # Determine OS based on country preferences
        os_choice = random.choices(
            list(os_preference.keys()), 
            weights=list(os_preference.values())
        )[0]
        
        if os_choice == "Windows":
            # Windows variations
            windows_versions = ["10.0", "11.0"]
            windows_builds = ["Win64; x64", "WOW64"]
            for version in chrome_versions:
                for webkit in webkit_versions:
                    for win_ver in windows_versions:
                        for build in windows_builds:
                            user_agents.append(f"Mozilla/5.0 (Windows NT {win_ver}; {build}) AppleWebKit/{webkit} (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/{webkit}")
        
        elif os_choice == "Mac":
            # macOS variations  
            mac_versions = ["10_15_7", "11_0_1", "12_0_1", "13_0", "14_0"]
            for version in chrome_versions:
                for webkit in webkit_versions:
                    for mac_ver in mac_versions:
                        user_agents.append(f"Mozilla/5.0 (Macintosh; Intel Mac OS X {mac_ver}) AppleWebKit/{webkit} (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/{webkit}")
        
        else:  # Linux
            # Linux variations
            linux_distros = ["X11; Linux x86_64", "X11; Linux i686", "X11; Ubuntu; Linux x86_64"]
            for version in chrome_versions:
                for webkit in webkit_versions:
                    for distro in linux_distros:
                        user_agents.append(f"Mozilla/5.0 ({distro}) AppleWebKit/{webkit} (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/{webkit}")
        
        # Use country-specific timezones and languages
        timezones = country_config["timezones"]
        languages = country_config["languages"]
        
        # Hardware profiles
        cpu_cores = [2, 4, 6, 8, 10, 12, 16, 20, 24, 32]
        ram_sizes = [2, 4, 6, 8, 12, 16, 24, 32, 48, 64]
        gpu_vendors = ["NVIDIA Corporation", "Advanced Micro Devices, Inc.", "Intel Inc.", "Apple Inc."]
        
        # Generate realistic GPU combinations
        nvidia_gpus = ["GeForce GTX 1060", "GeForce RTX 3070", "GeForce RTX 4080", "Quadro P2000"]
        amd_gpus = ["Radeon RX 580", "Radeon RX 6700 XT", "Radeon RX 7800 XT", "Radeon Pro W5500"]
        intel_gpus = ["Intel(R) UHD Graphics 620", "Intel(R) Iris(R) Xe Graphics", "Intel(R) Arc(TM) A770"]
        
        resolution = random.choice(resolutions)
        selected_ua = random.choice(user_agents)
        
        # Determine platform from user agent for consistency
        if "Windows" in selected_ua:
            platform = "Win32"
            platform_family = "Windows"
        elif "Macintosh" in selected_ua:
            platform = "MacIntel"  
            platform_family = "Mac"
        else:
            platform = "Linux x86_64"
            platform_family = "Linux"
        
        # Select appropriate GPU based on platform
        if platform_family == "Mac":
            gpu_vendor = "Apple Inc."
            gpu_renderer = "Apple M1" if random.random() > 0.5 else "Apple M2"
        else:
            gpu_vendor = random.choice(gpu_vendors)
            if "NVIDIA" in gpu_vendor:
                gpu_renderer = random.choice(nvidia_gpus)
            elif "Advanced Micro Devices" in gpu_vendor:
                gpu_renderer = random.choice(amd_gpus)
            else:
                gpu_renderer = random.choice(intel_gpus)
        
        # Generate consistent canvas and WebGL noise based on profile name (deterministic but unique)
        profile_seed = int(hashlib.md5(self.profile_name.encode()).hexdigest()[:8], 16)
        random.seed(profile_seed)
        
        canvas_noise = random.uniform(0.0001, 0.001)  # Realistic canvas noise
        webgl_noise = random.uniform(0.00001, 0.0001)  # WebGL noise
        audio_noise = random.uniform(0.000001, 0.00001)  # AudioContext noise
        
        # Reset random seed
        random.seed()
        
        fingerprint = {
            # Basic fingerprints
            'user_agent': selected_ua,
            'screen_width': resolution[0],
            'screen_height': resolution[1],
            'timezone': random.choice(timezones),
            'language': random.choice(languages),
            'platform': platform,
            'platform_family': platform_family,
            
            # Hardware fingerprints
            'hardware_concurrency': random.choice(cpu_cores),
            'device_memory': random.choice(ram_sizes),
            'max_touch_points': random.choice([0, 1, 5, 10]),
            
            # Graphics fingerprints
            'webgl_vendor': gpu_vendor,
            'webgl_renderer': gpu_renderer,
            'canvas_noise': canvas_noise,
            'webgl_noise': webgl_noise,
            
            # Audio fingerprints
            'audio_noise': audio_noise,
            'audio_sample_rate': random.choice([44100, 48000, 96000]),
            'audio_buffer_size': random.choice([128, 256, 512, 1024]),
            
            # Network fingerprints
            'connection_type': random.choice(['ethernet', 'wifi', 'cellular', 'unknown']),
            'connection_downlink': round(random.uniform(1.5, 100.0), 2),
            'connection_rtt': random.randint(10, 200),
            
            # Browser-specific
            'do_not_track': random.choice(['1', '0', 'unspecified']),
            'cookie_enabled': True,
            'java_enabled': False,  # Java is deprecated
            'plugins_length': random.randint(0, 5),
            
            # Viewport variations
            'viewport_width': resolution[0] - random.randint(0, 100),
            'viewport_height': resolution[1] - random.randint(50, 200),
            
            # Color depth and pixel ratio
            'color_depth': random.choice([24, 32]),
            'pixel_ratio': random.choice([1, 1.25, 1.5, 2, 2.5, 3]),
            
            # Battery (if available)
            'battery_charging': random.choice([True, False]),
            'battery_level': round(random.uniform(0.1, 1.0), 2),
            
            # Permissions
            'permissions': {
                'camera': random.choice(['granted', 'denied', 'prompt']),
                'microphone': random.choice(['granted', 'denied', 'prompt']),
                'notifications': random.choice(['granted', 'denied', 'prompt']),
                'geolocation': random.choice(['granted', 'denied', 'prompt'])
            }
        }
        
        return fingerprint
    
    def save_profile(self):
        """Save profile configuration to disk"""
        config = {
            'profile_name': self.profile_name,
            'proxy_config': self.proxy_config,
            'target_country': self.target_country,
            'fingerprint': self.fingerprint
        }
        
        config_file = self.profile_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    @classmethod
    def load_profile(cls, profile_name):
        """Load existing profile from disk"""
        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        profile_dir = script_dir / "profiles" / profile_name
        config_file = profile_dir / "config.json"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            profile = cls(profile_name, config.get('proxy_config'), config.get('target_country', 'USA'))
            profile.fingerprint = config.get('fingerprint', profile.fingerprint)
            return profile
        
        return None 