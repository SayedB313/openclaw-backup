# ClickUp MCP Tools Reference

## Quick Index

| Tool | Purpose | Read-Only |
|------|---------|-----------|
| `clickup_search` | Global search across workspace | ✅ |
| `clickup_get_workspace_hierarchy` | Spaces/folders/lists tree | ✅ |
| `clickup_get_task` | Task details by ID | ✅ |
| `clickup_create_task` | Create task in a list | ❌ |
| `clickup_update_task` | Update task properties | ❌ |
| `clickup_get_task_comments` | Get task comments | ✅ |
| `clickup_create_task_comment` | Add comment to task | ❌ |
| `clickup_attach_task_file` | Attach file to task | ❌ |
| `clickup_get_list` | Get list by ID or name | ✅ |
| `clickup_create_list` | Create list in space | ❌ |
| `clickup_create_list_in_folder` | Create list in folder | ❌ |
| `clickup_update_list` | Update list properties | ❌ |
| `clickup_get_folder` | Get folder by ID or name | ✅ |
| `clickup_create_folder` | Create folder in space | ❌ |
| `clickup_update_folder` | Update folder properties | ❌ |
| `clickup_add_tag_to_task` | Tag a task | ❌ |
| `clickup_remove_tag_from_task` | Untag a task | ❌ |
| `clickup_get_workspace_members` | List all members | ✅ |
| `clickup_find_member_by_name` | Find member by name/email | ✅ |
| `clickup_resolve_assignees` | Resolve names→IDs | ✅ |
| `clickup_get_task_time_entries` | Time entries for task | ✅ |
| `clickup_start_time_tracking` | Start timer | ❌ |
| `clickup_stop_time_tracking` | Stop timer | ❌ |
| `clickup_add_time_entry` | Manual time entry | ❌ |
| `clickup_get_current_time_entry` | Current running timer | ✅ |
| `clickup_get_chat_channels` | List chat channels | ✅ |
| `clickup_send_chat_message` | Send chat message | ❌ |
| `clickup_create_document` | Create doc in space/folder/list | ❌ |
| `clickup_list_document_pages` | List doc pages | ✅ |
| `clickup_get_document_pages` | Get page content | ✅ |
| `clickup_create_document_page` | Create page in doc | ❌ |
| `clickup_update_document_page` | Update page content | ❌ |

---

## Tool Details

### clickup_search

Global search across workspace. Finds tasks, docs, dashboards, attachments, whiteboards, chat.

```json
{
  "keywords": "string",
  "sort": [{"field": "created_at|updated_at", "direction": "asc|desc"}],
  "filters": {
    "assignees": ["user_id"],
    "creators": ["user_id"],
    "task_statuses": ["unstarted|active|done|closed|archived"],
    "location": {
      "projects": ["space_id"],
      "categories": ["folder_id"],
      "subcategories": ["list_id"]
    },
    "asset_types": ["task|doc|whiteboard|dashboard|attachment|chat"],
    "created_date_from": "YYYY-MM-DD",
    "created_date_to": "YYYY-MM-DD",
    "due_date_from": "YYYY-MM-DD",
    "due_date_to": "YYYY-MM-DD"
  },
  "count": 10,
  "cursor": "pagination_cursor"
}
```

### clickup_get_workspace_hierarchy

Returns space→folder→list tree. Pagination via `cursor`/`limit`. Control depth with `max_depth` (0=spaces, 1=+folders, 2=+lists).

```json
{
  "limit": 50,
  "max_depth": 2,
  "space_ids": ["id1"]
}
```

### clickup_create_task

**Required:** `name`, `list_id`

```json
{
  "name": "Task name",
  "list_id": "list_id",
  "description": "plain text",
  "markdown_description": "**markdown**",
  "status": "status_name",
  "priority": "urgent|high|normal|low",
  "due_date": "YYYY-MM-DD or YYYY-MM-DD HH:MM",
  "start_date": "YYYY-MM-DD or YYYY-MM-DD HH:MM",
  "parent": "parent_task_id",
  "tags": ["tag1"],
  "assignees": ["user_id"],
  "task_type": "Bug|Feature|etc",
  "custom_fields": [{"id": "field_id", "value": "val"}]
}
```

### clickup_get_task

**Required:** `task_id` (regular or custom ID like `DEV-1234`)

```json
{
  "task_id": "abc123",
  "subtasks": true,
  "detail_level": "summary|detailed"
}
```

### clickup_update_task

**Required:** `task_id` + at least one field to update. Same fields as create_task plus `time_estimate` (minutes as string).

### clickup_get_task_comments / clickup_create_task_comment

```json
// get
{"task_id": "abc", "start": 1703275200000, "start_id": "comment_id"}
// create
{"task_id": "abc", "comment_text": "text", "notify_all": false, "assignee": 12345}
```

### clickup_attach_task_file

Attach via base64 (`file_data` + `file_name`) or URL (`file_url`).

### Time Tracking

- `clickup_get_task_time_entries` — filter by `start_date`, `end_date`, `is_billable`
- `clickup_start_time_tracking` — `task_id` + optional `description`, `billable`, `tags`
- `clickup_stop_time_tracking` — no required params
- `clickup_add_time_entry` — `task_id` + `start` (YYYY-MM-DD HH:MM) + either `duration` (e.g. "1h 30m") or `end_time`
- `clickup_get_current_time_entry` — no params

### Lists & Folders

- `clickup_get_list` — by `list_id` or `list_name`
- `clickup_create_list` — `name` + `space_id` or `space_name`
- `clickup_create_list_in_folder` — `name` + `folder_id`
- `clickup_update_list` — `list_id` + fields to update
- `clickup_get_folder` — by `folder_id` or `folder_name` + space
- `clickup_create_folder` — `name` + `space_id` or `space_name`
- `clickup_update_folder` — `folder_id` + fields

### Documents

- `clickup_create_document` — `name`, `parent` (`{id, type}`), `visibility`, `create_page`
  - Parent types: 4=space, 5=folder, 6=list, 7=everything, 12=workspace
- `clickup_list_document_pages` — `document_id`, optional `max_page_depth`
- `clickup_get_document_pages` — `document_id`, `page_ids[]`, optional `content_format`
- `clickup_create_document_page` — `document_id`, `name`, `content`
- `clickup_update_document_page` — `document_id`, `page_id`, optional `content_edit_mode` (replace|append|prepend)

### Members

- `clickup_get_workspace_members` — no params
- `clickup_find_member_by_name` — `name_or_email`
- `clickup_resolve_assignees` — `assignees[]` (names/emails → IDs)

### Chat

- `clickup_get_chat_channels` — optional `cursor`
- `clickup_send_chat_message` — `channel_id`, `content`, optional `type` (message|post)

### Tags

- `clickup_add_tag_to_task` — `task_id`, `tag_name` (must exist in space)
- `clickup_remove_tag_from_task` — `task_id`, `tag_name`

---

## Workspace Structure (B's ClickUp)

| Space | Folders | Lists |
|-------|---------|-------|
| Mind/Health | — | Signal/Noise |
| Health & Everything Else | Health | Health Exercises |
| ILM | The Muslim Take, To Organize Better | Deen List |
| Oumafy | — | Foundation Oumafy List |
| Arki | Docs | Inbox |

**Workspace ID:** 9013663000

### Key IDs

- **ILM space:** 90138442298
- **Oumafy space:** 90134973836
- **Arki space:** 901313151685
- **Arki Inbox list:** 901325203728
- **Foundation Oumafy List:** 901307805676
- **Deen List:** 901311528628
- **The Muslim Take list:** 901307805452
