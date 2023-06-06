class DataParser:
    def __init__(self, filename):
        self.fn = filename

    def createArray(self):
        lines = []
        with open(self.fn, 'r') as f:
            for line in f:
                split_line = line.split(":---:")
                added_dict = {"role": split_line[0].strip(), "content": split_line[1].strip()}
                lines.append(added_dict)
        return lines
    
    def addEntry(self, message, category):
        if category == "other":
            return
        with open(self.fn, 'a') as f:
            if category == "scam/fraud":
                user_entry = "user:---:" + message + "\n"
                assistant_entry = "assistant:---:Reported. This message has been flagged for: fraud.\n"
                f.write(user_entry)
                f.write(assistant_entry)
            if category == "harassment":
                user_entry = "user:---:" + message + "\n"
                assistant_entry = "assistant:---:Reported. This message has been flagged for: harassment.\n"
                f.write(user_entry)
                f.write(assistant_entry)
            if category == "violence":
                user_entry = "user:---:" + message + "\n"
                assistant_entry = "assistant:---:Reported. This message has been flagged for: violence.\n"
                f.write(user_entry)
                f.write(assistant_entry)
        return