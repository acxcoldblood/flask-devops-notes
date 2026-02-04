import re

def check_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    stack = []
    
    # Simple regex to find {% if ... %} and {% endif %}
    # Also {% for ... %} and {% endfor %} just in case
    # And {% block ... %} and {% endblock %}
    
    # We only really care about blocks that require closing.
    # Note: {% else %} and {% elif %} are not openers/closers of blocks in the stack sense, they just split the block.
    
    tag_pattern = re.compile(r'{%\s*(if|for|block|with|macro)\s+.*?\s*%}|{%\s*(endif|endfor|endblock|endwith|endmacro)\s*%}')
    
    with open('check_log.txt', 'w', encoding='utf-8') as log_file:
        def log(msg):
            print(msg)
            log_file.write(msg + '\n')

        for i, line in enumerate(lines):
            # check for comments {# ... #} - basic check
            clean_line = re.sub(r'{#.*?#}', '', line)
            
            matches = tag_pattern.finditer(clean_line)
            for match in matches:
                tag = match.group(0)
                tag_type = match.group(1) or match.group(2)
                
                # clean tag_type
                tag_type = tag_type.strip()
                
                if tag_type in ['if', 'for', 'block', 'with', 'macro']:
                    stack.append((tag_type, i + 1))
                    log(f"Line {i+1}: Opened {tag_type}")
                elif tag_type.startswith('end'):
                    expected = tag_type[3:]
                    if not stack:
                        log(f"Line {i+1}: ERROR - Found {tag_type} but stack is empty")
                        return
                    
                    last_type, last_line = stack.pop()
                    if last_type != expected:
                        log(f"Line {i+1}: ERROR - Found {tag_type} but expected end{last_type} (opened at line {last_line})")
                        return
                    log(f"Line {i+1}: Closed {expected}")

        if stack:
            log("ERROR: Unclosed blocks remaining:")
            for tag_type, line_num in stack:
                log(f"  {tag_type} opened at line {line_num}")
        else:
            log("SUCCESS: All blocks closed correctly.")

if __name__ == '__main__':
    check_file('d:/study/Devops Practice/Devops_notes_manager/templates/base.html')
