#!/usr/bin/env python
"""Origin Pro MCP Server v1.1 - Control Origin Pro via COM automation + JSON-RPC over stdio."""

import sys, json, os, traceback
from typing import Any


class OriginBridge:
    def __init__(self):
        self.origin = None

    def connect(self):
        if self.origin is None:
            import win32com.client
            self.origin = win32com.client.Dispatch("Origin.Application")
            self.origin.Visible = True
        return self.origin

    def execute(self, script):
        return self.connect().Execute(script)

    def evaluate(self, expr):
        """Evaluate a LabTalk expression and return a float value."""
        return self.connect().Evaluate(expr)

    def import_csv(self, path):
        path = os.path.abspath(path)
        if not os.path.exists(path):
            return {"error": "File not found: " + path}
        self.connect()
        self.execute("newbook name:=TempData result:=bk$;")
        self.execute('impASC fname:="' + path + '" options.sparklines:=0;')
        bk = self.execute("bk\$").strip()
        return {"workbook": bk, "path": path}

    def create_plot(self, x_col, y_col, plot_type="line"):
        """Create a line/scatter plot. Uses corrected plotxy syntax (Origin 2024)."""
        pt_map = {"line": "200", "scatter": "201", "line+symbol": "202"}
        pt = pt_map.get(plot_type, "200")
        self.connect()
        self.execute("wks.col" + str(x_col) + ".type = 4;")
        self.execute("wks.col" + str(y_col) + ".type = 1;")
        # Corrected syntax: plotxy (sheet,col) plot:=type;
        self.execute("plotxy (1," + str(y_col) + ") plot:=" + pt + ";")
        # Find the graph page name
        graph_name = "Graph1"
        for i in range(self.connect().Pages.Count):
            p = self.connect().Pages(i)
            if "Graph" in str(p.Name):
                graph_name = str(p.Name)
                break
        return {"status": "ok", "x_col": x_col, "y_col": y_col, "plot_type": plot_type, "graph": graph_name}

    def set_axes(self, x_label="", y_label="", x_min=None, x_max=None, y_min=None, y_max=None):
        o = self.connect()
        if x_label:
            o.Execute('label -xb "' + x_label + '";')
        if y_label:
            o.Execute('label -yl "' + y_label + '";')
        if x_min is not None and x_max is not None:
            o.Execute("layer.x.from=" + str(x_min) + ";layer.x.to=" + str(x_max) + ";")
        if y_min is not None and y_max is not None:
            o.Execute("layer.y.from=" + str(y_min) + ";layer.y.to=" + str(y_max) + ";")
        return {"status": "ok"}

    def export_graph(self, path, fmt="png", width=1200, height=900):
        """Export graph. Tries expGraph then page.export as fallback."""
        path = os.path.abspath(path)
        o = self.connect()
        # Method 1: expGraph (older syntax)
        r1 = o.Execute('expGraph type:=' + fmt + ' fname:="' + path + '" width:=' + str(width) + ' height:=' + str(height) + ';')
        import time; time.sleep(0.5)
        if os.path.exists(path):
            return {"path": path, "format": fmt, "method": "expGraph"}
        # Method 2: page.export (Origin 2024)
        o.Execute('page.export(type:=' + fmt + ', filename:="' + path + '", width:=' + str(width) + ', height:=' + str(height) + ');')
        time.sleep(1)
        if os.path.exists(path):
            return {"path": path, "format": fmt, "method": "page.export"}
        return {"path": path, "format": fmt, "warning": "Export command executed but file not found - Origin may require manual export via Ctrl+E"}

    def save_project(self, path):
        """Save the current Origin project (OPJU)."""
        path = os.path.abspath(path)
        self.connect()
        self.execute('save -i "' + path + '";')
        return {"path": path, "exists": os.path.exists(path)}

    def new_worksheet(self, name=""):
        self.connect()
        if name:
            self.execute("newbook name:=" + name + " result:=bk$;")
        else:
            self.execute("newbook result:=bk$;")
        bk = self.execute("bk\$").strip()
        return {"workbook": bk}

    def set_column_data(self, col, data):
        self.connect()
        for i, val in enumerate(data, start=1):
            self.execute("col(" + str(col) + ")[" + str(i) + "] = " + str(val) + ";")
        return {"status": "ok", "col": col, "rows": len(data)}

    def get_column_data(self, col, start=1, end=-1):
        o = self.connect()
        if end == -1:
            end = int(o.Evaluate("wks.maxRows"))
        vals = []
        for i in range(start, end + 1):
            try:
                val = o.Evaluate("col(" + str(col) + ")[" + str(i) + "]")
                vals.append(val)
            except:
                vals.append(None)
        return {"col": col, "data": vals}


bridge = OriginBridge()

TOOLS = [
    {"name": "origin_connect", "description": "Connect to Origin Pro and make it visible. Call this first.",
     "inputSchema": {"type": "object", "properties": {}, "required": []}},
    {"name": "origin_import_csv", "description": "Import a CSV/TXT file into a new Origin worksheet.",
     "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "origin_create_plot", "description": "Create a line/scatter plot from columns (1-based indices).",
     "inputSchema": {"type": "object",
                     "properties": {"x_col": {"type": "integer"}, "y_col": {"type": "integer"},
                                    "plot_type": {"type": "string", "enum": ["line", "scatter", "line+symbol"]}},
                     "required": ["x_col", "y_col"]}},
    {"name": "origin_set_axes", "description": "Set axis labels and ranges for active graph.",
     "inputSchema": {"type": "object",
                     "properties": {"x_label": {"type": "string"}, "y_label": {"type": "string"},
                                    "x_min": {"type": "number"}, "x_max": {"type": "number"},
                                    "y_min": {"type": "number"}, "y_max": {"type": "number"}},
                     "required": []}},
    {"name": "origin_export_graph", "description": "Export active graph to PNG/SVG/PDF/JPG/TIF.",
     "inputSchema": {"type": "object",
                     "properties": {"path": {"type": "string"},
                                    "format": {"type": "string", "enum": ["png", "svg", "pdf", "jpg", "tif"]},
                                    "width": {"type": "integer"}, "height": {"type": "integer"}},
                     "required": ["path"]}},
    {"name": "origin_save_project", "description": "Save the current Origin project as OPJU file.",
     "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "origin_run_labtalk", "description": "Execute arbitrary LabTalk script in Origin.",
     "inputSchema": {"type": "object", "properties": {"script": {"type": "string"}}, "required": ["script"]}},
    {"name": "origin_new_worksheet", "description": "Create a new blank worksheet.",
     "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": []}},
    {"name": "origin_set_column_data", "description": "Set column values (1-based col index).",
     "inputSchema": {"type": "object",
                     "properties": {"col": {"type": "integer"}, "data": {"type": "array", "items": {"type": "number"}}},
                     "required": ["col", "data"]}},
    {"name": "origin_get_column_data", "description": "Read column data (1-based). Uses Evaluate for reliable float retrieval.",
     "inputSchema": {"type": "object",
                     "properties": {"col": {"type": "integer"}, "start": {"type": "integer"}, "end": {"type": "integer"}},
                     "required": ["col"]}},
]


def make_response(rid, result):
    return {"jsonrpc": "2.0", "id": rid, "result": result}


def make_error(rid, code, message):
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": message}}


def dispatch(name, args):
    if name == "origin_connect":
        bridge.connect()
        return {"status": "connected"}
    elif name == "origin_import_csv":
        return bridge.import_csv(args["path"])
    elif name == "origin_create_plot":
        return bridge.create_plot(args["x_col"], args["y_col"], args.get("plot_type", "line"))
    elif name == "origin_set_axes":
        return bridge.set_axes(
            args.get("x_label", ""), args.get("y_label", ""),
            args.get("x_min"), args.get("x_max"),
            args.get("y_min"), args.get("y_max"))
    elif name == "origin_export_graph":
        return bridge.export_graph(
            args["path"], args.get("format", "png"),
            args.get("width", 1200), args.get("height", 900))
    elif name == "origin_save_project":
        return bridge.save_project(args["path"])
    elif name == "origin_run_labtalk":
        return {"result": bridge.execute(args["script"])}
    elif name == "origin_new_worksheet":
        return bridge.new_worksheet(args.get("name", ""))
    elif name == "origin_set_column_data":
        return bridge.set_column_data(args["col"], args["data"])
    elif name == "origin_get_column_data":
        return bridge.get_column_data(args["col"], args.get("start", 1), args.get("end", -1))
    else:
        return {"error": "Unknown tool: " + name}


def handle(req):
    mid = req.get("id")
    method = req.get("method", "")
    params = req.get("params", {})
    if method == "initialize":
        return make_response(mid, {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "origin-mcp", "version": "1.1.0"}})
    elif method == "tools/list":
        return make_response(mid, {"tools": TOOLS})
    elif method == "tools/call":
        result = dispatch(params.get("name", ""), params.get("arguments", {}))
        content = [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]
        return make_response(mid, {"content": content})
    elif method == "notifications/initialized":
        return None
    elif method == "ping":
        return make_response(mid, {})
    else:
        return make_error(mid, -32601, "Method not found: " + method)


def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError:
            pass
        except Exception as e:
            err = make_error(None, -32603, str(e))
            sys.stdout.write(json.dumps(err, ensure_ascii=False) + "\n")
            sys.stdout.flush()
            traceback.print_exc(file=sys.stderr)


if __name__ == "__main__":
    main()