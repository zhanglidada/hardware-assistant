# techpowerup_cpu_scraper_enhanced.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
import random
from urllib.parse import urljoin
from typing import List, Dict, Optional
import os
import re
import json

# ----------------------------
# 配置
# ----------------------------
BASE_URL = "https://www.techpowerup.com"
CPU_SPECS_URL = f"{BASE_URL}/cpu-specs/"
OUTPUT_JSON = "techpowerup_cpu_specs_detailed_2026.json"
OUTPUT_CSV = "techpowerup_cpu_specs_detailed_2026.csv"  # 保留CSV输出作为备份
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
MAX_RETRIES = 3
DELAY_RANGE_LIST = (1.0, 2.5)   # 列表页延迟
DELAY_RANGE_DETAIL = (0.8, 1.8) # 详情页延迟（可稍快）

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("cpu_scraper_detailed.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def fetch_page(url: str, retries: int = MAX_RETRIES) -> BeautifulSoup:
    for attempt in range(retries):
        try:
            headers = {"User-Agent": USER_AGENT}
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{retries} failed for {url}: {e}")
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Failed to fetch {url}")


def parse_cpu_row(row) -> Optional[Dict]:
    cols = row.find_all("td")
    if len(cols) < 9:
        return None

    def text_or_na(tag):
        return tag.get_text(strip=True) if tag else "N/A"

    model_tag = cols[0].find("a")
    if not model_tag:
        return None
    model = text_or_na(model_tag)
    model_url = urljoin(BASE_URL, model_tag["href"])

    cores = text_or_na(cols[1])
    clocks = text_or_na(cols[2])
    smt = text_or_na(cols[3])
    cache = text_or_na(cols[4])
    process = text_or_na(cols[5])
    tdp = text_or_na(cols[6])
    released = text_or_na(cols[7])
    benchmark = text_or_na(cols[8])

    base_clock, turbo_clock = "N/A", "N/A"
    if "/" in clocks:
        parts = clocks.split("/")
        base_clock = parts[0].strip().replace(" GHz", "")
        turbo_clock = parts[1].strip().replace(" GHz", "")
    elif clocks != "N/A":
        base_clock = clocks.replace(" GHz", "")

    return {
        "model": model,
        "model_url": model_url,
        "cores": cores,
        "base_clock_ghz": base_clock,
        "turbo_clock_ghz": turbo_clock,
        "smt": smt,
        "l3_cache_mb": cache.replace(" MB", "") if "MB" in cache else cache,
        "process_nm": process.replace(" nm", "") if "nm" in process else process,
        "tdp_w": tdp.replace(" W", "") if "W" in tdp else tdp,
        "release_date": released,
        "relative_performance": benchmark,
    }


def parse_detail_page(soup: BeautifulSoup) -> Dict[str, str]:
    """从详情页提取高级参数"""
    data = {}

    # 找到 specs 表格（class="specs")
    spec_table = soup.select_one("table.specs")
    if not spec_table:
        return {"socket": "N/A", "memory_type": "N/A", "instruction_sets": "N/A", "integrated_graphics": "N/A"}

    for row in spec_table.find_all("tr"):
        th = row.find("th")
        td = row.find("td")
        if th and td:
            key = th.get_text(strip=True).lower().replace(" ", "_").replace(":", "")
            val = td.get_text(strip=True)
            data[key] = val

    # 提取关键字段
    socket = data.get("socket", "N/A")
    memory_type = data.get("memory_type", "N/A")
    instruction_sets = data.get("instruction_set", data.get("instructions", "N/A"))
    igpu = data.get("integrated_graphics", "N/A")

    # 清洗内存类型（如 "DDR5-5600, DDR4-3200" → 保留原样）
    # 清洗指令集（如 "MMX, SSE, SSE2, AVX, AVX2"）

    return {
        "socket": socket,
        "memory_type": memory_type,
        "instruction_sets": instruction_sets,
        "integrated_graphics": igpu,
    }


def scrape_all_cpus_with_details() -> List[Dict]:
    logger.info("Starting enhanced CPU scraping with detail pages...")
    all_cpus = []
    page = 1

    while True:
        url = f"{CPU_SPECS_URL}?page={page}"
        logger.info(f"Fetching list page {page}")
        soup = fetch_page(url)
        table = soup.select_one("table.styled-table")
        if not table:
            break

        rows = table.find_all("tr")[1:]
        if not rows:
            break

        for row in rows:
            try:
                basic = parse_cpu_row(row)
                if not basic or basic["model"] == "N/A":
                    continue

                # 抓取详情页
                logger.debug(f"Fetching detail for {basic['model']}")
                detail_soup = fetch_page(basic["model_url"])
                detail_info = parse_detail_page(detail_soup)

                # 合并数据
                cpu_record = {**basic, **detail_info}
                cpu_record["scraped_at"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                all_cpus.append(cpu_record)

                time.sleep(random.uniform(*DELAY_RANGE_DETAIL))

            except Exception as e:
                logger.error(f"Error processing {basic.get('model', 'Unknown')}: {e}")

        time.sleep(random.uniform(*DELAY_RANGE_LIST))
        next_button = soup.select_one("a:-soup-contains('Next')")
        if not next_button:
            break
        page += 1

    return all_cpus


def save_to_csv(data: List[Dict], filename: str):
    df = pd.DataFrame(data)
    # 按发布时间排序（可选）
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    logger.info(f"Saved {len(df)} records to {filename}")

def save_to_json(data: List[Dict], filename: str):
    """保存数据到JSON文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved {len(data)} records to {filename}")


def main():
    try:
        cpus = scrape_all_cpus_with_details()
        save_to_json(cpus, OUTPUT_JSON)
        save_to_csv(cpus, OUTPUT_CSV)  # 同时保存CSV作为备份
    except Exception as e:
        logger.exception(f"Scraping failed: {e}")
        raise


if __name__ == "__main__":
    main()