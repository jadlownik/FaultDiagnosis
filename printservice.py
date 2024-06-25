from tabulate import tabulate


class PrintService:
    def print_list(self, list, title=None):
        if title is not None:
            print(title)
        for ele in list:
            print(", ".join(map(str, ele)))

    def print_table(self, title,
                    all_minimal_conflicts, all_minimal_diagnosis,
                    minimal_conflicts, minimal_diagnosis,
                    gpt_minimal_conflicts, gpt_minimal_diagnosis):
        headers = ["Title",
                   "All minimal conflicts", "All minimal diagnosis",
                   "Minimal conflicts", "Minimal diagnosis",
                   "Minimal conflicts - GPT", "Minimal diagnosis - GPT",]

        formatted_all_minimal_conflicts = self._format_data(all_minimal_conflicts)
        formatted_all_minimal_diagnosis = self._format_data(all_minimal_diagnosis)
        formatted_minimal_conflicts = self._format_data(minimal_conflicts)
        formatted_minimal_diagnosis = self._format_data(minimal_diagnosis)
        formatted_gpt_minimal_conflicts = self._format_data(gpt_minimal_conflicts)
        formatted_gpt_minimal_diagnosis = self._format_data(gpt_minimal_diagnosis)

        data = [
            [title,
             formatted_all_minimal_conflicts, formatted_all_minimal_diagnosis,
             formatted_minimal_conflicts, formatted_minimal_diagnosis,
             formatted_gpt_minimal_conflicts, formatted_gpt_minimal_diagnosis]
        ]

        formatted_table = tabulate(data, headers=headers, tablefmt="pretty")
        print(formatted_table)

    def _format_data(self, data):
        formatted_data = []
        for sublist in data:
            formatted_data.append(", ".join(sublist))
        return "\n".join(formatted_data)
