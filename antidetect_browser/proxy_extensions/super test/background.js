
    console.log("Proxy authentication extension starting for gw.thunderproxy.net:5959");
    
    var credentials = {
        username: "0veAOAHVmW1Cdh12Ug-stc-isp-sid-0",
        password: "MjoYlZPyVLz16Jv"
    };
    
    console.log("Extension loaded with username:", credentials.username);

    function handleAuth(details) {
        console.log("AUTH CHALLENGE:", details);
        console.log("Responding with credentials for user:", credentials.username);
        
        return {
            authCredentials: {
                username: credentials.username,
                password: credentials.password
            }
        };
    }

    // Install the auth listener immediately
    chrome.webRequest.onAuthRequired.addListener(
        handleAuth,
        { urls: ["<all_urls>"] },
        ["blocking"]
    );
    
    console.log("Auth listener installed for all URLs");
    
    // Also try to preemptively set up auth for the proxy
    chrome.webRequest.onBeforeRequest.addListener(
        function(details) {
            console.log("Request intercepted:", details.url);
            return {};
        },
        { urls: ["<all_urls>"] },
        []
    );
    