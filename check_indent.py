with open('pbl/pp2.py', 'r') as f:
    lines = f.readlines()
    
# Find lines around draw_array end and start_sorting
for i, line in enumerate(lines[85:110], start=86):
    # Show the line with visible whitespace/tabs
    visible = line.replace('\t', '[TAB]').replace(' ', '·')
    print(f"{i}: {visible.rstrip()}")
