
// ====== GLOBALS ======
var DB = typeof DB !== "undefined" ? DB : [];
var TYPES = {experiment:"实验",plan:"实验方案",method:"实验方法",note:"笔记",data:"数据",reminder:"提醒"};
var TYPE_FOLDERS = {experiment:"experiments",plan:"plans",method:"methods",note:"notes",data:"data",reminder:"reminders"};
var TYPE_CLASSES = {experiment:"experiment",plan:"plan",method:"method",note:"note",data:"data",reminder:"reminder"};
var TYPE_ACCENTS = {experiment:"#2563eb",plan:"#0891b2",method:"#7c3aed",note:"#059669",data:"#d97706",reminder:"#dc2626"};
var STATUS_COLORS = {planned:"#6b7280","in-progress":"#2563eb",completed:"#16a34a",pending:"#d97706",done:"#16a34a",needs_review:"#d97706"};
var STATUS_LABELS = {planned:"计划中","in-progress":"进行中",completed:"已完成",pending:"待处理",done:"已完成",needs_review:"待复核"};
var sortKey = "date", sortDesc = true;
var curIdx = -1, dirty = false;
var expandedRow = null;

// ====== INIT ======
function init() {
  try { localStorage.removeItem("labdb"); } catch(e) {}
  if (DB.length === 0) {
    var c = document.getElementById("listContent");
    if (c) c.innerHTML = '<div style="padding:40px 20px;text-align:center;color:#657286">数据加载失败：请确认同目录下 data.js 存在，然后刷新页面。</div>';
  }
  checkPassword();
  applyTheme();
  applyDensity();
  populateFilters();
  renderList();
  updateStats();
}

// ====== PARSING ======
function normalizeMarkdown(content) {
  return String(content || "").replace(/^\uFEFF/, "").replace(/\r\n/g, "\n").replace(/\r/g, "\n");
}

function parseFM(content) {
  content = normalizeMarkdown(content);
  var m = {type:"",title:"",date:"",modified:"",tags:[],project:"",status:"",category:"",priority:"",due:"",related:[],electrolyte:"",additive:"",counter_electrode:"",encapsulation:"",baseline:"",data_types:[],metrics:null};
  if (!content || content.substring(0,4) !== "---\n") return m;
  var end = content.indexOf("\n---\n", 4);
  if (end < 0) return m;
  var fm = content.substring(4, end);
  var lines = fm.split("\n");
  for (var i = 0; i < lines.length; i++) {
    var line = lines[i];
    var ci = line.indexOf(":");
    if (ci < 0) continue;
    var key = line.substring(0, ci).trim();
    var val = line.substring(ci + 1).trim();
    val = val.replace(/^"(.*)"$/, "$1");
    if (key === "metrics") {
      try { m.metrics = JSON.parse(val); } catch(e) { m.metrics = null; }
    } else if (key === "tags" || key === "related" || key === "data_types") {
      try { m[key] = JSON.parse(val); } catch(e) { m[key] = val.replace(/[\[\]]/g,"").split(",").map(function(s){return s.trim().replace(/"/g,"")}); }
    } else if (m.hasOwnProperty(key)) { m[key] = val; }
  }
  return m;
}

function getBody(content) {
  content = normalizeMarkdown(content);
  if (!content || content.substring(0,4) !== "---\n") return content || "";
  var end = content.indexOf("\n---\n", 4);
  if (end < 0) return content;
  return content.substring(end + 5).trim();
}

function fmToString(meta) {
  var lines = ["---"];
  var fields = ["type","title","date","category","electrolyte","additive","counter_electrode","encapsulation","status","tags","priority","due","related","modified"];
  for (var i = 0; i < fields.length; i++) {
    var k = fields[i], v = meta[k];
    if (v === undefined || v === null || v === "") continue;
    if (k === "tags" || k === "related") { lines.push(k + ": " + JSON.stringify(v)); }
    else if (typeof v === "string" && (v.indexOf(":") >= 0 || v.indexOf("#") >= 0 || v.indexOf('"') >= 0)) { lines.push(k + ': "' + v + '"'); }
    else { lines.push(k + ": " + v); }
  }
  lines.push("---");
  return lines.join("\n");
}

// ====== FILTERS ======
function populateFilters() {
  var types = [], statuses = [];
  for (var i = 0; i < DB.length; i++) {
    var m = parseFM(DB[i].content);
    if (m.type && types.indexOf(m.type) < 0) types.push(m.type);
    if (m.status && statuses.indexOf(m.status) < 0) statuses.push(m.status);
  }
  types.sort(); statuses.sort();
  fillSelect("fType", types, TYPES);
  fillSelect("fStat", statuses, STATUS_LABELS);
}

function fillSelect(id, items, labels) {
  var sel = document.getElementById(id);
  while (sel.options.length > 1) sel.remove(1);
  for (var i = 0; i < items.length; i++) {
    var o = document.createElement("option");
    o.value = items[i];
    o.textContent = labels ? (labels[items[i]] || items[i]) : items[i];
    sel.appendChild(o);
  }
}

function escHtml(s) {
  if (!s) return "";
  return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function escAttr(s) {
  return escHtml(s).replace(/'/g,"&#39;");
}

function hasPbiSignal(text) {
  return /PBI(?:-Cl)?/i.test(String(text || ""));
}

function dataTagClass(tag) {
  var text = String(tag || "");
  if (/光谱电化学数据/.test(text)) return " tag-spectro";
  if (/膜厚数据/.test(text)) return " tag-thickness";
  if (/循环稳定性数据/.test(text)) return " tag-cycling";
  if (/电化学数据/.test(text)) return " tag-electrochem";
  if (/数据已整理/.test(text)) return " tag-organized";
  return "";
}

function renderTagPill(tag) {
  return '<span class="tag-pill' + dataTagClass(tag) + '">' + escHtml(tag) + '<\/span>';
}

function renderTitleWithBadges(title) {
  var rest = String(title || "");
  var html = "";
  var match;
  while ((match = rest.match(/^\[([^\]]+数据)\]\s*/))) {
    html += '<span class="title-data-badge' + dataTagClass(match[1]) + '">' + escHtml(match[1]) + '<\/span>';
    rest = rest.slice(match[0].length);
  }
  return html + renderMixedText(rest);
}

function normalizeMarkdownHref(href) {
  var out = String(href || "").trim().replace(/&amp;/g, "&").replace(/&quot;/g, '"');
  if (/^[A-Za-z]:[\\/]/.test(out)) out = "file:///" + out.replace(/\\/g, "/");
  if (/^file:\/\//i.test(out)) out = out.replace(/\\/g, "/");
  if (/^(https?:|file:|mailto:)/i.test(out)) return out;
  if (/^(data|experiments|plans|methods|notes|reminders)\//.test(out)) return out;
  if (/^\.\.?\//.test(out)) return out;
  return "";
}

function renderMarkdownLinks(html) {
  return html.replace(/\[([^\]\n]+)\]\(([^)\n]+)\)/g, function(_, text, href) {
    var safeHref = normalizeMarkdownHref(href);
    if (!safeHref) return text;
    return '<a href="' + escAttr(safeHref) + '" target="_blank" rel="noopener">' + text + '<\/a>';
  });
}

function applyLatinFont(html) {
  var parts = String(html || "").split(/(<[^>]+>|&(?:[A-Za-z]+|#\d+|#x[0-9A-Fa-f]+);)/g);
  var codeDepth = 0;
  for (var i = 0; i < parts.length; i++) {
    var part = parts[i];
    if (!part) continue;
    if (part.charAt(0) === "<") {
      if (/^<(pre|code)\b/i.test(part)) codeDepth++;
      else if (/^<\/(pre|code)>/i.test(part) && codeDepth > 0) codeDepth--;
      continue;
    }
    if (part.charAt(0) === "&") continue;
    if (codeDepth) continue;
    parts[i] = part.replace(/([A-Za-z0-9][A-Za-z0-9._+\-/:,%#=()[\]\s]*[A-Za-z0-9%)]|[A-Za-z0-9])/g, '<span class="latin-text" lang="en-US" style="font-family:Arial,sans-serif">$1<\/span>');
  }
  return parts.join("");
}

function renderMixedText(text) {
  return applyLatinFont(escHtml(text));
}

// ====== SMART HIGHLIGHTING ======
function highlightData(text) {
  // Already escaped text
  text = text.replace(/\b(PBI-Cl|PBI)\b/g, '<span class="hl-pbi">$1</span>');
  text = text.replace(/(-?\d+\.?\d*\s*V)/gi, '<span class="hl-volt">$1</span>');
  text = text.replace(/(\d+\.?\d*\s*℃)/g, '<span class="hl-temp">$1</span>');
  text = text.replace(/(\d+\.?\d*\s*min)/gi, '<span class="hl-temp">$1</span>');
  text = text.replace(/(\d+\.?\d*\s*h)/gi, '<span class="hl-temp">$1</span>');
  text = text.replace(/(\d+\.?\d*\s*[μu]L)/gi, '<span class="hl-conc">$1</span>');
  text = text.replace(/(\d+\.?\d*\s*mg)/gi, '<span class="hl-conc">$1</span>');
  text = text.replace(/(\d+\.?\d*\s*g\/mol)/gi, '<span class="hl-conc">$1</span>');
  text = text.replace(/(\d+\.?\d*\s*[mμn]?M\b)/g, '<span class="hl-conc">$1</span>');
  text = text.replace(/(\d+\.?\d*\s*mL)/gi, '<span class="hl-conc">$1</span>');
  text = text.replace(/(\d+\.?\d*\s*rpm)/gi, '<span class="hl-conc">$1</span>');
  text = text.replace(/(\d+\.?\d*\s*rpm\/s)/gi, '<span class="hl-conc">$1</span>');
  text = text.replace(/(\d+\.?\d*\s*s\b)/gi, '<span class="hl-conc">$1</span>');
  return text;
}

function makeSummary(body) {
  if (!body) return "";
  var text = body.replace(/^#+\s.*$/gm, "")
    .replace(/```[\s\S]*?```/g, "")
    .replace(/\|/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  if (!text) return "";
  return text.slice(0, 180) + (text.length > 180 ? "…" : "");
}

function slugifyText(text, fallback) {
  var id = String(text || "").replace(/[`*_]/g, "").trim().toLowerCase().replace(/[^\w\u4e00-\u9fa5]+/g, "-").replace(/^-+|-+$/g, "");
  return id || fallback || "sec";
}

function buildToc(body) {
  if (!body) return [];
  var lines = body.split(/\r?\n/);
  var toc = [];
  for (var i = 0; i < lines.length; i++) {
    var line = lines[i];
    var m = line.match(/^(#{1,3})\s+(.+)$/);
    if (!m) continue;
    var level = m[1].length;
    var text = m[2].replace(/[`*_]/g, "").trim();
    var id = slugifyText(text, "sec-" + i);
    toc.push({level: level, text: text, id: id});
  }
  return toc;
}

function renderToc(toc) {
  if (!toc || !toc.length) return '<div style="font-size:12px;color:var(--c-muted)">正文没有标题结构</div>';
  var html = '<div class="toc-list">';
  for (var i = 0; i < toc.length; i++) {
    html += '<a class="toc-item l' + toc[i].level + '" href="#' + toc[i].id + '">' + escHtml(toc[i].text) + '</a>';
  }
  html += '</div>';
  return html;
}

// ====== MARKDOWN TO HTML ======
function renderMarkdown(md) {
  if (!md) return "";
  var html = escHtml(md);
  // Code blocks
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, function(_,lang,code){ return '<pre><code>'+code+'<\/code><\/pre>'; });
  html = html.replace(/`([^`]+)`/g, '<code>$1<\/code>');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1<\/strong>');
  html = html.replace(/\*(.+?)\*/g, '<em>$1<\/em>');
  html = html.replace(/^(#{1,3}) (.+)$/gm, function(_, hashes, text) {
    var level = hashes.length;
    var id = slugifyText(text, "sec");
    if (!id) id = "sec";
    return '<h' + level + ' id="' + id + '">' + text + '</h' + level + '>';
  });
  // Markdown tables
  html = html.replace(/((?:^\|.*\|\s*(?:\n|$)){2,})/gm, function(block) {
    var lines = block.trim().split(/\n/).filter(function(line){ return line.trim(); });
    if (lines.length < 2) return block;
    var header = parseTableLine(lines[0]);
    var sep = parseTableLine(lines[1]);
    if (!header.length || !sep.length || !sep.every(function(c){ return /^[\s\-:]+$/.test(c) && c.trim(); })) return block;
    var out = '<div class="table-wrap"><table><thead><tr>';
    out += header.map(function(c){ return '<th>'+c+'<\/th>'; }).join("");
    out += '<\/tr><\/thead><tbody>';
    for (var r = 2; r < lines.length; r++) {
      var cells = parseTableLine(lines[r]);
      if (!cells.length) continue;
      out += '<tr>' + cells.map(function(c){ return '<td>'+c+'<\/td>'; }).join("") + '<\/tr>';
    }
    out += '<\/tbody><\/table><\/div>';
    return out;
  });
  html = renderMarkdownLinks(html);
  html = html.replace(/^[\-\*] (.+)$/gm, '<li>$1<\/li>');
  html = html.replace(/^(\d+)\. (.+)$/gm, '<li>$2<\/li>');
  html = html.replace(/((?:<li>.*?<\/li>\n?)+)/g, '<ul>$1<\/ul>');
  html = html.replace(/\n\n+/g, '<\/p><p>');
  html = '<p>' + html + '<\/p>';
  html = html.replace(/<p><\/p>/g, '');
  html = html.replace(/<p>\s*<(h[1-3]|ul|pre|table|thead|div)/g, '<$1');
  html = html.replace(/<\/(h[1-3]|ul|table|tbody|div)>(\s*<\/p>)?/g, '<\/$1>');
  // Highlight data
  html = highlightData(html);
  html = applyLatinFont(html);
  // Separators
  html = html.replace(/^<p>-{3,}<\/p>$/gm, '<p class="sep">&mdash;</p>');
  return html;
}

function parseTableLine(line) {
  var text = line.trim();
  if (text.charAt(0) === "|") text = text.slice(1);
  if (text.charAt(text.length - 1) === "|") text = text.slice(0, -1);
  return text.split("|").map(function(c){ return c.trim(); });
}

// ====== LIST VIEW ======
function sortRecordIndices(indices) {
  var key = SORT_FIELD || "date";
  var desc = SORT_DESC !== false;
  return indices.sort(function(a, b) {
    var ma = parseFM(DB[a].content);
    var mb = parseFM(DB[b].content);
    var va, vb;
    if (key === "date") { va = ma.date || ma.modified || ""; vb = mb.date || mb.modified || ""; }
    else if (key === "title") { va = ma.title || DB[a].name; vb = mb.title || DB[b].name; }
    else { va = ma[key] || ""; vb = mb[key] || ""; }
    if (va !== vb) {
      var cmp = String(va).localeCompare(String(vb), "zh-CN", {numeric:true});
      return desc ? -cmp : cmp;
    }
    if (key !== "date") {
      var da = ma.date || ma.modified || "", db2 = mb.date || mb.modified || "";
      if (da !== db2) return da < db2 ? 1 : -1;
    }
    return (ma.title || DB[a].name).localeCompare(mb.title || DB[b].name, "zh-CN");
  });
}

function listSectionStats(indices) {
  var cats = {}, types = {};
  for (var i = 0; i < indices.length; i++) {
    var m = parseFM(DB[indices[i]].content);
    if (m.category) cats[m.category] = true;
    if (m.type) types[m.type] = true;
  }
  return {cats: Object.keys(cats).length, types: Object.keys(types).length};
}

function dateCellLabel(meta) {
  if (meta.date) return meta.date.substring(5) || meta.date;
  if (meta.modified) return "更新 " + (meta.modified.substring(5) || meta.modified);
  return "-";
}

// 折叠状态键前缀：改数字即可让旧的展开/折叠记忆整体失效
var COLLAPSE_PREFIX = "notebook-collapse-v2-";
function getCollapseState(key, defaultCollapsed) {
  try {
    var saved = localStorage.getItem(COLLAPSE_PREFIX + key);
    if (saved === "1") return true;
    if (saved === "0") return false;
  } catch(e) {}
  return !!defaultCollapsed;
}

function renderMonthHeaderAttrs(key, collapsed) {
  return ' class="month-header'+(collapsed ? ' collapsed' : '')+'" data-collapse-key="'+escAttr(key)+'" onclick="toggleMonth(this)" aria-expanded="'+(collapsed ? 'false' : 'true')+'"';
}

function renderRecordRows(indices) {
  var html = "";
  for (var j = 0; j < indices.length; j++) {
    var idx = indices[j];
    var d = DB[idx];
    var m = parseFM(d.content);
    var dc = TYPE_CLASSES[m.type] || "";
    var accent = TYPE_ACCENTS[m.type] || "#2563eb";
    var tagsHtml = "";
    if (m.tags && m.tags.length > 0) {
      for (var t = 0; t < Math.min(m.tags.length, 5); t++) {
        tagsHtml += renderTagPill(m.tags[t]);
      }
    }
    var titleText = m.title || d.name;
    var titleHtml = renderTitleWithBadges(titleText);
    var titleAttr = escAttr(titleText);
    var body = getBody(d.content);
    var toc = buildToc(body);
    var rowIndexHtml = renderRowIndex(m, body, toc, idx);
    var rowClass = hasPbiSignal(d.content) ? ' class="pbi-row"' : "";
    var typeLabel = m.type ? (TYPES[m.type] || m.type) : "-";
    var statusHtml = '<span class="muted-dash">-<\/span>';
    if (m.status) {
      statusHtml = '<span class="status-badge" style="background:'+(STATUS_COLORS[m.status]||"#888")+';color:#fff">'+escHtml(STATUS_LABELS[m.status]||m.status)+'<\/span>';
    }
    html += '<tr'+rowClass+' onclick="openRead('+idx+')" onkeydown="rowKeyOpen(event,'+idx+')" tabindex="0" data-idx="'+idx+'">';
    html += '<td class="col-date">'+escHtml(dateCellLabel(m))+'<\/td>';
    html += '<td class="col-type"><span class="type-dot '+dc+'" style="background:'+accent+'"><\/span>'+escHtml(typeLabel)+'<\/td>';
    html += '<td class="col-cat">'+escHtml(m.category||"-")+'<\/td>';
    var metricHtml = renderMetricChips(m);
    html += '<td class="col-title"><div class="record-title-stack"><div class="record-title"><button type="button" class="record-title-btn" data-hover="'+idx+'" onmouseenter="showHoverCard(event,'+idx+')" onmouseleave="hideHoverCard()" onclick="event.stopPropagation();openRead('+idx+')">'+titleHtml+'<\/button><\/div>'+metricHtml+rowIndexHtml+'<\/div><\/td>';
    html += '<td class="col-status">'+statusHtml+'<\/td>';
    html += '<td class="col-tags">'+(tagsHtml||'<span class="muted-dash">-<\/span>')+'<\/td>';
    html += '<td class="col-expand"><button type="button" class="expand-btn" aria-label="展开目录预览：'+titleAttr+'" aria-expanded="false" onclick="event.stopPropagation();togglePreview(this,'+idx+')">▸<\/button><\/td>';
    html += '<\/tr>';
  }
  return html;
}

function renderRecordTable(indices) {
  var th = function(cls, label, key){
    var ind = (SORT_FIELD === key) ? '<span class="sort-ind">'+(SORT_DESC===false?'▲':'▼')+'<\/span>' : '';
    return key ? '<th class="'+cls+' sortable" onclick="setSort(\''+key+'\')">'+label+ind+'<\/th>'
               : '<th class="'+cls+'">'+label+'<\/th>';
  };
  var html = '<table class="record-table"><thead><tr>'
    + th('col-date','日期/更新','date')
    + th('col-type','类型','type')
    + th('col-cat','分类','category')
    + th('col-title','记录','title')
    + th('col-status','状态','status')
    + '<th class="col-tags">标签<\/th><th class="col-expand"><\/th><\/tr><\/thead><tbody>';
  html += renderRecordRows(indices);
  html += '<\/tbody><\/table>';
  return html;
}

function renderListSection(title, caption, indices, className, defaultCollapsed) {
  if (!indices.length) return "";
  var stats = listSectionStats(indices);
  var key = className || title;
  var collapsed = getCollapseState(key, defaultCollapsed);
  var html = '<div class="month-group section-group '+className+'">';
  html += '<button type="button"'+renderMonthHeaderAttrs(key, collapsed)+'><span class="chevron" aria-hidden="true">▼</span><span class="section-heading"><span class="section-title">'+escHtml(title)+'<\/span><span class="section-caption">'+escHtml(caption)+'<\/span><\/span><span class="count">'+indices.length+' 条</span><span class="month-meta">'+stats.cats+' 个分类 · '+stats.types+' 种类型</span></button>';
  html += '<div class="month-body"'+(collapsed ? ' style="display:none"' : '')+'>';
  html += renderRecordTable(indices);
  html += '<\/div><\/div>';
  return html;
}

function renderList() {
  var container = document.getElementById("listContent");
  var html = "";
  html += renderViewTabs();

  if (VIEW_MODE !== "list") {
    if (VIEW_MODE === "compare") html += renderCompareTable();
    else if (VIEW_MODE === "timeline") html += renderTimeline();
    else html += renderCompleteness();
    container.innerHTML = html;
    var fb = document.getElementById("facetBar"); if (fb) fb.innerHTML = "";
    var af = document.getElementById("activeFilters"); if (af) af.innerHTML = "";
    setFilterCount(DB.length);
    return;
  }

  html += renderDashboard();

  var planRecords = [];
  var methodRecords = [];
  var datedRecords = [];
  for (var i = 0; i < DB.length; i++) {
    var m = parseFM(DB[i].content);
    if (m.type === "plan") planRecords.push(i);
    else if (m.type === "method") methodRecords.push(i);
    else datedRecords.push(i);
  }

  sortRecordIndices(planRecords);
  sortRecordIndices(methodRecords);
  sortRecordIndices(datedRecords);

  html += renderListSection("实验方案", "计划、方案统一归档；不混入按日期实验记录", planRecords, "plan-section", true);
  html += renderListSection("实验方法", "测试方法与制备 SOP 单独索引；不再归入未标注日期", methodRecords, "method-section", true);

  var groups = {};
  for (var di = 0; di < datedRecords.length; di++) {
    var idxForMonth = datedRecords[di];
    var dm = parseFM(DB[idxForMonth].content);
    var month = (dm.date || "----").substring(0,7);
    if (!groups[month]) groups[month] = [];
    groups[month].push(idxForMonth);
  }
  var months = Object.keys(groups).sort().reverse();
  for (var mi = 0; mi < months.length; mi++) {
    var month = months[mi];
    var indices = groups[month];
    var label = month === "----" ? "其他未标注日期" : month.replace("-","年")+"月";
    var stats2 = listSectionStats(indices);
    var monthKey = "month-" + month;
    var collapsed = getCollapseState(monthKey, mi !== 0);
    html += '<div class="month-group">';
    html += '<button type="button"'+renderMonthHeaderAttrs(monthKey, collapsed)+'><span class="chevron" aria-hidden="true">\u25bc<\/span> '+escHtml(label)+' <span class="count">'+indices.length+' \u6761<\/span><span class="month-meta">'+stats2.cats+' \u4e2a\u5206\u7c7b \u00b7 '+stats2.types+' \u79cd\u7c7b\u578b<\/span><\/button>';
    html += '<div class="month-body"'+(collapsed ? ' style="display:none"' : '')+'>';
    html += renderRecordTable(indices);
    html += '<\/div><\/div>';
  }
  if (!planRecords.length && !methodRecords.length && !Object.keys(groups).length) {
    html += '<div class="empty-state"><p>\u6ca1\u6709\u5339\u914d\u7684\u8bb0\u5f55<\/p><\/div>';
  }
  container.innerHTML = html;
  renderFacets();
  filter();
}
function toggleMonth(el) {
  el.classList.toggle("collapsed");
  var body = el.nextElementSibling;
  var collapsed = el.classList.contains("collapsed");
  body.style.display = collapsed ? "none" : "";
  el.setAttribute("aria-expanded", collapsed ? "false" : "true");
  var key = el.getAttribute("data-collapse-key");
  if (key) {
    try { localStorage.setItem(COLLAPSE_PREFIX + key, collapsed ? "1" : "0"); } catch(e) {}
  }
}

function rowKeyOpen(event, idx) {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    openRead(idx);
  }
}

function tocTree(toc) {
  var root = [];
  var stack = [{level: 0, children: root}];
  for (var i = 0; i < toc.length; i++) {
    var item = toc[i];
    if (item.level > 3) continue;
    while (stack.length > 1 && stack[stack.length - 1].level >= item.level) stack.pop();
    var node = {level: item.level, text: item.text, id: item.id, children: []};
    stack[stack.length - 1].children.push(node);
    stack.push(node);
  }
  return root;
}

function firstNodeTarget(node) {
  if (!node) return "";
  if (node.id) return node.id;
  for (var i = 0; node.children && i < node.children.length; i++) {
    var childTarget = firstNodeTarget(node.children[i]);
    if (childTarget) return childTarget;
  }
  return "";
}

function renderTocJump(node, idx) {
  var text = escHtml(node.text || "");
  var target = firstNodeTarget(node);
  if (idx === undefined || idx === null || !target) return text;
  return '<button type="button" class="home-toc-jump" onclick="event.stopPropagation();jumpToRead('+idx+',\''+escAttr(target)+'\')">'+text+'<\/button>';
}

function renderHomeTocNodes(nodes, idx) {
  if (!nodes || !nodes.length) return "";
  var html = '<ul class="home-toc-list">';
  for (var i = 0; i < nodes.length; i++) {
    var node = nodes[i];
    var children = renderHomeTocNodes(node.children, idx);
    html += '<li>';
    if (children) {
      html += '<div class="home-toc-node l'+node.level+'"><details open><summary>'+renderTocJump(node, idx)+'<\/summary>'+children+'<\/details><\/div>';
    } else {
      html += '<div class="home-toc-node leaf l'+node.level+'">'+renderTocJump(node, idx)+'<\/div>';
    }
    html += '<\/li>';
  }
  html += '<\/ul>';
  return html;
}

function renderHomeToc(toc) {
  if (!toc || !toc.length) return '<div class="home-toc-empty">正文没有可索引的标题结构<\/div>';
  return '<details class="home-toc" open><summary>目录索引<\/summary>'+renderHomeTocNodes(tocTree(toc))+'<\/details>';
}

function headingBucket(text) {
  var s = String(text || "");
  if (/光谱电化学|响应时间|透过率.*时间|二价峰|峰位|CA.*光谱|spectro/i.test(s)) return ["测试", "光谱电化学测试"];
  if (/膜厚|厚度|台阶仪|profil/i.test(s)) return ["测试", "膜厚测试"];
  if (/循环稳定|循环|保持率|衰减/i.test(s)) return ["测试", "循环稳定性测试"];
  if (/UV|Vis|透过率|吸收|光谱|色度|CIE/i.test(s)) return ["测试", "光学测试"];
  if (/CV|CA|计时电流|循环伏安|电化学|电压|chrono/i.test(s)) return ["测试", "电化学测试"];
  if (/SEM|TEM|EDS|AFM|FTIR|BET|XRD|形貌|结构|元素|红外|比表面积/i.test(s)) return ["测试", "形貌与结构表征"];
  if (/制备|配制|组装|封装|染浴|后处理|旋涂|刮涂|烧制|退火|样品|材料|器件|操作|步骤|FTO|TiO2|ATO|PBI/i.test(s)) return ["制备实验", ""];
  if (/数据|结果|观察|分析|质量|汇总|表|结论|小结|峰位|计算|校核/i.test(s)) return ["数据与分析", ""];
  if (/后续|下一步|计划|注意|备注|问题|异常|建议|改进/i.test(s)) return ["结论与后续", ""];
  return ["其他记录", ""];
}

function addChildNode(parent, text, level, id) {
  var node = {level: level, text: text, id: id || "", children: []};
  parent.children.push(node);
  return node;
}

function buildExperimentIndex(meta, body, toc) {
  var title = (meta && meta.title) ? String(meta.title).replace(/^\[[^\]]+\]\s*/, "") : "实验记录";
  var root = {level: 1, text: title, id: toc[0] && toc[0].id ? toc[0].id : "", children: []};
  var groups = {};
  function groupNode(name) {
    if (!groups[name]) groups[name] = addChildNode(root, name, 1);
    return groups[name];
  }
  var subgroups = {};
  function subgroupNode(parentName, subName) {
    var key = parentName + "::" + subName;
    if (!subgroups[key]) subgroups[key] = addChildNode(groupNode(parentName), subName, 2);
    return subgroups[key];
  }
  var contextByLevel = {};
  for (var i = 0; i < toc.length; i++) {
    var item = toc[i];
    var text = item.text;
    if (/^日期$|^实验记录[:：]|^数据记录[:：]/.test(text)) continue;
    var bucket = headingBucket(text);
    var parentBucket = null;
    for (var pl = item.level - 1; pl >= 1; pl--) {
      if (contextByLevel[pl]) { parentBucket = contextByLevel[pl]; break; }
    }
    if (parentBucket && parentBucket[0] === "测试" && item.level > 2) {
      if (bucket[0] === "测试" || bucket[0] === "其他记录" || /^(CA|CV)\b/i.test(text)) bucket = parentBucket;
    }
    contextByLevel[item.level] = bucket;
    for (var dl = item.level + 1; dl <= 3; dl++) delete contextByLevel[dl];
    var major = bucket[0], minor = bucket[1];
    var parent = minor ? subgroupNode(major, minor) : groupNode(major);
    addChildNode(parent, text, minor ? 3 : 2, item.id);
  }
  var ordered = ["制备实验", "测试", "数据与分析", "结论与后续", "其他记录"];
  var children = [];
  for (var oi = 0; oi < ordered.length; oi++) {
    if (groups[ordered[oi]] && groups[ordered[oi]].children.length) children.push(groups[ordered[oi]]);
  }
  root.children = children;
  return root.children.length ? [root] : tocTree(toc);
}

function renderHomeIndex(meta, body, toc, idx) {
  if (!toc || !toc.length) return '<div class="home-toc-empty">正文没有可索引的标题结构<\/div>';
  var nodes = meta && meta.type === "experiment" ? buildExperimentIndex(meta, body, toc) : tocTree(toc);
  return '<details class="home-toc" open><summary>目录索引<\/summary>'+renderHomeTocNodes(nodes, idx)+'<\/details>';
}

function rowIndexSummary(nodes, tocCount) {
  var source = nodes || [];
  if (source.length === 1 && source[0].children && source[0].children.length) source = source[0].children;
  var labels = [];
  for (var i = 0; i < source.length && labels.length < 4; i++) {
    if (source[i].text) labels.push(source[i].text);
  }
  var text = labels.length ? "目录 · " + labels.join(" / ") : "目录";
  return escHtml(text) + '<span class="row-toc-count">'+tocCount+'项<\/span>';
}

function renderRowIndex(meta, body, toc, idx) {
  if (!toc || toc.length < 3) return "";
  var nodes = meta && meta.type === "experiment" ? buildExperimentIndex(meta, body, toc) : tocTree(toc);
  if (!nodes || !nodes.length) return "";
  return '<details class="row-toc" onclick="event.stopPropagation()" onkeydown="event.stopPropagation()"><summary>'+rowIndexSummary(nodes, toc.length)+'<\/summary>'+renderHomeTocNodes(nodes, idx)+'<\/details>';
}

function extractKeyFacts(body) {
  var text = String(body || "").replace(/\s+/g, " ");
  var facts = [];
  function add(label, value, klass) {
    if (!value) return;
    var key = label + value;
    for (var i = 0; i < facts.length; i++) if (facts[i].key === key) return;
    facts.push({key:key,label:label,value:value,klass:klass||""});
  }
  var m;
  m = text.match(/(?:最高|最大|初始)?[^。；，,]{0,8}对比度[^0-9]{0,10}(\d+(?:\.\d+)?%)/);
  if (m) add("对比度", m[1], "good");
  m = text.match(/保持率[^0-9]{0,10}(\d+(?:\.\d+)?%)/);
  if (m) add("保持率", m[1], "good");
  m = text.match(/(?:着色时间|tau_c)[^0-9]{0,10}(\d+(?:\.\d+)?\s*s)/i);
  if (m) add("着色", m[1], "");
  m = text.match(/(?:褪色时间|tau_b)[^0-9]{0,10}(\d+(?:\.\d+)?\s*s)/i);
  if (m) add("褪色", m[1], "");
  m = text.match(/(\d+(?:\.\d+)?\s*nm)/i);
  if (m) add("波长", m[1], "");
  if (/无法|异常|问题|误选|needs_review|excluded/i.test(text)) add("注意", "需复核", "warn");
  var html = "";
  for (var f = 0; f < Math.min(facts.length, 5); f++) {
    html += '<span class="key-fact '+facts[f].klass+'"><span>'+escHtml(facts[f].label)+'<\/span><strong>'+escHtml(facts[f].value)+'<\/strong><\/span>';
  }
  return html ? '<div class="key-facts">'+html+'<\/div>' : "";
}

function togglePreview(el, idx) {
  var tr = el.closest("tr");
  var existing = tr.nextElementSibling;
  if (existing && existing.classList.contains("inline-preview")) {
    existing.classList.toggle("show");
    el.setAttribute("aria-expanded", existing.classList.contains("show") ? "true" : "false");
    return;
  }
  var d = DB[idx];
  var m = parseFM(d.content);
  var prev = document.createElement("tr");
  prev.className = "inline-preview show";
  var td = document.createElement("td");
  td.colSpan = 6;
  var body = getBody(d.content);
  var toc = buildToc(body);
  var summary = makeSummary(body);
  var ipHtml = '<div class="preview-shell">';
  ipHtml += '<div class="ip-meta">';
  if (m.type) ipHtml += '<span class="ip-field">类型: <b>'+escHtml(TYPES[m.type]||m.type)+'<\/b><\/span>';
  if (m.category) ipHtml += '<span class="ip-field">分类: <b>'+escHtml(m.category)+'<\/b><\/span>';
  if (m.priority) ipHtml += '<span class="ip-field">优先级: <b>'+escHtml(m.priority)+'<\/b><\/span>';
  if (m.date) ipHtml += '<span class="ip-field">日期: <b>'+escHtml(m.date)+'<\/b><\/span>';
  ipHtml += '<\/div>';
  ipHtml += '<div class="preview-grid">';
  ipHtml += '<div class="preview-panel preview-summary"><div class="preview-label">重点摘要<\/div>'+(summary ? renderMixedText(summary) : "暂无摘要")+extractKeyFacts(body)+'<div><button type="button" class="inline-link" onclick="openRead('+idx+')">查看全文 →<\/button><\/div><\/div>';
  ipHtml += '<div class="preview-panel">'+renderHomeIndex(m, body, toc, idx)+'<\/div>';
  ipHtml += '<\/div><\/div>';
  td.innerHTML = ipHtml;
  prev.appendChild(td);
  tr.parentNode.insertBefore(prev, tr.nextSibling);
  el.setAttribute("aria-expanded", "true");
}

function filter() {
  var tf = document.getElementById("fType").value;
  var sf = document.getElementById("fStat").value;
  var q = (document.getElementById("fQ").value || "").toLowerCase();
  var count = 0;
  var rows = document.querySelectorAll(".record-table tbody tr:not(.inline-preview)");
  for (var r = 0; r < rows.length; r++) {
    var tr = rows[r];
    var idx = parseInt(tr.getAttribute("data-idx"));
    if (isNaN(idx)) { tr.style.display = "none"; continue; }
    var d = DB[idx];
    if (!d) { tr.style.display = "none"; continue; }
    var m = parseFM(d.content);
    var body = getBody(d.content);
    var ok = true;
    if (tf && m.type !== tf) ok = false;
    if (sf && m.status !== sf) ok = false;
    var fsel = ACTIVE_FACETS["__folder"];
    if (fsel && fsel.length && fsel.indexOf(d.folder) < 0) ok = false;
    for (var fk in ACTIVE_FACETS) {
      if (!Object.prototype.hasOwnProperty.call(ACTIVE_FACETS, fk)) continue;
      if (fk === "__folder") continue;
      var fvals = ACTIVE_FACETS[fk];
      if (fvals && fvals.length && fvals.indexOf(m[fk] || "") < 0) ok = false;
    }
    if (q) {
      var searchStr = (m.title+" "+d.name+" "+(m.tags||[]).join(" ")+" "+(m.category||"")+" "+body).toLowerCase();
      if (searchStr.indexOf(q) < 0) ok = false;
    }
    tr.style.display = ok ? "" : "none";
    // Also hide adjacent inline preview
    var next = tr.nextElementSibling;
    if (next && next.classList.contains("inline-preview")) next.style.display = ok ? "" : "none";
    if (ok) count++;
  }
  // Hide empty month groups
  var groups = document.querySelectorAll(".month-group");
  for (var g = 0; g < groups.length; g++) {
    var visible = groups[g].querySelector(".record-table tbody tr:not(.inline-preview)[style*='display: none']");
    var anyVisible = groups[g].querySelector(".record-table tbody tr:not(.inline-preview):not([style*='display: none'])");
    var hasRows = groups[g].querySelector(".record-table tbody tr:not(.inline-preview)");
    if (hasRows && !anyVisible) {
      groups[g].style.display = "none";
    } else {
      groups[g].style.display = "";
    }
  }
  document.getElementById("filterCount").textContent = count + " 条";
}

function updateStats() {
  var now = new Date();
  var thisMonth = now.getFullYear() + "-" + String(now.getMonth()+1).padStart(2,"0");
  var total = DB.length, expCount = 0, planCount = 0, metCount = 0, monthCount = 0;
  for (var i = 0; i < DB.length; i++) {
    var m = parseFM(DB[i].content);
    if (m.type === "experiment") expCount++;
    if (m.type === "plan") planCount++;
    if (m.type === "method") metCount++;
    if (m.date && m.date.substring(0,7) === thisMonth) monthCount++;
  }
  document.getElementById("statTotal").textContent = total;
  document.getElementById("statExp").textContent = expCount;
  document.getElementById("statPlan").textContent = planCount;
  document.getElementById("statMet").textContent = metCount;
  document.getElementById("statMonth").textContent = monthCount;
}

// ====== READ VIEW ======
function jumpToRead(idx, targetId) {
  openRead(idx, targetId);
}

function openRead(idx, targetId) {
  curIdx = idx;
  var d = DB[idx];
  if (d) { try { pushList("notebook-recent", recKey(d), 12); } catch(e) {} }
  var m = parseFM(d.content);
  var body = getBody(d.content);
  var toc = buildToc(body);
  var summary = makeSummary(body);
  var relCount = (m.related && m.related.length) ? m.related.length : 0;
  var color = TYPE_ACCENTS[m.type] || "#2563eb";
  var pbiClass = hasPbiSignal(d.content) ? " pbi-hero" : "";
  document.getElementById("listView").style.display = "none";
  document.getElementById("readView").style.display = "";

  var container = document.getElementById("readContent");
  var html = '<div class="read-container">';
  html += '<div class="read-shell">';
  html += '<div class="read-main">';
  html += '<div class="read-hero'+pbiClass+'" style="--hero-accent:'+color+'">';
  html += '<div class="read-hero-top"><div class="read-hero-title"><h2>'+renderTitleWithBadges(m.title||d.name)+'<\/h2><div class="read-path">'+escHtml(d.folder+"/"+d.name)+'<\/div><\/div><span class="status-badge" style="background:'+(STATUS_COLORS[m.status]||"#888")+';color:#fff">'+escHtml(STATUS_LABELS[m.status]||m.status||"-")+'<\/span><\/div>';
  html += '<button type="button" class="star-btn'+(isStarred(idx)?' on':'')+'" onclick="toggleStar('+idx+')" aria-pressed="'+(isStarred(idx)?"true":"false")+'" title="收藏本条">'+ (isStarred(idx)?"\u2605":"\u2606") +'<\/button>';
  html += '<div class="read-chips">';
  if (m.type) html += '<span class="read-chip"><strong>类型<\/strong> '+escHtml(TYPES[m.type]||m.type)+'<\/span>';
  if (m.date) html += '<span class="read-chip"><strong>日期<\/strong> '+escHtml(m.date)+'<\/span>';
  if (m.category) html += '<span class="read-chip"><strong>分类<\/strong> '+escHtml(m.category)+'<\/span>';
  if (m.electrolyte && m.electrolyte !== "不涉及") html += '<span class="read-chip"><strong>电解质<\/strong> '+escHtml(m.electrolyte)+'<\/span>';
  if (m.additive === "EMIMTFSI") html += '<span class="read-chip"><strong>添加剂<\/strong> EMIMTFSI<\/span>';
  if (m.counter_electrode && m.counter_electrode !== "不涉及" && m.counter_electrode !== "未标注") html += '<span class="read-chip"><strong>对电极<\/strong> '+escHtml(m.counter_electrode)+'<\/span>';
  if (m.encapsulation && m.encapsulation !== "不涉及" && m.encapsulation !== "未标注") html += '<span class="read-chip"><strong>隔层封装<\/strong> '+escHtml(m.encapsulation)+'<\/span>';
  if (m.baseline && m.baseline !== "不涉及" && m.baseline !== "未标注") html += '<span class="read-chip"><strong>基线<\/strong> '+escHtml(m.baseline)+'<\/span>';
  if (m.modified) html += '<span class="read-chip"><strong>更新<\/strong> '+escHtml(m.modified)+'<\/span>';
  if (relCount) html += '<span class="read-chip"><strong>关联<\/strong> '+relCount+' 条<\/span>';
  html += '<\/div>';
  if (summary) html += '<div class="read-excerpt">'+renderMixedText(summary)+'<\/div>';
  html += '<\/div>';
  html += '<div class="read-fm">';
  if (m.priority) html += '<span class="fm-item"><span class="fm-key">优先级<\/span> <span class="fm-val">'+escHtml(m.priority)+'<\/span><\/span>';
  if (m.due) html += '<span class="fm-item"><span class="fm-key">截止<\/span> <span class="fm-val">'+escHtml(m.due)+'<\/span><\/span>';
  if (m.category) html += '<span class="fm-item"><span class="fm-key">分类<\/span> <span class="fm-val">'+escHtml(m.category)+'<\/span><\/span>';
  if (m.tags && m.tags.length > 0) {
    html += '<span class="fm-item" style="grid-column:1/-1"><span class="fm-key">标签<\/span> <span class="fm-tags">';
    for (var ti = 0; ti < m.tags.length; ti++) html += renderTagPill(m.tags[ti]);
    html += '<\/span><\/span>';
  }
  if (m.related && m.related.length > 0) {
    html += '<span class="fm-item" style="grid-column:1/-1"><span class="fm-key">相关<\/span> <span class="fm-tags">';
    for (var ri = 0; ri < m.related.length; ri++) html += renderTagPill(m.related[ri]);
    html += '<\/span><\/span>';
  }
  if (m.metrics) {
    html += '<div class="fm-metrics"><div class="fm-key" style="margin-bottom:4px">关键指标<\/div>'+renderMetricChips(m)+
            '<div class="metric-basis">'+escHtml(m.metrics.basis||"")+'<\/div><\/div>';
  }
  html += '<\/div>';
  html += '<div class="read-content">'+renderMarkdown(body)+'<\/div>';
  html += renderBacklinks(idx);
  html += '<div class="read-bottom"><button class="btn" onclick="toggleStar('+idx+')">'+(isStarred(idx)?"取消收藏":"收藏")+'<\/button><button class="btn" onclick="scrollToRaw()">原文<\/button><button class="btn" onclick="goBack()">返回列表<\/button><\/div>';
  html += '<\/div>';
  html += '<div class="read-aside">';
  html += '<div class="side-panel summary-banner"><div class="label">快速摘要<\/div><div class="value">'+renderMixedText(summary || "暂无摘要")+'<\/div><\/div>';
  html += '<div class="side-panel"><h3>目录<\/h3>'+renderToc(toc)+'<\/div>';
  html += '<div class="side-panel"><h3>相关记录<\/h3><div class="related-list">'+renderRelated(m.related)+'<\/div><\/div>';
  html += '<\/div>';
  html += '<\/div>';
  html += '<details class="raw-source" id="rawSource"><summary>完整原始 Markdown<\/summary><pre>'+escHtml(d.content)+'<\/pre><\/details>';
  html += '<\/div>';
  container.innerHTML = html;
  if (targetId) {
    requestAnimationFrame(function(){
      var target = document.getElementById(targetId);
      if (target) {
        target.scrollIntoView({behavior:"smooth", block:"start"});
        target.classList.add("jump-focus");
        setTimeout(function(){ target.classList.remove("jump-focus"); }, 2200);
      }
      else window.scrollTo(0,0);
    });
  } else {
    window.scrollTo(0,0);
  }
}

function renderRelated(rel) {
  if (!rel || !rel.length) return '<span style="font-size:12px;color:var(--c-muted)">暂无</span>';
  var html = '';
  for (var i = 0; i < rel.length; i++) {
    html += '<span class="rel-chip dim">'+escHtml(rel[i])+'<\/span>';
  }
  return html;
}

function scrollToRaw() {
  var raw = document.getElementById("rawSource");
  if (raw) raw.open = true;
  var prefersReduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (raw) raw.scrollIntoView({behavior:prefersReduced ? "auto" : "smooth", block:"start"});
}

// ====== EDIT VIEW ======
var READ_ONLY_MSG = "网页为只读视图：修改请编辑对应 md 文件后运行 sync-data.py，或直接让 AI 修改。";
function readOnlyGuard() { showToast(READ_ONLY_MSG); return true; }

function openEditor(idx) {
  readOnlyGuard();
  return;
  curIdx = idx;
  dirty = false;
  var d = DB[idx];
  var m = parseFM(d.content);
  var body = getBody(d.content);
  
  document.getElementById("listView").style.display = "none";
  document.getElementById("readView").style.display = "none";
  document.getElementById("editView").style.display = "";
  document.getElementById("editTitle").textContent = m.title || d.name;
  document.getElementById("dirtyTag").style.display = "none";
  document.getElementById("saveStatus").textContent = "";
  
  // Build edit body
  var fields = [
    {key:"type",label:"类型",type:"select",options:TYPES},
    {key:"title",label:"标题",type:"text"},
    {key:"date",label:"日期",type:"text"},
    {key:"category",label:"分类",type:"text"},
    {key:"project",label:"项目",type:"text"},
    {key:"status",label:"状态",type:"select",options:STATUS_LABELS},
    {key:"priority",label:"优先级",type:"text"},
    {key:"due",label:"截止日",type:"text"},
    {key:"tags",label:"标签（逗号分隔）",type:"text"}
  ];
  var panelBody = "";
  for (var i = 0; i < fields.length; i++) {
    var f = fields[i];
    var val = m[f.key] || "";
    if (f.key === "tags" && Array.isArray(val)) val = val.join(", ");
    panelBody += '<div><label for="fm_'+f.key+'">'+f.label+'<\/label>';
    if (f.type === "select") {
      panelBody += '<select id="fm_'+f.key+'" name="fm_'+f.key+'" autocomplete="off" onchange="markDirty()"><option value=""><\/option>';
      for (var k in f.options) {
        if (f.options.hasOwnProperty(k)) panelBody += '<option value="'+k+'"'+(k===val?' selected':'')+'>'+f.options[k]+'<\/option>';
      }
      panelBody += '<\/select>';
    } else {
      panelBody += '<input id="fm_'+f.key+'" name="fm_'+f.key+'" autocomplete="off" value="'+escHtml(String(val))+'" oninput="markDirty()">';
    }
    panelBody += '<\/div>';
  }
  
  var html = '';
  html += '<div class="edit-panel" id="metaPanel">';
  html += '<button type="button" class="edit-panel-header" onclick="toggleMetaPanel(this)" aria-expanded="true"><span class="chevron" aria-hidden="true">▼<\/span> 元数据<\/button>';
  html += '<div class="edit-panel-body">'+panelBody+'<\/div><\/div>';
  
  html += '<div class="edit-body-area">';
  html += '<div class="edit-tabs" role="tablist" aria-label="正文编辑模式"><button type="button" class="tab active" id="tabEdit" role="tab" aria-selected="true" aria-controls="edBody" onclick="switchTab(0)">编辑<\/button><button type="button" class="tab" id="tabPrev" role="tab" aria-selected="false" aria-controls="pvPane" onclick="switchTab(1)">预览<\/button><\/div>';
  html += '<textarea class="edit-textarea" id="edBody" name="record-body" aria-label="记录正文" autocomplete="off" spellcheck="false" oninput="markDirty()">'+escHtml(body)+'<\/textarea>';
  html += '<div class="preview-pane" id="pvPane" role="tabpanel" aria-labelledby="tabPrev"><\/div><\/div>';
  
  html += '<div class="edit-actions"><span style="font-size:11px;color:var(--c-muted);font-family:var(--font-ui)">Ctrl+S 保存<\/span><\/div>';
  
  document.getElementById("editBody").innerHTML = html;
  switchTab(0);
  window.scrollTo(0,0);
  setTimeout(function(){ document.getElementById("edBody").focus(); }, 100);
}

function toggleMetaPanel(btn) {
  var panel = document.getElementById("metaPanel");
  panel.classList.toggle("collapsed");
  btn.setAttribute("aria-expanded", panel.classList.contains("collapsed") ? "false" : "true");
}

function switchTab(n) {
  document.getElementById("tabEdit").className = "tab" + (n===0?" active":"");
  document.getElementById("tabPrev").className = "tab" + (n===1?" active":"");
  document.getElementById("tabEdit").setAttribute("aria-selected", n===0 ? "true" : "false");
  document.getElementById("tabPrev").setAttribute("aria-selected", n===1 ? "true" : "false");
  document.getElementById("edBody").style.display = n===0?"":"none";
  document.getElementById("pvPane").style.display = n===1?"":"none";
  if (n===1) document.getElementById("pvPane").innerHTML = renderMarkdown(document.getElementById("edBody").value);
}

function readMetaForm() {
  var m = {};
  var fields = ["type","title","date","category","project","status","priority","due","tags"];
  for (var i = 0; i < fields.length; i++) {
    var el = document.getElementById("fm_"+fields[i]);
    if (el) {
      var v = el.value.trim();
      if (fields[i] === "tags") { m.tags = v ? v.split(",").map(function(s){return s.trim()}).filter(Boolean) : []; }
      else { m[fields[i]] = v; }
    }
  }
  return m;
}

function doSave() {
  readOnlyGuard();
  return;
  if (curIdx < 0) return;
  var meta = readMetaForm();
  var body = document.getElementById("edBody").value;
  meta.modified = new Date().toISOString().slice(0,10);
  if (!meta.date) meta.date = meta.modified;
  DB[curIdx].content = fmToString(meta) + "\n\n" + body;
  saveDB();
  dirty = false;
  document.getElementById("dirtyTag").style.display = "none";
  syncRecordToDisk(DB[curIdx]);
  showToast("已保存，正在同步到 GitHub Pages");
  // Return to read view
  openRead(curIdx);
}

function markDirty() {
  if (curIdx < 0) return;
  dirty = true;
  document.getElementById("dirtyTag").style.display = "inline";
}

function doDelete() {
  readOnlyGuard();
  return;
  if (curIdx < 0) return;
  if (!confirm("确定删除「"+(parseFM(DB[curIdx].content).title||DB[curIdx].name)+"」？")) return;
  var deleted = DB[curIdx];
  DB.splice(curIdx,1);
  saveDB();
  syncDeleteFromDisk(deleted);
  goBack();
  showToast("已删除，正在同步到 GitHub Pages");
}

function goBack() {
  if (dirty && !confirm("有未保存的修改，放弃？")) return;
  curIdx = -1;
  dirty = false;
  document.getElementById("readView").style.display = "none";
  document.getElementById("listView").style.display = "";
  renderList();
  updateStats();
  populateFilters();
  window.scrollTo(0,0);
}

// ====== CREATE ======
function showNewMenu() {
  readOnlyGuard();
  return;
  document.getElementById("modalNew").classList.add("show");
  setTimeout(function(){
    var first = document.querySelector("#modalNew button");
    if (first) first.focus();
  }, 0);
}
function closeNewMenu() { document.getElementById("modalNew").classList.remove("show"); }
function newRec(type) {
  readOnlyGuard();
  return;
  closeNewMenu();
  document.getElementById("modalNameTitle").textContent = "新建"+(TYPES[type]||type);
  document.getElementById("modalNameInput").value = "";
  document.getElementById("modalName").classList.add("show");
  document.getElementById("modalNameOk").onclick = function(){
    var name = document.getElementById("modalNameInput").value.trim();
    if (!name) return;
    if (name.indexOf(".md") < 0) name += ".md";
    var today = new Date().toISOString().slice(0,10);
    var title = name.replace(".md","");
    var content = "---\ntype: "+type+"\ntitle: "+title+"\ndate: "+today+"\ntags: []\nmodified: "+today+"\n---\n\n# "+(TYPES[type]||type)+"记录\n";
    DB.push({folder:folderForType(type),name:name,content:content});
    saveDB();
    closeNameModal();
    openEditor(DB.length-1);
  };
  setTimeout(function(){ document.getElementById("modalNameInput").focus(); },100);
}
function closeNameModal() { document.getElementById("modalName").classList.remove("show"); }

// ====== EXPORT/IMPORT ======
function doExportAll() {
  for (var i = 0; i < DB.length; i++) {
    var blob = new Blob([DB[i].content],{type:"text/markdown"});
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = DB[i].name;
    a.click();
  }
  showToast("已导出 "+DB.length+" 个文件");
}
function doImport() {
  readOnlyGuard();
  return;
  var inp = document.createElement("input");
  inp.type = "file"; inp.accept = ".md"; inp.multiple = true;
  inp.onchange = function(){
    var files = Array.from(inp.files);
    var loaded = 0;
    files.forEach(function(f){
      var reader = new FileReader();
      reader.onload = function(e){
        var c = e.target.result;
        if (c.charCodeAt(0)===0xFEFF) c = c.slice(1);
        var found = -1;
        for (var j=0;j<DB.length;j++){ if(DB[j].name===f.name){found=j;break;} }
        if (found>=0) DB[found].content = c;
        else { var pm = parseFM(c); DB.push({folder:folderForType(pm.type||"method"),name:f.name,content:c}); }
        loaded++;
        if (loaded===files.length){ saveDB(); location.reload(); }
      };
      reader.readAsText(f);
    });
  };
  inp.click();
}

// ====== UTILS ======
function saveDB() { try { localStorage.setItem("labdb",JSON.stringify(DB)); } catch(e) {} }
function folderForType(type) { return TYPE_FOLDERS[type] || "notes"; }
function syncRecordToDisk(record) {
  if (!record || location.protocol === "file:") return;
  fetch("/api/save", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(record)
  }).then(function(res){
    return res.json().then(function(data){
      if (!res.ok || !data.ok) throw new Error(data.error || "同步失败");
      showToast(data.message || "已保存并推送到 GitHub Pages");
    });
  }).catch(function(err){
    showToast("同步失败：请检查服务器窗口、网络代理或 GitHub 认证");
    console.error(err);
  });
}
function syncDeleteFromDisk(record) {
  if (!record || location.protocol === "file:") return;
  fetch("/api/delete", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({folder: record.folder, name: record.name})
  }).then(function(res){
    return res.json().then(function(data){
      if (!res.ok || !data.ok) throw new Error(data.error || "同步失败");
      showToast(data.message || "已删除并推送到 GitHub Pages");
    });
  }).catch(function(err){
    showToast("同步失败：请检查服务器窗口、网络代理或 GitHub 认证");
    console.error(err);
  });
}
function showToast(msg) {
  var el = document.getElementById("toast");
  el.textContent = msg;
  el.className = "toast show";
  setTimeout(function(){ el.className = "toast"; },2000);
}

// ====== KEYBOARD ======
document.addEventListener("keydown",function(e){
  if ((e.ctrlKey||e.metaKey) && e.key==="s") { e.preventDefault(); }
  if (e.key==="Escape") { if (curIdx>=0) goBack(); }
});

// ====== PASSWORD ======
var PW_UNLOCKED = false;
var PW_HASH = "9b7c0087c732664dca4dda5f65f36c6ca7c3b3c0225956bc6feb0cfab6ef6879";
function checkPassword() {
  document.getElementById("pwGate").style.display = "flex";
  document.getElementById("listView").classList.add("pw-locked");
  document.getElementById("pwInput").addEventListener("keydown", function(e) {
    if (e.key === "Enter") tryUnlock();
  });
  document.getElementById("pwInput").focus();
}
async function tryUnlock() {
  var input = document.getElementById("pwInput").value;
  if (!input) return;
  var hash = await sha256(input);
  if (hash === PW_HASH) {
    PW_UNLOCKED = true;
    document.getElementById("pwGate").style.display = "none";
    document.getElementById("listView").classList.remove("pw-locked");
  } else {
    document.getElementById("pwMsg").style.display = "block";
    document.getElementById("pwInput").value = "";
    document.getElementById("pwInput").focus();
  }
}
async function sha256(msg) {
  var enc = new TextEncoder().encode(msg);
  var buf = await crypto.subtle.digest("SHA-256", enc);
  return Array.from(new Uint8Array(buf)).map(b=>b.toString(16).padStart(2,"0")).join("");
}

// ============================================================
// 2026-10-21 新增：视图模式 / 排序 / 分面 / 主题 / 密度 /
//                 指标 / 悬停预览 / 仪表盘 / 可视化 / 反向链接
// ============================================================
var SORT_FIELD = "date";
var SORT_DESC = true;
var ACTIVE_FACETS = {};
var VIEW_MODE = "list";
var FACET_DEFS = [
  {key:"__folder", label:"文档类型"},
  {key:"category", label:"分类"},
  {key:"electrolyte", label:"电解质"},
  {key:"additive", label:"添加剂"},
  {key:"counter_electrode", label:"对电极"},
  {key:"encapsulation", label:"隔层"},
  {key:"baseline", label:"基线"},
  {key:"status", label:"状态"}
];
var FACET_SKIP = {"不涉及":1, "":1, "-":1};

function setSort(key) {
  if (SORT_FIELD === key) { SORT_DESC = !SORT_DESC; }
  else { SORT_FIELD = key; SORT_DESC = true; }
  renderList();
}

function setFilterCount(n) {
  var el = document.getElementById("filterCount");
  if (el) el.textContent = n + " 条";
}

// ---------- 分面筛选 ----------
var FOLDER_LABELS = {"experiments":"实验记录","plans":"实验方案","methods":"方法页","notes":"规范与汇总","reminders":"提醒","data":"数据"};
var FOLDER_ORDER = ["experiments","plans","methods","notes","reminders","data"];

function folderLabel(f){ return FOLDER_LABELS[f] || f; }

// 当前文档类型筛选范围；未选类型时返回 null（表示全部）
function facetScope() {
  var sel = ACTIVE_FACETS["__folder"];
  if (!sel || !sel.length) return null;
  var set = {};
  for (var i = 0; i < sel.length; i++) set[sel[i]] = 1;
  return set;
}

function renderFacets() {
  var bar = document.getElementById("facetBar");
  if (!bar) return;
  var html = "";
  var scope = facetScope();
  var i, k;

  // 1) 文档类型：一级分面，始终统计全部记录，便于切换
  var folderVals = {};
  for (i = 0; i < DB.length; i++) {
    var f = DB[i].folder;
    folderVals[f] = (folderVals[f] || 0) + 1;
  }
  var fkeys = [];
  for (var o = 0; o < FOLDER_ORDER.length; o++) {
    if (folderVals[FOLDER_ORDER[o]]) fkeys.push(FOLDER_ORDER[o]);
  }
  for (k in folderVals) {
    if (Object.prototype.hasOwnProperty.call(folderVals, k) && fkeys.indexOf(k) < 0) fkeys.push(k);
  }
  if (fkeys.length >= 2) {
    html += '<div class="facet-group"><span class="facet-label">文档类型</span>';
    for (var fk = 0; fk < fkeys.length; fk++) {
      var fv = fkeys[fk];
      var fon = (ACTIVE_FACETS["__folder"] || []).indexOf(fv) >= 0;
      html += '<button type="button" class="facet-chip' + (fon ? ' on' : '') + '" onclick="toggleFacet(\'__folder\',\'' + escAttr(fv) + '\')">' + escHtml(folderLabel(fv)) + ' ' + folderVals[fv] + '</button>';
    }
    html += '</div>';
  }

  // 2) 其余分面：只统计当前文档类型范围内的记录
  var pool = [];
  for (i = 0; i < DB.length; i++) {
    if (scope && !scope[DB[i].folder]) continue;
    pool.push(DB[i]);
  }
  for (var fi = 0; fi < FACET_DEFS.length; fi++) {
    var def = FACET_DEFS[fi];
    if (def.key === "__folder") continue;
    var vals = {};
    for (i = 0; i < pool.length; i++) {
      var m = parseFM(pool[i].content);
      var v = m[def.key] || "";
      if (FACET_SKIP[v]) continue;
      vals[v] = (vals[v] || 0) + 1;
    }
    var keys = Object.keys(vals).sort(function(a,b){ return vals[b]-vals[a]; });
    if (keys.length < 2) continue;
    html += '<div class="facet-group"><span class="facet-label">' + def.label + '</span>';
    for (k = 0; k < keys.length; k++) {
      var on = (ACTIVE_FACETS[def.key] || []).indexOf(keys[k]) >= 0;
      html += '<button type="button" class="facet-chip' + (on ? ' on' : '') + '" onclick="toggleFacet(\'' + def.key + '\',\'' + escAttr(keys[k]) + '\')">' + escHtml(keys[k]) + ' ' + vals[keys[k]] + '</button>';
    }
    html += '</div>';
  }
  bar.innerHTML = html;
  renderActiveFilters();
}

function toggleFacet(key, val) {
  if (!ACTIVE_FACETS[key]) ACTIVE_FACETS[key] = [];
  var arr = ACTIVE_FACETS[key];
  var p = arr.indexOf(val);
  if (p >= 0) arr.splice(p, 1); else arr.push(val);
  if (!arr.length) delete ACTIVE_FACETS[key];
  renderFacets();
  filter();
}

function renderActiveFilters() {
  var box = document.getElementById("activeFilters");
  if (!box) return;
  var keys = Object.keys(ACTIVE_FACETS);
  if (!keys.length) { box.innerHTML = ""; return; }
  var html = "";
  for (var i = 0; i < keys.length; i++) {
    var key = keys[i];
    var label = key;
    for (var f = 0; f < FACET_DEFS.length; f++) if (FACET_DEFS[f].key === key) label = FACET_DEFS[f].label;
    for (var j = 0; j < ACTIVE_FACETS[key].length; j++) {
      var shown = (key === "__folder") ? folderLabel(ACTIVE_FACETS[key][j]) : ACTIVE_FACETS[key][j];
      html += '<span class="af-chip">' + escHtml(label) + '：' + escHtml(shown) +
              '<button type="button" onclick="toggleFacet(\'' + key + '\',\'' + escAttr(ACTIVE_FACETS[key][j]) + '\')" aria-label="移除筛选">✕</button></span>';
    }
  }
  html += '<button type="button" class="af-clear" onclick="clearFacets()">清除全部筛选</button>';
  box.innerHTML = html;
}

function clearFacets() {
  ACTIVE_FACETS = {};
  renderFacets();
  filter();
}

// ---------- 指标 ----------
function renderMetricChips(m) {
  if (!m.metrics) return "";
  var html = '<div class="metric-chips">';
  var mc = m.metrics;
  if (mc.contrast) html += '<span class="metric-chip good">ΔT ' + escHtml(mc.contrast) + '</span>';
  if (mc.coloring) html += '<span class="metric-chip">着色 ' + escHtml(mc.coloring) + '</span>';
  if (mc.bleaching) html += '<span class="metric-chip">褪色 ' + escHtml(mc.bleaching) + '</span>';
  if (mc.wavelength) html += '<span class="metric-chip">' + escHtml(mc.wavelength) + '</span>';
  html += '</div>';
  return html;
}

// ---------- 主题 / 密度 ----------
function applyTheme() {
  var th = "default";
  try { th = localStorage.getItem("notebook-theme") || "default"; } catch (e) {}
  document.body.classList.toggle("theme-paper", th === "paper");
  var btn = document.getElementById("btnTheme");
  if (btn) btn.textContent = th === "paper" ? "纸感" : "常规";
}
function toggleTheme() {
  var cur = document.body.classList.contains("theme-paper") ? "paper" : "default";
  var next = cur === "paper" ? "default" : "paper";
  try { localStorage.setItem("notebook-theme", next); } catch (e) {}
  applyTheme();
}
function applyDensity() {
  var d = "comfortable";
  try { d = localStorage.getItem("notebook-density") || "comfortable"; } catch (e) {}
  document.body.classList.toggle("density-compact", d === "compact");
  var btn = document.getElementById("btnDensity");
  if (btn) btn.textContent = d === "compact" ? "紧凑" : "舒适";
}
function toggleDensity() {
  var cur = document.body.classList.contains("density-compact") ? "compact" : "comfortable";
  var next = cur === "compact" ? "comfortable" : "compact";
  try { localStorage.setItem("notebook-density", next); } catch (e) {}
  applyDensity();
}

// ---------- 悬停预览 ----------
var hoverTimer = null;
function showHoverCard(ev, idx) {
  hideHoverCard();
  hoverTimer = setTimeout(function () { doShowHoverCard(ev, idx); }, 320);
}
function doShowHoverCard(ev, idx) {
  var d = DB[idx]; if (!d) return;
  var m = parseFM(d.content);
  var body = getBody(d.content);
  var card = document.createElement("div");
  card.className = "hover-card";
  card.id = "hoverCard";
  var meta = [];
  if (m.date) meta.push(m.date);
  if (m.category) meta.push(m.category);
  if (m.electrolyte && m.electrolyte !== "不涉及") meta.push(m.electrolyte);
  if (m.status) meta.push(STATUS_LABELS[m.status] || m.status);
  card.innerHTML = '<h4>' + escHtml(m.title || d.name) + '</h4>' +
    '<div class="hc-meta">' + escHtml(meta.join(" · ")) + '</div>' +
    '<div class="hc-sum">' + renderMixedText(makeSummary(body)) + '</div>' + renderMetricChips(m);
  document.body.appendChild(card);
  var x = (ev && ev.clientX != null) ? ev.clientX + 16 : 200;
  var y = (ev && ev.clientY != null) ? ev.clientY + 16 : 200;
  var w = card.offsetWidth || 380, h = card.offsetHeight || 160;
  if (x + w > window.innerWidth - 12) x = window.innerWidth - w - 12;
  if (y + h > window.innerHeight - 12) y = Math.max(12, y - h - 28);
  card.style.left = x + "px";
  card.style.top = y + "px";
}
function hideHoverCard() {
  if (hoverTimer) { clearTimeout(hoverTimer); hoverTimer = null; }
  var c = document.getElementById("hoverCard");
  if (c && c.parentNode) c.parentNode.removeChild(c);
}

// ---------- 收藏 / 最近 ----------
function recKey(d) { return d.folder + "/" + d.name; }
function findIdxByKey(key) {
  for (var i = 0; i < DB.length; i++) if (recKey(DB[i]) === key) return i;
  return -1;
}
function getList(key) {
  try { return JSON.parse(localStorage.getItem(key) || "[]"); } catch (e) { return []; }
}
function pushList(key, val, max) {
  var a = getList(key);
  var p = a.indexOf(val);
  if (p >= 0) a.splice(p, 1);
  a.unshift(val);
  if (a.length > max) a = a.slice(0, max);
  try { localStorage.setItem(key, JSON.stringify(a)); } catch (e) {}
  return a;
}
function toggleStar(idx) {
  var k = recKey(DB[idx]);
  var a = getList("notebook-stars");
  var p = a.indexOf(k);
  if (p >= 0) a.splice(p, 1); else a.unshift(k);
  try { localStorage.setItem("notebook-stars", JSON.stringify(a)); } catch (e) {}
  var inRead = document.getElementById("readView") && document.getElementById("readView").style.display !== "none";
  if (inRead) { openRead(idx); return; }
  if (VIEW_MODE === "list") renderList();
  else openRead(idx);
}
function isStarred(idx) {
  return getList("notebook-stars").indexOf(recKey(DB[idx])) >= 0;
}

// ---------- 仪表盘 ----------
function renderDashboard() {
  var expCount = 0, dataCount = 0, reviewCount = 0;
  var nowMonth = new Date().getFullYear() + "-" + String(new Date().getMonth() + 1).padStart(2, "0");
  var monthCount = 0;
  var reviewItems = [];
  for (var i = 0; i < DB.length; i++) {
    var m = parseFM(DB[i].content);
    if (m.type === "experiment") expCount++;
    if (m.data_types && m.data_types.length) dataCount++;
    if (m.status === "needs_review") { reviewCount++; reviewItems.push(i); }
    if (m.date && m.date.substring(0, 7) === nowMonth) monthCount++;
  }
  var html = '<div class="dashboard"><div class="dash-grid">';

  html += '<div class="dash-card"><h4>本月实验</h4><div class="dc-big">' + monthCount + '</div>' +
          '<div class="muted">实验 ' + expCount + ' 条 · 含结构化数据 ' + dataCount + ' 条</div></div>';

  html += '<div class="dash-card"><h4>待复核</h4><div class="dc-big" style="color:' +
          (reviewCount ? '#b45309' : 'inherit') + '">' + reviewCount + '</div>';
  if (reviewCount) {
    html += '<ul>';
    for (var r = 0; r < Math.min(reviewItems.length, 4); r++) {
      var mm = parseFM(DB[reviewItems[r]].content);
      html += '<li><button type="button" class="dash-link" onclick="openRead(' + reviewItems[r] + ')">' +
              escHtml((mm.title || DB[reviewItems[r]].name).slice(0, 26)) + '</button></li>';
    }
    html += '</ul>';
  } else html += '<div class="muted">没有待复核项</div>';
  html += '</div>';

  var recent = getList("notebook-recent");
  var recIdx = [];
  for (var a = 0; a < recent.length && recIdx.length < 5; a++) {
    var ix = findIdxByKey(recent[a]);
    if (ix >= 0) recIdx.push(ix);
  }
  html += '<div class="dash-card"><h4>最近查看</h4>';
  if (recIdx.length) {
    html += '<ul>';
    for (var b = 0; b < recIdx.length; b++) {
      var rm = parseFM(DB[recIdx[b]].content);
      html += '<li><button type="button" class="dash-link" onclick="openRead(' + recIdx[b] + ')">' +
              escHtml((rm.title || DB[recIdx[b]].name).slice(0, 26)) + '</button></li>';
    }
    html += '</ul>';
  } else html += '<div class="muted">还没有浏览记录</div>';
  html += '</div>';

  var stars = getList("notebook-stars");
  var stIdx = [];
  for (var c = 0; c < stars.length; c++) {
    var sx = findIdxByKey(stars[c]);
    if (sx >= 0) stIdx.push(sx);
  }
  html += '<div class="dash-card"><h4>收藏</h4>';
  if (stIdx.length) {
    html += '<ul>';
    for (var d2 = 0; d2 < Math.min(stIdx.length, 5); d2++) {
      var sm = parseFM(DB[stIdx[d2]].content);
      html += '<li><button type="button" class="dash-link" onclick="openRead(' + stIdx[d2] + ')">' +
              escHtml((sm.title || DB[stIdx[d2]].name).slice(0, 26)) + '</button></li>';
    }
    html += '</ul>';
  } else html += '<div class="muted">阅读页点 ☆ 可收藏</div>';
  html += '</div>';

  html += '</div></div>';
  return html;
}

// ---------- 视图切换 ----------
function renderViewTabs() {
  var tabs = [
    {k:"list", t:"记录列表"},
    {k:"compare", t:"跨批次对比"},
    {k:"timeline", t:"实验时间轴"},
    {k:"completeness", t:"数据完整度"}
  ];
  var html = '<div class="facets" style="padding-top:10px">';
  for (var i = 0; i < tabs.length; i++) {
    var on = VIEW_MODE === tabs[i].k;
    html += '<button type="button" class="facet-chip' + (on ? ' on' : '') + '" onclick="setView(\'' + tabs[i].k + '\')">' + tabs[i].t + '</button>';
  }
  html += '</div>';
  return html;
}
function setView(mode) { VIEW_MODE = mode; renderList(); }

// ---------- 跨批次对比表 ----------
function buildCompareRows() {
  var rows = [];
  for (var i = 0; i < DB.length; i++) {
    var m = parseFM(DB[i].content);
    if (!m.metrics) continue;
    rows.push({idx:i, m:m});
  }
  return rows;
}
function renderCompareTable() {
  var rows = buildCompareRows();
  var html = '<div class="viz-section"><h3>跨批次关键指标对比</h3>' +
    '<div class="viz-hint">只显示已写入 metrics 的记录（当前 ' + rows.length + ' 条）。点表头可排序。</div>';
  if (!rows.length) {
    html += '<div class="muted">还没有记录写入 metrics 字段。</div></div>';
    return html;
  }
  html += '<table class="viz-table"><thead><tr>' +
    '<th onclick="setSort(\'date\')">日期</th><th>体系</th><th>电解质</th><th>对电极</th><th>隔层</th><th>基线</th>' +
    '<th>ΔT</th><th>着色</th><th>褪色</th><th>波长</th></tr></thead><tbody>';
  for (var i = 0; i < rows.length; i++) {
    var r = rows[i], m = r.m, mc = m.metrics;
    html += '<tr style="cursor:pointer" onclick="openRead(' + r.idx + ')">' +
      '<td>' + escHtml(m.date || "-") + '</td>' +
      '<td>' + escHtml((m.title || DB[r.idx].name).replace(/^\[[^\]]*\]\s*/, "").slice(0, 30)) + '</td>' +
      '<td>' + escHtml(m.electrolyte || "-") + '</td>' +
      '<td>' + escHtml(m.counter_electrode || "-") + '</td>' +
      '<td>' + escHtml(m.encapsulation || "-") + '</td>' +
      '<td>' + escHtml(m.baseline || "-") + '</td>' +
      '<td class="num">' + escHtml(mc.contrast || "-") + '</td>' +
      '<td class="num">' + escHtml(mc.coloring || "-") + '</td>' +
      '<td class="num">' + escHtml(mc.bleaching || "-") + '</td>' +
      '<td class="num">' + escHtml(mc.wavelength || "-") + '</td></tr>';
  }
  html += '</tbody></table></div>';
  return html;
}

// ---------- 时间轴 ----------
function renderTimeline() {
  var byDay = {};
  var minD = "9999", maxD = "0000";
  for (var i = 0; i < DB.length; i++) {
    var m = parseFM(DB[i].content);
    if (!m.date) continue;
    if (!byDay[m.date]) byDay[m.date] = [];
    byDay[m.date].push(i);
    if (m.date < minD) minD = m.date;
    if (m.date > maxD) maxD = m.date;
  }
  var days = Object.keys(byDay).sort();
  var html = '<div class="viz-section"><h3>实验时间轴</h3>' +
    '<div class="viz-hint">' + (days.length ? minD + " 至 " + maxD : "无日期数据") +
    ' · 每个方块是一天，颜色代表分类，实心=含结构化数据，点击可跳到该天第一条记录</div>';
  if (!days.length) { html += '</div>'; return html; }
  var CAT_COLORS = ["#2563eb","#0891b2","#7c3aed","#059669","#d97706","#dc2626","#db2777","#4b5563","#65a30d"];
  var cats = {};
  for (var c = 0; c < DB.length; c++) { var cm = parseFM(DB[c].content); if (cm.category) cats[cm.category] = 1; }
  var catList = Object.keys(cats).sort();

  html += '<div class="timeline-wrap"><svg width="' + (days.length * 22 + 20) + '" height="86" role="img" aria-label="实验时间轴">';
  for (var d = 0; d < days.length; d++) {
    var day = days[d];
    var first = byDay[day][0];
    var fm = parseFM(DB[first].content);
    var ci = catList.indexOf(fm.category);
    var color = CAT_COLORS[(ci < 0 ? 0 : ci) % CAT_COLORS.length];
    var hasData = fm.data_types && fm.data_types.length;
    var x = 10 + d * 22;
    html += '<rect x="' + x + '" y="18" width="16" height="16" rx="3" fill="' + color + '" fill-opacity="' +
            (hasData ? "1" : "0.32") + '" style="cursor:pointer" onclick="openRead(' + first + ')"><title>' +
            escHtml(day + " · " + (fm.category || "-") + " · " + (fm.title || "").slice(0, 20)) + '</title></rect>';
    if (byDay[day].length > 1) {
      html += '<text x="' + (x + 8) + '" y="45" font-size="9" fill="#657286" text-anchor="middle">' + byDay[day].length + '</text>';
    }
  }
  html += '</svg></div><div class="muted" style="margin-top:6px">';
  for (var k = 0; k < catList.length; k++) {
    html += '<span style="display:inline-flex;align-items:center;gap:4px;margin-right:12px">' +
      '<span style="width:10px;height:10px;border-radius:2px;background:' + CAT_COLORS[k % CAT_COLORS.length] + ';display:inline-block"></span>' +
      escHtml(catList[k]) + '</span>';
  }
  html += '</div></div>';
  return html;
}

// ---------- 数据完整度 ----------
var COMPLETENESS_FIELDS = [
  {key:"category", label:"分类"},
  {key:"electrolyte", label:"电解质"},
  {key:"counter_electrode", label:"对电极"},
  {key:"encapsulation", label:"隔层"},
  {key:"baseline", label:"基线"},
  {key:"status", label:"状态"},
  {key:"data_types", label:"数据类型"}
];
function renderCompleteness() {
  var html = '<div class="viz-section"><h3>数据完整度</h3>' +
    '<div class="viz-hint">绿色=已填且有区分度，橙色=填了“未标注”，灰色=不涉及/无。标“未标注”的项需要你补。</div>';
  var rows = [];
  for (var i = 0; i < DB.length; i++) {
    var m = parseFM(DB[i].content);
    if (m.type === "method") continue;
    rows.push({idx:i, m:m});
  }
  html += '<table class="viz-table"><thead><tr><th>记录</th><th>日期</th>';
  for (var f = 0; f < COMPLETENESS_FIELDS.length; f++) html += '<th>' + COMPLETENESS_FIELDS[f].label + '</th>';
  html += '</tr></thead><tbody>';
  for (var r = 0; r < rows.length; r++) {
    var m2 = rows[r].m;
    html += '<tr style="cursor:pointer" onclick="openRead(' + rows[r].idx + ')"><td>' +
      escHtml((m2.title || DB[rows[r].idx].name).replace(/^\[[^\]]*\]\s*/, "").slice(0, 28)) + '</td>' +
      '<td>' + escHtml(m2.date || "-") + '</td>';
    for (var g = 0; g < COMPLETENESS_FIELDS.length; g++) {
      var key = COMPLETENESS_FIELDS[g].key;
      var v = m2[key];
      if (key === "data_types") v = (v && v.length) ? "有" : "无";
      var bg = "#e7f7ee", fg = "#0f6e56";
      if (!v || v === "无") { bg = "#f1efe8"; fg = "#888780"; }
      else if (v === "未标注") { bg = "#fff1e6"; fg = "#b45309"; }
      else if (v === "不涉及") { bg = "#f8fafc"; fg = "#94a3b8"; }
      html += '<td><span style="background:' + bg + ';color:' + fg + ';padding:1px 6px;border-radius:999px;font-size:11px">' +
              escHtml(String(v || "-")) + '</span></td>';
    }
    html += '</tr>';
  }
  html += '</tbody></table></div>';

  var missing = [];
  for (var q = 0; q < DB.length; q++) {
    var mm = parseFM(DB[q].content);
    if (mm.type === "method") continue;
    for (var z = 0; z < COMPLETENESS_FIELDS.length; z++) {
      var kk = COMPLETENESS_FIELDS[z].key;
      var vv = mm[kk];
      if (kk === "data_types") continue;
      if (vv === "未标注") missing.push({idx:q, field:COMPLETENESS_FIELDS[z].label, title:mm.title || DB[q].name});
    }
  }
  html += '<div class="viz-section"><h3>待补清单（' + missing.length + ' 项）</h3>';
  if (!missing.length) html += '<div class="muted">没有“未标注”项，全部填齐了。</div>';
  else {
    html += '<div class="viz-hint">这些字段正文没写清楚，我不猜，等你确认后补。</div><ul style="list-style:none;padding:0">';
    for (var mi2 = 0; mi2 < Math.min(missing.length, 60); mi2++) {
      html += '<li style="font-size:12px;padding:3px 0"><button type="button" class="dash-link" onclick="openRead(' + missing[mi2].idx + ')">' +
              escHtml(missing[mi2].title.replace(/^\[[^\]]*\]\s*/, "").slice(0, 30)) + '</button> — ' + escHtml(missing[mi2].field) + '</li>';
    }
    html += '</ul>';
  }
  html += '</div>';
  return html;
}

// ---------- 反向链接 ----------
function renderBacklinks(idx) {
  var target = DB[idx]; if (!target) return "";
  var key = recKey(target);
  var short = target.name.replace(/\.md$/, "");
  var hits = [];
  for (var i = 0; i < DB.length; i++) {
    if (i === idx) continue;
    var m = parseFM(DB[i].content);
    for (var r = 0; r < (m.related || []).length; r++) {
      var rel = String(m.related[r]);
      var relShort = rel.replace(/\.md$/, "").split("/").pop();
      if (rel === key || relShort === short) { hits.push(i); break; }
    }
  }
  if (!hits.length) return '<div class="backlinks"><h3>被引用</h3><div class="muted">暂无其他记录引用本条</div></div>';
  var html = '<div class="backlinks"><h3>被引用（' + hits.length + '）</h3>';
  for (var h = 0; h < hits.length; h++) {
    var hm = parseFM(DB[hits[h]].content);
    html += '<button type="button" class="bl-item" onclick="openRead(' + hits[h] + ')">' +
            escHtml(hm.title || DB[hits[h]].name) + '</button>';
  }
  html += '</div>';
  return html;
}


init();
