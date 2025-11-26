/**
 * Fuzzy Search Engine
 * 
 * Hey future me - this is a lightweight fuzzy matching algorithm! Works like Spotlight/Cmd+K search.
 * Matches partial strings even with typos or missing characters. Example: "bhrap" matches "Bohemian Rhapsody".
 * 
 * Algorithm: For each character in the search pattern, we try to find it in the target string (case-insensitive).
 * If all pattern chars are found in order (not necessarily consecutive), it's a match. We also calculate
 * a score based on consecutive character matches - closer matches = higher score.
 * 
 * This is way better than simple .includes() because users can type abbreviated or misspelled queries.
 */

class FuzzySearch {
    constructor(items, options = {}) {
        this.items = items;
        this.options = {
            keys: options.keys || ['name', 'title'],
            threshold: options.threshold || 0.3,
            caseSensitive: options.caseSensitive || false,
            shouldSort: options.shouldSort !== false,
            limit: options.limit || 10,
            ...options
        };
    }
    
    /**
     * Search items with fuzzy matching
     * @param {string} query - Search query
     * @returns {Array} Matched items with scores
     */
    search(query) {
        if (!query || query.trim() === '') {
            return this.items.slice(0, this.options.limit);
        }
        
        const pattern = this.options.caseSensitive ? query : query.toLowerCase();
        const results = [];
        
        for (const item of this.items) {
            const searchableText = this.getSearchableText(item);
            const match = this.fuzzyMatch(searchableText, pattern);
            
            if (match.isMatch && match.score >= this.options.threshold) {
                results.push({
                    item: item,
                    score: match.score,
                    matches: match.matches
                });
            }
        }
        
        // Sort by score (highest first)
        if (this.options.shouldSort) {
            results.sort((a, b) => b.score - a.score);
        }
        
        // Limit results
        return results.slice(0, this.options.limit);
    }
    
    /**
     * Get searchable text from item
     * @private
     */
    getSearchableText(item) {
        const texts = [];
        
        for (const key of this.options.keys) {
            const value = this.getNestedValue(item, key);
            if (value) {
                texts.push(String(value));
            }
        }
        
        const combined = texts.join(' ');
        return this.options.caseSensitive ? combined : combined.toLowerCase();
    }
    
    /**
     * Get nested value from object using dot notation
     * @private
     */
    getNestedValue(obj, path) {
        return path.split('.').reduce((current, prop) => current?.[prop], obj);
    }
    
    /**
     * Fuzzy match algorithm with scoring
     * @private
     */
    fuzzyMatch(text, pattern) {
        let textIndex = 0;
        let patternIndex = 0;
        let score = 0;
        let consecutiveMatches = 0;
        const matches = [];
        
        while (textIndex < text.length && patternIndex < pattern.length) {
            if (text[textIndex] === pattern[patternIndex]) {
                // Character match found
                matches.push(textIndex);
                consecutiveMatches++;
                
                // Bonus for consecutive matches (rewards exact substrings)
                score += 1 + (consecutiveMatches * 0.5);
                
                // Bonus for match at word boundary
                if (textIndex === 0 || text[textIndex - 1] === ' ') {
                    score += 2;
                }
                
                patternIndex++;
            } else {
                consecutiveMatches = 0;
            }
            textIndex++;
        }
        
        const isMatch = patternIndex === pattern.length;
        
        if (isMatch) {
            // Normalize score (0 to 1)
            const maxScore = pattern.length * 3; // Max possible score
            score = Math.min(score / maxScore, 1);
            
            // Penalty for long text (shorter matches are better)
            const lengthRatio = pattern.length / text.length;
            score *= (0.5 + (lengthRatio * 0.5));
        }
        
        return {
            isMatch,
            score: isMatch ? score : 0,
            matches
        };
    }
    
    /**
     * Highlight matched characters in text
     * @param {string} text - Original text
     * @param {Array} matches - Array of matched indices
     * @returns {string} HTML string with highlighted matches
     */
    static highlight(text, matches, highlightClass = 'fuzzy-match') {
        if (!matches || matches.length === 0) return text;
        
        let result = '';
        let lastIndex = 0;
        
        for (const index of matches) {
            result += text.substring(lastIndex, index);
            result += `<span class="${highlightClass}">${text[index]}</span>`;
            lastIndex = index + 1;
        }
        
        result += text.substring(lastIndex);
        return result;
    }
}

/**
 * Advanced Multi-Filter Manager
 * 
 * Hey future me - this manages multiple filter criteria at once! Users can filter by status, priority,
 * date range, tags, etc. All filters are ANDed together (item must match ALL active filters).
 * Each filter is a simple function that returns true/false. Clean and extensible!
 */
class FilterManager {
    constructor() {
        this.filters = new Map();
        this.onChangeCallbacks = [];
    }
    
    /**
     * Add or update a filter
     * @param {string} name - Filter identifier
     * @param {Function} filterFn - Function that returns true if item passes filter
     */
    addFilter(name, filterFn) {
        this.filters.set(name, filterFn);
        this.notifyChange();
    }
    
    /**
     * Remove a filter
     * @param {string} name - Filter identifier
     */
    removeFilter(name) {
        this.filters.delete(name);
        this.notifyChange();
    }
    
    /**
     * Clear all filters
     */
    clearAll() {
        this.filters.clear();
        this.notifyChange();
    }
    
    /**
     * Apply all active filters to items
     * @param {Array} items - Items to filter
     * @returns {Array} Filtered items
     */
    apply(items) {
        if (this.filters.size === 0) return items;
        
        return items.filter(item => {
            // Item must pass ALL filters (AND logic)
            for (const filterFn of this.filters.values()) {
                if (!filterFn(item)) return false;
            }
            return true;
        });
    }
    
    /**
     * Get count of active filters
     */
    getActiveCount() {
        return this.filters.size;
    }
    
    /**
     * Subscribe to filter changes
     */
    onChange(callback) {
        this.onChangeCallbacks.push(callback);
    }
    
    /**
     * Notify all subscribers
     * @private
     */
    notifyChange() {
        for (const callback of this.onChangeCallbacks) {
            callback(this.filters);
        }
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { FuzzySearch, FilterManager };
}
