const { invoke } = window.__TAURI__.core;
// 支店名データをJSONファイルからインポート --- (*1)
import branchNameMap from "./branch_names.json" with { type: "json" };
// チャート描画したかどうかを管理する変数 --- (*2)
let salesChart = null;
// 支店IDから支店名を取得する関数 --- (*3)
function branchNameFromId(branchId) {
  return branchNameMap[branchId] ?? branchId;
}
// 金額を日本円表記にフォーマットする関数 --- (*4)
function formatYen(value) {
  return new Intl.NumberFormat("ja-JP", {
    style: "currency",
    currency: "JPY",
    maximumFractionDigits: 0,
  }).format(value);
}
// 集計結果をテーブルに描画する関数 --- (*5)
function renderTable(rows, tbody) {
  tbody.innerHTML = "";
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${branchNameFromId(row.branch)}</td>
      <td>${formatYen(row.total_sales)}</td>
      <td>${row.transaction_count.toLocaleString("ja-JP")}</td>
    `;
    tbody.appendChild(tr);
  });
}
// 集計結果をチャートに描画する関数 --- (*6)
function renderChart(rows, canvas) {
  const labels = rows.map((row) => branchNameFromId(row.branch));
  const values = rows.map((row) => row.total_sales);

  // 2回目以降は既存チャートのデータだけ更新して崩れを防ぐ。
  if (salesChart) {
    salesChart.data.labels = labels;
    salesChart.data.datasets[0].data = values;
    salesChart.update();
    return;
  }

  // Chart.jsで棒グラフを描画する --- (*7)
  salesChart = new Chart(canvas, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "売上合計",
          data: values,
          backgroundColor: "rgba(42, 138, 97, 0.85)",
          borderColor: "rgba(30, 102, 72, 1)",
          borderWidth: 1,
          borderRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false, },
      },
    },
  });
}
// 初期化処理を行うイベント --- (*8)
window.addEventListener("DOMContentLoaded", () => {
  const loadBtn = document.querySelector("#load-btn");
  const statusMsg = document.querySelector("#status-msg");
  const resultBody = document.querySelector("#result-body");
  const chartCanvas = document.querySelector("#sales-chart-canvas");
  // レポートを読み込んで表示する関数 --- (*9)
  const loadReport = async () => {
    loadBtn.disabled = true;
    statusMsg.textContent = "CSVを読み込んでいます...";

    try {
      // Rustのコマンドを呼び出して集計レポートを取得する --- (*10)
      const report = await invoke("load_branch_sales");
      renderTable(report.rows, resultBody);
      renderChart(report.rows, chartCanvas);
      statusMsg.textContent = `${report.rows.length}支店の集計が完了しました。`;
    } catch (error) {
      statusMsg.textContent = `エラー: ${String(error)}`;
      resultBody.innerHTML = "";
      if (salesChart) {
        salesChart.destroy();
        salesChart = null;
      }
    } finally {
      loadBtn.disabled = false;
    }
  };
  loadBtn.addEventListener("click", loadReport);
  // 起動後に初回集計を行う。
  void loadReport();
});
