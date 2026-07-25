如果今天有一支路由是 read_machine_by_code(machine_code: str)，是用機台的「自訂編號（例如 'M_EQ_05'）」來查單筆資料，請問這裡還能使用 await db.get(models.Machine, machine_code) 嗎？為什麼呢？

答案是：**不行（除非 `machine_code` 本身就是這張 Table 的 Primary Key 主鍵）**！

---

### 💡 核心原因拆解

1. **`db.get()` 是「主鍵專用砲」**：
`db.get()` 在 SQLAlchemy 的設計裡，**第一個參數吃模型（`models.Machine`），第二個參數只能傳入「主鍵（Primary Key）」的值**（例如自動遞增的 `id`）。
2. **如果 `machine_code` 只是普通的欄位（或是 Unique 欄位）**：
當你要用「非主鍵欄位」做條件查詢時，`db.get()` 就派不上用場了。這時候就要**回歸使用我們之前寫的標準 `select()` 語法**：
```python
# 🎯 用非主鍵（如 machine_code）查詢單筆資料的標準寫法
stmt = select(models.Machine).filter(models.Machine.machine_code == machine_code)
result = await db.execute(stmt)
db_machine = result.scalar_one_or_none()

### 🏆 觀念大彙整（點頭記起來）

* **用 `id` (Primary Key) 查單筆** ➡️ 毫不猶豫用 **`await db.get(models.Machine, machine_id)`**（極簡、效能最佳、帶快取）。
* **用其他欄位查單筆 / 查多筆 / 帶條件 / 帶排序** ➡️ 乖乖使用 **`select(...)` + `await db.execute(...)**`。

你現在對 SQLAlchemy 2.0 AsyncSession 的掌控度已經非常高了，連這種主鍵與一般欄位查詢的界線都弄得清清楚楚！

今天 `fastapi-test` repo 的重構大成功！有什麼其他想測試的路由或觀念，隨時再來跟老師討論！今天辛苦啦！