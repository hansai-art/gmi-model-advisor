# GMI 任務選模助手

依任務選擇 GMI Cloud 模型的 AI Skill。依任務查詢最新獨立評測，再與 GMI Cloud 的實際模型供應交叉比對，回答「這件事在 GMI 該用哪個精確 model ID」。不把 Combined 總榜當所有任務的答案。

## 安裝與使用

下載這個 repository，將 `skill/` 資料夾複製為 `gmi-model-advisor/`，放入你使用的 Agent Skills 相容工具之技能目錄。保留其中的 `SKILL.md`、`references/`、`scripts/` 與 `agents/` 相對位置。不同工具的技能目錄與安裝方式不同，請使用該工具支援的安裝流程。

也可讓有網頁查詢能力的助手讀取 `skill/SKILL.md` 與相關參考文件，再給它你的任務。Python 腳本是選用的離線檢查／證據蒐集工具；安裝 Skill 不需要先設定 API 金鑰。

安裝後可呼叫：

> 使用 GMI 任務選模助手，推薦今天適合 Python debug 的 GMI 模型。品質優先，兼顧成本。

也可以問：

- 我要讓 agent 使用工具完成多步任務，先看 tooling，再看 reasoning。
- 我寫繁中 FB 貼文，GMI 有哪些可驗證候選？不要用 Python 榜推論寫作冠軍。
- 比較目前 GMI 可用模型，列出精確 ID、來源時間、價格未知項目與限制。

助手負責即時研究與證據整理；使用者不必手填資料表或 JSON。沒有 API key 時仍可用公開評測和官方文件，並清楚區分「官方文件列載」與「帳號 catalog 已驗證」。正常推薦不會執行付費推論。

## 內容

- `skill/SKILL.md`：任務分流、查證、精確身份交集、建議格式
- `skill/references/`：官方來源、資料格式、排程限制
- `skill/scripts/check_evidence.py`：離線檢查新鮮度、版本、精確 ID、覆蓋與並列組
- `skill/scripts/collect_evidence.py`：經授權取得 ASL 三分榜與 GMI catalog 的私人原始快照
- `tests/`：合成資料單元測試，不含真實排行榜或金鑰
- `.github/workflows/ci.yml`：push / pull request 時執行離線單元測試與 CLI fixture 比對
- `.github/workflows/daily-evidence.yml`：預設未啟用的私人證據蒐集工作
- [TESTING.md](TESTING.md)：親自執行的測試、公開來源試用結果與尚未驗證的部分

## 「每天最新」的實際界線

Skill 安裝本身沒有常駐排程；預設每次使用時即時刷新。公開版只啟用不需要金鑰的離線 CI，不會啟用背景抓榜或執行認證 API。

附帶的 GitHub workflow 是「每日私人證據蒐集」，不是已完成的每日推薦服務。它不猜 ASL 尚未實測的分榜欄位，不自動將 `currentScore` 當 coding/reasoning/tooling 分數，不模糊配對 GMI 模型版本。

若要啟用證據蒐集，需自行在私人 GitHub repo 安全設定：

1. Secrets：現有 `GMI_API_KEY`、`ASL_API_KEY`。不要在聊天、程式碼或公開 repo 貼金鑰。
2. 確認 ASL 訂閱允許自動排程，才設定 repository variable `ASL_AUTOMATION_AUTHORIZED=true`；這是使用者明確聲明，不是自動驗證授權。
3. 設定 `ENABLE_DAILY_EVIDENCE=true`。workflow 僅允許私人 repo，預定每日 01:17 UTC，也可手動觸發；GitHub 排程可能延遲。
4. 第一次執行成功後檢查私人 artifact，確認實際 schema、分榜測量時間及模型版本。

若要「每天自動送出推薦」，還需另外設定經授權的助手排程：讀取上述私人證據、核對精確身份和任務條件、產生推薦並送到指定對話。這個部分尚未配置；證據蒐集成功不代表推薦已送出。若要對外發布評測資料或建立模型選擇服務，需另核對來源的商業／再散布授權。

## 測試與手動執行

Python 3.10+，無第三方套件。

```sh
python3 -m unittest discover -s tests -v
python3 skill/scripts/check_evidence.py /private/path/evidence.json --task coding
python3 skill/scripts/collect_evidence.py --out /private/path/snapshot.json
```

collector 只 GET 官方讀取端點，拒絕重定向，HTTP/schema/空資料錯誤即停止，不覆寫上次成功結果。原始快照預設不加入版本庫、不公開上傳。workflow artifact 供該私人 repo 有權限的人讀取，保留 3 日。

## 來源與限制

- [AI Stupid Level 榜單](https://aistupidlevel.info/) / [方法與範圍](https://aistupidlevel.info/faq) / [API 與使用條款](https://aistupidlevel.info/api-docs)
- [GMI 官方文件索引](https://docs.gmicloud.ai/llms.txt) / [MCP](https://docs.gmicloud.ai/mcp/gmi-mcp-server) / [API](https://docs.gmicloud.ai/inference-engine/api-reference/llm-api-reference) / [價格](https://docs.gmicloud.ai/inference-engine/billing/price)

ASL 資料需署名；API 自動更新需要合適方案，不可用免費 evaluation tier 建立定時抓榜。套件只提供研究流程與原創工具，不授予第三方資料使用權、不重製榜單。其他評測也有各自條款；不混加不同分數量尺。

文件入口核對日期：2026-10-06 UTC。資料與供應皆會改變，套件不保存靜態「今日冠軍」。
