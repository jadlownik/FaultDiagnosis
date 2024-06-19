class PrintService:
    def print_list(self, list, title=None):
        if title is not None:
            print(title)
        for ele in list:
            print(", ".join(map(str, ele)))
