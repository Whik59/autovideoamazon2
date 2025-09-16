import shutil
from pathlib import Path

def create_proxy_extension(host: str, port: int, user: str, passw: str, profile_name: str):
    """
    Creates an UNPACKED Chrome extension to handle proxy authentication.
    Returns the absolute path to the extension directory.
    """
    plugin_dir = Path("proxy_extensions") / profile_name
    
    # Clean up old extension files if they exist
    if plugin_dir.exists():
        shutil.rmtree(plugin_dir)
    
    plugin_dir.mkdir(parents=True, exist_ok=True)

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy Auth",
        "permissions": [
            "webRequest",
            "webRequestBlocking",
            "privacy",
            "tabs",
            "activeTab",
            "contentSettings",
            "<all_urls>"
        ],
        "background": {
            "scripts": ["background.js"],
            "persistent": true
        }
    }
    """

    background_js = """
    console.log("Proxy authentication extension starting for {host}:{port}");
    
    var credentials = {{
        username: "{user}",
        password: "{passw}"
    }};
    
    console.log("Extension loaded with username:", credentials.username);

    function handleAuth(details) {{
        console.log("AUTH CHALLENGE:", details);
        console.log("Responding with credentials for user:", credentials.username);
        
        return {{
            authCredentials: {{
                username: credentials.username,
                password: credentials.password
            }}
        }};
    }}

    // Install the auth listener immediately
    chrome.webRequest.onAuthRequired.addListener(
        handleAuth,
        {{ urls: ["<all_urls>"] }},
        ["blocking"]
    );
    
    console.log("Auth listener installed for all URLs");
    
    // Maximum WebRTC leak protection
    if (chrome.privacy && chrome.privacy.network) {{
        // Set the most restrictive WebRTC policy
        chrome.privacy.network.webRTCIPHandlingPolicy.set({{
            value: 'disable_non_proxied_udp'
        }}, function() {{
            console.log("WebRTC non-proxied UDP disabled");
        }});
    }}
    
    // Block WebRTC using content settings
    if (chrome.contentSettings) {{
        chrome.contentSettings.camera.set({{
            primaryPattern: '<all_urls>',
            setting: 'block'
        }});
        chrome.contentSettings.microphone.set({{
            primaryPattern: '<all_urls>',
            setting: 'block'
        }});
        console.log("Camera and microphone access blocked");
    }}
    
    // Block all WebRTC-related requests
    chrome.webRequest.onBeforeRequest.addListener(
        function(details) {{
            var url = details.url.toLowerCase();
            if (url.includes('stun:') || url.includes('turn:') || 
                url.includes('stun.') || url.includes('turn.') ||
                url.includes('webrtc') || url.includes('rtc') ||
                url.includes('ice') || url.includes('candidate')) {{
                console.log("Blocked WebRTC request:", details.url);
                return {{ cancel: true }};
            }}
            return {{}};
        }},
        {{ urls: ["<all_urls>"] }},
        ["blocking"]
    );
    
    // Inject WebRTC blocking script into all pages
    chrome.webRequest.onHeadersReceived.addListener(
        function(details) {{
            if (details.type === 'main_frame') {{
                // Inject script to disable WebRTC APIs
                chrome.tabs.executeScript(details.tabId, {{
                    code: `
                        // Override WebRTC APIs to prevent IP leaks
                        if (window.RTCPeerConnection) {{
                            window.RTCPeerConnection = undefined;
                        }}
                        if (window.webkitRTCPeerConnection) {{
                            window.webkitRTCPeerConnection = undefined;
                        }}
                        if (window.mozRTCPeerConnection) {{
                            window.mozRTCPeerConnection = undefined;
                        }}
                        if (navigator.getUserMedia) {{
                            navigator.getUserMedia = undefined;
                        }}
                        if (navigator.webkitGetUserMedia) {{
                            navigator.webkitGetUserMedia = undefined;
                        }}
                        if (navigator.mozGetUserMedia) {{
                            navigator.mozGetUserMedia = undefined;
                        }}
                        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {{
                            navigator.mediaDevices.getUserMedia = undefined;
                        }}
                        console.log("WebRTC APIs disabled by extension");
                    `,
                    runAt: 'document_start'
                }});
            }}
        }},
        {{ urls: ["<all_urls>"] }},
        ["responseHeaders"]
    );
    """.format(host=host, port=port, user=user, passw=passw)

    with open(plugin_dir / "manifest.json", "w") as f:
        f.write(manifest_json)
    
    with open(plugin_dir / "background.js", "w") as f:
        f.write(background_js)
    
    print(f"Proxy extension files created:")
    print(f"  - manifest.json: {plugin_dir / 'manifest.json'}")
    print(f"  - background.js: {plugin_dir / 'background.js'}")
    
    return str(plugin_dir.resolve()) 