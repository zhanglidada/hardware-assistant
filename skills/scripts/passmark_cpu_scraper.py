# passmark_cpu_scraper.py
import time
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os
import json
from typing import List, Dict

# ----------------------------
# 配置
# ----------------------------
PASSMARK_URL = "https://www.cpubenchmark.net/cpu_list.php"
OUTPUT_JSON = "passmark_cpu_benchmarks_2026.json"
OUTPUT_CSV = "passmark_cpu_benchmarks_2026.csv"  # 保留CSV输出作为备份
SCROLL_PAUSE_TIME = 1.5
MAX_SCROLL_ATTEMPTS = 10  # 防止无限滚动

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("passmark_scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def setup_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless")  # 无头模式（生产环境推荐）
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    return driver


def scroll_to_bottom(driver):
    """滚动到底部直到内容不再增加"""
    last_height = driver.execute_script("return document.body.scrollHeight")
    attempts = 0

    while attempts < MAX_SCROLL_ATTEMPTS:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            attempts += 1
            logger.info(f"No new content. Attempt {attempts}/{MAX_SCROLL_ATTEMPTS}")
        else:
            attempts = 0  # 重置计数器
        last_height = new_height

    logger.info("Finished scrolling.")


def extract_cpu_data(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("#cputable tbody tr")
    cpus = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 4:
            continue

        name_tag = cols[0].find("a")
        if not name_tag:
            continue

        name = name_tag.get_text(strip=True)
        rating = cols[1].get_text(strip=True)
        price = cols[2].get_text(strip=True).replace("$", "").replace(",", "")
        if price == "NA":
            price = None
        cores = cols[3].get_text(strip=True)

        # 提取 PassMark URL
        href = name_tag.get("href", "")
        passmark_url = f"https://www.cpubenchmark.net/{href}" if href else "N/A"

        cpus.append({
            "model": name,
            "passmark_score": rating,
            "price_usd": price,
            "cores": cores,
            "passmark_url": passmark_url,
            "scraped_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    return cpus


def main():
    driver = None
    try:
        logger.info("Launching Chrome for PassMark scraping...")
        driver = setup_driver()
        driver.get(PASSMARK_URL)

        # 等待表格加载
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "cputable"))
        )

        # 滚动到底部加载全部数据
        scroll_to_bottom(driver)

        # 获取完整 HTML
        full_html = driver.page_source
        cpu_list = extract_cpu_data(full_html)

        logger.info(f"Extracted {len(cpu_list)} CPUs from PassMark")
        
        # 保存为JSON
        with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(cpu_list, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved to {OUTPUT_JSON}")
        
        # 保存为CSV（备份）
        df = pd.DataFrame(cpu_list)
        df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
        logger.info(f"Saved to {OUTPUT_CSV}")

    except Exception as e:
        logger.exception(f"Error during PassMark scraping: {e}")
        raise
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()