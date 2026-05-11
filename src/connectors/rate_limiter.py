import time

class RateLimiter:
    def __init__(self, max_requests=55, window_seconds=30):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_count = 0
        self.reset_time = time.time()
        self.last_request_time = 0
    
    def wait_if_needed(self):
        current_time = time.time()
        
        # Reset counter every window
        if current_time - self.reset_time >= self.window_seconds:
            self.request_count = 0
            self.reset_time = current_time
        
        # Wait if approaching limit
        if self.request_count >= self.max_requests:
            wait_time = self.window_seconds - (current_time - self.reset_time)
            if wait_time > 0:
                print(f"\n   ⏳ Rate limit, waiting {wait_time:.1f}s...", end="", flush=True)
                time.sleep(wait_time + 0.5)
                self.request_count = 0
                self.reset_time = time.time()
        
        # Delay between requests
        if current_time - self.last_request_time < 0.5:
            time.sleep(0.5 - (current_time - self.last_request_time))
        
        self.last_request_time = time.time()
        self.request_count += 1
