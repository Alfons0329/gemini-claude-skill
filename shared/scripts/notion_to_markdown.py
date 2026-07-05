#!/usr/bin/env python3
import os
import sys
import re
import json
import urllib.request
import urllib.error
import urllib.parse
import time

class NotionClient:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

    def request(self, path, method="GET", body=None):
        url = f"{self.base_url}/{path.lstrip('/')}"
        data = json.dumps(body).encode('utf-8') if body else None
        req = urllib.request.Request(url, data=data, headers=self.headers, method=method)
        
        # Handle rate limits (HTTP 429) with up to 3 retries
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req) as response:
                    return json.loads(response.read().decode('utf-8'))
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    retry_after = int(e.headers.get("Retry-After", 1))
                    time.sleep(retry_after)
                    continue
                try:
                    err_body = json.loads(e.read().decode('utf-8'))
                    err_msg = err_body.get("message", str(e))
                except Exception:
                    err_msg = str(e)
                raise Exception(f"Notion API error (HTTP {e.code}): {err_msg}")
            except Exception as e:
                raise Exception(f"Request failed: {str(e)}")
        raise Exception("Request failed: Rate limit retry limit reached.")

    def get_block_children(self, block_id):
        results = []
        start_cursor = None
        while True:
            path = f"blocks/{block_id}/children?page_size=100"
            if start_cursor:
                path += f"&start_cursor={urllib.parse.quote(start_cursor)}"
            res = self.request(path)
            results.extend(res.get("results", []))
            if not res.get("has_more"):
                break
            start_cursor = res.get("next_cursor")
        return results

    def get_page_title(self, page_id):
        try:
            page = self.request(f"pages/{page_id}")
            props = page.get("properties", {})
            for name, prop in props.items():
                if prop.get("type") == "title":
                    title_list = prop.get("title", [])
                    return "".join([t.get("plain_text", "") for t in title_list])
        except Exception:
            pass
        return "untitled"

    def get_database_title(self, database_id):
        try:
            db = self.request(f"databases/{database_id}")
            title_list = db.get("title", [])
            return "".join([t.get("plain_text", "") for t in title_list])
        except Exception:
            pass
        return "untitled-database"

    def get_breadcrumbs(self, page_id):
        path_parts = []
        current_id = page_id
        current_type = "page_id"
        
        depth = 0
        while current_id and current_type in ("page_id", "database_id") and depth < 5:
            if current_type == "page_id":
                try:
                    page = self.request(f"pages/{current_id}")
                    props = page.get("properties", {})
                    title = ""
                    for name, prop in props.items():
                        if prop.get("type") == "title":
                            title = "".join([t.get("plain_text", "") for t in prop.get("title", [])])
                            break
                    if not title:
                        title = "untitled"
                    path_parts.append(title)
                    
                    parent_info = page.get("parent", {})
                    current_type = parent_info.get("type")
                    current_id = parent_info.get(current_type) if current_type else None
                except Exception:
                    break
            elif current_type == "database_id":
                try:
                    db = self.request(f"databases/{current_id}")
                    title = "".join([t.get("plain_text", "") for t in db.get("title", [])])
                    if not title:
                        title = "database"
                    path_parts.append(title)
                    
                    parent_info = db.get("parent", {})
                    current_type = parent_info.get("type")
                    current_id = parent_info.get(current_type) if current_type else None
                except Exception:
                    break
            depth += 1
            
        path_parts.reverse()
        return path_parts

def extract_page_id(url_or_id):
    url_or_id = url_or_id.strip()
    parsed = urllib.parse.urlparse(url_or_id)
    path = parsed.path if parsed.path else url_or_id
    
    # Matches standard 32-char UUID or dashed UUID format (8-4-4-4-12)
    uuid_pattern = re.compile(r'([a-fA-F0-9]{8}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{12})')
    match = uuid_pattern.search(path)
    if match:
        raw_id = match.group(1).replace('-', '')
        return f"{raw_id[:8]}-{raw_id[8:12]}-{raw_id[12:16]}-{raw_id[16:20]}-{raw_id[20:]}"
    return None

def clean_breadcrumb_name(name):
    name = name.lower()
    name = re.sub(r'[^a-z0-9]+', '-', name)
    name = name.strip('-')
    return name

def rich_text_to_markdown(rich_text_array):
    md = []
    for rt in rich_text_array:
        text_content = rt.get("plain_text", "")
        annotations = rt.get("annotations", {})
        href = rt.get("href")
        
        if annotations.get("code"):
            text_content = f"`{text_content}`"
        else:
            if annotations.get("bold"):
                text_content = f"**{text_content}**"
            if annotations.get("italic"):
                text_content = f"*{text_content}*"
            if annotations.get("strikethrough"):
                text_content = f"~~{text_content}~~"
            if annotations.get("underline"):
                text_content = f"<u>{text_content}</u>"
        
        if href:
            text_content = f"[{text_content}]({href})"
        md.append(text_content)
    return "".join(md)

class MarkdownExporter:
    def __init__(self, client):
        self.client = client
        self.exclude_list = []

    def block_to_markdown(self, block, indent_level=0):
        block_type = block.get("type")
        if not block_type:
            return ""
            
        indent = " " * indent_level
        
        if block_type == "paragraph":
            text = rich_text_to_markdown(block["paragraph"].get("rich_text", []))
            return f"{indent}{text}\n\n"
            
        elif block_type == "heading_1":
            text = rich_text_to_markdown(block["heading_1"].get("rich_text", []))
            return f"# {text}\n\n"
            
        elif block_type == "heading_2":
            text = rich_text_to_markdown(block["heading_2"].get("rich_text", []))
            return f"## {text}\n\n"
            
        elif block_type == "heading_3":
            text = rich_text_to_markdown(block["heading_3"].get("rich_text", []))
            return f"### {text}\n\n"
            
        elif block_type == "bulleted_list_item":
            text = rich_text_to_markdown(block["bulleted_list_item"].get("rich_text", []))
            res = f"{indent}- {text}\n"
            if block.get("has_children"):
                try:
                    children = self.client.get_block_children(block["id"])
                    for child in children:
                        res += self.block_to_markdown(child, indent_level + 2)
                except Exception:
                    pass
            return res
            
        elif block_type == "numbered_list_item":
            text = rich_text_to_markdown(block["numbered_list_item"].get("rich_text", []))
            res = f"{indent}1. {text}\n"
            if block.get("has_children"):
                try:
                    children = self.client.get_block_children(block["id"])
                    for child in children:
                        res += self.block_to_markdown(child, indent_level + 2)
                except Exception:
                    pass
            return res
            
        elif block_type == "to_do":
            text = rich_text_to_markdown(block["to_do"].get("rich_text", []))
            checked = block["to_do"].get("checked", False)
            box = "[x]" if checked else "[ ]"
            res = f"{indent}- {box} {text}\n"
            if block.get("has_children"):
                try:
                    children = self.client.get_block_children(block["id"])
                    for child in children:
                        res += self.block_to_markdown(child, indent_level + 2)
                except Exception:
                    pass
            return res
            
        elif block_type == "toggle":
            text = rich_text_to_markdown(block["toggle"].get("rich_text", []))
            res = f"{indent}<details><summary>{text}</summary>\n\n"
            if block.get("has_children"):
                try:
                    children = self.client.get_block_children(block["id"])
                    for child in children:
                        res += self.block_to_markdown(child, indent_level + 2)
                except Exception:
                    pass
            res += f"{indent}</details>\n\n"
            return res
            
        elif block_type == "code":
            rich_texts = block["code"].get("rich_text", [])
            text = "".join([t.get("plain_text", "") for t in rich_texts])
            lang = block["code"].get("language", "")
            return f"```{lang}\n{text}\n```\n\n"
            
        elif block_type == "quote":
            text = rich_text_to_markdown(block["quote"].get("rich_text", []))
            res = f"{indent}> {text}\n"
            if block.get("has_children"):
                try:
                    children = self.client.get_block_children(block["id"])
                    for child in children:
                        res += self.block_to_markdown(child, indent_level + 2)
                except Exception:
                    pass
            return res + "\n"
            
        elif block_type == "callout":
            text = rich_text_to_markdown(block["callout"].get("rich_text", []))
            res = f"{indent}> [!NOTE]\n{indent}> {text}\n"
            if block.get("has_children"):
                try:
                    children = self.client.get_block_children(block["id"])
                    for child in children:
                        child_md = self.block_to_markdown(child, indent_level)
                        for line in child_md.splitlines():
                            res += f"{indent}> {line}\n"
                except Exception:
                    pass
            return res + "\n"
            
        elif block_type == "divider":
            return f"{indent}---\n\n"
            
        elif block_type == "image":
            img_type = block["image"].get("type")
            url = block["image"].get(img_type, {}).get("url", "")
            caption = rich_text_to_markdown(block["image"].get("caption", []))
            cap_str = caption if caption else "image"
            return f"{indent}![{cap_str}]({url})\n\n"
            
        elif block_type == "table":
            res = ""
            if block.get("has_children"):
                try:
                    rows = self.client.get_block_children(block["id"])
                    table_md_rows = []
                    for row in rows:
                        if row.get("type") == "table_row":
                            cells = row["table_row"].get("cells", [])
                            cell_mds = [rich_text_to_markdown(cell) for cell in cells]
                            table_md_rows.append(cell_mds)
                    
                    if table_md_rows:
                        col_count = len(table_md_rows[0])
                        res += f"{indent}| " + " | ".join(table_md_rows[0]) + " |\n"
                        res += f"{indent}| " + " | ".join(["---"] * col_count) + " |\n"
                        for row in table_md_rows[1:]:
                            row_cells = row + [""] * (col_count - len(row))
                            res += f"{indent}| " + " | ".join(row_cells[:col_count]) + " |\n"
                        res += "\n"
                except Exception:
                    pass
            return res
            
        elif block_type == "column_list":
            res = ""
            if block.get("has_children"):
                try:
                    cols = self.client.get_block_children(block["id"])
                    for col in cols:
                        if col.get("type") == "column" and col.get("has_children"):
                            col_children = self.client.get_block_children(col["id"])
                            for child in col_children:
                                res += self.block_to_markdown(child, indent_level)
                except Exception:
                    pass
            return res
            
        elif block_type == "child_page":
            title = block["child_page"].get("title", "Untitled Page")
            return f"{indent}*(See subpage: {title})*\n\n"
            
        elif block_type == "child_database":
            title = block["child_database"].get("title", "Untitled Database")
            return f"{indent}*(Database: {title})*\n\n"
            
        else:
            res = ""
            if block.get("has_children"):
                try:
                    children = self.client.get_block_children(block["id"])
                    for child in children:
                        res += self.block_to_markdown(child, indent_level)
                except Exception:
                    pass
            return res

    def should_exclude(self, page_id, title):
        normalized_title = title.lower().strip()
        for pattern in self.exclude_list:
            pat = pattern.lower().strip()
            if pat == page_id or pat == normalized_title:
                return True
        return False

    def export_page_recursive(self, page_id, title=None):
        if not title:
            title = self.client.get_page_title(page_id)
            
        if self.should_exclude(page_id, title):
            print(f"Excluding subpage: '{title}' ({page_id})")
            return ""

        print(f"Processing page: '{title}' ({page_id})...")
        
        # Start with the page title as an H1 header
        markdown_content = f"# {title}\n\n"
        
        children = []
        try:
            children = self.client.get_block_children(page_id)
        except Exception as e:
            print(f"Error fetching page content blocks for '{title}': {str(e)}")
            return markdown_content + f"*Error loading content: {str(e)}*\n\n"

        subpages_to_process = []
        for block in children:
            if block.get("type") == "child_page":
                sub_id = block["id"]
                sub_title = block["child_page"].get("title", "Untitled Page")
                if not self.should_exclude(sub_id, sub_title):
                    subpages_to_process.append((sub_id, sub_title))
                markdown_content += self.block_to_markdown(block)
            else:
                markdown_content += self.block_to_markdown(block)
                
        # Now recursively append subpage contents in depth-first order
        for sub_id, sub_title in subpages_to_process:
            subpage_md = self.export_page_recursive(sub_id, sub_title)
            if subpage_md:
                markdown_content += "\n---\n\n" + subpage_md

        return markdown_content

def main():
    if len(sys.argv) < 3:
        print("Usage: python notion_to_markdown.py <notion-page-url> <output-directory-or-file> [--exclude <comma-separated-titles-or-ids>]", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    out_path = sys.argv[2]
    
    exclude_list = []
    if "--exclude" in sys.argv:
        try:
            idx = sys.argv.index("--exclude")
            if idx + 1 < len(sys.argv):
                exclude_list = [item.strip() for item in sys.argv[idx + 1].split(",") if item.strip()]
        except Exception:
            pass

    token = os.environ.get("NOTION_TOKEN")
    if not token:
        print("Error: NOTION_TOKEN environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    page_id = extract_page_id(url)
    if not page_id:
        print(f"Error: Invalid or unparseable Notion page URL/ID: {url}", file=sys.stderr)
        sys.exit(1)

    print(f"Connecting to Notion API. Target Page ID: {page_id}")
    client = NotionClient(token)
    
    # 1. Get breadcrumbs to determine filename
    try:
        breadcrumbs = client.get_breadcrumbs(page_id)
        if not breadcrumbs:
            root_title = client.get_page_title(page_id)
            breadcrumbs = [root_title] if root_title else ["untitled"]
    except Exception as e:
        print(f"Warning: Failed to construct breadcrumbs: {str(e)}", file=sys.stderr)
        root_title = client.get_page_title(page_id)
        breadcrumbs = [root_title] if root_title else ["untitled"]

    cleaned_names = [clean_breadcrumb_name(name) for name in breadcrumbs if name]
    filename = "--".join(cleaned_names) + ".md"
    if not filename or filename == ".md":
        filename = "export.md"
        
    # 2. Determine target output filepath
    out_path = os.path.expanduser(out_path)
    if os.path.isdir(out_path):
        target_file = os.path.join(out_path, filename)
    else:
        if out_path.endswith(".md"):
            target_file = out_path
        else:
            os.makedirs(out_path, exist_ok=True)
            target_file = os.path.join(out_path, filename)

    print(f"Resolved output target file: {target_file}")
    
    # 3. Export content recursively
    exporter = MarkdownExporter(client)
    exporter.exclude_list = exclude_list
    
    try:
        final_markdown = exporter.export_page_recursive(page_id, breadcrumbs[-1])
    except Exception as e:
        print(f"Error executing Notion export: {str(e)}", file=sys.stderr)
        sys.exit(1)
        
    # 4. Save to target file
    try:
        parent_dir = os.path.dirname(target_file)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(final_markdown)
        print(f"Successfully exported Notion page content to {target_file}")
    except Exception as e:
        print(f"Error saving output file: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
