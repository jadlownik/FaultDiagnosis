from tabulate import tabulate
import csv


class PrintService:
    def print_list(self, list, title=None):
        if title is not None:
            print(title)
        for ele in list:
            print(', '.join(map(str, ele)))

    def print_table(self, data):
        headers = ['Lp.', 'Title',
                   'Equations', 'Observations',
                #    'All minimal conflicts FDT', 'All minimal diagnosis FDT',
                #    'Minimal conflicts FDT', 'Minimal diagnosis FDT',
                   'All minimal conflicts', 'All minimal diagnosis',
                   'Minimal conflicts', 'Minimal diagnosis',
                   'Minimal conflicts - GPT', 'Minimal diagnosis - GPT']

        data.pop(-1)
        formatted_table = tabulate(data, headers=headers, tablefmt='pretty')
        print(formatted_table)

    def save_to_csv(self, data, filename='output.csv'):
        headers = ['Lp.', 'Title',
                   'Equations', 'Observations',
                #    'All minimal conflicts FDT', 'All minimal diagnosis FDT',
                #    'Minimal conflicts FDT', 'Minimal diagnosis FDT',
                   'All minimal conflicts', 'All minimal diagnosis',
                   'Minimal conflicts', 'Minimal diagnosis',
                   'Minimal conflicts - GPT', 'Minimal diagnosis - GPT']

        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(headers)  # Write headers
            writer.writerows(data)    # Write data rows

    def save_table_to_file(self, data, filename):
        headers = ['Lp.', 'Title',
                   'Equations', 'Observations',
                #    'All minimal conflicts FDT', 'All minimal diagnosis FDT',
                #    'Minimal conflicts FDT', 'Minimal diagnosis FDT',
                   'All minimal conflicts', 'All minimal diagnosis',
                   'Minimal conflicts', 'Minimal diagnosis',
                   'Minimal conflicts - GPT', 'Minimal diagnosis - GPT']

        data.pop(-1)

        formatted_table = tabulate(data, headers=headers, tablefmt='pretty')

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(formatted_table)
