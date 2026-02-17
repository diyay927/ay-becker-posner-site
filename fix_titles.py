#!/usr/bin/env python3
"""
Fix titles in existing Becker-Posner archive.
Run this in the becker-posner-site folder.
"""

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

def extract_title_from_html(html_content, url):
    """Extract a better title from HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    title = None
    
    # Try specific post title selectors first
    title_selectors = [
        'h2.entry-title a',
        'h2.entry-title',
        'h1.entry-title a',
        'h1.entry-title',
        '.entry-header h2 a',
        '.entry-header h2',
        '.entry-header h1',
        '.post-title a',
        '.post-title',
        'article h1',
        'article h2',
    ]
    
    for selector in title_selectors:
        title_elem = soup.select_one(selector)
        if title_elem:
            title = title_elem.get_text(strip=True)
            if title and title != "The Becker-Posner Blog" and len(title) > 5:
                break
            else:
                title = None
    
    # If still no title, try to extract from URL
    if not title:
        url_match = re.search(r'/\d{4}/\d{2}/([^/]+?)(?:\.html)?$', url)
        if url_match:
            title = url_match.group(1).replace('-', ' ').replace('_', ' ').title()
    
    # Last resort - use page title but clean it
    if not title:
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            title = re.sub(r'\s*[-|:]\s*The Becker-Posner Blog.*$', '', title, flags=re.IGNORECASE)
            title = re.sub(r'^The Becker-Posner Blog\s*[-|:]\s*', '', title, flags=re.IGNORECASE)
    
    if not title or title == "The Becker-Posner Blog":
        title = "Untitled Post"
    
    # Clean author from end of title
    title = re.sub(r'\s*[-–—]\s*[Bb]ecker\s*$', '', title)
    title = re.sub(r'\s*[-–—]\s*[Pp]osner\s*$', '', title)
    
    return title.strip()


def extract_author(title, url, html_content):
    """Determine author from title, URL, or content."""
    title_lower = title.lower() if title else ""
    url_lower = url.lower()
    
    # Check URL for author (most reliable for this blog)
    if "becker" in url_lower:
        return "Gary Becker"
    elif "posner" in url_lower:
        return "Richard Posner"
    
    # Check title
    if "becker" in title_lower:
        return "Gary Becker"
    elif "posner" in title_lower:
        return "Richard Posner"
    
    return "Unknown"


def fix_post_html(post_path, new_title, author):
    """Update the HTML file with the new title."""
    with open(post_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Update the <title> tag
    html = re.sub(
        r'<title>.*?</title>',
        f'<title>{new_title} - Becker-Posner Blog Archive</title>',
        html
    )
    
    # Update the <h1> tag
    html = re.sub(
        r'<h1>.*?</h1>',
        f'<h1>{new_title}</h1>',
        html,
        count=1
    )
    
    with open(post_path, 'w', encoding='utf-8') as f:
        f.write(html)


def main():
    posts_dir = Path("posts")
    data_dir = Path("data")
    
    if not posts_dir.exists():
        print("Error: posts/ folder not found. Run this from becker-posner-site folder.")
        return
    
    # Load existing posts.json
    posts_json_path = data_dir / "posts.json"
    with open(posts_json_path, 'r', encoding='utf-8') as f:
        posts = json.load(f)
    
    print(f"Processing {len(posts)} posts...")
    
    fixed_count = 0
    for post in posts:
        filename = post.get('filename')
        if not filename:
            continue
            
        post_path = posts_dir / f"{filename}.html"
        if not post_path.exists():
            continue
        
        # Read the HTML
        with open(post_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Get the original URL (stored in wayback_url)
        wayback_url = post.get('wayback_url', '')
        # Extract original URL from wayback URL
        url_match = re.search(r'web\.archive\.org/web/\d+/(.*)', wayback_url)
        original_url = url_match.group(1) if url_match else ''
        
        # Extract better title
        old_title = post.get('title', '')
        new_title = extract_title_from_html(html_content, original_url)
        
        # Get author
        author = extract_author(new_title, original_url, html_content)
        
        # Check if we improved the title
        if old_title == "The Becker-Posner Blog" or old_title == "Untitled Post" or len(old_title) < 10:
            if new_title != "The Becker-Posner Blog" and new_title != "Untitled Post":
                print(f"  Fixed: '{old_title}' -> '{new_title}'")
                post['title'] = new_title
                post['author'] = author
                fix_post_html(post_path, new_title, author)
                fixed_count += 1
        elif author != post.get('author'):
            # Update author even if title is okay
            post['author'] = author
    
    # Save updated posts.json
    with open(posts_json_path, 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2)
    
    print(f"\nDone! Fixed {fixed_count} titles.")
    print("Now run: git add . && git commit -m 'Fix titles' && git push")


if __name__ == "__main__":
    main()
