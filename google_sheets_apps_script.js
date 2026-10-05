/**
 * =========================================================================
 * CampFind - Google Sheets 自動化補全工具 (Google Apps Script)
 * =========================================================================
 * 使用方式：
 * 1. 打開 Google 試算表（已匯入 campfind_all_camps.csv）
 * 2. 點擊頂部功能表：Extensions (擴充功能) > Apps Script
 * 3. 刪除原有代碼，將此腳本全部貼上並儲存 (Ctrl + S)
 * 4. 重新整理試算表頁面，上方會出現「🏕️ CampFind 工具」自訂選單！
 * 5. 點擊「🏕️ CampFind 工具」>「🤖 自動補全選取列的營隊資料」即可！
 * =========================================================================
 */

function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🏕️ CampFind 工具')
    .addItem('🤖 補全目前選取列的營隊資料 (自動爬取)', 'enrichSelectedRows')
    .addItem('📊 統計目前缺少欄位覆蓋率', 'calculateMissingStats')
    .addToUi();
}

/**
 * 補全選取列的營隊資料
 */
function enrichSelectedRows() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const range = sheet.getActiveRange();
  const startRow = range.getRow();
  const numRows = range.getNumRows();

  if (startRow === 1 && numRows === 1) {
    SpreadsheetApp.getUi().alert('請先反白選取要補全的營隊資料列（不含標題列）。');
    return;
  }

  // 取得標題列對應的欄位索引 (1-indexed)
  const headerRow = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  const colWebsite = headerRow.findIndex(h => h.includes('Official Website')) + 1;
  const colPrice = headerRow.findIndex(h => h.includes('Weekly Price')) + 1;
  const colPhone = headerRow.findIndex(h => h.includes('Phone')) + 1;
  const colMissing = headerRow.findIndex(h => h.includes('Missing Fields')) + 1;

  if (colWebsite === 0) {
    SpreadsheetApp.getUi().alert('找不到 Official Website 官方網站欄位，請確認試算表格式。');
    return;
  }

  let enrichedCount = 0;

  for (let r = 0; r < numRows; r++) {
    const currentRow = startRow + r;
    if (currentRow === 1) continue; // 跳過標題

    const website = sheet.getRange(currentRow, colWebsite).getValue();
    if (!website || typeof website !== 'string' || !website.startsWith('http')) {
      continue;
    }

    try {
      // 嘗試抓取該網址文字
      const response = UrlFetchApp.fetch(website, {
        muteHttpExceptions: true,
        headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' }
      });

      if (response.getResponseCode() === 200) {
        const html = response.getContentText();
        // 簡單抽取電話號碼正規比對
        const phoneMatch = html.match(/\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/);
        if (phoneMatch && colPhone > 0) {
          const currentPhone = sheet.getRange(currentRow, colPhone).getValue();
          if (!currentPhone) {
            sheet.getRange(currentRow, colPhone).setValue(phoneMatch[0]);
            sheet.getRange(currentRow, colPhone).setBackground('#E8F5E9'); // 標記淡綠色
            enrichedCount++;
          }
        }
      }
    } catch (e) {
      Logger.log('Error fetching ' + website + ': ' + e.message);
    }
  }

  SpreadsheetApp.getUi().alert(`處理完畢！成功補全了 ${enrichedCount} 個欄位（已用綠色標示）。`);
}

/**
 * 統計目前資料覆蓋率
 */
function calculateMissingStats() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const lastRow = sheet.getLastRow();
  SpreadsheetApp.getUi().alert(`目前共有 ${lastRow - 1} 筆營隊資料。可搭配 Python JEV 批次工具進行全面高速補全！`);
}
