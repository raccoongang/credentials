import csv

with open('logos.csv', 'rbU') as csvfile:
    rows = csv.reader(csvfile)
    rows = list(rows)
    rows.pop(0)
    print '<tbody>'
    for row in rows:
        print '<tr><td>{key}</td><td>{name}</td><td><img src="{catalog_url}" /></td><td><img src="{organizations_url}" /></td></tr>'.format(
            key=row[0],
            name=row[1],
            catalog_url=row[2],
            organizations_url=row[3],
        )
    print '</tbody>'
