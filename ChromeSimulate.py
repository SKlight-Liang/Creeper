'''
Copyright(c) Liang Yiyan, Pekin University, 2025. All rights reserved.

This program is used to simulate the behavioral logic of some browsers, 
in order to bypass the checks of most anti crawling mechanisms.
Users may need to perform human-machine authentication to evade inspection mechanisms.
In this case, the program will automatically pause to wait for the completion of this process.

DISCLAIMER:
Please note that this program is only for scientific research and learning purposes.
The author shall not be held legally responsible for any consequences resulting from improper use of the program.

Function Table:
OpenWebpage(URL: str, Timeout: int = 15) -> bool -- Open webpage with human-machine verification handling
ScrollToBottom(SimulateHumans: bool = True, RollingTimes: int = 0) -> bool -- Scroll to the bottom of the page
RetrieveWebpageContent() -> str -- Retrieve webpage content
CloseBrowser() -> None -- Close the browser instance
'''

from selenium import webdriver

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

import time
import random

from FileProcess import LogMessage

# Global Chrome browser options
ChromeOptions = Options()

# Set Chrome options to enhance stealth and performance
ChromeOptions.add_argument("--no-sandbox")
ChromeOptions.add_argument("--disable-dev-shm-usage")
ChromeOptions.add_argument("--disable-gpu")
ChromeOptions.add_argument("--disable-software-rasterizer")
ChromeOptions.add_argument("--remote-debugging-port=9222")
ChromeOptions.add_argument("--window-size=1920,1080")
ChromeOptions.add_argument("--start-maximized")
ChromeOptions.add_argument("--disable-blink-features=AutomationControlled")
ChromeOptions.add_experimental_option("excludeSwitches", ["enable-automation"])
ChromeOptions.add_experimental_option('useAutomationExtension', False)

# Set more realistic User-Agent and browser fingerprint
ChromeOptions.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    
# Add more headers to simulate a real browser
ChromeOptions.add_argument('--lang=zh-CN,zh;q=0.9,en;q=0.8')
ChromeOptions.add_argument('--accept-language=zh-CN,zh;q=0.9,en;q=0.8')

# Create a Chrome browser instance
ChromeService = Service(ChromeDriverManager().install())
Driver = webdriver.Chrome(service=ChromeService, options=ChromeOptions)

# Hide webdriver features
Driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
    'source': '''
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en']
        });
    '''
})

# Whether we need to wait for the user to perform human-machine verification
HM_CHECK_FLAG = True
# Waiting time range for simulating human behavior
MINIMUM_WAITING_TIME = 3
MAXIMUM_WAITING_TIME = 5

# Open Webpage
def OpenWebpage(URL: str) -> bool:
    try:
        # Navigate to the target URL
        Driver.get(URL)

        # Waiting for the user to complete human-machine verification
        # After the user completes, enter any character to continue the program
        global HM_CHECK_FLAG
        if HM_CHECK_FLAG:
            input("Press Enter to continue ...")
            HM_CHECK_FLAG = False

        # Waiting for the webpage to load completely
        time.sleep(random.uniform(MINIMUM_WAITING_TIME, MAXIMUM_WAITING_TIME))
        LogMessage(f"Webpage opened successfully: {URL}")

        return True
    
    except Exception as e:
        LogMessage(f"Error opening webpage: {URL}. Error: {str(e)}", Type="ERROR")
        return False
    

# Scroll to the bottom of the page
def ScrollToBottom(SimulateHumans: bool = True, RollingTimes: int = 0) -> bool:

    if not SimulateHumans:
        # Directly jump to the bottom of the page
        try:
            Driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(MINIMUM_WAITING_TIME, MAXIMUM_WAITING_TIME))
            return True
        
        except Exception as e:
            LogMessage(f"Error scrolling to bottom of the page. Error: {str(e)}", Type="ERROR")
            return False
        
    # Simulate human scrolling behavior: gradual scrolling step by step
    
    # If RollingTimes is 0, scroll until the bottom of the page
    # Scrolling down one page height each time
    SCROLL_PAUSE_TIME = random.uniform(1.6, 3.0)

    ScreenHeight = Driver.execute_script("return window.screen.height;")
    if RollingTimes == 0:
        TotalHeight = Driver.execute_script("return document.body.scrollHeight;")
        RollingTimes = int(TotalHeight / ScreenHeight) + 1

    for _ in range(RollingTimes):
        try:
            # Scroll gradually, one screen height at a time
            Driver.execute_script(f"window.scrollBy(0, {ScreenHeight});")
            # Random pause to simulate reading content
            time.sleep(SCROLL_PAUSE_TIME + random.uniform(-0.3, 0.5))

            # Occasionally scroll up a bit to simulate looking back
            # 30% chance to look back
            if random.random() < 0.3:  
                ScrollBack = random.randint(50, 150)
                Driver.execute_script(f"window.scrollBy(0, -{ScrollBack});")
                time.sleep(random.uniform(0.5, 1.0))
                Driver.execute_script(f"window.scrollBy(0, {ScrollBack});")
        
        except Exception as e:
            LogMessage(f"Error during scrolling. Error: {str(e)}", Type="ERROR")
            return False
        
    # Waiting for the webpage to load completely
    time.sleep(random.uniform(MINIMUM_WAITING_TIME, MAXIMUM_WAITING_TIME))

    return True

# Retrieve webpage content
def RetrieveWebpageContent() -> str:
    try:
        # Get the webpage content
        content = Driver.execute_script("return document.body.innerHTML;")
        LogMessage("Webpage content retrieved successfully.")
        return content

    except Exception as e:
        LogMessage(f"Error retrieving webpage content. Error: {str(e)}", Type="ERROR")
        return ""

# Close browser
def CloseBrowser() -> None:
    try:
        Driver.quit()
        LogMessage("Browser closed successfully.")
    
    except Exception as e:
        LogMessage(f"Error closing browser. Error: {str(e)}", Type="ERROR")
