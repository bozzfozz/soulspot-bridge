# Advanced Search Interface - User Guide

## Overview

The Advanced Search Interface provides a powerful and intuitive way to search for music tracks with advanced filtering, autocomplete suggestions, bulk actions, and search history management.

## Access the Search

Navigate to **Search** from the main navigation menu, or visit `/ui/search`.

## Features

### 1. Search Bar with Autocomplete

#### Basic Search
Type your search query in the search bar and press Enter or click the Search button.

**Search Tips:**
- Search by track name: "Bohemian Rhapsody"
- Search by artist: "Queen"
- Search by album: "A Night at the Opera"
- Combined search: "Queen Bohemian Rhapsody"

#### Autocomplete Suggestions
As you type (after 2+ characters), the system automatically shows up to 5 relevant suggestions from Spotify.

**How to Use:**
1. Start typing in the search bar
2. Wait 300ms for suggestions to appear
3. Click a suggestion or use arrow keys to navigate
4. Press Enter to select

**Keyboard Navigation:**
- `↓` / `↑` - Navigate through suggestions
- `Enter` - Select highlighted suggestion
- `Esc` - Close suggestions dropdown

---

### 2. Advanced Filters Panel

Located on the left sidebar, the filters panel allows you to refine your search results.

#### Quality Filter
Filter tracks by audio quality:
- **FLAC (Lossless)** - Highest quality, lossless compression
- **320kbps MP3** - High quality MP3
- **256kbps+** - Good quality (256kbps or higher)
- **Any Quality** - No quality restrictions (default)

#### Artist Filter
Enter an artist name to show only tracks by that artist. The filter updates results in real-time as you type.

#### Album Filter
Enter an album name to show only tracks from that album. Works with partial matches.

#### Duration Filter
Filter tracks by length:
- **Short** - Less than 3 minutes
- **Medium** - 3 to 5 minutes
- **Long** - More than 5 minutes

You can select multiple duration ranges.

#### Clear All Filters
Click "Clear All" at the top of the filters panel to reset all filters to default.

---

### 3. Search Results

#### Result Cards
Each track is displayed in an expandable card showing:
- Track name
- Artist(s)
- Album name
- Duration
- Checkbox for bulk selection
- Action buttons (Download, Spotify link)

#### Expand Details
Click the down arrow icon (▼) on any track to see:
- Track ID
- Spotify URI
- Full duration
- Complete album information

#### Individual Actions
Each track card has:
- **Download** button - Download the track immediately
- **Spotify** button - Open the track in Spotify
- **Checkbox** - Add to bulk selection

---

### 4. Bulk Actions

Select multiple tracks to perform batch operations.

#### How to Select Tracks
1. **Individual Selection:** Click the checkbox on any track card
2. **Select All:** Check the "Select All" checkbox in the bulk actions bar
3. **Clear Selection:** Click "Clear Selection" button

#### Bulk Actions Bar
When you select one or more tracks, a blue bar appears at the top showing:
- Number of tracks selected
- Select All checkbox
- Download Selected button
- Clear Selection button

#### Bulk Download
Click "Download Selected" to download all selected tracks at once. The system will:
1. Queue all downloads
2. Show progress toasts
3. Display success/failure count
4. Clear the selection automatically

---

### 5. Search History

Your recent searches are saved for quick access.

#### Features
- **Automatic Saving:** Every search is automatically saved
- **Maximum 10 Searches:** Only the 10 most recent searches are kept
- **No Duplicates:** Repeated searches won't create duplicates
- **Click to Search:** Click any history item to repeat that search
- **Persistent:** History is saved in your browser (localStorage)

#### Clear History
Click the "Clear" button in the Search History panel to remove all saved searches.

---

## Keyboard Shortcuts

### Global
- `Tab` - Navigate between elements
- `Enter` - Activate buttons, submit search
- `Esc` - Close autocomplete dropdown

### Search Bar
- `Ctrl/Cmd + K` - Focus search input (when implemented)
- `↓` / `↑` - Navigate autocomplete suggestions
- `Enter` - Submit search or select suggestion

### Results
- `Tab` - Navigate between track cards
- `Space` - Toggle checkbox on focused track
- `Enter` - Expand/collapse track details

---

## Tips & Best Practices

### Effective Searching
1. **Be Specific:** Include both artist and track name for best results
2. **Use Filters:** Narrow down results with quality and duration filters
3. **Check History:** Reuse previous searches quickly
4. **Bulk Download:** Select multiple tracks to save time

### Quality Selection
- **For Archival:** Choose FLAC for lossless quality
- **For Most Uses:** 320kbps MP3 provides excellent quality
- **For Compatibility:** "Any Quality" finds more results

### Managing Results
1. Use filters AFTER searching to refine results
2. Expand track details to verify it's the right version
3. Check the Spotify link if unsure about the track
4. Use bulk download for albums or playlists

---

## Troubleshooting

### No Autocomplete Suggestions
**Problem:** Suggestions don't appear when typing

**Solutions:**
- Ensure you're authenticated with Spotify (check /ui/auth)
- Type at least 2 characters
- Wait 300ms after stopping typing
- Check browser console for errors

### Search Returns No Results
**Problem:** Search completes but shows "No Results Found"

**Solutions:**
- Try a different search query
- Remove some filters
- Check spelling
- Use more general terms (e.g., artist name only)

### Download Fails
**Problem:** Download button shows error

**Solutions:**
- Ensure you're authenticated with Spotify
- Check if the track is available in your region
- Verify your connection to the Soulseek network
- Try downloading a different quality

### Filters Not Working
**Problem:** Filters don't affect results

**Solutions:**
- Perform a search first (filters only work on results)
- Clear filters and try again
- Refresh the page
- Check browser console for errors

---

## Technical Details

### Browser Storage
The search interface uses **localStorage** to save:
- Search history (max 10 entries)
- No personal data or credentials are stored

### Data Privacy
- All searches go directly to Spotify API
- Search history stays in your browser
- No search data is sent to external servers
- Clear your browser data to remove history

### Browser Compatibility
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Requires JavaScript enabled

---

## Examples

### Example 1: Find a Specific Track
```
1. Type "Bohemian Rhapsody Queen" in search bar
2. Select from autocomplete or press Enter
3. Results show all versions of the track
4. Use Quality filter to find FLAC version
5. Click Download button
```

### Example 2: Bulk Download an Album
```
1. Search for "Dark Side of the Moon"
2. Apply Artist filter: "Pink Floyd"
3. Click "Select All" checkbox
4. Click "Download Selected"
5. All tracks begin downloading
```

### Example 3: Filter by Duration
```
1. Search for "Metallica"
2. Apply Duration filter: "Long (> 5 min)"
3. Results show only songs longer than 5 minutes
4. Perfect for finding epic tracks!
```

---

## Frequently Asked Questions

### Q: Can I search without Spotify authentication?
**A:** No, the search uses Spotify's API which requires authentication. Visit /ui/auth to connect your account.

### Q: How many tracks can I select for bulk download?
**A:** There's no hard limit, but downloading too many tracks at once may impact performance. We recommend batches of 20-30 tracks.

### Q: Will my search history sync across devices?
**A:** No, search history is stored locally in your browser. Each device maintains its own history.

### Q: Can I export search results?
**A:** Not currently, but you can select and download all results using the bulk actions feature.

### Q: What happens if a download fails?
**A:** The system will show an error message. You can retry individual tracks or check the Downloads page for status.

---

## Related Documentation

- [Keyboard Navigation Guide](keyboard-navigation.md) - Full keyboard shortcuts
- [UI/UX Visual Guide](ui-ux-visual-guide.md) - Component showcase
- [Downloads Guide](downloads.md) - Managing your downloads

---

## Feedback & Support

If you encounter issues or have suggestions for improving the search interface:
1. Check the Troubleshooting section above
2. Review browser console for error messages
3. Report issues through the project's GitHub repository

---

**Version:** 1.0  
**Last Updated:** 2025-11-13  
**Status:** Active
