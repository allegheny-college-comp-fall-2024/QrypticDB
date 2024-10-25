# this file is how i will tag the decoy values
class TaggedData:
    def __init__(self, data, tag):
        self.data = data
        self._tag = tag  # the underscore one hides it

    def reveal_tag(self):
        return self._tag

    # when user requests items will ahve a final check to see if it's tagged with real


# Usage
item = TaggedData("my_data", "secret_tag")
print(item.data)  # Outputs: my_data
print(item.reveal_tag())  # Outputs: secret_tag
