# 🛒 SuperSuperSave

**SuperSuperSave** is a smart mobile companion designed to take the guesswork out of grocery shopping. Instead of hopping from store to store or manually checking flyers, SuperSuperSave calculates the most cost-effective way to fill your pantry.

---

## 💡 The Idea

The premise is simple: **Stop overpaying for essentials.** Users input their desired grocery list, and the app cross-references real-time data from various retailers. The result is a clear breakdown of where to shop to get the lowest total price. 

### Key Features
* **Smart Shopping Lists:** Input your items once; see prices everywhere.
* **Total Price Comparison:** Compare the final "basket" price across different supermarket chains.
* **Savings Tracker:** A personal dashboard showing your shopping history and cumulative savings over time.
* **Mobile-First Experience:** Designed for quick use while on the go or standing in the aisle.

---

## 🏗️ Architecture Draft

The project follows a modern decoupled architecture, ensuring the mobile frontend remains snappy while the FastAPI backend handles the heavy lifting of data scraping and price calculations.



### High-Level Components
1.  **Mobile Client:** The user interface for creating lists, viewing store comparisons, and tracking savings history.
2.  **FastAPI Backend:** A high-performance Python API that manages user accounts, processes shopping lists, and calculates price totals.
3.  **Data Provider/Scraper:** A specialized service that aggregates pricing data from various grocery retail APIs or web sources.
4.  **Database:** Stores user lists, historical price data, and "Savings Earned" metrics.

---
Data source:

- [] lidl: api | https://www.lidl.pt/q/api/search?assortment=PT&locale=pt_PT&version=v2.0.0
- [x] continente | webscrap (https://github.com/botclimber/groceryListGenerator)
- [x] pingo doce | webscrap
- [x] intermarche | tampermonkey script to download html + local html webscrapper to extract data (here they use DataDome security so by doing this we bypass them with style)
- [] mini preco
- [x] auchan
- [] mercadona (no online store in Portugal)

TODO:
- complete intermarche list
- check all data from all sources