# API Reference
_Auto-generated from /openapi.json — do not edit by hand._

---

## GET /

**Summary:** Root

**Response 200:** Any

---

## GET /notes/

**Summary:** List all notes

**Response 200:** Array of `NoteRead`
```json
[{ "id": integer, "title": string, "content": string }]
```

---

## POST /notes/

**Summary:** Create a note

**Request Body:** `NoteCreate` (required)
```json
{ "title": string (min 1), "content": string (min 1) }
```

**Response 201:** `NoteRead`
```json
{ "id": integer, "title": string, "content": string }
```

---

## GET /notes/search/

**Summary:** Search notes (case-insensitive across title and content)

**Query Parameters:**
| Name | Type | Required |
|------|------|----------|
| `q` | string \| null | No |

**Response 200:** Array of `NoteRead`
```json
[{ "id": integer, "title": string, "content": string }]
```

---

## GET /notes/{note_id}

**Summary:** Get a single note by ID

**Path Parameters:**
| Name | Type | Required |
|------|------|----------|
| `note_id` | integer | Yes |

**Response 200:** `NoteRead`
```json
{ "id": integer, "title": string, "content": string }
```

---

## PUT /notes/{note_id}

**Summary:** Update a note

**Path Parameters:**
| Name | Type | Required |
|------|------|----------|
| `note_id` | integer | Yes |

**Request Body:** `NoteUpdate` (required)
```json
{ "title": string (min 1) | null, "content": string (min 1) | null }
```

**Response 200:** `NoteRead`
```json
{ "id": integer, "title": string, "content": string }
```

---

## DELETE /notes/{note_id}

**Summary:** Delete a note

**Path Parameters:**
| Name | Type | Required |
|------|------|----------|
| `note_id` | integer | Yes |

**Response 204:** No content

---

## GET /action-items/

**Summary:** List all action items

**Response 200:** Array of `ActionItemRead`
```json
[{ "id": integer, "description": string, "completed": boolean }]
```

---

## POST /action-items/

**Summary:** Create an action item

**Request Body:** `ActionItemCreate` (required)
```json
{ "description": string }
```

**Response 201:** `ActionItemRead`
```json
{ "id": integer, "description": string, "completed": boolean }
```

---

## PUT /action-items/{item_id}/complete

**Summary:** Mark an action item as complete

**Path Parameters:**
| Name | Type | Required |
|------|------|----------|
| `item_id` | integer | Yes |

**Response 200:** `ActionItemRead`
```json
{ "id": integer, "description": string, "completed": boolean }
```
