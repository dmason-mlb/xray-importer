import json

with open('logs/folder_organization_report_20250731_131907.json') as f:
    data = json.load(f)

print('Preconditions analysis:')
print(f'Total preconditions: {len(data["preconditions"])}')

in_root = 0
in_folders = 0

for p in data['preconditions']:
    if p['current_folder'] == '/':
        in_root += 1
    else:
        in_folders += 1
        print(f"  {p['key']}: {p['current_folder']}")

print(f'\nIn root folder: {in_root}')
print(f'In other folders: {in_folders}')