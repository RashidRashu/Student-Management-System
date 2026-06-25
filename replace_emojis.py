import os
import glob
import re

replacements = {
    '👨‍🎓': '<i data-lucide="users" class="icon-heading"></i>',
    '👨‍🏫': '<i data-lucide="graduation-cap" class="icon-heading"></i>',
    '🎓': '<i data-lucide="book-open" class="icon-heading"></i>',
    '📝': '<i data-lucide="clipboard-list" class="icon-heading"></i>',
    '📢': '<i data-lucide="megaphone" class="icon-heading"></i>',
    '🏠': '<i data-lucide="home" class="icon-heading"></i>',
    '📊': '<i data-lucide="bar-chart-2" class="icon-heading"></i>',
    '✏️': '<i data-lucide="edit" class="icon-inline"></i>',
    '➕': '<i data-lucide="plus" class="icon-heading"></i>',
    '🗑️': '<i data-lucide="trash-2" style="width:48px; height:48px; color:var(--danger);"></i>',
    '🛡️': '<i data-lucide="shield" class="icon-heading"></i>',
    '🔑': '<i data-lucide="key" class="icon-heading"></i>',
    '⚙': '<i data-lucide="settings" class="icon-heading"></i>',
    '🚪': '<i data-lucide="door-open" class="icon-heading"></i>'
}

templates_dir = r'c:\Users\HP\Desktop\aaaRashid\Django Project\studentms\students\templates\students'
for filepath in glob.glob(os.path.join(templates_dir, '*.html')):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Updated {os.path.basename(filepath)}')
