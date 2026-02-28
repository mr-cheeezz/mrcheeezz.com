## API Usage

Swagger above is the source of truth for endpoint paths, parameters, and responses.
Use this section for quick usage notes only.

### Route parameters
- Do not include `:` when replacing placeholders.
- Replace placeholders with real values.
- Example: use `roblox` not `:username`.

### Query string parameters
- Most query params are optional.
- Start query params with `?`.
- Example: `?show_user=true`
- Add more params with `&`.
- Example: `?show_user=true&use_display=true`

---

## Quick Bot Examples

### Roblox Presence
**Nightbot**
```text
$(urlfetch https://mrcheeezz.com/api/roblox/presence/{username})
```

**Fossabot**
```text
$(customapi https://mrcheeezz.com/api/roblox/presence/{username})
```

**StreamElements**
```text
${customapi.https://mrcheeezz.com/api/roblox/presence/{username}}
```

### Roblox Max Players (game-based)
**Nightbot**
```text
$(urlfetch https://mrcheeezz.com/api/roblox/max_players/game_based/$(query))
```

**Fossabot**
```text
$(customapi https://mrcheeezz.com/api/roblox/max_players/game_based/$(index1))
```

**StreamElements**
```text
${customapi.https://mrcheeezz.com/api/roblox/max_players/game_based/${1}}
```

---

## Spotify (Public User Linking)

Link your Spotify account here:

<a class="button-link" href="/spotify/api/connect/">Connect Spotify for API usage</a>

After linking, you will be redirected to a success page that shows your `user_id`.
Use that `user_id` in Spotify API endpoints.

### Example Endpoints

- `GET /api/spotify/now-playing/{user_id}`
- `GET /api/spotify/top-tracks/{user_id}?limit=5&time_range=short`
- `GET /api/spotify/last-song/{user_id}`

### Quick Example

```text
https://mrcheeezz.com/api/spotify/now-playing/{user_id}
```

---

For everything else, use the Swagger sections above.
